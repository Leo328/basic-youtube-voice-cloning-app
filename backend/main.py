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

# Use relative imports
from .youtube import extract_audio_from_youtube, cleanup_audio_file
from .voice_store import add_voice, get_voice_id, list_voices, remove_voice

# Load environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"
TEMP_AUDIO_DIR = "temp_audio"

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
async def extract_audio(youtube_url: YouTubeURL, background_tasks: BackgroundTasks) -> AudioExtractionResponse:
    """
    Extract audio from a YouTube video.
    The audio file will be automatically cleaned up after processing.
    """
    try:
        # Extract audio from YouTube
        audio_file = extract_audio_from_youtube(youtube_url.url, TEMP_AUDIO_DIR)
        if not audio_file:
            raise HTTPException(status_code=400, detail="Failed to extract audio from YouTube")
            
        # Schedule cleanup for later
        background_tasks.add_task(cleanup_audio_file, audio_file)
        
        return AudioExtractionResponse(
            status="success",
            message="Audio extracted successfully",
            file_path=audio_file
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting audio: {str(e)}")

@app.post("/clone-voice")
async def clone_voice(youtube_url: YouTubeURL) -> Dict[str, str]:
    """
    Extract audio from YouTube video and create voice clone using ElevenLabs.
    """
    # Extract audio using our new endpoint
    audio_response = await extract_audio(youtube_url, BackgroundTasks())
    if not audio_response.file_path:
        raise HTTPException(status_code=400, detail="Failed to download audio")

    try:
        # Upload audio to ElevenLabs
        with open(audio_response.file_path, 'rb') as f:
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
            
    except Exception as e:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 