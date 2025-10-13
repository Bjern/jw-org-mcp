"""Data models for JW.Org MCP Tool."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """A single search result."""

    title: str
    snippet: str
    url: str
    type: str
    subtype: str | None = None
    context: str | None = None
    publication: str | None = None
    year: int | None = None
    rank: int | None = None


class SearchResponse(BaseModel):
    """Search API response."""

    results: list[SearchResult]
    total: int
    page: int
    filter: str
    query: str


class ArticleContent(BaseModel):
    """Parsed article content."""

    title: str
    paragraphs: list[str]
    references: list[str] = Field(default_factory=list)
    source_url: str


class ScriptureContent(BaseModel):
    """Scripture content."""

    text: str
    reference: str
    context: list[str] = Field(default_factory=list)
    source_url: str


class ResponseMetadata(BaseModel):
    """Metadata for all responses."""

    source_domain: str
    source_url: str
    timestamp: datetime
    query_params: dict[str, Any] = Field(default_factory=dict)
    cache_hit: bool = False


class MCPResponse(BaseModel):
    """Standard MCP response format."""

    data: dict[str, Any]
    metadata: ResponseMetadata


class ErrorResponse(BaseModel):
    """Error response format."""

    code: str
    message: str
    details: str | None = None
    timestamp: datetime


class CDNInfo(BaseModel):
    """CDN information."""

    base_url: str
    discovered_at: datetime


class JWTToken(BaseModel):
    """JWT token information."""

    token: str
    expires_at: datetime
    issued_at: datetime
