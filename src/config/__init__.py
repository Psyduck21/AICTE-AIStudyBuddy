"""Configuration package initialization"""
from typing import Dict, Any

def get_config_dict() -> Dict[str, Any]:
    """Get configuration dictionary from the config module"""
    from . import config
    
    # Get all uppercase variables from config module
    return {
        name: getattr(config, name)
        for name in dir(config)
        if name.isupper()
    }