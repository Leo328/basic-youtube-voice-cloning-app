import yt_dlp as youtube_dl
import os

def download_audio(url):
    # Set up options to extract only the audio and download it in mp3 format
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        # Add Windows-specific configurations
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        },
        'nocheckcertificate': True,  # Skip certificate verification
        'cookiefile': 'cookies.txt',  # Save cookies to file
        'socket_timeout': 30,  # Increase timeout
        # Add player and signature extraction options
        'player_client': 'all',  # Try all player clients
        'allow_unplayable_formats': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['all'],
                'player_skip': ['js', 'configs'],  # Skip problematic player components
            }
        }
    }

    # Download the audio
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_filename = os.path.splitext(filename)[0] + '.mp3'
        print(f"Downloaded file saved at: {os.path.abspath(mp3_filename)}")

# Use the provided URL directly
video_url = "https://www.youtube.com/watch?v=CCRuLhF-YBE"
download_audio(video_url) 