"""Authentication and CDN discovery for JW.Org API."""

import logging
import re
import uuid
from datetime import UTC, datetime, timedelta

import httpx

from .config import settings
from .exceptions import AuthenticationError, CDNDiscoveryError
from .models import CDNInfo, JWTToken

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication with JW.Org APIs."""

    def __init__(self) -> None:
        """Initialize the auth manager."""
        self._cdn_info: CDNInfo | None = None
        self._jwt_token: JWTToken | None = None
        self._client_id: str = str(uuid.uuid4())
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
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", '
                    '"Not_A Brand";v="24"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                },
                follow_redirects=True,
            )
        return self._http_client

    async def discover_cdn(self) -> CDNInfo:
        """Discover the CDN base URL from jw.org homepage.

        Returns:
            CDNInfo object with CDN base URL

        Raises:
            CDNDiscoveryError: If CDN discovery fails
        """
        if self._cdn_info is not None:
            return self._cdn_info

        try:
            client = await self._get_http_client()
            logger.info(f"Discovering CDN from {settings.jworg_home_url}")

            response = await client.get(settings.jworg_home_url)
            response.raise_for_status()

            # Look for CDN URL pattern: *.jw-cdn.org
            cdn_pattern = r"https?://([a-z0-9-]+\.jw-cdn\.org)"
            matches = re.findall(cdn_pattern, response.text)

            if not matches:
                raise CDNDiscoveryError("Could not find CDN URL in jw.org homepage")

            # Use the first match
            cdn_url = f"https://{matches[0]}"
            self._cdn_info = CDNInfo(base_url=cdn_url, discovered_at=datetime.now(UTC))

            logger.info(f"Discovered CDN: {cdn_url}")
            return self._cdn_info

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during CDN discovery: {e}")
            raise CDNDiscoveryError(f"Failed to discover CDN: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during CDN discovery: {e}")
            raise CDNDiscoveryError(f"Unexpected error during CDN discovery: {e}") from e

    async def get_jwt_token(self, force_refresh: bool = False) -> str:
        """Get JWT token, refreshing if necessary.

        Args:
            force_refresh: Force token refresh even if not expired

        Returns:
            JWT token string

        Raises:
            AuthenticationError: If authentication fails
        """
        # Check if we have a valid token
        if not force_refresh and self._jwt_token is not None:
            # Check if token is still valid (with 5 minute buffer)
            if datetime.now(UTC) < self._jwt_token.expires_at - timedelta(minutes=5):
                return self._jwt_token.token

        # Need to get a new token
        try:
            cdn_info = await self.discover_cdn()
            token_url = f"{cdn_info.base_url}/tokens/jworg.jwt"

            client = await self._get_http_client()
            logger.info("Requesting JWT token")

            response = await client.get(token_url)
            response.raise_for_status()

            token = response.text.strip()

            # Parse JWT to get expiry (simple extraction without validation)
            exp_time = self._extract_token_expiry(token)

            self._jwt_token = JWTToken(
                token=token, expires_at=exp_time, issued_at=datetime.now(UTC)
            )

            logger.info(f"JWT token acquired, expires at {exp_time}")
            return token

        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting JWT token: {e}")
            raise AuthenticationError(f"Failed to get JWT token: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error getting JWT token: {e}")
            raise AuthenticationError(f"Unexpected error getting JWT token: {e}") from e

    def _extract_token_expiry(self, token: str) -> datetime:
        """Extract expiry time from JWT token.

        Args:
            token: JWT token string

        Returns:
            Expiry datetime
        """
        try:
            import base64
            import json

            # JWT structure: header.payload.signature
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            # Decode payload (add padding if needed)
            payload = parts[1]
            padding = 4 - (len(payload) % 4)
            if padding != 4:
                payload += "=" * padding

            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)

            # Get exp claim (Unix timestamp)
            exp_timestamp = payload_data.get("exp")
            if exp_timestamp is None:
                # Default to 7 days if no exp claim
                return datetime.now(UTC) + timedelta(days=7)

            return datetime.fromtimestamp(exp_timestamp, UTC)

        except Exception as e:
            logger.warning(f"Could not extract token expiry: {e}, using default")
            # Default to 7 days
            return datetime.now(UTC) + timedelta(days=7)

    async def get_authenticated_headers(self) -> dict[str, str]:
        """Get headers with authentication for API requests.

        Returns:
            Dictionary of HTTP headers

        Raises:
            AuthenticationError: If authentication fails
        """
        token = await self.get_jwt_token()

        return {
            "Accept": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
            "X-Client-ID": self._client_id,
            "Referer": settings.jworg_base_url,
            "Accept-Encoding": "gzip, deflate, br",
        }

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
