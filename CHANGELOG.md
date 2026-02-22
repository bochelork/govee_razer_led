# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-02-19

### Added
- Initial release of Govee Razer LED Controller integration
- Support for Govee LED strips using Razer/DreamView UDP protocol
- UI-based configuration flow for easy setup
- Multi-section color control (up to 10 sections per strip)
- Three built-in effects:
  - `double`: Repeats section colors twice
  - `mirror`: Mirrors section colors
  - `stretched`: Smooth interpolation between colors
- Brightness wave animation system
  - Configurable amplitude (0-100)
  - Configurable speed (-100 to 100)
  - Smooth sinusoidal wave across strip
- `govee_razer_led.set_wave` service for dynamic wave control
- Automatic keep-alive mechanism (prevents timeout)
- Configurable update interval for performance tuning
- Support for multiple strips simultaneously
- Per-section entity control
- Main strip entity for overall control
- HACS compatibility
- Comprehensive documentation:
  - Installation guide (INSTALL.md)
  - Protocol documentation (PROTOCOL.md)
  - Example configurations
  - Troubleshooting guide

### Features
- **Direct UDP Control**: Low-latency local control without cloud
- **Per-LED Support**: Full per-LED color control capability
- **Dynamic Effects**: Real-time color interpolation and waves
- **Home Assistant Native**: First-class integration with HA ecosystem
- **Multi-Strip**: Control multiple strips independently
- **Configurable**: Extensive configuration options via UI or YAML

### Technical
- XOR checksum validation
- Base64 JSON packet encoding
- Gradient and discrete color modes
- Automatic protocol enable/keep-alive
- Asyncio-based update loop
- Thread-safe color management

### Known Limitations
- Matrix devices (curtains, panels) have limited support
- No device discovery (manual IP configuration required)
- UDP protocol (no delivery confirmation)
- 1-minute timeout requires keep-alive

## [0.1.0] - 2024-02-15

### Added
- Initial development version
- Basic protocol implementation
- Proof of concept

