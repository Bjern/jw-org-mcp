"""Content parsers for JW.Org responses."""

import logging
import re
from typing import Any

from bs4 import BeautifulSoup

from .exceptions import ParseError
from .models import ArticleContent, PublicationIndex, PublicationIndexEntry, SearchResult

logger = logging.getLogger(__name__)


class QueryParser:
    """Parses user queries to extract meaningful search terms."""

    # Common question patterns to remove
    QUESTION_PATTERNS = [
        r"^what\s+(does|do|is|are)\s+the\s+bible\s+say\s+about\s+",
        r"^what\s+does\s+.*?\s+say\s+about\s+",
        r"^how\s+(does|do|can|should)\s+",
        r"^why\s+(does|do|is|are)\s+",
        r"^when\s+(does|do|will|should)\s+",
        r"^where\s+(does|do|is|can)\s+",
        r"^who\s+(is|are|was|were)\s+",
        r"^tell\s+me\s+about\s+",
        r"^explain\s+",
        r"^find\s+information\s+about\s+",
    ]

    @classmethod
    def extract_search_terms(cls, query: str) -> str:
        """Extract meaningful search terms from a natural language query.

        Args:
            query: User's natural language query

        Returns:
            Extracted search terms
        """
        # Clean the query
        cleaned = query.strip().lower()

        # Remove question patterns
        for pattern in cls.QUESTION_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Remove trailing question marks and periods
        cleaned = cleaned.rstrip("?.!")

        # If we removed too much, return original
        if not cleaned or len(cleaned) < 3:
            return query.strip()

        return cleaned.strip()


class SearchResponseParser:
    """Parses search API responses."""

    @staticmethod
    def parse_search_results(
        data: dict[str, Any], query: str, filter_type: str
    ) -> list[SearchResult]:
        """Parse search results from API response.

        Args:
            data: Raw API response data
            query: Original search query
            filter_type: Filter type used

        Returns:
            List of SearchResult objects

        Raises:
            ParseError: If parsing fails
        """
        try:
            results = []
            raw_results = data.get("results", [])

            for item in raw_results:
                # Handle nested group structure (for 'all' filter)
                if item.get("type") == "group":
                    nested_results = item.get("results", [])
                    for nested_item in nested_results:
                        result = SearchResponseParser._parse_single_result(nested_item)
                        if result:
                            results.append(result)
                # Handle flat structure (for other filters)
                else:
                    result = SearchResponseParser._parse_single_result(item)
                    if result:
                        results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            raise ParseError(f"Failed to parse search results: {e}") from e

    @staticmethod
    def _parse_single_result(item: dict[str, Any]) -> SearchResult | None:
        """Parse a single search result item.

        Args:
            item: Raw result item

        Returns:
            SearchResult object or None if invalid
        """
        try:
            # Extract basic fields
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            item_type = item.get("type", "item")
            subtype = item.get("subtype", "")

            # Clean HTML from snippet
            snippet = SearchResponseParser._clean_html(snippet)

            # Extract URL (prefer wol link)
            links = item.get("links", {})
            url = links.get("wol") or links.get("jw.org") or ""

            # Extract context and metadata
            context = item.get("context")
            rank = item.get("insight", {}).get("rank")

            # Try to extract publication and year from context
            publication = None
            year = None
            if context:
                year_match = re.search(r"\((\d{4})\)", context)
                if year_match:
                    year = int(year_match.group(1))
                    publication = context.replace(f"({year})", "").strip()
                else:
                    publication = context

            return SearchResult(
                title=title,
                snippet=snippet,
                url=url,
                type=item_type,
                subtype=subtype,
                context=context,
                publication=publication,
                year=year,
                rank=rank,
            )

        except Exception as e:
            logger.warning(f"Could not parse result item: {e}")
            return None

    @staticmethod
    def _clean_html(text: str) -> str:
        """Remove HTML tags from text.

        Args:
            text: Text with HTML tags

        Returns:
            Clean text
        """
        if not text:
            return ""

        # Use BeautifulSoup to extract text
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ", strip=True)


class ArticleParser:
    """Parses article content from wol.jw.org."""

    @staticmethod
    def parse_article(html: str, url: str) -> ArticleContent | PublicationIndex:
        """Parse article content from HTML.

        If the page is a publication index/table of contents (no article
        paragraphs but contains links to individual articles), returns a
        PublicationIndex instead.

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            ArticleContent or PublicationIndex object

        Raises:
            ParseError: If parsing fails
        """
        try:
            soup = BeautifulSoup(html, "lxml")

            # Find article container
            article = soup.find("article", id="article")
            if not article:
                raise ParseError("Could not find article container in HTML")

            # Extract title
            title_elem = article.find("h1")
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"

            # Extract paragraphs
            paragraphs = []
            references = []

            # Find all paragraph elements with data-pid attribute
            para_elements = article.find_all("p", {"data-pid": True})

            for para in para_elements:
                # Skip if paragraph has class indicating it's not content
                classes = para.get("class", [])
                if any(cls in ["caption", "footnote", "boxTtl"] for cls in classes):
                    continue

                # Extract text, ignoring span highlights
                text = para.get_text(separator=" ", strip=True)
                if text:
                    paragraphs.append(text)

                # Extract scripture references
                scripture_refs = para.find_all("a", {"class": "b"})
                for ref in scripture_refs:
                    ref_text = ref.get_text(strip=True)
                    if ref_text:
                        references.append(ref_text)

            if paragraphs:
                return ArticleContent(
                    title=title,
                    paragraphs=paragraphs,
                    references=list(set(references)),  # Remove duplicates
                    source_url=url,
                )

            # No paragraphs found — try parsing as a publication index/TOC
            index = ArticleParser._try_parse_publication_index(soup, url)
            if index:
                return index

            raise ParseError("Could not extract any paragraphs from article")

        except ParseError:
            raise
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            raise ParseError(f"Failed to parse article: {e}") from e

    @staticmethod
    def _try_parse_publication_index(
        soup: BeautifulSoup, url: str
    ) -> PublicationIndex | None:
        """Try to parse the page as a publication index/table of contents.

        Detects pages that list links to individual articles (e.g., a magazine
        issue's table of contents).

        Args:
            soup: Parsed HTML
            url: Source URL

        Returns:
            PublicationIndex if article links are found, None otherwise
        """
        # Look for links to individual articles (/wol/d/ pattern)
        article_links = soup.find_all("a", href=re.compile(r"/wol/d/"))
        if not article_links:
            return None

        entries: list[PublicationIndexEntry] = []
        seen_urls: set[str] = set()

        for link in article_links:
            href = link.get("href", "")
            link_title = link.get_text(strip=True)

            if not href or not link_title:
                continue

            # Build full URL
            full_url = f"https://wol.jw.org{href}" if href.startswith("/") else href

            # Strip query parameters from the URL for deduplication and cleanliness
            clean_url = full_url.split("?")[0]

            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)

            entries.append(PublicationIndexEntry(title=link_title, url=clean_url))

        if not entries:
            return None

        # Get publication title from page heading
        h1 = soup.find("h1")
        pub_title = h1.get_text(strip=True) if h1 else "Publication Index"

        return PublicationIndex(
            title=pub_title,
            articles=entries,
            source_url=url,
        )
