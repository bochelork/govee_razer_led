"""Config flow for Govee Razer LED integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_NUM_LEDS,
    CONF_NUM_SECTIONS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_NUM_LEDS,
    DEFAULT_NUM_SECTIONS,
    DEFAULT_UPDATE_INTERVAL,
    MIN_SECTIONS,
    MAX_SECTIONS,
    MIN_UPDATE_INTERVAL,
    MAX_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class GoveeRazerLEDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Govee Razer LED."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input
            try:
                # Validate host format
                host = user_input[CONF_HOST]
                if not host:
                    errors["base"] = "invalid_host"
                else:
                    # Create a unique ID based on host
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()

                    if not errors:
                        return self.async_create_entry(
                            title=user_input[CONF_NAME],
                            data=user_input,
                        )
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        # Show the form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Govee Strip"): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_NUM_LEDS, default=DEFAULT_NUM_LEDS): vol.All(
                    cv.positive_int, vol.Range(min=1, max=100)
                ),
                vol.Optional(CONF_NUM_SECTIONS, default=DEFAULT_NUM_SECTIONS): vol.All(
                    cv.positive_int, vol.Range(min=MIN_SECTIONS, max=MAX_SECTIONS)
                ),
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(
                    cv.positive_float,
                    vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return GoveeRazerLEDOptionsFlowHandler(config_entry)


class GoveeRazerLEDOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Govee Razer LED."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the config entry with new values
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={**self._config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data={})

        # Get current values from either options or data
        current_num_leds = self._config_entry.options.get(
            CONF_NUM_LEDS,
            self._config_entry.data.get(CONF_NUM_LEDS, DEFAULT_NUM_LEDS)
        )
        current_num_sections = self._config_entry.options.get(
            CONF_NUM_SECTIONS,
            self._config_entry.data.get(CONF_NUM_SECTIONS, DEFAULT_NUM_SECTIONS)
        )
        current_update_interval = self._config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            self._config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_NUM_LEDS,
                    default=current_num_leds,
                ): vol.All(cv.positive_int, vol.Range(min=1, max=100)),
                vol.Optional(
                    CONF_NUM_SECTIONS,
                    default=current_num_sections,
                ): vol.All(cv.positive_int, vol.Range(min=MIN_SECTIONS, max=MAX_SECTIONS)),
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=current_update_interval,
                ): vol.All(
                    cv.positive_float,
                    vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
