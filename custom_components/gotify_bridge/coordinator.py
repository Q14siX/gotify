"""Coordinator for the Gotify integration."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GotifyApiClient, GotifyAuthError, GotifyConnectionError, GotifyError
from .const import (
    CONF_APP_TOKEN,
    CONF_CLIENT_TOKEN,
    CONF_ENABLE_WEBSOCKET,
    CONF_MONITORED_APPLICATION_ID,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    EVENT_MESSAGE_RECEIVED,
)

_LOGGER = logging.getLogger(__name__)


class GotifyCoordinator(DataUpdateCoordinator):
    """Coordinate polling and streaming for Gotify."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: GotifyApiClient,
        entry,
    ) -> None:
        """Initialize coordinator."""
        self.hass = hass
        self.api = api
        self.entry = entry

        self.client_token: str | None = entry.data.get(CONF_CLIENT_TOKEN)
        self.app_token: str | None = entry.data.get(CONF_APP_TOKEN)
        self.enable_websocket: bool = entry.options.get(
            CONF_ENABLE_WEBSOCKET,
            entry.data.get(CONF_ENABLE_WEBSOCKET, True),
        )
        self.monitored_application_id: int | None = entry.options.get(
            CONF_MONITORED_APPLICATION_ID,
            entry.data.get(CONF_MONITORED_APPLICATION_ID),
        )

        self.stream_connected = False
        self.last_received_message: dict[str, Any] | None = None
        self.received_messages_total = 0

        self._ws_task: asyncio.Task | None = None
        self._message_listeners: list[Callable[[dict[str, Any]], None]] = []

        update_seconds = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, 60),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"Gotify ({entry.title})",
            update_interval=timedelta(seconds=update_seconds),
        )

    def register_message_listener(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> Callable[[], None]:
        """Register a callback for incoming messages."""
        self._message_listeners.append(callback)

        def _unsubscribe() -> None:
            if callback in self._message_listeners:
                self._message_listeners.remove(callback)

        return _unsubscribe

    async def async_start(self) -> None:
        """Start the coordinator."""
        await self.async_config_entry_first_refresh()
        await self._start_websocket()

    async def async_stop(self) -> None:
        """Stop the coordinator."""
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            self._ws_task = None
        self.stream_connected = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch state from Gotify."""
        try:
            health = await self.api.async_get_health()
            version = await self.api.async_get_version()

            user: dict[str, Any] | None = None
            applications: list[dict[str, Any]] = []
            clients: list[dict[str, Any]] = []
            monitored_messages: list[dict[str, Any]] = []
            monitored_messages_paging: dict[str, Any] = {}

            if self.client_token:
                user = await self.api.async_get_current_user(self.client_token)
                applications = await self.api.async_get_applications(self.client_token)
                clients = await self.api.async_get_clients(self.client_token)

                if self.monitored_application_id is not None:
                    messages_payload = await self.api.async_get_messages(
                        self.client_token,
                        application_id=self.monitored_application_id,
                        limit=50,
                    )
                    monitored_messages = messages_payload.get("messages", [])
                    monitored_messages_paging = {
                        key: value
                        for key, value in messages_payload.items()
                        if key != "messages"
                    }

            data: dict[str, Any] = {
                "health": health,
                "version": version,
                "user": user,
                "applications": applications,
                "clients": clients,
                "monitored_application_id": self.monitored_application_id,
                "monitored_messages": monitored_messages,
                "monitored_messages_paging": monitored_messages_paging,
                "stream_connected": self.stream_connected,
                "last_received_message": self.last_received_message,
                "received_messages_total": self.received_messages_total,
            }
            return data

        except GotifyAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except GotifyConnectionError as err:
            raise UpdateFailed(f"Connection failed: {err}") from err
        except GotifyError as err:
            raise UpdateFailed(f"Gotify error: {err}") from err

    async def _start_websocket(self) -> None:
        """Start websocket listener if configured."""
        if not self.client_token or not self.enable_websocket:
            self.stream_connected = False
            return

        if self._ws_task and not self._ws_task.done():
            return

        self._ws_task = self.hass.async_create_task(self._async_run_websocket())

    async def _async_run_websocket(self) -> None:
        """Keep the websocket open and feed entities/events."""
        assert self.client_token is not None

        while True:
            try:
                self.stream_connected = True
                self.async_update_listeners()

                async for payload in self.api.async_stream_messages(self.client_token):
                    self.last_received_message = payload
                    self.received_messages_total += 1
                    self.stream_connected = True

                    for listener in list(self._message_listeners):
                        try:
                            listener(payload)
                        except Exception:
                            _LOGGER.exception("Error in Gotify message listener")

                    self.hass.bus.async_fire(
                        EVENT_MESSAGE_RECEIVED,
                        {
                            "entry_id": self.entry.entry_id,
                            "title": payload.get("title"),
                            "message": payload.get("message"),
                            "priority": payload.get("priority"),
                            "id": payload.get("id"),
                            "appid": payload.get("appid"),
                            "date": payload.get("date"),
                            "extras": payload.get("extras"),
                            "raw": payload,
                        },
                    )

                    self.async_update_listeners()

            except asyncio.CancelledError:
                raise
            except GotifyConnectionError as err:
                _LOGGER.debug("Gotify websocket disconnected: %s", err)
            except Exception:
                _LOGGER.exception("Unexpected websocket error in Gotify integration")
            finally:
                self.stream_connected = False
                self.async_update_listeners()

            await asyncio.sleep(10)

    async def async_send_message(
        self,
        *,
        message: str,
        title: str | None = None,
        priority: int = 5,
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a message via Gotify."""
        if not self.app_token:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="missing_app_token",
            )

        result = await self.api.async_send_message(
            self.app_token,
            message=message,
            title=title,
            priority=priority,
            extras=extras,
        )
        await self.async_request_refresh()
        return result

    async def async_delete_message(self, message_id: int) -> None:
        """Delete a message by id."""
        if not self.client_token:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="missing_client_token",
            )

        await self.api.async_delete_message(self.client_token, message_id)
        await self.async_request_refresh()

    async def async_clear_messages(self) -> None:
        """Clear all messages for the configured monitored application."""
        if not self.client_token:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="missing_client_token",
            )
        if self.monitored_application_id is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="missing_monitored_application",
            )

        await self.api.async_clear_application_messages(
            self.client_token,
            self.monitored_application_id,
        )
        await self.async_request_refresh()
