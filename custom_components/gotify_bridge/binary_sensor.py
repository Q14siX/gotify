"""Binary sensors for the Gotify integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GotifyCoordinator
from .entity import GotifyEntityMixin


async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Gotify binary sensors."""
    coordinator: GotifyCoordinator = hass.data[DOMAIN]["entries"][entry.entry_id]
    if coordinator.client_token:
        async_add_entities([GotifyWebsocketBinarySensor(coordinator, entry)])


class GotifyWebsocketBinarySensor(GotifyEntityMixin, CoordinatorEntity, BinarySensorEntity):
    """Binary sensor showing websocket status."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: GotifyCoordinator, entry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_websocket_connected"
        self._attr_translation_key = "websocket_connected"

    @property
    def is_on(self) -> bool:
        """Return true if websocket is connected."""
        return self.coordinator.stream_connected
