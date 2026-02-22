# Govee Razer Protocol Technical Documentation

This document describes the UDP protocol used by Govee LED devices for the Razer Chroma / DreamView integration.

## Protocol Overview

The protocol uses UDP packets on port 4003, with binary data wrapped in JSON format.

## Packet Structure

### JSON Wrapper

All packets are wrapped in JSON:

```json
{
  "msg": {
    "cmd": "razer",
    "data": {
      "pt": "<base64_encoded_binary_data>"
    }
  }
}
```

### Binary Packet Format

The binary data (before base64 encoding) has this structure:

```
Byte 0:    0xBB           (Magic byte / Protocol identifier)
Byte 1:    0x00           (Extended size - for packets >255 bytes)
Byte 2:    <data_size>    (Size of command + data in bytes)
Byte 3:    <command>      (Command type: 0xB1 or 0xB0)
Byte 4+:   <data>         (Variable length data)
Last byte: <checksum>     (XOR checksum of all previous bytes)
```

### Checksum Calculation

The checksum is calculated by XORing all bytes before the checksum byte:

```python
checksum = 0
for byte in packet:
    checksum ^= byte
```

## Commands

### Command 0xB1: Enable Razer Protocol

Activates the Razer/DreamView control mode on the device.

**Packet Structure:**
```
BB 00 01 B1 <enable_flag> <checksum>
```

**Fields:**
- `enable_flag`: `0x01` to enable, `0x00` to disable

**Example (Enable):**
```
BB 00 01 B1 01 0A
```

**Notes:**
- Must be sent before LED data can be controlled
- Device has 1-minute timeout - will revert to app control if no LED data received
- Recommended to send keep-alive enable packet every 30-45 seconds

### Command 0xB0: LED Color Data

Sends color information for individual LEDs or color sections.

**Packet Structure:**
```
BB 00 <data_size> B0 <gradient_mode> <color_count> <RGB_data> <checksum>
```

**Fields:**
- `data_size`: Total bytes of data following (2 + color_count × 3)
- `gradient_mode`: 
  - `0x00` = Discrete segments (each color controls specific LEDs)
  - `0x01` = Gradient mode (interpolate between colors)
- `color_count`: Number of RGB color triplets in the packet
- `RGB_data`: Sequence of R, G, B bytes (3 bytes per color)

**Data Size Calculation:**
```
data_size = 2 + (color_count × 3)
```

For 10 colors:
```
data_size = 2 + (10 × 3) = 32 (0x20)
```

**Example (10 colors):**
```
BB 00 20 B0 01 0A [30 bytes of RGB data] <checksum>
```

## Color Modes

### Discrete Mode (gradient_mode = 0x00)

Each RGB triplet controls a specific LED or group of LEDs. The device divides the strip into sections based on the color count.

Example with 5 colors on a 10-LED strip:
- Color 1 → LEDs 1-2
- Color 2 → LEDs 3-4
- Color 3 → LEDs 5-6
- Color 4 → LEDs 7-8
- Color 5 → LEDs 9-10

### Gradient Mode (gradient_mode = 0x01)

The device interpolates smoothly between the provided colors across the entire strip.

Example with 5 colors on a 10-LED strip:
- The colors are smoothly blended across all 10 LEDs
- Creates smooth color transitions

## Implementation Details

### Keep-Alive Mechanism

To maintain control, send an enable command (0xB1) every 30 seconds:

```python
import time

last_enable_time = 0

def send_colors():
    # Check if we need to send keep-alive
    if time.time() - last_enable_time > 30:
        send_enable_command()
        last_enable_time = time.time()
    
    # Send color data
    send_led_colors()
```

### Recommended Update Rate

- **20-60 FPS** (0.017-0.05 seconds): Smooth animations
- **10-20 FPS** (0.05-0.1 seconds): Good balance for most effects
- **< 10 FPS** (> 0.1 seconds): Noticeable stepping, lower network usage

### Error Handling

UDP is unreliable (fire-and-forget):
- Packets may be lost
- No acknowledgment from device
- Consider sending critical frames multiple times
- Monitor device state via other means if needed

### Network Configuration

- **Protocol**: UDP (no connection, no ACK)
- **Port**: 4003
- **MTU**: Standard Ethernet (1500 bytes) - plenty of room
- **Multicast**: Not used - direct to device IP
- **Broadcast**: Not recommended - use device-specific IPs

## Color Calculation Examples

### Basic RGB

```python
def create_color_packet(colors):
    """
    Create LED data packet.
    
    Args:
        colors: List of (r, g, b) tuples
    """
    color_count = len(colors)
    data_size = 2 + (color_count * 3)
    
    packet = bytes([
        0xBB,           # Magic
        0x00,           # Extended size
        data_size,      # Data size
        0xB0,           # LED command
        0x01,           # Gradient mode
        color_count     # Color count
    ])
    
    # Add RGB data
    for r, g, b in colors:
        packet += bytes([r, g, b])
    
    # Add checksum
    checksum = 0
    for byte in packet:
        checksum ^= byte
    packet += bytes([checksum])
    
    return packet
```

### Brightness Adjustment

```python
def apply_brightness(rgb, brightness):
    """
    Apply brightness to RGB color.
    
    Args:
        rgb: (r, g, b) tuple (0-255 each)
        brightness: 0-255
    
    Returns:
        (r, g, b) tuple with brightness applied
    """
    scale = brightness / 255.0
    return (
        int(rgb[0] * scale),
        int(rgb[1] * scale),
        int(rgb[2] * scale)
    )
```

### Interpolation

```python
def interpolate_color(color1, color2, position):
    """
    Interpolate between two colors.
    
    Args:
        color1: (r, g, b) tuple
        color2: (r, g, b) tuple
        position: 0.0 to 1.0
    
    Returns:
        (r, g, b) tuple
    """
    r = int(color1[0] + (color2[0] - color1[0]) * position)
    g = int(color1[1] + (color2[1] - color1[1]) * position)
    b = int(color1[2] + (color2[2] - color1[2]) * position)
    return (r, g, b)
```

## Device-Specific Notes

### LED Count Detection

There is no known command to query the LED count. You must:
1. Check in Govee app (Settings → Layout and Calibration)
2. Consult device manual
3. Test empirically

### Common LED Counts

- **5 segments**: Basic light bars
- **10 segments**: Common for strips
- **15-20 segments**: Longer strips
- **30-50 segments**: Extended strips

### Matrix Devices

Matrix devices (curtains, wall panels) have limited or no support for this protocol. The official Govee API may be better for these devices.

## Troubleshooting

### Device Not Responding

1. Verify LAN Control is enabled in Govee app
2. Check device IP address (may change if using DHCP)
3. Ensure port 4003 is not blocked by firewall
4. Confirm device is on same network as controller
5. Try power cycling the device

### Colors Don't Match

1. Check color_count matches device expectations
2. Try different gradient_mode values
3. Verify RGB byte order (some devices may differ)
4. Check brightness scaling

### Intermittent Control

1. Check network stability
2. Reduce update frequency
3. Ensure keep-alive is sent regularly
4. Monitor for packet loss

## References

- [OpenRGB Govee Implementation](https://gitlab.com/CalcProgrammer1/OpenRGB/-/merge_requests/2172)
- [LedFx Govee Support](https://docs.ledfx.app/en/latest/devices/govee.html)
- [SignalRGB Govee Plugin](https://github.com/fu-raz/signalrgb-govee-direct-connect)
- [Official Govee LAN API](https://app-h5.govee.com/user-manual/wlan-guide) (limited, single color only)

## License

This protocol documentation is provided for educational and interoperability purposes.
