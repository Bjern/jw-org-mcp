# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**JW.Org MCP Tool** is a Model Context Protocol (MCP) server that provides controlled, verifiable access to jw.org content. It ensures LLMs receive accurate, official doctrinal information exclusively from jw.org, preventing hallucinations and external contamination.

## Development Setup

### Package Management
This project uses **[uv](https://github.com/astral-sh/uv)** for package management and virtual environment setup.

### Required Python Version
- Python 3.13+

### Key Dependencies
- **fastmcp**: Framework for building MCP tools
- **requests**: HTTP client for jw.org content retrieval
- **brotli**: Compression support for bandwidth optimization
- **pytest**: Testing framework
- **ruff**: Linting and code formatting

## Common Commands

### Running the MCP Server
```bash
uv run jw-org-mcp
```

### Running Tests
```bash
uv run pytest
```

### Linting/Formatting
```bash
uv run ruff check .
uv run ruff format .
```

## Architecture

### JW.Org API Integration Flow

The MCP server interfaces with jw.org's search infrastructure through a multi-step authentication and query process:

1. **CDN Discovery**: Fetch https://www.jw.org/en/ (once) to discover the CDN base URL (pattern: `*.jw-cdn.org`)
2. **Authentication**: Obtain JWT token from `{cdn_base_url}/tokens/jworg.jwt`
3. **Search API**: Make authenticated requests to `{cdn_base_url}/apis/search/results/{language}/{filter}?q={query}`

### Search API Structure

**Endpoint Pattern**: `https://b.jw-cdn.org/apis/search/results/{LANGUAGE}/{FILTER}?q={QUERY}`

**Language Codes**: Use `E` for English (other language codes available)

**Filter Types**:
- `all` - All content (articles, videos, publications, etc.)
- `videos` - Video content only
- `publications` - Publication articles only
- `audio` - Audio content (music, dramas)
- `bible` - Scripture verses
- `indexes` - Publication index subjects

**Required Headers**:
- `Accept: application/json; charset=utf-8`
- `Authorization: Bearer {jwt_token}`
- `X-Client-ID: {uuid}`
- `Referer: https://www.jw.org/`

### Response Processing

**For `all` filter**: Results contain nested structure with `type: "group"` and nested `results` arrays. Extract articles with:
- Path: `results[].results[]` where `subtype == "article"`
- Fields: `title`, `snippet`, `links.wol` (article URL)

**For other filters**: Flat structure in `results[]` array with direct access to `title`, `snippet`, and `links`

### Article Content Extraction

Articles are hosted on `wol.jw.org`. Extract content from:
- Main container: `<article id="article" class="article...">`
- Paragraphs: `<p id="p1" data-pid="1"...>` (ids increment: p1, p2, p3...)
- Ignore `<span>` highlighting tags in paragraphs

## Code Quality Standards

- **Style**: PEP8 compliance required
- **Type Hints**: All functions must include type annotations (mypy compliance)
- **Testing**: Minimum 80% test coverage
- **Async I/O**: Use async patterns for network calls to support scaling
- **No JavaScript**: Raw HTML requests only—no browser automation

## MCP Tool Design Principles

### Query Parameter Design

When implementing MCP endpoints, design parameters that help LLMs extract meaningful search terms:

**Example**: User asks "what does the bible say about peace and security?"
- Extract subject: `"peace and security"` (not "what does the bible say")
- The answer interpretation comes from result analysis, not the query

### Response Format Requirements

All MCP responses should include:
- **Reference URL**: For content verification
- **Timestamp**: When data was fetched
- **Source Domain**: Confirm `jw.org` or `jw-cdn.org`

### Error Handling

- Graceful fallbacks if pages/endpoints are missing
- No persistent logging of queries or PII
- Health check endpoint for MCP readiness validation

## Project Structure

```
jw-org-mcp/
├── src/
│   └── jw_org_mcp/
│       └── __init__.py         # Entry point with main() function
├── docs/
│   └── jw-org-mcp-concept.md   # Detailed API documentation and examples
├── pyproject.toml              # Project configuration and dependencies
└── README.md                   # Project documentation
```

## Important Notes

- **No Media Loading**: Skip JavaScript, images, and other media—text content only
- **Caching Strategy**: Implement optional local/temporary caching to minimize redundant network calls
- **JWT Token Lifecycle**: Tokens expire and need refresh (check `exp` claim in JWT)
- **Search Query Transformation**: User queries need intelligent parsing to extract actual search subjects vs. question framing
