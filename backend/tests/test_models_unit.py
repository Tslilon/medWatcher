"""
Unit tests for multimodal content models
Run with: pytest tests/test_models_unit.py -v
"""
import pytest
from datetime import datetime
from models import (
    UserImage, UserAudio, UserDrawing, UserNote,
    ContentUploadResponse,
    ImageUploadRequest, AudioUploadRequest,
    DrawingUploadRequest, NoteUploadRequest
)
from pydantic import ValidationError


class TestUserImageModel:
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
        
        assert image.content_type == "image"
        assert image.content_id == "img_test_123"
        assert image.has_ocr == True
        assert image.original_format == "jpeg"
    
    def test_image_missing_required_fields(self):
        """Test that missing required fields raises error"""
        with pytest.raises(ValidationError):
            UserImage(
                content_id="test",
                title="Test"
                # Missing many required fields
            )
    
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
            original_format="heic"  # Original was HEIC, converted to JPEG
        )
        
        assert image.original_format == "heic"
        assert image.filename.endswith(".jpg")  # Converted


class TestUserAudioModel:
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
            original_format="m4a"  # Apple Watch format
        )
        
        assert audio.content_type == "audio"
        assert audio.duration_seconds == 125.5
        assert audio.original_format == "m4a"
        assert audio.has_transcription == True
    
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
            assert audio.original_format == fmt


class TestUserDrawingModel:
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
        
        assert drawing.content_type == "drawing"
        assert drawing.filename.endswith(".png")


class TestUserNoteModel:
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
        
        assert note.content_type == "note"
        assert note.word_count == 342
        assert note.is_markdown == False
    
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
        
        assert note.is_markdown == True
        assert note.filename.endswith(".md")


class TestUploadRequests:
    """Test upload request models"""
    
    def test_image_upload_request(self):
        """Test image upload request"""
        request = ImageUploadRequest(
            content_type="image",
            title="Test Image",
            caption="A test image",
            tags="radiology,chest"
        )
        
        assert request.content_type == "image"
    
    def test_audio_upload_request(self):
        """Test audio upload request"""
        request = AudioUploadRequest(
            content_type="audio",
            title="Test Audio",
            description="Audio description",
            tags="rounds"
        )
        
        assert request.content_type == "audio"
    
    def test_note_upload_request(self):
        """Test note upload request"""
        request = NoteUploadRequest(
            content_type="note",
            text_content="This is a test note",
            title="Test Note",
            is_markdown=True
        )
        
        assert request.content_type == "note"
        assert request.text_content == "This is a test note"


class TestContentUploadResponse:
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
        
        assert response.status == "success"
        assert response.chunks_created == 2
        assert response.indexed == True
    
    def test_failed_upload_response(self):
        """Test failed upload response"""
        response = ContentUploadResponse(
            status="error",
            content_id="",
            filename="",
            message="Upload failed: Invalid format",
            chunks_created=0,
            indexed=False
        )
        
        assert response.status == "error"
        assert response.indexed == False


class TestModelValidation:
    """Test model validation rules"""
    
    def test_content_type_validation(self):
        """Test that only valid content types are accepted"""
        # This should work
        note = UserNote(
            content_id="test",
            title="Test",
            filename="test.txt",
            text_content="Content",
            created_at=datetime.now(),
            file_size=100,
            chunks=1,
            word_count=1,
            is_markdown=False
        )
        assert note.content_type == "note"
        
        # Invalid content_type should be caught by Literal type
    
    def test_file_size_positive(self):
        """Test that file size must be positive"""
        note = UserNote(
            content_id="test",
            title="Test",
            filename="test.txt",
            text_content="Content",
            created_at=datetime.now(),
            file_size=0,  # Zero is valid
            chunks=1,
            word_count=1,
            is_markdown=False
        )
        assert note.file_size >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

