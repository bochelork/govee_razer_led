"""Govee Razer Protocol Handler."""
import base64
import json
import logging
import socket
import time
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class GoveeProtocol:
    """Handle Govee Razer UDP protocol communication."""

    # Protocol constants
    MAGIC_BYTE = 0xBB
    EXTENDED_SIZE = 0x00
    CMD_ENABLE = 0xB1
    CMD_LED_DATA = 0xB0

    def __init__(self, host: str, port: int = 4003):
        """Initialize the Govee protocol handler."""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_enable_time = 0

    def _checksum(self, data: bytes) -> int:
        """Calculate XOR checksum for the data."""
        chksum = 0
        for byte in data:
            chksum ^= byte
        return chksum

    def _create_packet(self, command: int, data: bytes) -> bytes:
        """Create a protocol packet with checksum."""
        packet = bytes(
            [
                self.MAGIC_BYTE,
                self.EXTENDED_SIZE,
                len(data),
                command,
            ]
        ) + data
        
        checksum = self._checksum(packet)
        return packet + bytes([checksum])

    def _wrap_json(self, payload: bytes) -> bytes:
        """Wrap binary payload in JSON format."""
        base64_payload = base64.b64encode(payload).decode("ascii")
        msg = {"msg": {"cmd": "razer", "data": {"pt": base64_payload}}}
        return json.dumps(msg).encode("utf-8")

    def send_enable(self, enable: bool = True) -> None:
        """Send protocol enable command."""
        data = bytes([0x01 if enable else 0x00])
        packet = self._create_packet(self.CMD_ENABLE, data)
        json_packet = self._wrap_json(packet)
        
        try:
            self.socket.sendto(json_packet, (self.host, self.port))
            self.last_enable_time = time.time()
            _LOGGER.debug("Sent enable command to %s:%s", self.host, self.port)
        except Exception as err:
            _LOGGER.error("Failed to send enable command: %s", err)

    def send_colors(
        self,
        colors: list,
        num_leds: int = 10,
        gradient_mode: bool = True,
    ) -> None:
        """
        Send LED color data.
        
        Args:
            colors: List of RGB tuples [(r,g,b), ...]
            num_leds: Total number of LEDs
            gradient_mode: If True, interpolate between colors
        """
        # Keep-alive check (send enable every 30 seconds)
        if time.time() - self.last_enable_time > 30:
            self.send_enable(True)

        # Prepare color data
        color_count = len(colors)
        gradient_flag = 0x01 if gradient_mode else 0x00
        
        # Build data: [gradient_flag, color_count, r, g, b, r, g, b, ...]
        data = bytes([gradient_flag, color_count])
        
        for r, g, b in colors:
            data += bytes([r, g, b])

        packet = self._create_packet(self.CMD_LED_DATA, data)
        json_packet = self._wrap_json(packet)

        try:
            self.socket.sendto(json_packet, (self.host, self.port))
            _LOGGER.debug(
                "Sent %d colors to %s:%s (gradient=%s)",
                color_count,
                self.host,
                self.port,
                gradient_mode,
            )
        except Exception as err:
            _LOGGER.error("Failed to send color data: %s", err)

    def close(self) -> None:
        """Close the socket."""
        try:
            self.socket.close()
        except Exception as err:
            _LOGGER.error("Error closing socket: %s", err)


class GoveeColorManager:
    """Manage color interpolation and effects."""

    def __init__(self, num_leds: int, num_sections: int):
        """Initialize the color manager."""
        self.num_leds = num_leds
        self.num_sections = num_sections
        self.section_colors = [[0, 0, 0] for _ in range(num_sections)]

    def set_section_color(self, section: int, rgb: tuple) -> None:
        """Set color for a specific section."""
        if 0 <= section < self.num_sections:
            self.section_colors[section] = list(rgb)

    def get_section_color(self, section: int) -> Optional[list]:
        """Get color for a specific section."""
        if 0 <= section < self.num_sections:
            return self.section_colors[section]
        return None

    def interpolate(self, start_color: list, end_color: list, steps: int) -> list:
        """Interpolate between two colors."""
        if steps == 0:
            return [start_color]
        
        result = []
        for i in range(steps + 1):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * i / steps)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * i / steps)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * i / steps)
            result.append([r, g, b])
        return result

    def generate_effect_colors(self, effect: str = "stretched") -> list:
        """
        Generate LED colors based on effect type.
        
        Args:
            effect: Effect name (double, mirror, stretched)
            
        Returns:
            List of RGB tuples for each LED
        """
        if effect == "double":
            # Repeat section colors twice
            colors = []
            leds_per_repeat = self.num_leds // 2
            leds_per_section = leds_per_repeat // self.num_sections
            
            for _ in range(2):
                for section in range(self.num_sections):
                    color = self.section_colors[section]
                    for _ in range(leds_per_section):
                        colors.append(tuple(color))
            
            # Fill remaining LEDs
            while len(colors) < self.num_leds:
                colors.append(tuple(self.section_colors[0]))
                
        elif effect == "mirror":
            # Mirror section colors
            colors = []
            leds_per_section = self.num_leds // (2 * self.num_sections)
            
            # First half
            for section in range(self.num_sections):
                color = self.section_colors[section]
                for _ in range(leds_per_section):
                    colors.append(tuple(color))
            
            # Second half (mirrored)
            for section in range(self.num_sections - 1, -1, -1):
                color = self.section_colors[section]
                for _ in range(leds_per_section):
                    colors.append(tuple(color))
            
            # Fill remaining LEDs
            while len(colors) < self.num_leds:
                colors.append(tuple(self.section_colors[0]))
                
        else:  # stretched (default)
            # Interpolate between section colors
            colors = []
            leds_per_section = self.num_leds // self.num_sections
            
            for i in range(self.num_sections):
                start_color = self.section_colors[i]
                end_color = self.section_colors[(i + 1) % self.num_sections]
                
                interpolated = self.interpolate(start_color, end_color, leds_per_section - 1)
                for color in interpolated[:-1]:  # Avoid duplicate at boundaries
                    colors.append(tuple(color))
            
            # Add final color and fill to num_leds
            colors.append(tuple(self.section_colors[-1]))
            while len(colors) < self.num_leds:
                colors.append(tuple(self.section_colors[0]))

        return colors[:self.num_leds]  # Ensure exact number of LEDs
