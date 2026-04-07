"""Config flow for the Gotify integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_APP_TOKEN,
    CONF_CLIENT_TOKEN,
    CONF_ENABLE_WEBSOCKET,
    CONF_MODE,
    CONF_MONITORED_APPLICATION_ID,
    CONF_MONITORED_APPLICATION_NAME,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    CONF_VERIFY_SSL,
    DEFAULT_ENABLE_WEBSOCKET,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MODE_FULL,
    MODE_RECEIVE_ONLY,
    MODE_SEND_ONLY,
)


def _normalize_base_url(url: str) -> str:
    """Normalize a user-provided base URL."""
    cleaned = url.strip().rstrip("/")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned.rstrip("/")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gotify."""

    VERSION = 1
    MINOR_VERSION = 3

    def __init__(self) -> None:
        """Initialize the flow."""
        super().__init__()
        self._data: dict[str, Any] = {}
        self._applications: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Collect base server settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = _normalize_base_url(user_input[CONF_URL])
            self._data.update(user_input)
            self._data[CONF_URL] = url

            try:
                from .api import GotifyApiClient, GotifyConnectionError

                api = GotifyApiClient(
                    async_get_clientsession(self.hass),
                    url,
                    verify_ssl=user_input[CONF_VERIFY_SSL],
                )
                await api.async_get_health()
            except GotifyConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return await self.async_step_access()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=self._data.get(CONF_NAME, DEFAULT_NAME)): str,
                vol.Required(CONF_URL, default=self._data.get(CONF_URL, "")): str,
                vol.Required(
                    CONF_VERIFY_SSL,
                    default=self._data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                ): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_access(self, user_input: dict[str, Any] | None = None):
        """Collect mode and token settings."""
        errors: dict[str, str] = {}

        current_mode = self._data.get(CONF_MODE, MODE_FULL)
        if user_input is not None:
            current_mode = user_input[CONF_MODE]

            self._data[CONF_MODE] = current_mode
            if CONF_APP_TOKEN in user_input:
                self._data[CONF_APP_TOKEN] = user_input[CONF_APP_TOKEN]
            else:
                self._data.pop(CONF_APP_TOKEN, None)
            if CONF_CLIENT_TOKEN in user_input:
                self._data[CONF_CLIENT_TOKEN] = user_input[CONF_CLIENT_TOKEN]
            else:
                self._data.pop(CONF_CLIENT_TOKEN, None)

            requires_client_token = current_mode in (MODE_FULL, MODE_RECEIVE_ONLY)

            if requires_client_token:
                try:
                    from .api import (
                        GotifyApiClient,
                        GotifyAuthError,
                        GotifyConnectionError,
                    )

                    api = GotifyApiClient(
                        async_get_clientsession(self.hass),
                        self._data[CONF_URL],
                        verify_ssl=self._data[CONF_VERIFY_SSL],
                    )
                    await api.async_get_current_user(self._data[CONF_CLIENT_TOKEN])
                    self._applications = await api.async_get_applications(
                        self._data[CONF_CLIENT_TOKEN]
                    )
                except GotifyAuthError:
                    errors["base"] = "invalid_client_token"
                except GotifyConnectionError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "unknown"

            if not errors:
                return await self.async_step_behavior()

        requires_app_token = current_mode in (MODE_FULL, MODE_SEND_ONLY)
        requires_client_token = current_mode in (MODE_FULL, MODE_RECEIVE_ONLY)

        schema_dict: dict[Any, Any] = {
            vol.Required(
                CONF_MODE,
                default=current_mode,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_FULL, MODE_SEND_ONLY, MODE_RECEIVE_ONLY],
                    translation_key="mode",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        }
        if requires_app_token:
            schema_dict[
                vol.Required(CONF_APP_TOKEN, default=self._data.get(CONF_APP_TOKEN, ""))
            ] = str
        if requires_client_token:
            schema_dict[
                vol.Required(
                    CONF_CLIENT_TOKEN,
                    default=self._data.get(CONF_CLIENT_TOKEN, ""),
                )
            ] = str

        return self.async_show_form(
            step_id="access",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )

    async def async_step_behavior(self, user_input: dict[str, Any] | None = None):
        """Collect polling and streaming behavior."""
        if user_input is not None:
            self._data.update(user_input)

            if self._data[CONF_MODE] in (MODE_FULL, MODE_RECEIVE_ONLY) and self._applications:
                return await self.async_step_application()

            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)

        schema_dict: dict[Any, Any] = {
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=self._data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
            )
        }

        if self._data.get(CONF_MODE) in (MODE_FULL, MODE_RECEIVE_ONLY):
            schema_dict[
                vol.Required(
                    CONF_ENABLE_WEBSOCKET,
                    default=self._data.get(
                        CONF_ENABLE_WEBSOCKET,
                        DEFAULT_ENABLE_WEBSOCKET,
                    ),
                )
            ] = bool

        return self.async_show_form(
            step_id="behavior",
            data_schema=vol.Schema(schema_dict),
        )

    async def async_step_application(self, user_input: dict[str, Any] | None = None):
        """Optionally select a monitored application."""
        if user_input is not None:
            selected = user_input.get(CONF_MONITORED_APPLICATION_ID)
            self._data.pop(CONF_MONITORED_APPLICATION_ID, None)
            self._data.pop(CONF_MONITORED_APPLICATION_NAME, None)
            if selected:
                for app in self._applications:
                    if str(app.get("id")) == str(selected):
                        self._data[CONF_MONITORED_APPLICATION_ID] = app.get("id")
                        self._data[CONF_MONITORED_APPLICATION_NAME] = app.get("name")
                        break
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)

        options = {"": "—"}
        for app in self._applications:
            app_id = app.get("id")
            name = app.get("name") or f"#{app_id}"
            description = app.get("description")
            label = f"{name} ({app_id})"
            if description:
                label = f"{label} · {description}"
            options[str(app_id)] = label

        schema = vol.Schema(
            {vol.Optional(CONF_MONITORED_APPLICATION_ID, default=""): vol.In(options)}
        )
        return self.async_show_form(step_id="application", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return GotifyOptionsFlow(config_entry)


class GotifyOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Gotify."""

    def __init__(self, entry) -> None:
        """Initialize options flow."""
        self.entry = entry
        self._applications: list[dict[str, Any]] = []
        self._options: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage behavior options."""
        if user_input is not None:
            self._options.update(user_input)
            if self.entry.data.get(CONF_CLIENT_TOKEN):
                return await self.async_step_application()
            return self.async_create_entry(title="", data=self._options)

        self._options = dict(self.entry.options)
        schema_dict: dict[Any, Any] = {
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=self.entry.options.get(
                    CONF_SCAN_INTERVAL,
                    self.entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
            ),
            vol.Required(
                CONF_VERIFY_SSL,
                default=self.entry.options.get(
                    CONF_VERIFY_SSL,
                    self.entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                ),
            ): bool,
        }

        if self.entry.data.get(CONF_CLIENT_TOKEN):
            schema_dict[
                vol.Required(
                    CONF_ENABLE_WEBSOCKET,
                    default=self.entry.options.get(
                        CONF_ENABLE_WEBSOCKET,
                        self.entry.data.get(
                            CONF_ENABLE_WEBSOCKET,
                            DEFAULT_ENABLE_WEBSOCKET,
                        ),
                    ),
                )
            ] = bool

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))

    async def async_step_application(self, user_input: dict[str, Any] | None = None):
        """Manage the monitored application option."""
        if not self.entry.data.get(CONF_CLIENT_TOKEN):
            return self.async_create_entry(title="", data=self._options)

        if not self._applications:
            try:
                from .api import GotifyApiClient

                api = GotifyApiClient(
                    async_get_clientsession(self.hass),
                    self.entry.data[CONF_URL],
                    verify_ssl=self._options.get(
                        CONF_VERIFY_SSL,
                        self.entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                    ),
                )
                self._applications = await api.async_get_applications(
                    self.entry.data[CONF_CLIENT_TOKEN]
                )
            except Exception:
                self._applications = []

        if user_input is not None:
            new_options = dict(self._options)
            selected = user_input.get(CONF_MONITORED_APPLICATION_ID)
            if selected:
                new_options[CONF_MONITORED_APPLICATION_ID] = int(selected)
                for app in self._applications:
                    if str(app.get("id")) == str(selected):
                        new_options[CONF_MONITORED_APPLICATION_NAME] = app.get("name")
                        break
            else:
                new_options.pop(CONF_MONITORED_APPLICATION_ID, None)
                new_options.pop(CONF_MONITORED_APPLICATION_NAME, None)

            return self.async_create_entry(title="", data=new_options)

        app_options = {"": "—"}
        for app in self._applications:
            app_id = app.get("id")
            name = app.get("name") or f"#{app_id}"
            description = app.get("description")
            label = f"{name} ({app_id})"
            if description:
                label = f"{label} · {description}"
            app_options[str(app_id)] = label

        current_app_id = self.entry.options.get(
            CONF_MONITORED_APPLICATION_ID,
            self.entry.data.get(CONF_MONITORED_APPLICATION_ID, ""),
        )
        current_app_id = "" if current_app_id in (None, "") else str(current_app_id)

        schema = vol.Schema(
            {vol.Optional(CONF_MONITORED_APPLICATION_ID, default=current_app_id): vol.In(app_options)}
        )
        return self.async_show_form(step_id="application", data_schema=schema)
