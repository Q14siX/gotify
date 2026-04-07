"""Notify platform for Gotify."""

from __future__ import annotations

from typing import Any

from homeassistant.components.notify import NotifyEntity

from .const import DEFAULT_PRIORITY, DOMAIN
from .coordinator import GotifyCoordinator
from .entity import GotifyEntityMixin


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Gotify notify entity."""
    coordinator: GotifyCoordinator = hass.data[DOMAIN]["entries"][entry.entry_id]
    if coordinator.app_token:
        async_add_entities([GotifyNotifyEntity(coordinator, entry)])


class GotifyNotifyEntity(GotifyEntityMixin, NotifyEntity):
    """Home Assistant notify entity for Gotify."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GotifyCoordinator, entry) -> None:
        """Initialize entity."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_notify"
        self._attr_translation_key = "notifier"

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send message through Gotify."""
        await self.coordinator.async_send_message(
            message=message,
            title=kwargs.get("title"),
            priority=int(kwargs.get("data", {}).get("priority", DEFAULT_PRIORITY)),
            extras=kwargs.get("data", {}).get("extras"),
        )
        self.async_write_ha_state()
