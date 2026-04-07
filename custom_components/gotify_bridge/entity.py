"""Shared entity helpers for the Gotify integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import CONF_URL, DOMAIN


class GotifyEntityMixin:
    """Mixin providing common device information for all Gotify entities."""

    entry: object

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this config entry."""
        version: str | None = None
        coordinator = getattr(self, "coordinator", None)
        if coordinator is not None:
            data = getattr(coordinator, "data", None) or {}
            version = (data.get("version") or {}).get("version")

        kwargs: dict[str, str] = {}
        if version:
            kwargs["sw_version"] = version

        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
            name=self.entry.title,
            manufacturer="Gotify",
            model="Server",
            configuration_url=self.entry.data.get(CONF_URL),
            **kwargs,
        )
