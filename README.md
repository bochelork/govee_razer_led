# Govee Razer LED Controller for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/github/license/bochelork/govee_razer_led)](LICENSE)

Control your Govee LED strips using the Razer/DreamView UDP protocol directly from Home Assistant. This integration provides full per-LED control with dynamic effects, brightness waves, and color interpolation.

## Features

- 🎨 **Per-Section Color Control**: Control up to 5 color sections per strip
- 🌊 **Dynamic Effects**: Built-in effects including double, mirror, and stretched modes
- ✨ **Brightness Waves**: Animated brightness variations across the strip
- 🎯 **Direct UDP Control**: Low-latency local control without cloud dependency
- 🔄 **Multiple Strips**: Support for controlling multiple Govee strips simultaneously
- ⚡ **Configurable Refresh Rate**: Adjust update interval for smooth animations

## Supported Devices

Any Govee LED device that supports the Razer Chroma / DreamView protocol, including:
- H6046 (Gaming Light Bars)
- H6062 (Glide)
- H605C, H6054, H6056, H6059, H6072, H6073
- Most RGBIC strips with LAN control support

## Prerequisites

1. **Enable LAN Control** in the Govee app:
   - Open Govee Home app
   - Select your device
   - Go to Settings → LAN Control
   - Enable LAN Control
   
2. **Find your device IP address**:
   - In the Govee app, go to Settings → Device Info
   - Note the IP address
   - Consider setting a DHCP reservation on your router

3. **Determine segment count**:
   - In Govee app, go to Settings → Layout and Calibration
   - Count the number of addressable segments

## Installation

### HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/bochelork/govee_razer_led`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the Govee Razer LED Controller card
9. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/govee_razer_led` directory
2. Copy it to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Govee Razer LED"
4. Follow the configuration wizard

### Via configuration.yaml

```yaml
light:
  - platform: govee_razer_led
    strips:
      - name: "Living Room Strip"
        host: "192.168.1.126"
        port: 4003
        num_leds: 10
        num_sections: 5
        update_interval: 0.05
        
      - name: "Bedroom Strip"
        host: "192.168.1.104"
        port: 4003
        num_leds: 10
        num_sections: 5
        update_interval: 0.05
```

### Configuration Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `name` | Yes | - | Friendly name for the strip |
| `host` | Yes | - | IP address of the Govee device |
| `port` | No | 4003 | UDP port (usually 4003) |
| `num_leds` | No | 10 | Total number of LEDs on the strip |
| `num_sections` | No | 5 | Number of color sections (2-10) |
| `update_interval` | No | 0.05 | Update interval in seconds (0.01-1.0) |

## Usage

### Basic Light Control

The integration creates light entities for each strip. Each strip has 5 sections that can be controlled individually:

- `light.living_room_strip_section_1`
- `light.living_room_strip_section_2`
- `light.living_room_strip_section_3`
- `light.living_room_strip_section_4`
- `light.living_room_strip_section_5`

You can also control the entire strip:
- `light.living_room_strip`

### Effects

Select an effect using the effect service call:

```yaml
service: light.turn_on
target:
  entity_id: light.living_room_strip
data:
  effect: "stretched"
```

Available effects:
- **double**: Repeats the 5 section colors twice across the strip
- **mirror**: Mirrors the colors (1,2,3,4,5,5,4,3,2,1)
- **stretched**: Interpolates smoothly between section colors

### Brightness Waves

Control the wave animation parameters:

```yaml
service: govee_razer_led.set_wave
target:
  entity_id: light.living_room_strip
data:
  amplitude: 50      # Wave intensity (0-100)
  speed: 30          # Wave speed (-100 to 100, negative reverses)
```

### Advanced: Setting Section Colors

```yaml
service: light.turn_on
target:
  entity_id: light.living_room_strip_section_1
data:
  rgb_color: [255, 0, 0]
  brightness: 200
```

### Automation Example

Create a dynamic sunset effect:

```yaml
automation:
  - alias: "Sunset Effect"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - service: light.turn_on
        target:
          entity_id: 
            - light.living_room_strip_section_1
            - light.living_room_strip_section_2
        data:
          rgb_color: [255, 100, 0]  # Orange
      - service: light.turn_on
        target:
          entity_id:
            - light.living_room_strip_section_3
            - light.living_room_strip_section_4
        data:
          rgb_color: [255, 50, 100]  # Pink
      - service: light.turn_on
        target:
          entity_id: light.living_room_strip_section_5
        data:
          rgb_color: [100, 0, 150]  # Purple
      - service: light.turn_on
        target:
          entity_id: light.living_room_strip
        data:
          effect: "stretched"
      - service: govee_razer_led.set_wave
        target:
          entity_id: light.living_room_strip
        data:
          amplitude: 30
          speed: 10
```

## Services

### `govee_razer_led.set_wave`

Configure brightness wave animation.

**Service Data:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity_id` | string | Yes | Entity ID of the strip |
| `amplitude` | integer | No | Wave amplitude (0-100), default: 50 |
| `speed` | integer | No | Wave speed (-100 to 100), default: 30 |

### `govee_razer_led.set_effect`

Set the color distribution effect.

**Service Data:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity_id` | string | Yes | Entity ID of the strip |
| `effect` | string | Yes | Effect name: double, mirror, or stretched |

## Troubleshooting

### Lights not responding

1. **Check LAN Control is enabled** in Govee app
2. **Verify IP address** - use `ping <ip>` to test connectivity
3. **Check firewall rules** - UDP port 4003 must be allowed
4. **Confirm device is on same network** as Home Assistant
5. **Try restarting the Govee device** (power cycle)

### Choppy or laggy animations

1. **Reduce update_interval** (increase the number, e.g., from 0.05 to 0.1)
2. **Check network congestion**
3. **Ensure Home Assistant has sufficient resources**

### Wrong number of LEDs

1. **Check num_leds setting** matches your device
2. **Verify in Govee app** - Settings → Layout and Calibration
3. **Try common values**: 10, 15, 20, 30, 40, 50

### Colors don't match sections

1. **Confirm num_sections** is correct (typically 5)
2. **Try different effects** to see which works best
3. **Some devices may have different layouts** - experiment with settings

### Device goes back to app control

The Razer protocol has a 1-minute timeout. The integration automatically sends keep-alive packets, but if you see this:
1. **Check Home Assistant logs** for errors
2. **Verify the integration is running** (check entity states)
3. **Restart the integration** if needed

## Technical Details

This integration uses the Govee "Razer" / "DreamView" UDP protocol:

- **Port**: 4003 (UDP)
- **Protocol**: Binary data wrapped in JSON
- **Refresh**: Configurable (default 50ms for smooth 20 FPS)
- **Keep-alive**: Automatic every 30 seconds
- **Checksum**: XOR of all packet bytes

For more technical details, see [PROTOCOL.md](PROTOCOL.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

- Protocol reverse-engineered from Govee Desktop App and Razer Synapse integration
- Thanks to the OpenRGB and LedFx projects for protocol documentation
- Original Python implementation by the community

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with, endorsed by, or supported by Govee. Use at your own risk.

## Support

If you find this integration helpful, consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs via GitHub Issues
- 💡 Suggesting features via GitHub Discussions

---

**Made with ❤️ for the Home Assistant community**
