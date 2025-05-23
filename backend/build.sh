#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies first
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Chrome dependencies
echo "Updating package lists and installing Chrome dependencies..."
apt-get update && apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    wget \
    unzip

# Download and install Chrome
echo "Downloading and installing Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

echo "Installed Chrome version:"
google-chrome --version

# Download and install ChromeDriver
echo "Downloading and installing ChromeDriver..."
# Get the latest stable ChromeDriver version for the installed Chrome
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1)
echo "Detected Chrome major version: $CHROME_VERSION"

# Fallback to a known good version if detection fails or for older Chrome versions
# ChromeDriver versions can be found at https://googlechromelabs.github.io/chrome-for-testing/
# We will try to get the LATEST_RELEASE for the specific version first
# If you know the exact Chrome version Render installs, you can hardcode this.
LATEST_RELEASE_URL="https://storage.googleapis.com/chrome-for-testing-public"
# Attempt to find a matching major version
CHROME_DRIVER_VERSION=$(curl -s ${LATEST_RELEASE_URL}/LATEST_RELEASE_${CHROME_VERSION})

if [ -z "$CHROME_DRIVER_VERSION" ]; then
    echo "Could not automatically determine ChromeDriver version for Chrome $CHROME_VERSION. Falling back to a recent known good version."
    # Find a recent version from https://googlechromelabs.github.io/chrome-for-testing/
    # This might need updating if Chrome on Render is very old or very new.
    # Example: Manually find the closest one or use a generic latest if the API changes.
    # As a broader fallback, let's try to get the latest stable, though this can be risky.
    CHROME_DRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
fi

echo "Using ChromeDriver version: $CHROME_DRIVER_VERSION"
wget -N https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip -P ~/ || wget -N ${LATEST_RELEASE_URL}/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip -P ~/
if [ -f ~/chromedriver_linux64.zip ]; then
    unzip ~/chromedriver_linux64.zip -d ~/ && rm ~/chromedriver_linux64.zip
    mv -f ~/chromedriver /usr/local/bin/chromedriver
elif [ -f ~/chromedriver-linux64.zip ]; then # New naming scheme
    unzip ~/chromedriver-linux64.zip -d ~/ && rm ~/chromedriver-linux64.zip
    mv -f ~/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
    rm -rf ~/chromedriver-linux64 # Clean up the directory
else
    echo "Failed to download ChromeDriver. Please check the version and URL."
    exit 1
fi

chown root:root /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

echo "Installed ChromeDriver version:"
chromedriver --version

echo "Build script completed."

# The line below was removed as it makes the script non-executable after running it.
# chmod +x build.sh 