"""The Govee Razer LED Controller integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.NUMBER]


class GoveeWaveCoordinator:
    """Coordinator to manage wave parameters across entities."""

    def __init__(self):
        """Initialize the coordinator."""
        self.amplitude = 50
        self.speed = 30
        self.color_flow_speed = 0
        self.strip_entity = None
        self.amplitude_entity = None
        self.speed_entity = None
        self.color_flow_entity = None

    def update_amplitude(self, value: int):
        """Update amplitude and sync entities."""
        self.amplitude = value
        if self.amplitude_entity:
            self.amplitude_entity._value = value
            self.amplitude_entity.async_write_ha_state()
        if self.strip_entity:
            self.strip_entity._amplitude = value

    def update_speed(self, value: int):
        """Update speed and sync entities."""
        self.speed = value
        if self.speed_entity:
            self.speed_entity._value = value
            self.speed_entity.async_write_ha_state()
        if self.strip_entity:
            self.strip_entity._speed = value
            # Update wave steps
            if value != 0:
                import math
                self.strip_entity._wave_steps = round((2 * math.pi / (value / 100)) + 1)
            else:
                self.strip_entity._wave_steps = 100

    def update_color_flow_speed(self, value: int):
        """Update color flow speed and sync entities."""
        self.color_flow_speed = value
        if self.color_flow_entity:
            self.color_flow_entity._value = value
            self.color_flow_entity.async_write_ha_state()
        if self.strip_entity:
            self.strip_entity._color_flow_speed = value


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Govee Razer LED component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Govee Razer LED from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create coordinator for this entry
    coordinator = GoveeWaveCoordinator()
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
