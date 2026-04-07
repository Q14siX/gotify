"""Async API client for Gotify."""

from __future__ import annotations

from typing import Any, AsyncIterator
from urllib.parse import quote, urlparse, urlunparse

from aiohttp import ClientError, ClientSession, ClientTimeout, WSMsgType


class GotifyError(Exception):
    """Base Gotify exception."""


class GotifyApiError(GotifyError):
    """Gotify API error."""


class GotifyAuthError(GotifyApiError):
    """Authentication failed."""


class GotifyConnectionError(GotifyError):
    """Connection failed."""


def normalize_base_url(url: str) -> str:
    """Normalize a user provided base URL."""
    cleaned = url.strip().rstrip("/")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned.rstrip("/")


def build_ws_url(url: str, path: str) -> str:
    """Build a websocket URL from a HTTP base URL and path."""
    parsed = urlparse(normalize_base_url(url))
    scheme = "wss" if parsed.scheme == "https" else "ws"
    new_path = f"{parsed.path.rstrip('/')}{path}"
    return urlunparse((scheme, parsed.netloc, new_path, "", "", ""))


class GotifyApiClient:
    """Small async client for the Gotify HTTP and websocket APIs."""

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        *,
        verify_ssl: bool = True,
        timeout: float = 20.0,
    ) -> None:
        self._session = session
        self.base_url = normalize_base_url(base_url)
        self.verify_ssl = verify_ssl
        self._timeout = ClientTimeout(total=timeout)

    async def _safe_error_text(self, response) -> str:
        """Safely extract an error message."""
        try:
            if response.content_type == "application/json":
                payload = await response.json()
                if isinstance(payload, dict):
                    if "error" in payload:
                        return str(payload["error"])
                    if "errorDescription" in payload:
                        return str(payload["errorDescription"])
                    if "message" in payload:
                        return str(payload["message"])
                    return str(payload)
            text = await response.text()
            return text.strip()
        except Exception:
            return ""

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> Any:
        """Perform a request against the Gotify API."""
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                headers=headers,
                json=json_data,
                ssl=self.verify_ssl,
                timeout=self._timeout,
            ) as response:
                if response.status in (401, 403):
                    raise GotifyAuthError(await self._safe_error_text(response) or "Authentication failed")

                if response.status >= 400:
                    raise GotifyApiError(
                        f"HTTP {response.status}: {await self._safe_error_text(response) or 'Gotify API error'}"
                    )

                if not expect_json:
                    return await response.text()

                if response.content_type == "application/json":
                    return await response.json()

                text = await response.text()
                return {"raw": text}
        except GotifyError:
            raise
        except ClientError as err:
            raise GotifyConnectionError(str(err)) from err
        except TimeoutError as err:
            raise GotifyConnectionError("Request timed out") from err

    async def async_get_health(self) -> dict[str, Any]:
        """Return server health info."""
        result = await self._request("GET", "/health")
        return result if isinstance(result, dict) else {}

    async def async_get_version(self) -> dict[str, Any]:
        """Return version information."""
        result = await self._request("GET", "/version")
        return result if isinstance(result, dict) else {}

    async def async_get_current_user(self, client_token: str) -> dict[str, Any]:
        """Return current user for a client token."""
        headers = {"X-Gotify-Key": client_token}
        result = await self._request("GET", "/current/user", headers=headers)
        return result if isinstance(result, dict) else {}

    async def async_get_applications(self, client_token: str) -> list[dict[str, Any]]:
        """Return applications visible to the client token."""
        headers = {"X-Gotify-Key": client_token}
        result = await self._request("GET", "/application", headers=headers)
        return result if isinstance(result, list) else []

    async def async_get_clients(self, client_token: str) -> list[dict[str, Any]]:
        """Return clients visible to the client token."""
        headers = {"X-Gotify-Key": client_token}
        result = await self._request("GET", "/client", headers=headers)
        return result if isinstance(result, list) else []

    async def async_get_messages(
        self,
        client_token: str,
        *,
        application_id: int | None = None,
        limit: int = 50,
        since: int | None = None,
    ) -> dict[str, Any]:
        """Return messages."""
        headers = {"X-Gotify-Key": client_token}
        path = "/message" if application_id is None else f"/application/{application_id}/message"
        params: dict[str, Any] = {"limit": limit}
        if since is not None:
            params["since"] = since
        result = await self._request("GET", path, headers=headers, params=params)
        return result if isinstance(result, dict) else {}

    async def async_delete_message(self, client_token: str, message_id: int) -> None:
        """Delete a single message."""
        headers = {"X-Gotify-Key": client_token}
        await self._request("DELETE", f"/message/{message_id}", headers=headers, expect_json=False)

    async def async_clear_application_messages(self, client_token: str, application_id: int) -> None:
        """Clear all messages for an application."""
        headers = {"X-Gotify-Key": client_token}
        await self._request(
            "DELETE",
            f"/application/{application_id}/message",
            headers=headers,
            expect_json=False,
        )

    async def async_send_message(
        self,
        app_token: str,
        *,
        message: str,
        title: str | None = None,
        priority: int = 5,
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a message using an application token."""
        params = {"token": app_token}
        payload: dict[str, Any] = {
            "message": message,
            "priority": priority,
        }
        if title:
            payload["title"] = title
        if extras:
            payload["extras"] = extras
        result = await self._request("POST", "/message", params=params, json_data=payload)
        return result if isinstance(result, dict) else {}

    async def async_stream_messages(self, client_token: str) -> AsyncIterator[dict[str, Any]]:
        """Yield Gotify stream messages via websocket."""
        ws_url = build_ws_url(self.base_url, f"/stream?token={quote(client_token)}")
        try:
            async with self._session.ws_connect(
                ws_url,
                heartbeat=30,
                ssl=self.verify_ssl,
                timeout=self._timeout,
            ) as websocket:
                async for msg in websocket:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            payload = msg.json()
                        except ValueError:
                            continue
                        if isinstance(payload, dict):
                            yield payload
                    elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR):
                        break
        except ClientError as err:
            raise GotifyConnectionError(str(err)) from err
        except TimeoutError as err:
            raise GotifyConnectionError("Websocket timed out") from err
