"""
Whisper-based audio transcription with medical context
Uses OpenAI's Whisper API for high-quality medical terminology recognition
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class WhisperTranscriber:
    """Transcribe audio using OpenAI Whisper API with medical context"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Medical prompt to guide Whisper toward medical terminology
        self.medical_prompt = """
This is a medical query about Harrison's Principles of Internal Medicine.
Common medical terms include: hyponatremia, hypernatremia, hypokalemia, hyperkalemia,
acute myocardial infarction, pneumonia, sepsis, diabetes mellitus, heart failure,
acute kidney injury, chronic kidney disease, electrolyte disturbances, workup,
management, treatment, diagnosis, pathophysiology, etiology, complications.
"""
    
    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> dict:
        """
        Transcribe audio file using Whisper API
        
        Args:
            audio_file_path: Path to audio file (webm, mp3, wav, etc.)
            language: Language code (default: "en")
        
        Returns:
            dict with 'text' and 'success' keys
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    prompt=self.medical_prompt,
                    response_format="text"
                )
            
            return {
                "success": True,
                "text": transcript.strip()
            }
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.webm", language: str = "en") -> dict:
        """
        Transcribe audio from bytes
        
        Args:
            audio_bytes: Audio file content as bytes
            filename: Filename with extension (for format detection)
            language: Language code (default: "en")
        
        Returns:
            dict with 'text' and 'success' keys
        """
        try:
            # Create a file-like object from bytes
            from io import BytesIO
            audio_file = BytesIO(audio_bytes)
            audio_file.name = filename
            
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                prompt=self.medical_prompt,
                response_format="text"
            )
            
            return {
                "success": True,
                "text": transcript.strip()
            }
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }

# Global instance
_transcriber = None

def get_transcriber() -> WhisperTranscriber:
    """Get or create global transcriber instance"""
    global _transcriber
    if _transcriber is None:
        _transcriber = WhisperTranscriber()
    return _transcriber

