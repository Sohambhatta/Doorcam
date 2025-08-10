import json
from pathlib import Path
from typing import Dict, Any

class PetConfig:
    """Configuration management for pet detection system"""
    
    def __init__(self, config_file: str = "pet_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "detection_thresholds": {
                "confidence_threshold": 0.7,
                "overlap_threshold": 0.3
            },
            "distance_thresholds": {
                "front_facing": {
                    "close": 250000,
                    "medium": 150000,
                    "far": 50000
                },
                "side_profile": {
                    "close": 180000,
                    "medium": 100000,
                    "far": 40000
                },
                "back_facing": {
                    "close": 200000,
                    "medium": 120000,
                    "far": 45000
                },
                "upside_down_front": {
                    "close": 220000,
                    "medium": 130000,
                    "far": 48000
                },
                "upside_down_side": {
                    "close": 160000,
                    "medium": 95000,
                    "far": 38000
                }
            },
            "camera_settings": {
                "device": "/dev/video0",
                "resolution": {
                    "width": 1920,
                    "height": 1080
                },
                "fps": 30
            },
            "gui_settings": {
                "theme": "modern_dark",
                "window_size": {
                    "width": 1200,
                    "height": 800
                }
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self.merge_configs(default_config, config)
            except (json.JSONDecodeError, IOError):
                pass
        
        return default_config
    
    def merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Recursively merge custom config with defaults"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'camera_settings.fps')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_distance_threshold(self, pose: str, distance_type: str) -> int:
        """Get distance threshold for specific pose and distance type"""
        thresholds = self.get(f"distance_thresholds.{pose}")
        if thresholds and distance_type in thresholds:
            return thresholds[distance_type]
        
        # Fallback to front_facing if pose not found
        front_thresholds = self.get("distance_thresholds.front_facing")
        return front_thresholds.get(distance_type, 150000)
    
    def update_distance_threshold(self, pose: str, distance_type: str, value: int):
        """Update distance threshold for specific pose and distance type"""
        self.set(f"distance_thresholds.{pose}.{distance_type}", value)
