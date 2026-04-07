"""Diagnostics support for Gotify."""

from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data

from .const import CONF_APP_TOKEN, CONF_CLIENT_TOKEN, DOMAIN


TO_REDACT = {
    CONF_APP_TOKEN,
    CONF_CLIENT_TOKEN,
}


async def async_get_config_entry_diagnostics(hass, entry):
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN]["entries"][entry.entry_id]

    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": async_redact_data(dict(entry.options), TO_REDACT),
        "runtime": {
            "stream_connected": coordinator.stream_connected,
            "received_messages_total": coordinator.received_messages_total,
        },
        "data": async_redact_data(coordinator.data or {}, TO_REDACT),
    }
