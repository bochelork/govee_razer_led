# Installation Guide

This guide will walk you through installing and configuring the Govee Razer LED Controller integration for Home Assistant.

## Prerequisites

Before you begin, make sure you have:

1. **Home Assistant** installed and running (version 2023.1.0 or later)
2. **HACS** (Home Assistant Community Store) installed - [Installation instructions](https://hacs.xyz/docs/setup/download)
3. **Govee LED device** that supports LAN control with Razer/DreamView protocol
4. Device and Home Assistant on the **same local network**

## Step 1: Prepare Your Govee Device

### 1.1 Enable LAN Control

1. Open the **Govee Home** app on your phone
2. Select your LED device
3. Tap the **settings icon** (gear/cog)
4. Find and enable **LAN Control**
5. Note: Some devices may call this "DreamView" or "Razer Chroma Connect"

### 1.2 Find Your Device IP Address

There are several ways to find your device's IP:

**Method A: Govee App**
1. In Govee app, go to Settings → Device Info
2. Look for "IP Address" or "Network Info"
3. Write down the IP address (e.g., `192.168.1.126`)

**Method B: Router Admin Panel**
1. Log into your router's admin panel
2. Look for connected devices list
3. Find your Govee device (usually named "Govee-XXXX")
4. Note the IP address

**Method C: Network Scanner**
1. Use an app like "Fing" or "Network Analyzer"
2. Scan your network
3. Look for Govee devices
4. Note the IP address

### 1.3 Set Static IP (Highly Recommended)

To prevent your device IP from changing:

1. Log into your router's admin panel
2. Find DHCP/IP reservation settings
3. Create a reservation for your Govee device's MAC address
4. Assign a fixed IP (e.g., `192.168.1.126`)
5. Save and reboot your router if needed

### 1.4 Check Number of LEDs

1. In Govee app, go to Settings → Layout and Calibration
2. Count the number of addressable segments
3. Common values: 5, 10, 15, 20, 30, 40, 50
4. Write this down for later configuration

## Step 2: Install via HACS

### 2.1 Add Custom Repository

1. Open **HACS** in Home Assistant
2. Click on **"Integrations"**
3. Click the **three dots** (⋮) in the top right
4. Select **"Custom repositories"**
5. Add repository URL: `https://github.com/bochelork/govee_razer_led`
6. Select category: **"Integration"**
7. Click **"Add"**

### 2.2 Install the Integration

1. In HACS, search for **"Govee Razer LED Controller"**
2. Click on the integration
3. Click **"Download"** or **"Install"**
4. Select the latest version
5. Click **"Download"** again to confirm

### 2.3 Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **"Restart"** (top right)
3. Click **"Restart Home Assistant"**
4. Wait for Home Assistant to fully restart (1-2 minutes)

## Step 3: Configure the Integration

### 3.1 Add Integration via UI

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"** (bottom right)
3. Search for **"Govee Razer LED"**
4. Click on it to start configuration

### 3.2 Configuration Form

Fill in the following information:

| Field | Example | Description |
|-------|---------|-------------|
| **Strip Name** | `Living Room Strip` | Friendly name for your strip |
| **IP Address** | `192.168.1.126` | Device IP from Step 1.2 |
| **Port** | `4003` | UDP port (leave default) |
| **Number of LEDs** | `10` | Total LEDs from Step 1.4 |
| **Number of Sections** | `5` | Color sections (typically 5) |
| **Update Interval** | `0.05` | Seconds between updates |

### 3.3 Click Submit

The integration will create:
- 1 main strip entity: `light.living_room_strip`
- 5 section entities: `light.living_room_strip_section_1` through `section_5`

## Step 4: Test Your Setup

### 4.1 Basic Test

1. Go to **Settings** → **Devices & Services**
2. Find your Govee device
3. Click on it to see all entities
4. Click on `light.living_room_strip`
5. Toggle the light **ON**
6. Your LEDs should light up!

### 4.2 Test Colors

1. With the light on, click **"Pick a color"**
2. Select different colors
3. Try adjusting brightness
4. Verify colors display correctly

### 4.3 Test Sections

1. Turn off the main strip
2. Click on `light.living_room_strip_section_1`
3. Turn it on with a specific color (e.g., red)
4. Turn on `section_2` with a different color (e.g., blue)
5. Continue with other sections
6. Observe the color distribution

### 4.4 Test Effects

1. Select the main strip entity
2. Go to **"Effect"** dropdown
3. Try each effect:
   - **double**: Repeats pattern twice
   - **mirror**: Mirrors the colors
   - **stretched**: Smooth interpolation

## Step 5: Configure Wave Effects

### 5.1 Using Developer Tools

1. Go to **Developer Tools** → **Services**
2. Select service: `govee_razer_led.set_wave`
3. Fill in:
   ```yaml
   target:
     entity_id: light.living_room_strip
   data:
     amplitude: 50
     speed: 30
   ```
4. Click **"Call Service"**
5. Observe the brightness wave animation

### 5.2 Wave Parameters

- **Amplitude** (0-100): Wave intensity
  - 0 = No wave (static brightness)
  - 50 = Medium wave
  - 100 = Maximum wave intensity

- **Speed** (-100 to 100): Wave animation speed
  - Positive = Forward direction
  - Negative = Reverse direction
  - Higher absolute value = Faster
  - 0 = Frozen wave

### 5.3 Example Waves

**Subtle breathing:**
```yaml
amplitude: 30
speed: 10
```

**Fast pulse:**
```yaml
amplitude: 80
speed: 60
```

**Reverse slow wave:**
```yaml
amplitude: 40
speed: -20
```

## Step 6: Create Automations

### 6.1 Simple Automation

Create a simple sunset automation:

1. Go to **Settings** → **Automations & Scenes**
2. Click **"Create Automation"**
3. Click **"Start with an empty automation"**
4. Set trigger: **Sun** → **Sunset** (with -30 minute offset)
5. Add action: **Call service** → `light.turn_on`
6. Select your section entities
7. Set colors and brightness
8. Save automation

### 6.2 Advanced Automation

See `examples/configuration.yaml` for complete automation examples.

## Step 7: Multiple Strips

### 7.1 Add Additional Strips

To add more strips, repeat Step 3 for each device:

1. **Settings** → **Devices & Services**
2. **"+ Add Integration"**
3. Search **"Govee Razer LED"**
4. Configure with different:
   - Name
   - IP address
   - LED count (if different model)

### 7.2 Organize in Areas

1. Go to **Settings** → **Areas**
2. Create areas (Living Room, Bedroom, etc.)
3. Go back to **Devices & Services**
4. Click on each Govee device
5. Assign to appropriate area

## Troubleshooting

### Issue: Lights don't respond

**Solutions:**
1. Verify LAN Control is enabled in Govee app
2. Check device IP with `ping <ip_address>`
3. Verify both devices on same network
4. Check firewall isn't blocking UDP port 4003
5. Power cycle the Govee device
6. Restart Home Assistant

### Issue: Wrong colors or sections

**Solutions:**
1. Verify `num_leds` setting matches your device
2. Check `num_sections` (usually 5)
3. Try different effects
4. Reconfigure in Govee app layout settings

### Issue: Choppy animations

**Solutions:**
1. Increase `update_interval` (e.g., from 0.05 to 0.1)
2. Reduce wave speed
3. Check network congestion
4. Verify Home Assistant has sufficient CPU/RAM

### Issue: Lights revert to app control

**Solutions:**
1. Check Home Assistant logs for errors
2. Verify integration is running
3. Restart integration
4. Check network stability

### Issue: Can't find device IP

**Solutions:**
1. Use network scanner app (Fing)
2. Check router DHCP client list
3. Reset device and check Govee app
4. Ensure device is connected to WiFi (not just Bluetooth)

## Advanced Configuration

### Update Interval Guidelines

Choose based on your needs:

| FPS | Interval | Use Case |
|-----|----------|----------|
| 60 | 0.017s | Very smooth, gaming, music reactive |
| 30 | 0.033s | Smooth animations, recommended |
| 20 | 0.05s | Default, good balance |
| 10 | 0.1s | Slower animations, lower network usage |
| 5 | 0.2s | Minimal network usage |

### Configuration via YAML

If you prefer YAML configuration:

1. Edit `configuration.yaml`
2. Add entries as shown in `examples/configuration.yaml`
3. Restart Home Assistant
4. Devices will appear automatically

Note: UI configuration is recommended for easier management.

## Getting Help

If you encounter issues:

1. **Check the logs:**
   - Settings → System → Logs
   - Look for `govee_razer_led` errors

2. **Enable debug logging:**
   Add to `configuration.yaml`:
   ```yaml
   logger:
     default: warning
     logs:
       custom_components.govee_razer_led: debug
   ```

3. **Open an issue:**
   - Visit: https://github.com/bochelork/govee_razer_led/issues
   - Include:
     - Home Assistant version
     - Integration version
     - Device model
     - Error logs
     - Configuration details

## Next Steps

- Explore automation examples
- Set up scenes with different color combinations
- Integrate with music/media players
- Create dashboard cards for quick control
- Share your configurations with the community!

---

**Congratulations!** You've successfully installed and configured the Govee Razer LED Controller. Enjoy your dynamic lighting! 🎉
