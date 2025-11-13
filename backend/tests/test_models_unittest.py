"""
Unit tests for multimodal content models (using unittest)
Run with: python run_all_tests.py
"""
import unittest
from datetime import datetime
from models import (
    UserImage, UserAudio, UserDrawing, UserNote,
    ContentUploadResponse
)
from pydantic import ValidationError


class TestUserImageModel(unittest.TestCase):
    """Test UserImage model"""
    
    def test_valid_image_creation(self):
        """Test creating a valid image model"""
        image = UserImage(
            content_id="img_test_123",
            title="Test X-Ray",
            filename="img_test_123.jpg",
            caption="Chest X-ray",
            tags=["radiology"],
            created_at=datetime.now(),
            file_size=245678,
            chunks=2,
            has_ocr=True,
            ocr_text="Right lower lobe opacity",
            original_format="jpeg"
        )
        
        self.assertEqual(image.content_type, "image")
        self.assertEqual(image.content_id, "img_test_123")
        self.assertTrue(image.has_ocr)
        self.assertEqual(image.original_format, "jpeg")
    
    def test_image_with_heic_format(self):
        """Test image with HEIC format (iPhone)"""
        image = UserImage(
            content_id="img_iphone_456",
            title="iPhone Photo",
            filename="img_iphone_456.jpg",
            tags=["mobile"],
            created_at=datetime.now(),
            file_size=123456,
            chunks=1,
            has_ocr=False,
            original_format="heic"
        )
        
        self.assertEqual(image.original_format, "heic")
        self.assertTrue(image.filename.endswith(".jpg"))


class TestUserAudioModel(unittest.TestCase):
    """Test UserAudio model"""
    
    def test_valid_audio_creation(self):
        """Test creating a valid audio model"""
        audio = UserAudio(
            content_id="audio_test_789",
            title="Morning Rounds",
            filename="audio_test_789.mp3",
            description="DKA case discussion",
            tags=["rounds", "dka"],
            created_at=datetime.now(),
            file_size=1245678,
            chunks=3,
            duration_seconds=125.5,
            has_transcription=True,
            transcription="Patient presented with DKA...",
            original_format="m4a"
        )
        
        self.assertEqual(audio.content_type, "audio")
        self.assertEqual(audio.duration_seconds, 125.5)
        self.assertEqual(audio.original_format, "m4a")
        self.assertTrue(audio.has_transcription)
    
    def test_audio_formats(self):
        """Test various audio formats"""
        formats = ["webm", "m4a", "aac", "caf", "wav", "mp4"]
        
        for fmt in formats:
            audio = UserAudio(
                content_id=f"audio_{fmt}",
                title=f"Test {fmt.upper()}",
                filename=f"audio.mp3",
                created_at=datetime.now(),
                file_size=100000,
                chunks=1,
                duration_seconds=60.0,
                has_transcription=False,
                original_format=fmt
            )
            self.assertEqual(audio.original_format, fmt)


class TestUserDrawingModel(unittest.TestCase):
    """Test UserDrawing model"""
    
    def test_valid_drawing_creation(self):
        """Test creating a valid drawing model"""
        drawing = UserDrawing(
            content_id="draw_test_abc",
            title="ECG Sketch",
            filename="draw_test_abc.png",
            caption="ST elevation pattern",
            tags=["ecg"],
            created_at=datetime.now(),
            file_size=125430,
            chunks=1,
            has_ocr=False
        )
        
        self.assertEqual(drawing.content_type, "drawing")
        self.assertTrue(drawing.filename.endswith(".png"))


class TestUserNoteModel(unittest.TestCase):
    """Test UserNote model"""
    
    def test_valid_note_creation(self):
        """Test creating a valid note model"""
        note = UserNote(
            content_id="note_test_xyz",
            title="Hyponatremia",
            filename="note_test_xyz.txt",
            text_content="Hyponatremia management...",
            tags=["electrolytes"],
            created_at=datetime.now(),
            file_size=1234,
            chunks=2,
            word_count=342,
            is_markdown=False
        )
        
        self.assertEqual(note.content_type, "note")
        self.assertEqual(note.word_count, 342)
        self.assertFalse(note.is_markdown)
    
    def test_markdown_note(self):
        """Test markdown note"""
        note = UserNote(
            content_id="note_md_001",
            title="Protocol",
            filename="note_md_001.md",
            text_content="# Protocol\n\n## Steps",
            tags=["protocol"],
            created_at=datetime.now(),
            file_size=100,
            chunks=1,
            word_count=10,
            is_markdown=True
        )
        
        self.assertTrue(note.is_markdown)
        self.assertTrue(note.filename.endswith(".md"))


class TestContentUploadResponse(unittest.TestCase):
    """Test upload response model"""
    
    def test_successful_upload_response(self):
        """Test successful upload response"""
        response = ContentUploadResponse(
            status="success",
            content_id="img_123",
            filename="img_123.jpg",
            message="Image uploaded successfully",
            chunks_created=2,
            indexed=True
        )
        
        self.assertEqual(response.status, "success")
        self.assertEqual(response.chunks_created, 2)
        self.assertTrue(response.indexed)


if __name__ == "__main__":
    unittest.main(verbosity=2)

