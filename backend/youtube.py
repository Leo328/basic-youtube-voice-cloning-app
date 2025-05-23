"""
Module for handling YouTube video audio extraction using cnvmp3.com via browser automation.
"""

import os
import re
import time
import random
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
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

def get_random_viewport_size():
    """
    Return a random, realistic viewport size.
    Most common resolutions from real browsers.
    """
    viewports = [
        (1920, 1080),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1280, 720),
    ]
    return random.choice(viewports)

def get_random_user_agent():
    """
    Return a random, recent Chrome user agent.
    """
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ]
    return random.choice(agents)

def add_random_mouse_movement(driver):
    """
    Simulate natural mouse movements.
    """
    action = ActionChains(driver)
    
    # Get viewport size
    viewport_width = driver.execute_script("return window.innerWidth;")
    viewport_height = driver.execute_script("return window.innerHeight;")
    
    # Generate random points for natural-looking movement
    points = [(random.randint(0, viewport_width), random.randint(0, viewport_height)) for _ in range(3)]
    
    # Move mouse through points with random delays
    for x, y in points:
        action.move_by_offset(x, y)
        action.pause(random.uniform(0.1, 0.3))
    
    action.perform()

def setup_chrome_driver(download_path: str) -> webdriver.Chrome:
    """
    Set up Chrome WebDriver with sophisticated anti-detection measures.
    
    Args:
        download_path: Path where downloaded files should be saved
        
    Returns:
        Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    
    # Random viewport size
    width, height = get_random_viewport_size()
    chrome_options.add_argument(f'--window-size={width},{height}')
    
    # Enable headless mode with modern Chrome settings
    chrome_options.add_argument('--headless=new')
    
    # Set random user agent
    chrome_options.add_argument(f'--user-agent={get_random_user_agent()}')
    
    # Mimic real Chrome browser settings
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-automation')
    chrome_options.add_argument('--disable-infobars')
    
    # Add language and platform preferences like a real browser
    chrome_options.add_argument('--lang=en-US,en;q=0.9')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    
    # Add realistic browser features
    chrome_options.add_argument('--enable-javascript')
    chrome_options.add_argument('--enable-cookies')
    
    # Set permissions to appear more natural
    chrome_options.add_argument('--enable-notifications')
    
    # Advanced browser fingerprinting evasion
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set up download behavior and other preferences
    prefs = {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
        'profile.default_content_settings.popups': 0,
        'profile.password_manager_enabled': True,
        'credentials_enable_service': True,
        # Add common plugins to look more realistic
        'plugins.plugins_list': [
            {'enabled': True, 'name': 'Chrome PDF Viewer'},
            {'enabled': True, 'name': 'Chrome PDF Plugin'},
            {'enabled': True, 'name': 'Native Client'}
        ],
        # Add common browser settings
        'profile.default_content_setting_values': {
            'notifications': 1,  # 0=Ask, 1=Allow, 2=Block
            'geolocation': 2,
            'media_stream_mic': 2,
            'media_stream_camera': 2,
        }
    }
    
    chrome_options.add_experimental_option('prefs', prefs)
    
    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute CDP commands to modify browser fingerprint
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // Override navigator properties
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }
            ]});
            
            // Add language settings
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            
            // Modify WebGL fingerprint
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter.apply(this, arguments);
            };
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
            # Navigate to the converter website with random timing
            print("Accessing converter website...(main)")
            driver.get("https://cnvmp3.com/")
            time.sleep(random.uniform(1, 2))  # Random initial wait
            
            # Add some random mouse movements
            add_random_mouse_movement(driver)
            
            # Wait for and find the URL input field
            url_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "input-field-url"))
            )
            
            # Enter the YouTube URL with human-like typing
            url_input.clear()
            for char in url:
                url_input.send_keys(char)
                time.sleep(random.uniform(0.01, 0.03))  # Random typing delay
            
            time.sleep(random.uniform(0.5, 1))  # Random pause after typing
            
            # More random mouse movements
            add_random_mouse_movement(driver)
            
            # Find and click the convert button
            convert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "convert-button-1"))
            )
            
            # Move to button naturally and click
            action = ActionChains(driver)
            action.move_to_element(convert_button)
            action.pause(random.uniform(0.1, 0.3))
            action.click()
            action.perform()
            
            # Wait for download to complete with random checking intervals
            print("Waiting for download to complete...")
            max_wait = 60
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
                
                time.sleep(random.uniform(0.5, 1.5))  # Random check interval
            
            print("Timeout waiting for download")
            return None
            
        finally:
            # Add final random movements before closing
            add_random_mouse_movement(driver)
            time.sleep(random.uniform(0.5, 1))
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