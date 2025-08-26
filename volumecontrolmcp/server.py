"""
Windows Volume Control MCP Server

This MCP server provides tools to control Windows system volume including:
- Get current volume level
- Set volume to specific percentage
- Mute/unmute system
- Toggle mute status
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("volume-control-server")

# Define volume presets
class VolumePreset(Enum):
    MUTED = ("Muted", 0, True)
    LOW = ("Low", 25, False)
    MEDIUM = ("Medium", 50, False)
    HIGH = ("High", 75, False)
    MAX = ("Maximum", 100, False)

    def __init__(self, label: str, volume: int, muted: bool):
        self.label = label
        self.volume = volume
        self.muted = muted

# Create the MCP server
mcp = FastMCP("Volume Control")

# Define MCP Prompts
@mcp.prompt("volume-control-help")
def volume_control_help_prompt() -> str:
    """
    Get help with volume control commands and usage examples.
    This prompt provides guidance on how to use the volume control tools.
    """
    return """
    # Volume Control Help
    
    ## Available Commands:
    1. **get_volume**: Check current volume level and mute status
    2. **set_volume**: Set volume to specific percentage (0-100)
    3. **mute**: Mute the system audio
    4. **unmute**: Unmute the system audio
    5. **toggle_mute**: Toggle between muted/unmuted
    6. **apply_preset**: Use predefined volume settings
    
    ## Volume Presets:
    - MUTED: 0% volume, muted
    - LOW: 25% volume, unmuted
    - MEDIUM: 50% volume, unmuted
    - HIGH: 75% volume, unmuted
    - MAX: 100% volume, unmuted
    
    ## Usage Examples:
    - "Set volume to 50"
    - "Apply preset MEDIUM"
    - "Toggle mute"
    """

@mcp.prompt("volume-settings")
def volume_settings_prompt() -> str:
    """
    Template for configuring volume settings with various options.
    Use this prompt to set up volume configurations.
    """
    return """
    # Volume Settings Configuration
    
    Please specify your volume preferences:
    
    1. **Target Volume Level**: Enter percentage (0-100)
    2. **Mute Preference**: 
       - true: Start muted
       - false: Start unmuted
    3. **Preset Selection**: Choose from MUTED, LOW, MEDIUM, HIGH, MAX
    
    ## Quick Commands:
    - For quiet environment: Use LOW or MEDIUM preset
    - For presentations: Use HIGH preset
    - For privacy: Use MUTED preset
    """

@mcp.prompt("volume-troubleshooting")
def volume_troubleshooting_prompt() -> str:
    """
    Troubleshooting guide for volume control issues.
    """
    return """
    # Volume Control Troubleshooting
    
    ## Common Issues:
    1. **Volume not changing**: Check if audio drivers are working
    2. **Mute not working**: Verify system audio permissions
    3. **Preset not applying**: Ensure preset name is uppercase
    
    ## System Requirements:
    - Windows operating system
    - Audio drivers installed
    - System audio permissions
    
    ## Diagnostic Steps:
    1. Run `get_volume` to check current status
    2. Try setting volume to 50% with `set_volume`
    3. Test mute/unmute functionality
    """

# Define MCP Resources
@mcp.resource("volume://current-state")
def current_volume_state() -> Dict[str, Any]:
    """
    Real-time volume state resource showing current audio settings.
    """
    try:
        volume_info = volume_controller.get_volume()
        return {
            "uri": "volume://current-state",
            "name": "Current Volume State",
            "description": "Real-time system volume and mute status",
            "mime_type": "application/json",
            "content": {
                "volume_percentage": volume_info.get("volume_percentage", 0),
                "volume_db": volume_info.get("volume_db", 0),
                "is_muted": volume_info.get("is_muted", False),
                "status": volume_info.get("status", "unknown"),
                "timestamp": "2025-01-25T12:00:00Z"
            }
        }
    except Exception as e:
        return {
            "uri": "volume://current-state",
            "name": "Current Volume State",
            "description": "Error getting volume state",
            "mime_type": "application/json",
            "content": {"error": str(e)}
        }

@mcp.resource("volume://presets")
def volume_presets_resource() -> Dict[str, Any]:
    """
    Available volume presets resource with all predefined settings.
    """
    presets = []
    for preset in VolumePreset:
        presets.append({
            "name": preset.name,
            "label": preset.label,
            "volume_percentage": preset.volume,
            "is_muted": preset.muted,
            "description": f"{preset.label} preset: {preset.volume}% volume, {'muted' if preset.muted else 'unmuted'}"
        })
    
    return {
        "uri": "volume://presets",
        "name": "Volume Presets",
        "description": "Predefined volume configurations for different scenarios",
        "mime_type": "application/json",
        "content": {
            "presets": presets,
            "total_presets": len(presets),
            "usage": "Use apply_preset tool with preset name"
        }
    }

@mcp.resource("volume://capabilities")
def volume_capabilities_resource() -> Dict[str, Any]:
    """
    System audio capabilities and supported operations.
    """
    return {
        "uri": "volume://capabilities",
        "name": "Volume Control Capabilities",
        "description": "System audio control capabilities and features",
        "mime_type": "application/json",
        "content": {
            "supported_operations": [
                "get_volume",
                "set_volume", 
                "mute",
                "unmute",
                "toggle_mute",
                "apply_preset"
            ],
            "volume_range": {
                "minimum": 0,
                "maximum": 100,
                "unit": "percentage"
            },
            "audio_features": {
                "supports_mute": True,
                "supports_volume_control": True,
                "supports_presets": True,
                "real_time_monitoring": True
            },
            "system_info": {
                "platform": "Windows",
                "audio_api": "Windows Core Audio API (WASAPI)",
                "library": "pycaw"
            }
        }
    }

class VolumeController:
    """Handles all volume control operations using pycaw library"""
    
    def __init__(self):
        self._volume = None
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Initialize the audio interface"""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            # Get the default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume = interface.QueryInterface(IAudioEndpointVolume)
            
            logger.info("Audio interface initialized successfully")
            
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize audio interface: {e}")
            raise
    
    def get_volume(self) -> dict:
        """Get current volume level and mute status"""
        try:
            if not self._volume:
                raise RuntimeError("Audio interface not initialized")
            
            # Get current volume information
            volume_scalar = self._volume.GetMasterVolumeLevelScalar()  # 0.0 to 1.0
            volume_db = self._volume.GetMasterVolumeLevel()           # Decibels
            is_muted = self._volume.GetMute()                         # Boolean
            
            # Convert to percentage
            volume_percentage = round(volume_scalar * 100, 1)
            
            return {
                "volume_percentage": volume_percentage,
                "volume_scalar": volume_scalar,
                "volume_db": round(volume_db, 2),
                "is_muted": bool(is_muted),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def set_volume(self, percentage: float) -> dict:
        """Set volume to specific percentage (0-100)"""
        try:
            if not self._volume:
                raise RuntimeError("Audio interface not initialized")
            
            # Validate input
            if not 0 <= percentage <= 100:
                raise ValueError("Volume percentage must be between 0 and 100")
            
            # Convert percentage to scalar (0.0 to 1.0)
            volume_scalar = percentage / 100.0
            
            # Set the volume
            self._volume.SetMasterVolumeLevelScalar(volume_scalar, None)
            
            # Get the actual set volume (might be slightly different due to hardware)
            actual_volume = self._volume.GetMasterVolumeLevelScalar()
            actual_percentage = round(actual_volume * 100, 1)
            
            logger.info(f"Volume set to {actual_percentage}%")
            
            return {
                "requested_percentage": percentage,
                "actual_percentage": actual_percentage,
                "volume_scalar": actual_volume,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def mute(self) -> dict:
        """Mute the system"""
        try:
            if not self._volume:
                raise RuntimeError("Audio interface not initialized")
            
            # Check current mute status
            was_muted = self._volume.GetMute()
            
            if was_muted:
                return {
                    "message": "System was already muted",
                    "was_muted": True,
                    "is_muted": True,
                    "status": "success"
                }
            
            # Mute the system
            self._volume.SetMute(1, None)
            
            logger.info("System muted")
            
            return {
                "message": "System muted successfully",
                "was_muted": False,
                "is_muted": True,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to mute: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def unmute(self) -> dict:
        """Unmute the system"""
        try:
            if not self._volume:
                raise RuntimeError("Audio interface not initialized")
            
            # Check current mute status
            was_muted = self._volume.GetMute()
            
            if not was_muted:
                return {
                    "message": "System was already unmuted",
                    "was_muted": False,
                    "is_muted": False,
                    "status": "success"
                }
            
            # Unmute the system
            self._volume.SetMute(0, None)
            
            logger.info("System unmuted")
            
            return {
                "message": "System unmuted successfully",
                "was_muted": True,
                "is_muted": False,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to unmute: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def toggle_mute(self) -> dict:
        """Toggle mute status"""
        try:
            if not self._volume:
                raise RuntimeError("Audio interface not initialized")
            
            # Get current mute status
            current_mute = self._volume.GetMute()
            
            # Toggle mute
            new_mute = not current_mute
            self._volume.SetMute(1 if new_mute else 0, None)
            
            action = "muted" if new_mute else "unmuted"
            logger.info(f"System {action} (toggled)")
            
            return {
                "message": f"System {action} successfully",
                "was_muted": bool(current_mute),
                "is_muted": bool(new_mute),
                "action": action,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to toggle mute: {e}")
            return {
                "error": str(e),
                "status": "error"
            }


# Initialize the volume controller
volume_controller = VolumeController()

@mcp.tool(description="Get current system volume and mute status")
def get_volume() -> str:
    """
    Get the current system volume level and mute status.
    Returns volume percentage, mute status, and decibel level.
    """
    result = volume_controller.get_volume()
    
    if result["status"] == "success":
        return f"🔊 Volume: {result['volume_percentage']}% | Muted: {'Yes' if result['is_muted'] else 'No'} | dB: {result['volume_db']}"
    else:
        return f"❌ Error: {result['error']}"

@mcp.tool(description="Set system volume to a specific percentage")
def set_volume(percentage: float) -> str:
    """
    Set the system volume to a specific percentage.
    
    Args:
        percentage: Volume percentage (0-100)
    """
    result = volume_controller.set_volume(percentage)
    
    if result["status"] == "success":
        return f"🔊 Volume set to {result['actual_percentage']}% (requested: {result['requested_percentage']}%)"
    else:
        return f"❌ Error: {result['error']}"

@mcp.tool(description="Mute the system audio")
def mute() -> str:
    """
    Mute the system audio.
    """
    result = volume_controller.mute()
    
    if result["status"] == "success":
        return f"� {result['message']}"
    else:
        return f"❌ Error: {result['error']}"

@mcp.tool(description="Unmute the system audio")
def unmute() -> str:
    """
    Unmute the system audio.
    """
    result = volume_controller.unmute()
    
    if result["status"] == "success":
        return f"🔇 {result['message']}"
    else:
        return f"❌ Error: {result['error']}"

@mcp.tool(description="Toggle between muted and unmuted states")
def toggle_mute() -> str:
    """
    Toggle the system mute status (mute if unmuted, unmute if muted).
    """
    result = volume_controller.toggle_mute()
    
    if result["status"] == "success":
        return f"🔇 {result['message']}"
    else:
        return f"❌ Error: {result['error']}"

@mcp.tool(description="Apply a predefined volume preset")
def apply_preset(preset_name: str) -> str:
    """
    Apply a predefined volume preset.
    
    Args:
        preset_name: Name of the preset to apply (MUTED, LOW, MEDIUM, HIGH, MAX)
    """
    try:
        preset = VolumePreset[preset_name.upper()]
        volume_result = volume_controller.set_volume(preset.volume)
        
        if preset.muted:
            mute_result = volume_controller.mute()
        else:
            mute_result = volume_controller.unmute()
            
        if volume_result["status"] == "success" and mute_result["status"] == "success":
            return f"🎚️ Applied {preset.label} preset: Volume {preset.volume}%, {'Muted' if preset.muted else 'Unmuted'}"
        return f"❌ Error applying preset"
    except KeyError:
        return f"❌ Invalid preset: {preset_name}"

def main():
    """Main entry point for the console script"""
    import logging
    import signal
    import sys
    
    # Set up logging to show server activity
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    def signal_handler(sig, frame):
        print("\n🛑 Server shutdown requested", file=sys.stderr)
        sys.exit(0)
    
    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Volume Control MCP Server", file=sys.stderr)
    print("📚 Features: 6 tools, 3 resources, 3 prompts", file=sys.stderr)
    print("⏹️  Press Ctrl+C to stop", file=sys.stderr)
    
    try:
        # Run in stdio mode for MCP clients (default)
        mcp.run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()