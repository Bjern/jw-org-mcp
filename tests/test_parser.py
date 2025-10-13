"""Tests for parser module."""


from jw_org_mcp.parser import ArticleParser, QueryParser, SearchResponseParser


class TestQueryParser:
    """Tests for QueryParser."""

    def test_extract_simple_query(self) -> None:
        """Test extracting simple query."""
        result = QueryParser.extract_search_terms("love")
        assert result == "love"

    def test_extract_from_what_question(self) -> None:
        """Test extracting from 'what does the bible say' question."""
        result = QueryParser.extract_search_terms(
            "What does the Bible say about peace and security?"
        )
        assert result == "peace and security"

    def test_extract_from_how_question(self) -> None:
        """Test extracting from 'how' question."""
        result = QueryParser.extract_search_terms("How can I find true happiness?")
        assert result == "i find true happiness"

    def test_extract_from_tell_me_about(self) -> None:
        """Test extracting from 'tell me about' request."""
        result = QueryParser.extract_search_terms("Tell me about Jehovah's love")
        assert result == "jehovah's love"

    def test_preserve_original_if_too_short(self) -> None:
        """Test that original query is preserved if extraction is too short."""
        result = QueryParser.extract_search_terms("What is it?")
        # Query parser converts to lowercase, so check normalized version
        assert result == "what is it"


class TestSearchResponseParser:
    """Tests for SearchResponseParser."""

    def test_parse_flat_structure(self) -> None:
        """Test parsing flat result structure."""
        data = {
            "results": [
                {
                    "type": "item",
                    "subtype": "verse",
                    "title": "John 3:16",
                    "snippet": "For God loved the world...",
                    "links": {"jw.org": "https://www.jw.org/..."},
                }
            ]
        }

        results = SearchResponseParser.parse_search_results(data, "love", "bible")

        assert len(results) == 1
        assert results[0].title == "John 3:16"
        assert results[0].subtype == "verse"

    def test_parse_nested_structure(self) -> None:
        """Test parsing nested group structure."""
        data = {
            "results": [
                {
                    "type": "group",
                    "results": [
                        {
                            "type": "item",
                            "subtype": "article",
                            "title": "Peace and Security",
                            "snippet": "The need for peace...",
                            "links": {"wol": "https://wol.jw.org/..."},
                            "context": "The Watchtower (1985)",
                        }
                    ],
                }
            ]
        }

        results = SearchResponseParser.parse_search_results(data, "peace", "all")

        assert len(results) == 1
        assert results[0].title == "Peace and Security"
        assert results[0].publication == "The Watchtower"
        assert results[0].year == 1985

    def test_clean_html_in_snippet(self) -> None:
        """Test that HTML is cleaned from snippets."""
        data = {
            "results": [
                {
                    "type": "item",
                    "subtype": "article",
                    "title": "Test",
                    "snippet": "<strong>Peace</strong> and <em>security</em>",
                    "links": {"wol": "https://wol.jw.org/..."},
                }
            ]
        }

        results = SearchResponseParser.parse_search_results(data, "peace", "all")

        assert len(results) == 1
        assert "<strong>" not in results[0].snippet
        assert "Peace" in results[0].snippet


class TestArticleParser:
    """Tests for ArticleParser."""

    def test_parse_basic_article(self) -> None:
        """Test parsing basic article structure."""
        html = """
        <html>
            <article id="article">
                <h1>Test Article</h1>
                <p data-pid="1">First paragraph.</p>
                <p data-pid="2">Second paragraph.</p>
            </article>
        </html>
        """

        article = ArticleParser.parse_article(html, "https://test.com")

        assert article.title == "Test Article"
        assert len(article.paragraphs) == 2
        assert article.paragraphs[0] == "First paragraph."
        assert article.source_url == "https://test.com"

    def test_extract_scripture_references(self) -> None:
        """Test extracting scripture references."""
        html = """
        <html>
            <article id="article">
                <h1>Test</h1>
                <p data-pid="1">
                    See <a class="b">John 3:16</a> and <a class="b">1 John 4:8</a>.
                </p>
            </article>
        </html>
        """

        article = ArticleParser.parse_article(html, "https://test.com")

        assert len(article.references) == 2
        assert "John 3:16" in article.references
        assert "1 John 4:8" in article.references

    def test_skip_non_content_paragraphs(self) -> None:
        """Test that captions and footnotes are skipped."""
        html = """
        <html>
            <article id="article">
                <h1>Test</h1>
                <p data-pid="1">Content paragraph.</p>
                <p data-pid="2" class="caption">This is a caption.</p>
                <p data-pid="3" class="footnote">This is a footnote.</p>
            </article>
        </html>
        """

        article = ArticleParser.parse_article(html, "https://test.com")

        assert len(article.paragraphs) == 1
        assert article.paragraphs[0] == "Content paragraph."
