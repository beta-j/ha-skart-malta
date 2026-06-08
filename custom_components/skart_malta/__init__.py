"""The Skart Malta integration."""

from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_COLLECTION_TIME,
    CONF_GLASS_WEEKDAY,
    CONF_GLASS_WEEKS,
    DEFAULT_COLLECTION_TIME,
    DEFAULT_GLASS_WEEKDAY,
    DEFAULT_GLASS_WEEKS,
    DOMAIN,
    next_glass_date,
    streams_for_date,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Recompute a little after midnight so "today" rolls over reliably.
UPDATE_INTERVAL = timedelta(minutes=30)


class MaltaWasteCoordinator(DataUpdateCoordinator):
    """Computes the waste schedule. No network — pure date logic."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry

    def _options(self) -> tuple[int, list[int], str]:
        data = {**self.entry.data, **self.entry.options}
        weekday = data.get(CONF_GLASS_WEEKDAY, DEFAULT_GLASS_WEEKDAY)
        weeks = data.get(CONF_GLASS_WEEKS, DEFAULT_GLASS_WEEKS)
        # Options may come back as strings from the UI selector.
        weeks = [int(w) for w in weeks]
        collection_time = data.get(CONF_COLLECTION_TIME, DEFAULT_COLLECTION_TIME)
        return int(weekday), weeks, collection_time

    async def _async_update_data(self) -> dict:
        weekday, weeks, collection_time = self._options()
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return {
            "today": streams_for_date(today, weekday, weeks),
            "tomorrow": streams_for_date(tomorrow, weekday, weeks),
            "today_date": today.isoformat(),
            "tomorrow_date": tomorrow.isoformat(),
            "collection_time": collection_time,
            "next_glass": (
                d.isoformat()
                if (d := next_glass_date(today, weekday, weeks))
                else None
            ),
        }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Skart Malta from a config entry."""
    coordinator = MaltaWasteCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
