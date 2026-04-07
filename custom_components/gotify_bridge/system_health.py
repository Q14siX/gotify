"""System health for Gotify."""

from __future__ import annotations

from homeassistant.components import system_health

from .const import CONF_APP_TOKEN, CONF_CLIENT_TOKEN, CONF_ENABLE_WEBSOCKET, DOMAIN


async def async_register(hass, register):
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass):
    """Return system health info."""
    entries = hass.data.get(DOMAIN, {}).get("entries", {})
    first = next(iter(entries.values()), None)

    base_info = {
        "loaded_entries": len(entries),
    }

    if first is None:
        return base_info

    try:
        can_reach = await system_health.async_check_can_reach_url(
            hass,
            first.api.base_url,
        )
    except Exception:
        can_reach = "failed"

    return {
        **base_info,
        "can_reach_server": can_reach,
        "websocket_enabled": first.entry.options.get(
            CONF_ENABLE_WEBSOCKET,
            first.entry.data.get(CONF_ENABLE_WEBSOCKET, True),
        ),
        "has_app_token": bool(first.entry.data.get(CONF_APP_TOKEN)),
        "has_client_token": bool(first.entry.data.get(CONF_CLIENT_TOKEN)),
    }
