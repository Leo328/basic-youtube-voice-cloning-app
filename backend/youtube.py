"""
Module for handling YouTube video audio extraction using cnvmp3.com via browser automation.
"""

import os
import re
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID if found, None otherwise
    """
    patterns = [
        r'(?:v=|/v/|/embed/|youtu\.be/)([^&?/]+)',  # Standard and embed URLs
        r'(?:youtube\.com/shorts/)([^&?/]+)',        # YouTube Shorts
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def setup_chrome_driver(download_path: str) -> webdriver.Chrome:
    """
    Set up Chrome WebDriver with appropriate options.
    
    Args:
        download_path: Path where downloaded files should be saved
        
    Returns:
        Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    
    # Enable headless mode for cloud deployment
    chrome_options.add_argument('--headless=new')
    
    # Mimic regular Chrome browser
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    
    # Disable automation flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Required for cloud/container environments
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Additional stealth settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Set up download behavior
    chrome_options.add_experimental_option(
        'prefs',
        {
            'download.default_directory': download_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True,
            # Additional prefs to make the browser appear more real
            'profile.default_content_settings.popups': 0,
            'profile.password_manager_enabled': False,
            'credentials_enable_service': False
        }
    )
    
    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute CDP commands to make the browser appear more real
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    return driver

def extract_audio_from_youtube(url: str, output_path: str) -> Optional[str]:
    """
    Extract audio from YouTube video using cnvmp3.com via browser automation.
    
    Args:
        url: YouTube video URL
        output_path: Directory where the audio file will be saved
        
    Returns:
        Path to the downloaded audio file or None if extraction fails
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Extract video ID for filename tracking
        video_id = get_video_id(url)
        if not video_id:
            print("Invalid YouTube URL")
            return None
        
        # Set up Chrome WebDriver
        driver = setup_chrome_driver(os.path.abspath(output_path))
        
        try:
            # Navigate to the converter website
            print("Accessing converter website...")
            driver.get("https://cnvmp3.com/")
            
            # Wait for and find the URL input field
            url_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "input-field-url"))
            )
            
            # Enter the YouTube URL
            url_input.clear()
            url_input.send_keys(url)
            
            # Find and click the convert button
            convert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "convert-button-1"))
            )
            convert_button.click()
            
            # Wait for download to complete (monitor the download directory)
            print("Waiting for download to complete...")
            max_wait = 60  # Maximum wait time in seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Check for downloaded files
                files = os.listdir(output_path)
                mp3_files = [f for f in files if f.endswith('.mp3')]
                
                if mp3_files:
                    # Get the most recently downloaded file
                    latest_file = max([os.path.join(output_path, f) for f in mp3_files], 
                                    key=os.path.getctime)
                    print(f"Download completed: {latest_file}")
                    return latest_file
                
                time.sleep(1)
            
            print("Timeout waiting for download")
            return None
            
        finally:
            # Clean up
            driver.quit()
            
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        return None

def cleanup_audio_file(file_path: str) -> None:
    """
    Remove downloaded audio file to free up space.
    
    Args:
        file_path: Path to the audio file to be removed
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}") 