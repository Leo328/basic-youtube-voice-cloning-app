#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting build process for Render..."

# 1. Update package lists and install essential packages
echo "Updating package lists and installing essential tools (python3, pip, wget, ffmpeg, Chrome dependencies)..."
sudo apt-get update -y
# Install essential tools and Chrome dependencies
# Added common dependencies for headless Chrome to run reliably.
sudo apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    wget \
    ffmpeg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils

# 2. Download Google Chrome
echo "Downloading Google Chrome..."
wget --no-verbose -O google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 3. Install Google Chrome
echo "Installing Google Chrome..."
# The DEBIAN_FRONTEND=noninteractive helps avoid prompts during installation.
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ./google-chrome-stable_current_amd64.deb
# Attempt to fix any broken dependencies that Chrome's installation might cause.
echo "Fixing any potential broken dependencies after Chrome install..."
sudo apt-get install -f -y

# 4. Upgrade pip and install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
# Use sudo for pip3 if installing system-wide, but it's better to ensure pip3 installs to user or virtual env.
# However, in build scripts like this for Render, pip3 might be installing to a globally accessible Python site-packages.
# Let's try without sudo for pip first, as it's generally safer unless permissions require it.
pip3 install --no-cache-dir --upgrade pip
# Assumes requirements.txt is in the same directory as this script (e.g., ./backend/requirements.txt)
if [ -f "requirements.txt" ]; then
    pip3 install --no-cache-dir -r requirements.txt
else
    echo "Warning: requirements.txt not found. Skipping Python dependency installation."
fi

# 5. Clean up downloaded files
echo "Cleaning up downloaded Chrome package..."
rm google-chrome-stable_current_amd64.deb

echo "Build script completed successfully."
echo "Ensure your Render service start command is set correctly (e.g., uvicorn backend.main:app --host 0.0.0.0 --port $PORT)"

# The line below was removed as it makes the script non-executable after running it.
# chmod +x build.sh 