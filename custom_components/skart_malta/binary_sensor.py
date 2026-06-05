"""Binary sensor platform for Skart Malta."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaltaWasteCoordinator
from .const import DOMAIN, STREAM_GLASS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MaltaWasteCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MaltaWasteGlassToday(coordinator, entry)])


class MaltaWasteGlassToday(CoordinatorEntity, BinarySensorEntity):
    """True when glass is collected today."""

    _attr_has_entity_name = True
    _attr_name = "Glass day today"
    _attr_icon = "mdi:bottle-wine"

    def __init__(
        self, coordinator: MaltaWasteCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_glass_today"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Skart Malta",
            model="National Schedule",
        )

    @property
    def is_on(self) -> bool:
        return STREAM_GLASS in self.coordinator.data["today"]
