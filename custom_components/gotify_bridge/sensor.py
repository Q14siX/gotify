"""Sensors for the Gotify integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GotifyCoordinator
from .entity import GotifyEntityMixin


async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Gotify sensors."""
    coordinator: GotifyCoordinator = hass.data[DOMAIN]["entries"][entry.entry_id]

    entities: list[SensorEntity] = [
        GotifyValueSensor(
            coordinator,
            entry,
            "server_version",
            ("version", "version"),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyValueSensor(
            coordinator,
            entry,
            "server_commit",
            ("version", "commit"),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyValueSensor(
            coordinator,
            entry,
            "health",
            ("health", "health"),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyValueSensor(
            coordinator,
            entry,
            "database_health",
            ("health", "database"),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyValueSensor(
            coordinator,
            entry,
            "current_user",
            ("user", "name"),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyComputedSensor(
            coordinator,
            entry,
            "applications_count",
            lambda data: len(data.get("applications", [])),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyComputedSensor(
            coordinator,
            entry,
            "clients_count",
            lambda data: len(data.get("clients", [])),
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        GotifyComputedSensor(
            coordinator,
            entry,
            "monitored_messages_count",
            lambda data: len(data.get("monitored_messages", [])),
        ),
        GotifyComputedSensor(
            coordinator,
            entry,
            "received_messages_total",
            lambda data: data.get("received_messages_total", 0),
        ),
        GotifyComputedSensor(
            coordinator,
            entry,
            "last_message_title",
            lambda data: (data.get("last_received_message") or {}).get("title"),
        ),
        GotifyComputedSensor(
            coordinator,
            entry,
            "last_message_priority",
            lambda data: (data.get("last_received_message") or {}).get("priority"),
        ),
    ]
    async_add_entities(entities)


class _BaseGotifySensor(GotifyEntityMixin, CoordinatorEntity, SensorEntity):
    """Base class for Gotify sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GotifyCoordinator, entry, key: str, *, entity_category=None) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_entity_category = entity_category


class GotifyValueSensor(_BaseGotifySensor):
    """Sensor reading a nested value from coordinator data."""

    def __init__(
        self,
        coordinator: GotifyCoordinator,
        entry,
        key: str,
        value_path: tuple[str, ...],
        *,
        entity_category=None,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry, key, entity_category=entity_category)
        self._value_path = value_path

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        data: Any = self.coordinator.data or {}
        for part in self._value_path:
            if not isinstance(data, dict):
                return None
            data = data.get(part)
        return data


class GotifyComputedSensor(_BaseGotifySensor):
    """Sensor based on a callback."""

    def __init__(
        self,
        coordinator: GotifyCoordinator,
        entry,
        key: str,
        value_func,
        *,
        entity_category=None,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry, key, entity_category=entity_category)
        self._value_func = value_func

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        return self._value_func(self.coordinator.data or {})
