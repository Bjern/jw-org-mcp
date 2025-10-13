"""MCP server implementation for JW.Org."""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from .client import JWOrgClient
from .config import settings
from .exceptions import JWOrgMCPError

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create MCP server
app = Server("jw-org-mcp")

# Create client instance
client = JWOrgClient()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_content",
            description=(
                "Search JW.Org content including articles, videos, publications, "
                "audio, and scriptures. Extracts meaningful search terms from natural "
                "language queries."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The search query. Can be natural language like "
                            "'What does the Bible say about love?' The tool will "
                            "extract 'love' as the search term."
                        ),
                    },
                    "filter": {
                        "type": "string",
                        "description": "Content type filter",
                        "enum": ["all", "publications", "videos", "audio", "bible", "indexes"],
                        "default": "all",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (E=English, S=Spanish, etc)",
                        "default": "E",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_article",
            description=(
                "Retrieve full article content from a JW.Org URL. "
                "Returns the article text with paragraphs and scripture references."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The article URL from wol.jw.org",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="get_scripture",
            description=(
                "Get scripture text by reference (e.g., 'John 3:16', '1 Thessalonians 5:3'). "
                "Returns the scripture text and reference."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "string",
                        "description": "Scripture reference (e.g., 'John 3:16')",
                    },
                    "translation": {
                        "type": "string",
                        "description": "Bible translation code",
                        "default": "nwtsty",
                    },
                },
                "required": ["reference"],
            },
        ),
        Tool(
            name="get_cache_stats",
            description="Get cache statistics including hit rate and entry count.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_content":
            return await _handle_search(arguments)
        elif name == "get_article":
            return await _handle_get_article(arguments)
        elif name == "get_scripture":
            return await _handle_get_scripture(arguments)
        elif name == "get_cache_stats":
            return await _handle_cache_stats()
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]
    except JWOrgMCPError as e:
        logger.error(f"Tool error: {e}")
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}",
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}",
            )
        ]


async def _handle_search(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle search_content tool call."""
    query = arguments.get("query", "")
    filter_type = arguments.get("filter", "all")
    language = arguments.get("language", "E")
    limit = arguments.get("limit", 10)

    logger.info(f"Searching: query={query}, filter={filter_type}, language={language}")

    response, metadata = await client.search(
        query=query,
        filter_type=filter_type,
        language=language,
        limit=limit,
    )

    # Format results
    result_text = f"# Search Results for '{response.query}'\n\n"
    result_text += f"**Total Results:** {response.total}\n"
    result_text += f"**Filter:** {response.filter}\n"
    result_text += f"**Source:** {metadata.source_url}\n"
    result_text += f"**Timestamp:** {metadata.timestamp.isoformat()}\n"
    result_text += f"**Cached:** {metadata.cache_hit}\n\n"

    if not response.results:
        result_text += "No results found.\n"
    else:
        result_text += f"## Results (showing {len(response.results)} of {response.total})\n\n"
        for i, result in enumerate(response.results, 1):
            result_text += f"### {i}. {result.title}\n\n"
            if result.context:
                result_text += f"**Source:** {result.context}\n\n"
            result_text += f"{result.snippet}\n\n"
            result_text += f"**URL:** {result.url}\n\n"
            result_text += "---\n\n"

    return [TextContent(type="text", text=result_text)]


async def _handle_get_article(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_article tool call."""
    url = arguments.get("url", "")

    logger.info(f"Fetching article: {url}")

    article, metadata = await client.get_article(url)

    # Format article
    result_text = f"# {article.title}\n\n"
    result_text += f"**Source:** {metadata.source_url}\n"
    result_text += f"**Timestamp:** {metadata.timestamp.isoformat()}\n"
    result_text += f"**Cached:** {metadata.cache_hit}\n\n"

    result_text += "## Content\n\n"
    for para in article.paragraphs:
        result_text += f"{para}\n\n"

    if article.references:
        result_text += "## Scripture References\n\n"
        for ref in article.references:
            result_text += f"- {ref}\n"

    return [TextContent(type="text", text=result_text)]


async def _handle_get_scripture(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_scripture tool call."""
    reference = arguments.get("reference", "")
    translation = arguments.get("translation", "nwtsty")

    logger.info(f"Fetching scripture: {reference}")

    scripture, metadata = await client.get_scripture(reference, translation)

    # Format scripture
    result_text = f"# {scripture['reference']}\n\n"
    result_text += f"{scripture['text']}\n\n"
    result_text += f"**Source:** {metadata.source_url}\n"
    result_text += f"**Timestamp:** {metadata.timestamp.isoformat()}\n"

    return [TextContent(type="text", text=result_text)]


async def _handle_cache_stats() -> list[TextContent]:
    """Handle get_cache_stats tool call."""
    stats = client.get_cache_stats()

    result_text = "# Cache Statistics\n\n"
    result_text += f"**Entries:** {stats['entries']}\n"
    result_text += f"**Hits:** {stats['hits']}\n"
    result_text += f"**Misses:** {stats['misses']}\n"
    result_text += f"**Hit Rate:** {stats['hit_rate']}%\n"

    return [TextContent(type="text", text=result_text)]


async def cleanup() -> None:
    """Cleanup resources on shutdown."""
    logger.info("Shutting down JW.Org MCP server")
    await client.close()
