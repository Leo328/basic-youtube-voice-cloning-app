"""
Module for managing voice IDs and their associated names.
Uses a simple in-memory dictionary for development.
"""

from typing import Dict, Optional

# Hardcoded voice mappings
VOICE_STORE = {
    "Morgan Freeman": "2EiwWnXFnvU5JabPnv8n",
    "David Attenborough": "pNInz6obpgDQGcFmaJgB",
    "Example Voice": "jsCqWAovK2LkecY7zXl4"
}

def load_voices() -> Dict[str, str]:
    """
    Load voice mappings from memory.
    
    Returns:
        Dictionary mapping voice names to their IDs
    """
    return VOICE_STORE

def add_voice(name: str, voice_id: str) -> None:
    """
    Add a new voice mapping.
    
    Args:
        name: Name of the voice
        voice_id: ElevenLabs voice ID
    """
    VOICE_STORE[name] = voice_id

def get_voice_id(name: str) -> Optional[str]:
    """
    Get voice ID by name.
    
    Args:
        name: Name of the voice
        
    Returns:
        Voice ID if found, None otherwise
    """
    return VOICE_STORE.get(name)

def list_voices() -> Dict[str, str]:
    """
    Get all stored voices.
    
    Returns:
        Dictionary of all voice names and their IDs
    """
    return VOICE_STORE

def remove_voice(name: str) -> bool:
    """
    Remove a voice mapping.
    
    Args:
        name: Name of the voice to remove
        
    Returns:
        True if voice was removed, False if not found
    """
    if name in VOICE_STORE:
        del VOICE_STORE[name]
        return True
    return False 