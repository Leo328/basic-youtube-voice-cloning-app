"""
Module for handling YouTube video audio extraction using cnvmp3.com via stealth headless browser automation.
This version implements advanced anti-detection measures for cloud deployment.
"""

import os
import re
import time
import random
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def get_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:v=|/v/|/embed/|youtu\.be/)([^&?/]+)',  # Standard and embed URLs
        r'(?:youtube\.com/shorts/)([^&?/]+)',        # YouTube Shorts
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_random_viewport_size() -> Tuple[int, int]:
    """Return a conservative, realistic viewport size."""
    viewports = [
        (1366, 768),   # Common laptop
        (1280, 720),   # HD
        (1024, 768),   # Standard
    ]
    return random.choice(viewports)

def get_random_user_agent() -> str:
    """Return a random, recent Chrome user agent."""
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    return random.choice(agents)

def simulate_human_interaction(driver: webdriver.Chrome) -> None:
    """Simulate natural human-like interactions with bounds checking."""
    try:
        action = ActionChains(driver)
        
        # Get viewport size with fallback values
        try:
            viewport_width = driver.execute_script("return Math.min(window.innerWidth, document.documentElement.clientWidth);") or 800
            viewport_height = driver.execute_script("return Math.min(window.innerHeight, document.documentElement.clientHeight);") or 600
        except:
            viewport_width = 800
            viewport_height = 600
        
        # Use very conservative bounds (central 50% of viewport)
        safe_width = min(viewport_width // 2, 400)  # Half of viewport, max 400px
        safe_height = min(viewport_height // 2, 300)  # Half of viewport, max 300px
        
        # Calculate safe boundaries (center of screen)
        center_x = viewport_width // 2
        center_y = viewport_height // 2
        start_x = center_x - (safe_width // 2)
        start_y = center_y - (safe_height // 2)
        
        # Generate 2-3 safe points within the central area
        points = []
        num_points = random.randint(2, 3)
        
        for _ in range(num_points):
            x = random.randint(start_x, start_x + safe_width)
            y = random.randint(start_y, start_y + safe_height)
            points.append((x, y))
        
        # Reset mouse to center
        action.move_by_offset(center_x, center_y).perform()
        time.sleep(random.uniform(0.1, 0.2))
        
        # Move through points with natural delays
        current_x = center_x
        current_y = center_y
        
        for x, y in points:
            # Calculate relative movement
            delta_x = x - current_x
            delta_y = y - current_y
            
            # Move in smaller steps
            steps = random.randint(2, 3)
            for step in range(steps):
                step_x = delta_x // steps
                step_y = delta_y // steps
                action.move_by_offset(step_x, step_y)
                action.pause(random.uniform(0.05, 0.1))
            
            current_x = x
            current_y = y
        
        action.perform()
        time.sleep(random.uniform(0.2, 0.3))
        
    except Exception as e:
        print(f"Warning: Mouse movement simulation failed: {str(e)}")
        # Continue execution even if mouse movement fails

def setup_stealth_driver(download_path: str) -> webdriver.Chrome:
    """Set up Chrome WebDriver with advanced anti-detection measures."""
    chrome_options = Options()
    
    # Set random viewport and user agent
    width, height = get_random_viewport_size()
    chrome_options.add_argument(f'--window-size={width},{height}')
    chrome_options.add_argument(f'--user-agent={get_random_user_agent()}')
    
    # Headless mode with modern settings
    chrome_options.add_argument('--headless=new')
    
    # Advanced anti-detection measures
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-automation')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Mimic real browser behavior
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--enable-javascript')
    chrome_options.add_argument('--lang=en-US,en;q=0.9')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    
    # Set up download behavior and preferences
    prefs = {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
        'profile.default_content_settings.popups': 0,
        'plugins.always_open_pdf_externally': True,
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Inject scripts to modify browser fingerprint
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // Override navigator properties
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Add common plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "PDF Document"},
                        description: "PDF Document",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }
                ]
            });
            
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

def extract_audio_stealth(url: str, output_path: str, progress_callback=None) -> Optional[str]:
    """
    Extract audio from YouTube video using stealth browser automation.
    
    Args:
        url: YouTube video URL
        output_path: Directory where the audio file will be saved
        progress_callback: Optional callback function to report progress
        
    Returns:
        Path to the downloaded audio file or None if extraction fails
    """
    def log_progress(message: str):
        """Helper to handle progress updates"""
        print(message)  # Still log to console
        if progress_callback:
            progress_callback(message)
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Extract video ID
        video_id = get_video_id(url)
        if not video_id:
            log_progress("Invalid YouTube URL")
            return None
        
        # Set up stealth browser
        log_progress("Setting up secure browser environment...")
        driver = setup_stealth_driver(os.path.abspath(output_path))
        
        try:
            # Navigate to converter with random timing
            log_progress("Accessing audio converter website... (stealth)")
            driver.get("https://cnvmp3.com/")
            time.sleep(random.uniform(2, 3))  # Initial page load wait
            
            # Find and interact with URL input
            url_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "input-field-url"))
            )
            
            # Clear the input field using JavaScript (more reliable than clear())
            driver.execute_script("arguments[0].value = '';", url_input)
            time.sleep(random.uniform(0.3, 0.5))
            
            # Verify the field is empty
            current_value = driver.execute_script("return arguments[0].value;", url_input)
            if current_value:
                log_progress("Clearing previous input...")
                driver.execute_script("arguments[0].value = '';", url_input)
                time.sleep(0.5)
            
            # Type URL with human-like timing
            log_progress("Entering YouTube URL...")
            for char in url:
                url_input.send_keys(char)
                time.sleep(random.uniform(0.02, 0.05))
            
            # Verify the entered URL
            entered_url = driver.execute_script("return arguments[0].value;", url_input)
            if entered_url != url:
                log_progress("Verifying URL input...")
                driver.execute_script("arguments[0].value = '';", url_input)
                time.sleep(0.5)
                url_input.send_keys(url)
            
            time.sleep(random.uniform(0.7, 1.2))
            simulate_human_interaction(driver)
            
            # Click convert button
            log_progress("Starting audio extraction...")
            convert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "convert-button-1"))
            )
            
            # Move to button naturally and click
            action = ActionChains(driver)
            action.move_to_element(convert_button)
            action.pause(random.uniform(0.2, 0.4))
            action.click()
            action.perform()
            
            # Wait for download with random intervals
            log_progress("Processing audio... this may take a minute...")
            max_wait = 60
            start_time = time.time()
            last_progress = 0
            
            while time.time() - start_time < max_wait:
                current_time = time.time() - start_time
                progress_percent = int((current_time / max_wait) * 100)
                
                # Update progress every 10%
                if progress_percent >= last_progress + 10:
                    last_progress = progress_percent
                    if progress_percent < 90:  # Don't show 90%+ unless actually done
                        log_progress(f"Still working... {progress_percent}% of timeout...")
                
                files = os.listdir(output_path)
                mp3_files = [f for f in files if f.endswith('.mp3')]
                
                if mp3_files:
                    latest_file = max([os.path.join(output_path, f) for f in mp3_files],
                                    key=os.path.getctime)
                    log_progress("Audio download completed!")
                    return latest_file
                
                time.sleep(random.uniform(0.8, 1.5))
            
            log_progress("Timeout waiting for download")
            return None
            
        finally:
            # Final random interaction before closing
            simulate_human_interaction(driver)
            time.sleep(random.uniform(0.5, 1))
            driver.quit()
            log_progress("Cleanup complete")
            
    except Exception as e:
        error_msg = f"Error extracting audio: {str(e)}"
        log_progress(error_msg)
        return None 