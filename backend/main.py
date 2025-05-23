"""
Main FastAPI application for the voice cloning service.
Handles API endpoints and coordinates between YouTube download and ElevenLabs API.
"""

import os
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use absolute imports
from youtube import extract_audio_from_youtube, cleanup_audio_file
from youtube_stealth import extract_audio_stealth
from voice_store import add_voice, get_voice_id, list_voices, remove_voice

# Configuration
USE_STEALTH_MODE = os.getenv("USE_STEALTH_MODE", "true").lower() == "true"  # Default to true

# Load environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Ensure TEMP_AUDIO_DIR is an absolute path and exists
TEMP_AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_audio"))
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
print(f"Temporary audio directory configured at: {TEMP_AUDIO_DIR}")

app = FastAPI(title="Voice Cloning App")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YouTubeURL(BaseModel):
    url: str

class VoiceName(BaseModel):
    name: str

class SpeakRequest(BaseModel):
    voice_name: str
    text: str

class SaveVoiceRequest(BaseModel):
    name: str

class AudioExtractionResponse(BaseModel):
    status: str
    message: str
    file_path: Optional[str] = None
    progress_updates: list[str] = []  # List of progress messages

class CloneVoiceRequest(BaseModel):
    audio_file: str

async def rename_voice_in_elevenlabs(voice_id: str, name: str) -> bool:
    """
    Rename a voice in ElevenLabs.
    Returns True if successful, False otherwise.
    """
    try:
        response = requests.patch(
            f"{ELEVENLABS_API_URL}/voices/{voice_id}",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            json={
                "name": name,
                "labels": {"accent": "neutral"}
            }
        )
        if response.status_code != 200:
            print(f"Error renaming voice: Status {response.status_code}, Response: {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Error renaming voice in ElevenLabs: {str(e)}")
        return False

@app.post("/extract-audio")
async def extract_audio(youtube_url: YouTubeURL) -> AudioExtractionResponse:
    """
    Extract audio from a YouTube video.
    """
    progress_updates = []
    
    try:
        # Extract audio from YouTube using the configured method
        if USE_STEALTH_MODE:
            progress_updates.append("Initializing stealth browser...")
            audio_file = extract_audio_stealth(youtube_url.url, TEMP_AUDIO_DIR, progress_callback=progress_updates.append)
        else:
            progress_updates.append("Using standard download mode...")
            audio_file = extract_audio_from_youtube(youtube_url.url, TEMP_AUDIO_DIR, progress_callback=progress_updates.append)
            
        if not audio_file:
            raise HTTPException(status_code=400, detail="Failed to extract audio from YouTube")
            
        progress_updates.append("Audio extraction completed successfully!")
        return AudioExtractionResponse(
            status="success",
            message="Audio extracted successfully",
            file_path=audio_file,
            progress_updates=progress_updates
        )
        
    except Exception as e:
        error_msg = f"Error extracting audio: {str(e)}"
        progress_updates.append(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/clone-voice")
async def clone_voice(request: CloneVoiceRequest) -> Dict[str, str]:
    """
    Create voice clone using ElevenLabs from an already downloaded audio file.
    """
    try:
        audio_file = request.audio_file
        print(f"Attempting to access audio file at: {audio_file}")
        
        # Handle both absolute and relative paths
        if not os.path.isabs(audio_file):
            audio_file = os.path.join(os.path.dirname(__file__), audio_file)
        
        if not os.path.exists(audio_file):
            raise HTTPException(
                status_code=400, 
                detail=f"Audio file not found at path: {audio_file}"
            )

        print(f"Found audio file at: {audio_file}")
        
        try:
            # Upload audio to ElevenLabs
            with open(audio_file, 'rb') as f:
                # Create form data
                files = {
                    "files": ("audio.mp3", f, "audio/mpeg")
                }
                form_data = {
                    "name": "Voice Clone",
                    "description": "Voice cloned from YouTube audio",
                    "labels": '{"accent": "neutral"}'
                }
                
                # Make the request
                response = requests.post(
                    f"{ELEVENLABS_API_URL}/voices/add",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    files=files,
                    data=form_data
                )
                
                # Print response for debugging
                print(f"ElevenLabs API Response Status: {response.status_code}")
                print(f"ElevenLabs API Response: {response.text}")
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"ElevenLabs API error: {response.text}"
                    )
                
                voice_id = response.json()["voice_id"]
                return {"voice_id": voice_id}
                
        finally:
            # Clean up the audio file after we're done with it
            print(f"Cleaning up audio file: {audio_file}")
            cleanup_audio_file(audio_file)
            
    except Exception as e:
        print(f"Error in clone_voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cloning voice: {str(e)}")

@app.post("/save-voice")
async def save_voice(voice_id: str, request: SaveVoiceRequest) -> Dict[str, str]:
    """
    Save a voice with a given name and rename it in ElevenLabs.
    """
    # First rename the voice in ElevenLabs
    renamed = await rename_voice_in_elevenlabs(voice_id, request.name)
    if not renamed:
        print(f"Warning: Failed to rename voice {voice_id} in ElevenLabs")
    
    # Save the voice locally
    add_voice(request.name, voice_id)
    return {"status": "success"}

@app.get("/voices")
async def get_voices() -> Dict[str, str]:
    """
    Get all stored voices.
    """
    return list_voices()

@app.post("/speak")
async def text_to_speech(request: SpeakRequest) -> Response:
    """
    Generate speech using a saved voice.
    
    Args:
        request: SpeakRequest containing voice_name and text to speak
    """
    voice_id = get_voice_id(request.voice_name)
    if not voice_id:
        raise HTTPException(status_code=404, detail=f"Voice '{request.voice_name}' not found")
        
    response = requests.post(
        f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": request.text,
            "model_id": "eleven_monolingual_v1"
        }
    )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"ElevenLabs API error: {response.text}"
        )
        
    # Return the audio data with proper content type
    return Response(
        content=response.content,
        media_type="audio/mpeg"
    )

@app.delete("/voices/{voice_name}")
async def delete_voice(voice_name: str) -> Dict[str, str]:
    """
    Delete a voice from ElevenLabs and local store.
    
    Args:
        voice_name: Name of the voice to delete
    """
    try:
        # Get voice ID from local store
        voice_id = get_voice_id(voice_name)
        if not voice_id:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")
            
        # Delete from ElevenLabs
        response = requests.delete(
            f"{ELEVENLABS_API_URL}/voices/{voice_id}",
            headers={"xi-api-key": ELEVENLABS_API_KEY}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ElevenLabs API error: {response.text}"
            )
            
        # Delete from local store
        if not remove_voice(voice_name):
            raise HTTPException(status_code=500, detail="Failed to remove voice from local store")
            
        return {"status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting voice: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 