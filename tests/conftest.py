"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_search_response() -> dict:
    """Sample search API response."""
    return {
        "layout": ["flat"],
        "results": [
            {
                "type": "group",
                "results": [
                    {
                        "type": "item",
                        "subtype": "article",
                        "links": {
                            "wol": "https://wol.jw.org/en/wol/d/r1/lp-e/1985720"
                        },
                        "title": "Peace and Security—The Hope",
                        "snippet": "The need for peace and security",
                        "context": "The Watchtower (1985)",
                        "insight": {"rank": 1},
                    }
                ],
            }
        ],
        "insight": {
            "query": "peace and security",
            "filter": "all",
            "page": 1,
            "total": {"value": 100, "relation": "gte"},
        },
    }


@pytest.fixture
def sample_article_html() -> str:
    """Sample article HTML."""
    return """
    <html>
        <article id="article">
            <h1>Peace and Security</h1>
            <p data-pid="1">The world has long sought peace.</p>
            <p data-pid="2">
                The Bible shows at <a class="b">1 Thessalonians 5:3</a>
                that true peace comes from God.
            </p>
            <p data-pid="3" class="caption">A caption to skip</p>
        </article>
    </html>
    """
