# YouTube Voice Cloning App

A web application that allows you to clone voices from YouTube videos using ElevenLabs API.

## Local Development

1. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   # Backend (.env)
   ELEVENLABS_API_KEY=your_api_key
   USE_STEALTH_MODE=true

   # Frontend (.env)
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. Run the development servers:
   ```bash
   # Backend
   cd backend
   python main.py

   # Frontend
   cd frontend
   npm run dev
   ```

## Cloud Deployment

### Backend (DigitalOcean Droplet)

1. Create a new Ubuntu droplet
2. SSH into your droplet and install dependencies:
   ```bash
   # Update system
   sudo apt-get update
   sudo apt-get upgrade -y

   # Install Python and pip
   sudo apt-get install python3-pip -y

   # Install Chrome and ChromeDriver
   sudo apt-get install chromium-browser chromium-chromedriver -y

   # Clone the repository
   git clone <your-repo-url>
   cd voice_cloning_app/backend
   pip3 install -r requirements.txt
   ```

3. Create .env file with your configuration:
   ```bash
   ELEVENLABS_API_KEY=your_api_key
   USE_STEALTH_MODE=true
   ```

4. Run the server (using screen or pm2):
   ```bash
   # Using screen
   screen -S voice-app
   python3 main.py
   # Ctrl+A+D to detach
   ```

### Frontend (Netlify/Vercel)

1. Create a new site from your Git repository
2. Add environment variable in the deployment settings:
   ```
   VITE_API_BASE_URL=https://your-droplet-ip-or-domain
   ```
3. Deploy!

## Notes

- For demo purposes, this app uses a simple deployment setup
- The backend requires Chrome/ChromeDriver for YouTube audio extraction
- Make sure to set CORS origins in backend/main.py to match your frontend domain
- The app uses local file storage and JSON for simplicity

## Features
- Extract audio from YouTube videos
- Clone voices using ElevenLabs API
- Simple voice management interface
- Text-to-speech preview using cloned voices

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