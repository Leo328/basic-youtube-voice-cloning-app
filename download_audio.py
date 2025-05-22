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
