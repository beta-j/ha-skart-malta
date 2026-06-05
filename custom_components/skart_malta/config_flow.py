"""Config flow for Skart Malta."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_COLLECTION_TIME,
    CONF_GLASS_WEEKDAY,
    CONF_GLASS_WEEKS,
    CONF_NAME,
    DEFAULT_COLLECTION_TIME,
    DEFAULT_GLASS_WEEKDAY,
    DEFAULT_GLASS_WEEKS,
    DEFAULT_NAME,
    DOMAIN,
)

WEEKDAYS = [
    selector.SelectOptionDict(value="0", label="Monday"),
    selector.SelectOptionDict(value="1", label="Tuesday"),
    selector.SelectOptionDict(value="2", label="Wednesday"),
    selector.SelectOptionDict(value="3", label="Thursday"),
    selector.SelectOptionDict(value="4", label="Friday"),
    selector.SelectOptionDict(value="5", label="Saturday"),
    selector.SelectOptionDict(value="6", label="Sunday"),
]

WEEK_OPTIONS = [
    selector.SelectOptionDict(value="1", label="1st"),
    selector.SelectOptionDict(value="2", label="2nd"),
    selector.SelectOptionDict(value="3", label="3rd"),
    selector.SelectOptionDict(value="4", label="4th"),
]


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)
            ): str,
            vol.Required(
                CONF_COLLECTION_TIME,
                default=defaults.get(CONF_COLLECTION_TIME, DEFAULT_COLLECTION_TIME),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_GLASS_WEEKDAY,
                default=str(defaults.get(CONF_GLASS_WEEKDAY, DEFAULT_GLASS_WEEKDAY)),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(options=WEEKDAYS)
            ),
            vol.Required(
                CONF_GLASS_WEEKS,
                default=[
                    str(w)
                    for w in defaults.get(CONF_GLASS_WEEKS, DEFAULT_GLASS_WEEKS)
                ],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=WEEK_OPTIONS, multiple=True
                )
            ),
        }
    )


def _normalise(user_input: dict[str, Any]) -> dict[str, Any]:
    """Coerce selector strings into the types the rest of the code expects."""
    out = dict(user_input)
    out[CONF_GLASS_WEEKDAY] = int(out[CONF_GLASS_WEEKDAY])
    out[CONF_GLASS_WEEKS] = sorted(int(w) for w in out[CONF_GLASS_WEEKS])
    return out


class MaltaWasteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            data = _normalise(user_input)
            await self.async_set_unique_id(data[CONF_NAME].lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=data[CONF_NAME], data=data)

        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return MaltaWasteOptionsFlow(entry)


class MaltaWasteOptionsFlow(OptionsFlow):
    """Allow editing the glass schedule and collection time after setup."""

    def __init__(self, entry: ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="", data=_normalise(user_input)
            )

        current = {**self.entry.data, **self.entry.options}
        return self.async_show_form(
            step_id="init", data_schema=_schema(current)
        )
