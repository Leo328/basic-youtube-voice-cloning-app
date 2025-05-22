"""
Test script for YouTube audio extraction functionality.
"""

from youtube import extract_audio_from_youtube, cleanup_audio_file

def test_audio_extraction():
    """Test audio extraction from a YouTube video."""
    # Test video URL (YouTube Shorts)
    test_url = "https://www.youtube.com/shorts/axeoABqxqHA"
    output_path = "temp_audio"
    
    print("Testing audio extraction...")
    print(f"URL: {test_url}")
    
    try:
        # Extract audio
        audio_file = extract_audio_from_youtube(test_url, output_path)
        
        if audio_file:
            print(f"Success! Audio saved to: {audio_file}")
            # Clean up the file
            cleanup_audio_file(audio_file)
            print("Cleaned up temporary file")
        else:
            print("Failed to extract audio")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_audio_extraction() 