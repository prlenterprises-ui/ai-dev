"""
Config Loader - Load configuration from database with config.json fallback.

This module provides utilities to load configuration from the database (primary)
with automatic fallback to config.json if database is unavailable.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from sqlmodel import select

from python.database import Config, get_session, init_db


async def load_config_from_db(config_name: str) -> Optional[Dict]:
    """
    Load configuration from database.
    
    Args:
        config_name: Name of the config to load (e.g., "auto-apply", "matching_service")
        
    Returns:
        Configuration dictionary or None if not found
    """
    try:
        await init_db()
        async for session in get_session():
            result = await session.execute(
                select(Config).where(Config.name == config_name)
            )
            config_obj = result.scalar_one_or_none()
            
            if config_obj:
                return json.loads(config_obj.config_json)
            return None
    except Exception as e:
        print(f"⚠️  Database config load failed: {e}")
        return None


def load_config_from_json(config_path: Optional[Path] = None) -> Dict:
    """
    Load configuration from config.json file.
    
    Args:
        config_path: Optional path to config.json. Defaults to apps/config.json
        
    Returns:
        Configuration dictionary (empty dict if file not found)
    """
    if config_path is None:
        # Try multiple possible locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "apps" / "config.json",
            Path(__file__).parent.parent / "config.json",
            Path.cwd() / "config.json"
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
    
    if config_path and config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    return {}


async def get_config(config_name: str, fallback_to_json: bool = True) -> Dict:
    """
    Load configuration from database with optional fallback to config.json.
    
    This is the main entry point for loading configuration. It will:
    1. Try to load from database first
    2. Optionally fallback to config.json if database fails
    3. Return empty dict if both fail
    
    Args:
        config_name: Name of config to load (e.g., "auto-apply")
        fallback_to_json: Whether to fallback to config.json if DB fails
        
    Returns:
        Configuration dictionary
        
    Example:
        >>> config = await get_config("auto-apply")
        >>> jsearch_settings = config.get("jsearch", {})
    """
    # Try database first
    config = await load_config_from_db(config_name)
    
    if config:
        print(f"✅ Loaded '{config_name}' from database")
        return config
    
    # Fallback to config.json if enabled
    if fallback_to_json:
        file_config = load_config_from_json()
        
        # Map config names to keys in config.json
        key_mapping = {
            "auto-apply": None,  # Return entire config for auto-apply
            "matching_service": "score_matching",
            "jsearch": "jsearch"
        }
        
        config_key = key_mapping.get(config_name)
        
        if config_key:
            config = {config_key: file_config.get(config_key, {})}
        elif config_name == "auto-apply":
            # Auto-apply gets both jsearch and score_matching
            config = {
                "jsearch": file_config.get("jsearch", {}),
                "score_matching": file_config.get("score_matching", {})
            }
        else:
            config = file_config.get(config_name, {})
        
        if config:
            print(f"⚠️  Loaded '{config_name}' from config.json (fallback)")
            return config
    
    print(f"❌ No config found for '{config_name}'")
    return {}


async def update_config_in_db(config_name: str, config_data: Dict, title: str = "", description: str = "") -> bool:
    """
    Update or create configuration in database.
    
    Args:
        config_name: Name of the config
        config_data: Configuration dictionary to store
        title: Display title for the config
        description: Optional description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        await init_db()
        async for session in get_session():
            result = await session.execute(
                select(Config).where(Config.name == config_name)
            )
            config_obj = result.scalar_one_or_none()
            
            if config_obj:
                # Update existing
                config_obj.config_json = json.dumps(config_data)
                if title:
                    config_obj.title = title
                if description:
                    config_obj.description = description
                print(f"✅ Updated '{config_name}' in database")
            else:
                # Create new
                config_obj = Config(
                    name=config_name,
                    title=title or config_name,
                    description=description,
                    config_json=json.dumps(config_data)
                )
                session.add(config_obj)
                print(f"✅ Created '{config_name}' in database")
            
            await session.commit()
            return True
            
    except Exception as e:
        print(f"❌ Failed to update config in database: {e}")
        return False
