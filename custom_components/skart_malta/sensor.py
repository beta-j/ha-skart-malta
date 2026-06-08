"""Sensor platform for Skart Malta."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaltaWasteCoordinator
from .const import (
    DOMAIN,
    STREAM_ICONS,
    STREAM_LABELS,
    STREAM_NONE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MaltaWasteCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MaltaWasteDaySensor(coordinator, entry, "today", "Today"),
            MaltaWasteDaySensor(coordinator, entry, "tomorrow", "Tomorrow"),
            MaltaWasteNextGlassSensor(coordinator, entry),
        ]
    )


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Skart Malta",
        model="National Schedule",
    )


class MaltaWasteDaySensor(CoordinatorEntity, SensorEntity):
    """Waste collected on a given day."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MaltaWasteCoordinator,
        entry: ConfigEntry,
        key: str,
        label: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> str:
        streams = self.coordinator.data[self._key]
        return ", ".join(STREAM_LABELS[s] for s in streams)

    @property
    def icon(self) -> str:
        streams = self.coordinator.data[self._key]
        primary = next((s for s in streams if s != STREAM_NONE), STREAM_NONE)
        return STREAM_ICONS[primary]

    @property
    def extra_state_attributes(self) -> dict:
        streams = self.coordinator.data[self._key]
        return {
            "streams": streams,
            "date": self.coordinator.data[f"{self._key}_date"],
            "is_glass_day": "glass" in streams,
            "collection_time": self.coordinator.data.get("collection_time"),
        }


class MaltaWasteNextGlassSensor(CoordinatorEntity, SensorEntity):
    """Date of the next glass collection."""

    _attr_has_entity_name = True
    _attr_name = "Next glass collection"
    _attr_icon = "mdi:bottle-wine"
    _attr_device_class = "date"

    def __init__(
        self, coordinator: MaltaWasteCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_glass"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self):
        from datetime import date

        value = self.coordinator.data.get("next_glass")
        return date.fromisoformat(value) if value else None
