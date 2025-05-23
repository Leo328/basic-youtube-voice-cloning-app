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

This application is designed to be deployed with the backend on a service like Render (as a Web Service) and the frontend on a static hosting service like Render (as a Static Site), Netlify, or Vercel.

### Backend (Render Web Service)

1.  Create a new **Web Service** on Render.
2.  Connect your Git repository.
3.  Set the **Build Command** to (or ensure your `build.sh` does this):\
    `pip install -r requirements.txt`
4.  Set the **Start Command** to:\
    `python main.py` (or `uvicorn main:app --host 0.0.0.0 --port $PORT` if Render doesn't default to Uvicorn correctly for FastAPI).
5.  Add the following **Environment Variables** in the Render dashboard for your backend service:
    *   `ELEVENLABS_API_KEY`: Your ElevenLabs API key.
    *   `USE_STEALTH_MODE`: `true` or `false` (defaults to `true`).
    *   `PYTHON_VERSION`: Specify a Python version (e.g., `3.10.4`).
    *   `FRONTEND_URL`: The full URL of your deployed frontend (e.g., `https://frontend-basic-youtube-voice-cloning-app.onrender.com`). This is used for CORS.
6.  **Ensure your `backend/build.sh` script installs Chrome and ChromeDriver if `USE_STEALTH_MODE` is true.** Render's native environment might not have these. You may need to adapt the DigitalOcean instructions below or use a Dockerfile.
7.  Deploy.

### Frontend (Render Static Site / Netlify / Vercel)

1.  Create a new **Static Site** on Render (or a new site on Netlify/Vercel).
2.  Connect your Git repository.
3.  Set the **Build Command** to: `npm run build` (or `vite build`).
4.  Set the **Publish Directory** to: `dist` (or `frontend/dist` if your build output is nested).
5.  Add the following **Environment Variable** in the deployment settings:
    *   `VITE_API_BASE_URL`: The full URL of your deployed backend service (e.g., `https://basic-youtube-voice-cloning-app.onrender.com`).
6.  Deploy!

### Example: Backend on DigitalOcean Droplet (Alternative to Render Web Service)

If you prefer a traditional VM:

1.  Create a new Ubuntu droplet.
2.  SSH into your droplet and install dependencies:
    ```bash
   # Update system
   sudo apt-get update
   sudo apt-get upgrade -y

   # Install Python and pip
   sudo apt-get install python3-pip -y

   # Install Chrome and ChromeDriver (Essential for USE_STEALTH_MODE=true)
   # (Ensure these commands are up-to-date and compatible with your OS)
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo apt install ./google-chrome-stable_current_amd64.deb -y
   sudo apt-get install -y unzip # If not already installed
   CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1,2,3))
   wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
   unzip chromedriver_linux64.zip
   sudo mv chromedriver /usr/local/bin/chromedriver
   sudo chown root:root /usr/local/bin/chromedriver
   sudo chmod +x /usr/local/bin/chromedriver
   rm google-chrome-stable_current_amd64.deb chromedriver_linux64.zip
   # Clone the repository
   git clone <your-repo-url>
   cd voice_cloning_app/backend
   pip3 install -r requirements.txt
   ```

3.  Create `.env` file in the `backend` directory with your configuration:
    ```bash
    ELEVENLABS_API_KEY=your_api_key
    USE_STEALTH_MODE=true
    FRONTEND_URL=https://your-frontend-domain # e.g., https://frontend-app.onrender.com
    ```

4.  Run the server (using screen or pm2):
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
   VITE_API_BASE_URL=https://your-droplet-ip-or-domain-for-backend # e.g., https://backend-app.onrender.com or http://your_droplet_ip:8000
   ```
3. Deploy!

## Notes

- For demo purposes, this app uses a simple deployment setup
- The backend requires Chrome/ChromeDriver for YouTube audio extraction
- Make sure to set CORS origins in `backend/main.py` and the `FRONTEND_URL` environment variable for the backend to match your frontend domain.
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