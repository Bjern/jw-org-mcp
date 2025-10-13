"""JW.Org API client."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from .auth import AuthManager
from .cache import Cache
from .config import settings
from .exceptions import ContentRetrievalError, SearchError
from .models import ArticleContent, ResponseMetadata, SearchResponse
from .parser import ArticleParser, QueryParser, SearchResponseParser

logger = logging.getLogger(__name__)


class JWOrgClient:
    """Client for interacting with JW.Org APIs."""

    def __init__(self) -> None:
        """Initialize the client."""
        self._auth_manager = AuthManager()
        self._cache = Cache(ttl_seconds=settings.cache_ttl_seconds)
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=settings.request_timeout,
                limits=httpx.Limits(
                    max_connections=settings.connection_pool_size,
                    max_keepalive_connections=settings.connection_pool_size,
                ),
                follow_redirects=True,
            )
        return self._http_client

    async def search(
        self,
        query: str,
        filter_type: str = "all",
        language: str = "E",
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[SearchResponse, ResponseMetadata]:
        """Search JW.Org content.

        Args:
            query: Search query
            filter_type: Content filter (all, publications, videos, audio, bible, indexes)
            language: Language code (default: E for English)
            limit: Number of results (not directly supported by API)
            offset: Result offset for pagination

        Returns:
            Tuple of (SearchResponse, ResponseMetadata)

        Raises:
            SearchError: If search fails
        """
        # Parse query to extract meaningful search terms
        search_terms = QueryParser.extract_search_terms(query)

        # Check cache
        cache_key_parts = (search_terms, filter_type, language, offset)
        if settings.enable_cache:
            cached = self._cache.get(*cache_key_parts)
            if cached is not None:
                logger.info(f"Cache hit for search: {search_terms}")
                response, metadata = cached
                metadata.cache_hit = True
                return response, metadata

        try:
            # Get CDN and auth
            cdn_info = await self._auth_manager.discover_cdn()
            headers = await self._auth_manager.get_authenticated_headers()

            # Build search URL
            search_url = (
                f"{cdn_info.base_url}/apis/search/results/"
                f"{language}/{filter_type}?q={search_terms}"
            )

            if offset > 0:
                search_url += f"&offset={offset}"

            logger.info(f"Searching: {search_url}")

            # Make request
            client = await self._get_http_client()
            response = await client.get(search_url, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = SearchResponseParser.parse_search_results(
                data, search_terms, filter_type
            )

            # Get total count
            insight = data.get("insight", {})
            total_data = insight.get("total", {})
            total = total_data.get("value", len(results))

            # Build response
            search_response = SearchResponse(
                results=results[:limit] if limit > 0 else results,
                total=total,
                page=insight.get("page", 1),
                filter=filter_type,
                query=search_terms,
            )

            metadata = ResponseMetadata(
                source_domain="jw-cdn.org",
                source_url=search_url,
                timestamp=datetime.now(UTC),
                query_params={
                    "query": search_terms,
                    "filter": filter_type,
                    "language": language,
                    "offset": offset,
                },
                cache_hit=False,
            )

            # Cache result
            if settings.enable_cache:
                self._cache.set(*cache_key_parts, value=(search_response, metadata))

            return search_response, metadata

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            raise SearchError(f"Search failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise SearchError(f"Unexpected error during search: {e}") from e

    async def get_article(self, url: str) -> tuple[ArticleContent, ResponseMetadata]:
        """Get article content from wol.jw.org.

        Args:
            url: Article URL

        Returns:
            Tuple of (ArticleContent, ResponseMetadata)

        Raises:
            ContentRetrievalError: If content retrieval fails
        """
        # Check cache
        if settings.enable_cache:
            cached = self._cache.get(url, "article")
            if cached is not None:
                logger.info(f"Cache hit for article: {url}")
                content, metadata = cached
                metadata.cache_hit = True
                return content, metadata

        try:
            logger.info(f"Fetching article: {url}")

            client = await self._get_http_client()
            response = await client.get(url)
            response.raise_for_status()

            # Parse article
            article = ArticleParser.parse_article(response.text, url)

            metadata = ResponseMetadata(
                source_domain="wol.jw.org",
                source_url=url,
                timestamp=datetime.now(UTC),
                query_params={"url": url},
                cache_hit=False,
            )

            # Cache result
            if settings.enable_cache:
                self._cache.set(url, "article", value=(article, metadata))

            return article, metadata

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching article: {e}")
            raise ContentRetrievalError(f"Failed to fetch article: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error fetching article: {e}")
            raise ContentRetrievalError(
                f"Unexpected error fetching article: {e}"
            ) from e

    async def get_scripture(
        self, reference: str, translation: str = "nwtsty"
    ) -> tuple[dict[str, Any], ResponseMetadata]:
        """Get scripture content.

        Args:
            reference: Scripture reference (e.g., "John 3:16")
            translation: Bible translation code

        Returns:
            Tuple of (scripture data, ResponseMetadata)

        Raises:
            ContentRetrievalError: If content retrieval fails
        """
        # Search for the scripture reference
        search_response, _ = await self.search(reference, filter_type="bible")

        if not search_response.results:
            raise ContentRetrievalError(f"Scripture not found: {reference}")

        # Get the first result
        result = search_response.results[0]

        scripture_data = {
            "text": result.snippet,
            "reference": result.title,
            "source_url": result.url,
        }

        metadata = ResponseMetadata(
            source_domain="jw.org",
            source_url=result.url,
            timestamp=datetime.now(UTC),
            query_params={"reference": reference, "translation": translation},
            cache_hit=False,
        )

        return scripture_data, metadata

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return self._cache.get_stats()

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()

    async def close(self) -> None:
        """Close all connections."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

        await self._auth_manager.close()
