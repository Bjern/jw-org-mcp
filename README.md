# JW.Org MCP Tool

[![Tests](https://github.com/Bjern/jw-org-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/Bjern/jw-org-mcp/actions/workflows/tests.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Model Context Protocol (MCP) server that provides controlled, verifiable access to content from jw.org for AI applications and LLM integrations.

## Overview

The JW.Org MCP Tool ensures that scriptural and doctrinal information comes exclusively from official jw.org sources, eliminating the risk of hallucinations or external contamination when handling religious queries. This tool acts as a trusted intermediary between AI applications and jw.org content.

## Features

- **Trusted Source Enforcement**: Fetches data strictly from jw.org domains
- **Comprehensive Search**: Search across articles, videos, publications, audio, and scriptures
- **Intelligent Query Parsing**: Extracts meaningful search terms from natural language queries
- **Full Article Retrieval**: Get complete article content with scripture references
- **Scripture Lookup**: Direct scripture reference search
- **Performance Optimized**: 15-minute caching, Brotli compression, async operations
- **Structured Output**: Machine-readable responses with verification metadata

## Installation

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for package management

### Install with uv

```bash
# Clone the repository
git clone https://github.com/Bjern/jw-org-mcp.git
cd jw-org-mcp

# Install dependencies
uv sync

# Install with development dependencies
uv sync --group dev
```

## Usage

### Running the MCP Server

```bash
uv run jw-org-mcp
```

The server runs in stdio mode and communicates via the Model Context Protocol.

### Adding to Claude Desktop

To use this MCP server with Claude Desktop, add it to your Claude configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "jw-org": {
      "command": "uv",
      "args": [
        "--directory",
        "E:\\Projects\\Python\\jw-org-mcp",
        "run",
        "jw-org-mcp"
      ]
    }
  }
}
```

**Note:** Replace `E:\\Projects\\Python\\jw-org-mcp` with the actual path to your project directory. On Windows, use double backslashes (`\\`) in the path.

>WINDOWS -> FEB 2026 -> If you are using this as a custom connector MCP tool, then, you might find that the Claude Desktop app on Windows is not working properly. The app does not launch, etc...
>
>This is because, there is a bug that the new app (Since Feb 2026) has changed it's default folder to the MSIX virtualized path:
>
>C:\Users\{username}\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
>
> Or paste %localappdata%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude in the windows Run dialog.

After saving the configuration:
1. Restart Claude Desktop
2. The JW.Org MCP tools will be available in your conversations
3. Look for tools like `search_content`, `get_article`, and `get_scripture`

### Configuration

Configuration is done via environment variables with the prefix `JWORG_MCP_`:

```bash
# Cache settings
export JWORG_MCP_CACHE_TTL_SECONDS=900  # 15 minutes (default)
export JWORG_MCP_ENABLE_CACHE=true

# Request settings
export JWORG_MCP_REQUEST_TIMEOUT=30
export JWORG_MCP_MAX_RETRIES=3

# Search settings
export JWORG_MCP_DEFAULT_LANGUAGE=E  # English
export JWORG_MCP_DEFAULT_SEARCH_LIMIT=10

# Logging
export JWORG_MCP_LOG_LEVEL=INFO
```

## MCP Tools

### search_content

Search JW.Org content across multiple types.

**Parameters:**
- `query` (required): Search query - can be natural language
- `filter` (optional): Content type - `all`, `publications`, `videos`, `audio`, `bible`, `indexes` (default: `all`)
- `language` (optional): Language code - `E` for English, `S` for Spanish, etc. (default: `E`)
- `limit` (optional): Maximum results (default: 10)

**Example:**
```json
{
  "query": "What does the Bible say about love?",
  "filter": "all",
  "limit": 5
}
```

The query parser automatically extracts "love" as the search term.

### get_article

Retrieve full article content from a jw.org URL. Supports both direct article URLs and publication finder URLs.

When given a publication-level URL (e.g., a magazine issue), the tool returns a table of contents listing individual articles with their direct URLs, which can then be fetched individually.

**Parameters:**
- `url` (required): Article URL from wol.jw.org or a publication finder URL

**Example:**
```json
{
  "url": "https://wol.jw.org/en/wol/d/r1/lp-e/1985720"
}
```

### get_scripture

Get scripture text by reference.

**Parameters:**
- `reference` (required): Scripture reference (e.g., "John 3:16", "1 Thessalonians 5:3")
- `translation` (optional): Bible translation code (default: "nwtsty")

**Example:**
```json
{
  "reference": "John 3:16"
}
```

### get_cache_stats

Get cache statistics including hit rate and entry count.

**Parameters:** None

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv sync --group dev

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=jw_org_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_parser.py
```

### Code Quality

```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy src/

# Security scan
uv run bandit -r src/ -c pyproject.toml
```

### Project Structure

```
jw-org-mcp/
├── .github/
│   └── workflows/
│       └── tests.yml         # CI pipeline (lint, type check, security, tests)
├── src/
│   └── jw_org_mcp/
│       ├── __init__.py       # Entry point
│       ├── auth.py           # Authentication & CDN discovery
│       ├── cache.py          # Caching layer
│       ├── client.py         # JW.Org API client
│       ├── config.py         # Configuration management
│       ├── exceptions.py     # Custom exceptions
│       ├── models.py         # Data models
│       ├── parser.py         # Content parsers
│       └── server.py         # MCP server implementation
├── tests/                    # Test suite
├── docs/                     # Documentation
├── pyproject.toml            # Project configuration
└── README.md
```

## Architecture

### Authentication Flow

1. Discover CDN URL from jw.org homepage
2. Request JWT token from CDN endpoint
3. Use token for authenticated API requests
4. Automatically refresh token before expiration

### Search Flow

1. Parse user query to extract search terms
2. Check cache for existing results
3. Make authenticated API request if cache miss
4. Parse and structure response
5. Cache results for 15 minutes
6. Return structured data

### Content Retrieval

1. Fetch HTML content from wol.jw.org
2. If the page is a publication index (table of contents), extract article links and return them
3. Otherwise, parse article structure (title, paragraphs, references)
4. Extract clean text without HTML artifacts
5. Cache parsed content
6. Return structured article data

## API Response Format

All responses include metadata for verification:

```json
{
  "data": {
    // Response-specific data
  },
  "metadata": {
    "source_domain": "jw.org",
    "source_url": "https://...",
    "timestamp": "2024-01-01T00:00:00Z",
    "query_params": {},
    "cache_hit": false
  }
}
```

## Performance

- **Response Time**: < 2 seconds for search queries (cached: < 100ms)
- **Cache TTL**: 15 minutes (configurable)
- **Compression**: Brotli for all API requests
- **Concurrency**: Async I/O with connection pooling

## Error Handling

The tool provides graceful error handling with specific exception types:

- `AuthenticationError`: JWT token issues
- `CDNDiscoveryError`: CDN discovery failures
- `SearchError`: Search operation failures
- `ContentRetrievalError`: Content fetch failures
- `ParseError`: Content parsing failures

All errors are logged and returned with descriptive messages.

## Security & Privacy

- **No PII Logging**: No personally identifiable information is logged
- **HTTPS Only**: All external requests use HTTPS
- **Token Security**: JWT tokens are managed securely in memory
- **Input Validation**: All user inputs are sanitized

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Support

For issues and questions:
- GitHub Issues: https://github.com/Bjern/jw-org-mcp/issues
- Documentation: See `docs/` folder

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses the Model Context Protocol standard
- Provides verified access to jw.org content
