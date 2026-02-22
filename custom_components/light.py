"""Light platform for Govee Razer LED."""
import asyncio
import logging
import math
from typing import Any, Optional

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import (
    DOMAIN,
    CONF_NUM_LEDS,
    CONF_NUM_SECTIONS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_NUM_LEDS,
    DEFAULT_NUM_SECTIONS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_BRIGHTNESS,
    DEFAULT_AMPLITUDE,
    DEFAULT_SPEED,
    EFFECTS,
    EFFECT_STRETCHED,
    SERVICE_SET_WAVE,
    ATTR_AMPLITUDE,
    ATTR_SPEED,
)
from .govee_protocol import GoveeColorManager, GoveeProtocol

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Govee Razer LED lights from a config entry."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_data["coordinator"]
    config = entry_data["config"]
    
    host = config[CONF_HOST]
    name = config[CONF_NAME]
    port = config.get(CONF_PORT, DEFAULT_PORT)
    num_leds = config.get(CONF_NUM_LEDS, DEFAULT_NUM_LEDS)
    num_sections = config.get(CONF_NUM_SECTIONS, DEFAULT_NUM_SECTIONS)
    update_interval = config.get(
        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
    )

    # Create the main strip controller
    strip = GoveeRazerStrip(
        hass, name, host, port, num_leds, num_sections, update_interval, coordinator
    )
    
    # Register strip with coordinator
    coordinator.strip_entity = strip

    # Create section entities
    entities = [strip]
    for i in range(num_sections):
        entities.append(
            GoveeRazerSection(
                hass, f"{name} Section {i+1}", strip, i, config_entry.entry_id
            )
        )

    async_add_entities(entities)

    # Register services
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_SET_WAVE,
        {
            vol.Optional(ATTR_AMPLITUDE): vol.All(
                cv.positive_int, vol.Range(min=0, max=100)
            ),
            vol.Optional(ATTR_SPEED): vol.All(vol.Coerce(int), vol.Range(min=-100, max=100)),
        },
        "async_set_wave",
    )


