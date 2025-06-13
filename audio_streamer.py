import pygame
import threading
import requests
import tempfile
import os
import time

class AudioStreamer:
    def __init__(self, stream_url="http://radio.freeplace.info:8000/MagicFM.mp3"):
        """Initialize the audio streamer with the given stream URL."""
        self.stream_url = stream_url
        self.is_playing = False
        self.temp_file = None
        self.stream_thread = None
        self.volume = 0.5  # Default volume (0.0 to 1.0)
        
    def start_streaming(self):
        """Start streaming audio from the URL in a separate thread."""
        if self.is_playing:
            return
            
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.is_playing = True
        self.stream_thread = threading.Thread(target=self._stream_audio)
        self.stream_thread.daemon = True  # Thread will close when main program exits
        self.stream_thread.start()
        
    def stop_streaming(self):
        """Stop the audio stream."""
        self.is_playing = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Clean up temp file
        if self.temp_file and os.path.exists(self.temp_file.name):
            self.temp_file.close()
            
    def set_volume(self, volume):
        """Set the volume of the stream (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        
    def _stream_audio(self):
        """Internal method to handle the streaming process."""
        try:
            # Create a temporary file to store the stream data
            self.temp_file = tempfile.NamedTemporaryFile(delete=False)
            
            # Stream the audio in chunks
            response = requests.get(self.stream_url, stream=True, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Write initial buffer to temp file
            chunk_size = 8192
            buffer_size = chunk_size * 64  # Buffer ~0.5MB before starting playback
            
            # Write initial buffer
            bytes_written = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not self.is_playing:
                    break
                    
                if chunk:
                    self.temp_file.write(chunk)
                    bytes_written += len(chunk)
                    
                    if bytes_written >= buffer_size:
                        break
            
            # Flush and prepare for playback
            self.temp_file.flush()
            
            # Start playback
            pygame.mixer.music.load(self.temp_file.name)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            # Continue streaming while playing
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not self.is_playing:
                    break
                    
                if chunk:
                    self.temp_file.write(chunk)
                    self.temp_file.flush()
                    
                # If music stopped playing, restart it
                if not pygame.mixer.music.get_busy() and self.is_playing:
                    self.temp_file.flush()
                    pygame.mixer.music.load(self.temp_file.name)
                    pygame.mixer.music.play()
                    
        except Exception as e:
            print(f"Streaming error: {e}")
            self.is_playing = False
        finally:
            # Clean up
            if self.temp_file and os.path.exists(self.temp_file.name):
                self.temp_file.close()
                try:
                    os.unlink(self.temp_file.name)
                except:
                    pass