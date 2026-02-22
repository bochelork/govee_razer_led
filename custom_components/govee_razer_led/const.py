"""Constants for the Govee Razer LED integration."""

DOMAIN = "govee_razer_led"

# Configuration options
CONF_NUM_LEDS = "num_leds"
CONF_NUM_SECTIONS = "num_sections"
CONF_UPDATE_INTERVAL = "update_interval"

# Default values
DEFAULT_PORT = 4003
DEFAULT_NUM_LEDS = 10
DEFAULT_NUM_SECTIONS = 5
DEFAULT_UPDATE_INTERVAL = 0.05
DEFAULT_BRIGHTNESS = 128
DEFAULT_AMPLITUDE = 50
DEFAULT_SPEED = 30
DEFAULT_COLOR_FLOW_SPEED = 0  # 0 = disabled

# Limits
MIN_SECTIONS = 2
MAX_SECTIONS = 10
MIN_UPDATE_INTERVAL = 0.01
MAX_UPDATE_INTERVAL = 1.0

# Effects
EFFECT_DOUBLE = "double"
EFFECT_MIRROR = "mirror"
EFFECT_STRETCHED = "stretched"

EFFECTS = [EFFECT_DOUBLE, EFFECT_MIRROR, EFFECT_STRETCHED]

# Services
SERVICE_SET_WAVE = "set_wave"

# Service parameters
ATTR_AMPLITUDE = "amplitude"
ATTR_SPEED = "speed"
ATTR_COLOR_FLOW_SPEED = "color_flow_speed"