class GoveeRazerStrip(LightEntity):
    """Representation of a Govee Razer LED strip."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        port: int,
        num_leds: int,
        num_sections: int,
        update_interval: float,
        coordinator,
    ):
        """Initialize the strip."""
        self.hass = hass
        self._name = name
        self._host = host
        self._port = port
        self._num_leds = num_leds
        self._num_sections = num_sections
        self._update_interval = update_interval
        self._coordinator = coordinator

        # State
        self._is_on = False
        self._brightness = DEFAULT_BRIGHTNESS
        self._effect = EFFECT_STRETCHED
        
        # Wave parameters - use coordinator values
        self._amplitude = coordinator.amplitude
        self._speed = coordinator.speed
        self._wave_step = 0
        self._wave_steps = 100

        # Protocol and color management
        self._protocol = GoveeProtocol(host, port)
        self._color_manager = GoveeColorManager(num_leds, num_sections)

        # Update task
        self._update_task: Optional[asyncio.Task] = None
        self._running = False

    @property
    def name(self) -> str:
        """Return the name of the light."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_strip"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self._brightness

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.RGB

    @property
    def supported_color_modes(self) -> set:
        """Flag supported color modes."""
        return {ColorMode.RGB}

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return LightEntityFeature.EFFECT

    @property
    def effect_list(self) -> list:
        """Return the list of supported effects."""
        return EFFECTS

    @property
    def effect(self) -> Optional[str]:
        """Return the current effect."""
        return self._effect

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        if ATTR_EFFECT in kwargs:
            self._effect = kwargs[ATTR_EFFECT]

        self._is_on = True
        
        if not self._running:
            await self._start_update_loop()

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        self._is_on = False
        await self._stop_update_loop()
        
        # Send all black
        await self.hass.async_add_executor_job(
            self._protocol.send_colors, [(0, 0, 0)] * self._num_sections, self._num_leds, True
        )
        
        self.async_write_ha_state()

    async def async_set_wave(self, amplitude: Optional[int] = None, speed: Optional[int] = None) -> None:
        """Set wave parameters."""
        if amplitude is not None:
            self._coordinator.update_amplitude(amplitude)
            self._amplitude = amplitude
            
        if speed is not None:
            self._coordinator.update_speed(speed)
            self._speed = speed
            if speed != 0:
                self._wave_steps = round((2 * math.pi / (speed / 100)) + 1)
            else:
                self._wave_steps = 100

        _LOGGER.debug("Set wave: amplitude=%s, speed=%s", self._amplitude, self._speed)
        self.async_write_ha_state()

    def _calculate_brightness_wave(self, led_index: int) -> int:
        """Calculate brightness for a specific LED based on wave parameters."""
        if self._amplitude == 0:
            return self._brightness

        phase = (2 * math.pi * led_index) / (self._num_leds - 1)
        wave_offset = self._amplitude * math.sin(phase + self._wave_step * (self._speed / 100))
        brightness = self._brightness + wave_offset
        return max(0, min(255, int(brightness)))

    async def _update_loop(self) -> None:
        """Main update loop for sending LED data."""
        self._running = True
        
        # Enable protocol
        await self.hass.async_add_executor_job(self._protocol.send_enable, True)

        while self._running:
            try:
                if self._is_on:
                    # Generate effect colors
                    base_colors = self._color_manager.generate_effect_colors(self._effect)
                    
                    # Apply brightness wave
                    final_colors = []
                    for i, (r, g, b) in enumerate(base_colors):
                        led_brightness = self._calculate_brightness_wave(i)
                        scale = led_brightness / 255.0
                        final_colors.append(
                            (int(r * scale), int(g * scale), int(b * scale))
                        )

                    # Send to device
                    await self.hass.async_add_executor_job(
                        self._protocol.send_colors,
                        final_colors,
                        self._num_leds,
                        self._effect == EFFECT_STRETCHED,
                    )

                    # Update wave step
                    self._wave_step = (self._wave_step + 1) % self._wave_steps

                await asyncio.sleep(self._update_interval)

            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("Error in update loop: %s", err)
                await asyncio.sleep(1)

        self._running = False

    async def _start_update_loop(self) -> None:
        """Start the update loop."""
        if self._update_task is None or self._update_task.done():
            self._update_task = self.hass.async_create_task(self._update_loop())

    async def _stop_update_loop(self) -> None:
        """Stop the update loop."""
        self._running = False
        if self._update_task and not self._update_task.done():
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        self._update_task = None

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when entity is removed."""
        await self._stop_update_loop()
        await self.hass.async_add_executor_job(self._protocol.close)


class GoveeRazerSection(LightEntity):
    """Representation of a single section of the LED strip."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        strip: GoveeRazerStrip,
        section_index: int,
        entry_id: str,
    ):
        """Initialize a section."""
        self.hass = hass
        self._name = name
        self._strip = strip
        self._section_index = section_index
        self._entry_id = entry_id
        
        # State
        self._rgb_color = (255, 255, 255)
        self._brightness = 255

    @property
    def name(self) -> str:
        """Return the name of the section."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._strip._host}_section_{self._section_index}"

    @property
    def is_on(self) -> bool:
        """Return true if section is on."""
        return self._strip.is_on

    @property
    def brightness(self) -> int:
        """Return the brightness."""
        return self._brightness

    @property
    def rgb_color(self) -> tuple:
        """Return the RGB color."""
        return self._rgb_color

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode."""
        return ColorMode.RGB

    @property
    def supported_color_modes(self) -> set:
        """Flag supported color modes."""
        return {ColorMode.RGB}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the section."""
        if ATTR_RGB_COLOR in kwargs:
            self._rgb_color = kwargs[ATTR_RGB_COLOR]
            
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        # Apply brightness to RGB
        scale = self._brightness / 255.0
        adjusted_rgb = tuple(int(c * scale) for c in self._rgb_color)
        
        # Update color manager
        self._strip._color_manager.set_section_color(self._section_index, adjusted_rgb)

        # Turn on the strip if it's off
        if not self._strip.is_on:
            await self._strip.async_turn_on()

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the section."""
        # Set section to black
        self._strip._color_manager.set_section_color(self._section_index, (0, 0, 0))
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._strip._host)},
            "name": self._strip.name,
            "manufacturer": "Govee",
            "model": "Razer LED Strip",
        }
