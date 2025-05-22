# Voice Cloning App

A web application that clones voices from YouTube videos using ElevenLabs API.

## Features
- Extract audio from YouTube videos
- Clone voices using ElevenLabs API
- Simple voice management interface
- Text-to-speech preview using cloned voices

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your ElevenLabs API key:
```
ELEVENLABS_API_KEY=your_api_key_here
```

3. Start the backend server:
```bash
uvicorn main:app --reload
```

4. In a new terminal, start the Svelte frontend:
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
voice_cloning_app/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── voice_store.py    # Voice ID storage
│   └── youtube.py        # YouTube audio extraction
├── frontend/
│   └── src/              # Svelte frontend code
├── .env                  # Environment variables
└── requirements.txt      # Python dependencies
``` 