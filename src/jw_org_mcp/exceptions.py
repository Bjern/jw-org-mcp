"""Custom exceptions for JW.Org MCP Tool."""


class JWOrgMCPError(Exception):
    """Base exception for JW.Org MCP Tool."""

    pass


class AuthenticationError(JWOrgMCPError):
    """Raised when authentication with jw.org fails."""

    pass


class CDNDiscoveryError(JWOrgMCPError):
    """Raised when CDN discovery fails."""

    pass


class TokenRefreshError(JWOrgMCPError):
    """Raised when JWT token refresh fails."""

    pass


class SearchError(JWOrgMCPError):
    """Raised when search operation fails."""

    pass


class ContentRetrievalError(JWOrgMCPError):
    """Raised when content retrieval fails."""

    pass


class ParseError(JWOrgMCPError):
    """Raised when parsing content fails."""

    pass


class RateLimitError(JWOrgMCPError):
    """Raised when rate limit is exceeded."""

    pass


class NetworkError(JWOrgMCPError):
    """Raised when network operation fails."""

    pass
