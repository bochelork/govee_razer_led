"""Number platform for Govee Razer LED."""
import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Govee Razer LED number entities from a config entry."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_data["coordinator"]
    config = entry_data["config"]
    
    host = config[CONF_HOST]
    name = config[CONF_NAME]

    amplitude_entity = GoveeWaveAmplitude(hass, name, host, config_entry.entry_id, coordinator)
    speed_entity = GoveeWaveSpeed(hass, name, host, config_entry.entry_id, coordinator)
    
    # Register with coordinator
    coordinator.amplitude_entity = amplitude_entity
    coordinator.speed_entity = speed_entity
    
    entities = [amplitude_entity, speed_entity]

    async_add_entities(entities)


class GoveeWaveAmplitude(NumberEntity):
    """Representation of wave amplitude control."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:wave"

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        entry_id: str,
        coordinator,
    ):
        """Initialize the amplitude control."""
        self.hass = hass
        self._name = f"{name} Wave Amplitude"
        self._host = host
        self._entry_id = entry_id
        self._coordinator = coordinator
        self._value = coordinator.amplitude

    @property
    def name(self) -> str:
        """Return the name of the number entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wave_amplitude"

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Update the value via coordinator."""
        self._value = int(value)
        self._coordinator.update_amplitude(int(value))
        
        # Also call the strip's async_set_wave to trigger the update
        if self._coordinator.strip_entity:
            await self._coordinator.strip_entity.async_set_wave(amplitude=int(value))
        
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._name.replace(" Wave Amplitude", ""),
            "manufacturer": "Govee",
            "model": "Razer LED Strip",
        }


class GoveeWaveSpeed(NumberEntity):
    """Representation of wave speed control."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = -100
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:speedometer"

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        entry_id: str,
        coordinator,
    ):
        """Initialize the speed control."""
        self.hass = hass
        self._name = f"{name} Wave Speed"
        self._host = host
        self._entry_id = entry_id
        self._coordinator = coordinator
        self._value = coordinator.speed

    @property
    def name(self) -> str:
        """Return the name of the number entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wave_speed"

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Update the value via coordinator."""
        self._value = int(value)
        self._coordinator.update_speed(int(value))
        
        # Also call the strip's async_set_wave to trigger the update
        if self._coordinator.strip_entity:
            await self._coordinator.strip_entity.async_set_wave(speed=int(value))
        
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._name.replace(" Wave Speed", ""),
            "manufacturer": "Govee",
            "model": "Razer LED Strip",
        }
