# 1. Base Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# 2. Install system dependencies
# Includes dependencies for ffmpeg, wget, and headless Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \\\
    ffmpeg \\\
    wget \\\
    ca-certificates \\\
    fonts-liberation \\\
    libappindicator3-1 \\\
    libasound2 \\\
    libatk-bridge2.0-0 \\\
    libatk1.0-0 \\\
    libc6 \\\
    libcairo2 \\\
    libcups2 \\\
    libdbus-1-3 \\\
    libexpat1 \\\
    libfontconfig1 \\\
    libgbm1 \\\
    libgcc1 \\\
    libglib2.0-0 \\\
    libgtk-3-0 \\\
    libnspr4 \\\
    libnss3 \\\
    libpango-1.0-0 \\\
    libpangocairo-1.0-0 \\\
    libstdc++6 \\\
    libx11-6 \\\
    libx11-xcb1 \\\
    libxcb1 \\\
    libxcomposite1 \\\
    libxcursor1 \\\
    libxdamage1 \\\
    libxext6 \\\
    libxfixes3 \\\
    libxi6 \\\
    libxrandr2 \\\
    libxrender1 \\\
    libxss1 \\\
    libxtst6 \\\
    lsb-release \\\
    xdg-utils \\\
    # Clean up apt lists to reduce image size
    && rm -rf /var/lib/apt/lists/*

# 3. Download and install Google Chrome
RUN wget --no-verbose -O google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \\\
    && apt-get update \\\
    # DEBIAN_FRONTEND=noninteractive helps avoid prompts
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb \\\
    && apt-get install -f -y \\\
    && rm google-chrome-stable_current_amd64.deb \\\
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . /app/

# 6. Expose port
EXPOSE 8000

# 7. Run the application
# Note: If your main.py is inside a subdirectory (e.g., backend/main.py from the project root),
# and you copy the entire backend directory content into /app, the command might need adjustment
# based on how you structure the COPY. Assuming main.py is at /app/main.py
# Also ensure TEMP_AUDIO_DIR and voice_store.json paths in your Python code are compatible with this structure or use absolute paths/env vars.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 