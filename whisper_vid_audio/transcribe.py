import os
import subprocess
import whisper
import logging
from typing import Optional, Dict, Union
from pathlib import Path

class WhisperTranscriber:
    """
    A class to handle audio/video transcription using OpenAI's Whisper model.
    Supports multiple input formats and handles conversion to WAV using FFmpeg.
    """
    
    def __init__(self):
        """
        Initialize the transcriber with the 'base' Whisper model.
        """
        self.setup_logging()
        self.model = whisper.load_model("base")
        self.language = "en"

    def setup_logging(self) -> None:
        """Configure logging for the transcriber."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def convert_to_wav(self, input_file: Union[str, Path], output_dir: Optional[str] = None) -> Optional[str]:
        """
        Convert input audio/video file to WAV format using FFmpeg.
        
        Args:
            input_file (Union[str, Path]): Path to input audio/video file
            output_dir (Optional[str]): Directory for output WAV file
            
        Returns:
            Optional[str]: Path to output WAV file if successful, None otherwise
        """
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                self.logger.error(f"Input file not found: {input_file}")
                return None
            
            # Determine output path
            if output_dir:
                output_path = Path(output_dir) / f"{input_path.stem}.wav"
            else:
                output_path = input_path.with_suffix('.wav')
                
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # FFmpeg command for conversion
            command = [
                'ffmpeg',
                '-i', str(input_path),
                '-ar', '16000',  # Sample rate 16kHz
                '-ac', '1',      # Mono audio
                '-c:a', 'pcm_s16le',  # 16-bit PCM encoding
                str(output_path),
                '-y'  # Overwrite output file if exists
            ]
            
            self.logger.info(f"Converting {input_path} to WAV format")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return None
                
            self.logger.info("Conversion successful")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error during conversion: {str(e)}")
            return None
    
    def transcribe(self, 
                  input_file: Union[str, Path], 
                  output_dir: Optional[str] = None,
                  cleanup: bool = True) -> Dict:
        """
        Transcribe audio/video file using Whisper.
        
        Args:
            input_file (Union[str, Path]): Path to input audio/video file
            output_dir (Optional[str]): Directory for temporary WAV file
            cleanup (bool): Whether to delete temporary WAV file after transcription
            
        Returns:
            Dict: Transcription result containing text and other metadata
        """
        try:
            # Convert to WAV if input is not already WAV
            input_path = Path(input_file)
            if input_path.suffix.lower() != '.wav':
                self.logger.info("Converting input file to WAV format")
                wav_file = self.convert_to_wav(input_file, output_dir)
                if not wav_file:
                    raise RuntimeError("Failed to convert input file to WAV format")
            else:
                wav_file = str(input_path)
            
            # Perform transcription
            self.logger.info("Starting transcription")
            result = self.model.transcribe(wav_file, language=self.language)
            self.logger.info("Transcription completed successfully")
            
            # Cleanup temporary WAV file if requested
            if cleanup and input_path.suffix.lower() != '.wav':
                try:
                    os.remove(wav_file)
                    self.logger.info(f"Cleaned up temporary WAV file: {wav_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup temporary file: {str(e)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            raise