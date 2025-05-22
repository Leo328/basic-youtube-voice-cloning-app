"""
Module for managing voice IDs and their associated names.
Uses a JSON file for simple persistent storage.
"""

import json
import os
from typing import Dict, Optional

VOICE_STORE_FILE = "voice_store.json"

def load_voices() -> Dict[str, str]:
    """
    Load voice mappings from JSON file.
    
    Returns:
        Dictionary mapping voice names to their IDs
    """
    try:
        if os.path.exists(VOICE_STORE_FILE):
            with open(VOICE_STORE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading voice store: {str(e)}")
    return {}

def save_voices(voices: Dict[str, str]) -> None:
    """
    Save voice mappings to JSON file.
    
    Args:
        voices: Dictionary mapping voice names to their IDs
    """
    try:
        with open(VOICE_STORE_FILE, 'w') as f:
            json.dump(voices, f, indent=2)
    except Exception as e:
        print(f"Error saving voice store: {str(e)}")

def add_voice(name: str, voice_id: str) -> None:
    """
    Add a new voice mapping.
    
    Args:
        name: Name of the voice
        voice_id: ElevenLabs voice ID
    """
    voices = load_voices()
    voices[name] = voice_id
    save_voices(voices)

def get_voice_id(name: str) -> Optional[str]:
    """
    Get voice ID by name.
    
    Args:
        name: Name of the voice
        
    Returns:
        Voice ID if found, None otherwise
    """
    voices = load_voices()
    return voices.get(name)

def list_voices() -> Dict[str, str]:
    """
    Get all stored voices.
    
    Returns:
        Dictionary of all voice names and their IDs
    """
    return load_voices()

def remove_voice(name: str) -> bool:
    """
    Remove a voice mapping.
    
    Args:
        name: Name of the voice to remove
        
    Returns:
        True if voice was removed, False if not found
    """
    voices = load_voices()
    if name in voices:
        del voices[name]
        save_voices(voices)
        return True
    return False 