"""The Gotify integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_BIG_IMAGE_URL,
    ATTR_CLICK_URL,
    ATTR_ENTRY_ID,
    ATTR_EXTRAS,
    ATTR_INTENT_URL,
    ATTR_MARKDOWN,
    ATTR_MESSAGE_ID,
    ATTR_PRIORITY,
    CONF_URL,
    CONF_VERIFY_SSL,
    DATA_ENTRIES,
    DEFAULT_PRIORITY,
    DOMAIN,
    PLATFORMS,
    SERVICE_CLEAR_MESSAGES,
    SERVICE_DELETE_MESSAGE,
    SERVICE_REFRESH,
    SERVICE_SEND_MESSAGE,
)

FIELD_MESSAGE = "message"
FIELD_TITLE = "title"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _build_extras(service_data: Mapping[str, Any]) -> dict[str, Any] | None:
    """Build a Gotify extras payload from service data."""
    extras: dict[str, Any] = {}

    if service_data.get(ATTR_MARKDOWN):
        extras.setdefault("client::display", {})["contentType"] = "text/markdown"

    click_url = service_data.get(ATTR_CLICK_URL)
    if click_url:
        extras.setdefault("client::notification", {})["click"] = {"url": click_url}

    big_image_url = service_data.get(ATTR_BIG_IMAGE_URL)
    if big_image_url:
        extras.setdefault("client::notification", {})["bigImageUrl"] = big_image_url

    intent_url = service_data.get(ATTR_INTENT_URL)
    if intent_url:
        extras.setdefault("android::action", {})["onReceive"] = {"intentUrl": intent_url}

    raw_extras = service_data.get(ATTR_EXTRAS)
    if isinstance(raw_extras, dict):
        for namespace, value in raw_extras.items():
            extras.setdefault(namespace, value)

    return extras or None


def _get_target_entry(hass: HomeAssistant, service_call: ServiceCall):
    """Get the targeted config entry coordinator."""
    entries = hass.data[DOMAIN][DATA_ENTRIES]
    entry_id = service_call.data.get(ATTR_ENTRY_ID)

    if entry_id:
        if entry_id not in entries:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unknown_entry_id",
                translation_placeholders={"entry_id": entry_id},
            )
        return entries[entry_id]

    if len(entries) == 1:
        return next(iter(entries.values()))

    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="entry_id_required",
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Gotify integration."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_ENTRIES, {})

    async def handle_send_message(service_call: ServiceCall) -> None:
        coordinator = _get_target_entry(hass, service_call)
        await coordinator.async_send_message(
            message=service_call.data[FIELD_MESSAGE],
            title=service_call.data.get(FIELD_TITLE),
            priority=service_call.data.get(ATTR_PRIORITY, DEFAULT_PRIORITY),
            extras=_build_extras(service_call.data),
        )

    async def handle_delete_message(service_call: ServiceCall) -> None:
        coordinator = _get_target_entry(hass, service_call)
        await coordinator.async_delete_message(service_call.data[ATTR_MESSAGE_ID])

    async def handle_clear_messages(service_call: ServiceCall) -> None:
        coordinator = _get_target_entry(hass, service_call)
        await coordinator.async_clear_messages()

    async def handle_refresh(service_call: ServiceCall) -> None:
        coordinator = _get_target_entry(hass, service_call)
        await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_MESSAGE,
            handle_send_message,
            schema=vol.Schema(
                {
                    vol.Optional(ATTR_ENTRY_ID): cv.string,
                    vol.Required(FIELD_MESSAGE): cv.string,
                    vol.Optional(FIELD_TITLE): cv.string,
                    vol.Optional(ATTR_PRIORITY, default=DEFAULT_PRIORITY): vol.Coerce(int),
                    vol.Optional(ATTR_MARKDOWN, default=False): cv.boolean,
                    vol.Optional(ATTR_CLICK_URL): cv.string,
                    vol.Optional(ATTR_BIG_IMAGE_URL): cv.string,
                    vol.Optional(ATTR_INTENT_URL): cv.string,
                    vol.Optional(ATTR_EXTRAS): dict,
                }
            ),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_DELETE_MESSAGE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_DELETE_MESSAGE,
            handle_delete_message,
            schema=vol.Schema(
                {
                    vol.Optional(ATTR_ENTRY_ID): cv.string,
                    vol.Required(ATTR_MESSAGE_ID): vol.Coerce(int),
                }
            ),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CLEAR_MESSAGES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_MESSAGES,
            handle_clear_messages,
            schema=vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string}),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REFRESH,
            handle_refresh,
            schema=vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string}),
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up Gotify from a config entry."""
    from .api import GotifyApiClient
    from .coordinator import GotifyCoordinator

    session = async_get_clientsession(hass)
    api = GotifyApiClient(
        session,
        entry.data[CONF_URL],
        verify_ssl=entry.options.get(
            CONF_VERIFY_SSL, entry.data.get(CONF_VERIFY_SSL, True)
        ),
    )

    coordinator = GotifyCoordinator(hass, api, entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_ENTRIES, {})
    hass.data[DOMAIN][DATA_ENTRIES][entry.entry_id] = coordinator

    await coordinator.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN][DATA_ENTRIES].pop(entry.entry_id, None)
        if coordinator is not None:
            await coordinator.async_stop()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry) -> None:
    """Reload config entry after updates."""
    await hass.config_entries.async_reload(entry.entry_id)
