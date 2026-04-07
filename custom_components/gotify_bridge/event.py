"""Event platform for Gotify."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.event import EventDeviceClass, EventEntity

from .const import DOMAIN
from .coordinator import GotifyCoordinator
from .entity import GotifyEntityMixin


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Gotify event entity."""
    coordinator: GotifyCoordinator = hass.data[DOMAIN]["entries"][entry.entry_id]
    if coordinator.client_token:
        async_add_entities([GotifyIncomingMessageEventEntity(coordinator, entry)])


class GotifyIncomingMessageEventEntity(GotifyEntityMixin, EventEntity):
    """Represent incoming Gotify messages as an event entity."""

    _attr_has_entity_name = True
    _attr_device_class = EventDeviceClass.BUTTON
    _attr_event_types = ["received"]

    def __init__(self, coordinator: GotifyCoordinator, entry) -> None:
        """Initialize entity."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_incoming_message"
        self._attr_translation_key = "incoming_message"
        self._unsubscribe: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Register callback when entity is added."""
        await super().async_added_to_hass()
        self._unsubscribe = self.coordinator.register_message_listener(self._handle_message)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        await super().async_will_remove_from_hass()

    def _handle_message(self, payload: dict) -> None:
        """Push an incoming websocket message into the event entity."""
        self._trigger_event(
            "received",
            {
                "id": payload.get("id"),
                "appid": payload.get("appid"),
                "title": payload.get("title"),
                "message": payload.get("message"),
                "priority": payload.get("priority"),
                "date": payload.get("date"),
                "extras": payload.get("extras"),
                "raw": payload,
            },
        )
