"""
Module for managing voice IDs and their associated names.
Uses a simple in-memory dictionary for development.
"""

import json
import os
from typing import Dict, Optional

# Path to the JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_STORE_FILE = os.path.join(BASE_DIR, "voice_store.json")

# In-memory cache for voices
VOICE_STORE: Dict[str, str] = {}

def load_voices() -> Dict[str, str]:
    """
    Load voice mappings from the JSON file.
    Populates the in-memory VOICE_STORE.
    
    Returns:
        Dictionary mapping voice names to their IDs
    """
    global VOICE_STORE
    try:
        if os.path.exists(VOICE_STORE_FILE):
            with open(VOICE_STORE_FILE, 'r') as f:
                content = f.read()
                if not content: # Handle empty file
                    VOICE_STORE = {}
                    return VOICE_STORE
                VOICE_STORE = json.loads(content)
        else:
            # If file doesn't exist, start with an empty store and create the file
            VOICE_STORE = {}
            save_voices_to_file() 
            print(f"Info: {VOICE_STORE_FILE} not found. Initializing with an empty voice store.")
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load voices from {VOICE_STORE_FILE}. Error: {e}. Starting with an empty voice store.")
        VOICE_STORE = {} # Reset to empty on error
    return VOICE_STORE

def save_voices_to_file() -> None:
    """
    Save the current in-memory VOICE_STORE to the JSON file.
    """
    try:
        with open(VOICE_STORE_FILE, 'w') as f:
            json.dump(VOICE_STORE, f, indent=4)
    except IOError as e:
        print(f"Error: Could not save voices to {VOICE_STORE_FILE}. Error: {e}")

def add_voice(name: str, voice_id: str) -> None:
    """
    Add a new voice mapping and save to file.
    
    Args:
        name: Name of the voice
        voice_id: ElevenLabs voice ID
    """
    VOICE_STORE[name] = voice_id
    save_voices_to_file()

def get_voice_id(name: str) -> Optional[str]:
    """
    Get voice ID by name from the in-memory store.
    
    Args:
        name: Name of the voice
        
    Returns:
        Voice ID if found, None otherwise
    """
    return VOICE_STORE.get(name)

def list_voices() -> Dict[str, str]:
    """
    Get all stored voices from the in-memory store.
    
    Returns:
        Dictionary of all voice names and their IDs
    """
    return VOICE_STORE

def remove_voice(name: str) -> bool:
    """
    Remove a voice mapping and save to file.
    
    Args:
        name: Name of the voice to remove
        
    Returns:
        True if voice was removed, False if not found
    """
    if name in VOICE_STORE:
        del VOICE_STORE[name]
        save_voices_to_file()
        return True
    return False

# Initial load of voices when the module is imported
load_voices()
print(f"Voice store initialized. Loaded voices: {list(VOICE_STORE.keys())}") 