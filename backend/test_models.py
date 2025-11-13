"""
Test script for multimodal content models
Run with: python test_models.py
"""
from datetime import datetime
from models import (
    UserImage, UserAudio, UserDrawing, UserNote,
    ContentUploadResponse
)

def test_user_image():
    """Test UserImage model"""
    print("Testing UserImage model...")
    image = UserImage(
        content_id="img_test_123",
        title="Test X-Ray",
        filename="img_test_123.jpg",
        caption="Chest X-ray showing infiltrates",
        tags=["radiology", "chest"],
        created_at=datetime.now(),
        file_size=245678,
        metadata={"camera": "iPhone 14"},
        chunks=2,
        has_ocr=True,
        ocr_text="Right lower lobe opacity",
        thumbnail_url="/api/content/image/img_test_123.jpg?thumbnail=true",
        original_format="jpeg"
    )
    
    assert image.content_type == "image"
    assert image.content_id == "img_test_123"
    assert image.has_ocr == True
    print("  ✅ UserImage model works!")
    return image

def test_user_audio():
    """Test UserAudio model"""
    print("Testing UserAudio model...")
    audio = UserAudio(
        content_id="audio_test_456",
        title="Morning Rounds - DKA Case",
        filename="audio_test_456.mp3",
        caption="Discussion of DKA management",
        tags=["case", "dka", "rounds"],
        created_at=datetime.now(),
        file_size=1245678,
        metadata={"device": "Apple Watch"},
        chunks=3,
        duration_seconds=125.5,
        has_transcription=True,
        transcription="Patient presented with DKA...",
        original_format="m4a",
        playback_url="/api/content/audio/audio_test_456.mp3"
    )
    
    assert audio.content_type == "audio"
    assert audio.duration_seconds == 125.5
    assert audio.original_format == "m4a"
    print("  ✅ UserAudio model works!")
    return audio

def test_user_drawing():
    """Test UserDrawing model"""
    print("Testing UserDrawing model...")
    drawing = UserDrawing(
        content_id="draw_test_789",
        title="ECG Interpretation",
        filename="draw_test_789.png",
        caption="ST elevation in V1-V4",
        tags=["ecg", "cardiology"],
        created_at=datetime.now(),
        file_size=125430,
        metadata={},
        chunks=1,
        has_ocr=False,
        thumbnail_url="/api/content/image/draw_test_789.png?thumbnail=true"
    )
    
    assert drawing.content_type == "drawing"
    assert drawing.content_id == "draw_test_789"
    print("  ✅ UserDrawing model works!")
    return drawing

def test_user_note():
    """Test UserNote model"""
    print("Testing UserNote model...")
    note = UserNote(
        content_id="note_test_abc",
        title="Hyponatremia Management",
        filename="note_test_abc.txt",
        caption="Quick reference for hyponatremia treatment",
        tags=["electrolytes", "treatment"],
        created_at=datetime.now(),
        file_size=1234,
        metadata={},
        chunks=2,
        text_content="Hyponatremia management depends on severity...",
        word_count=342,
        is_markdown=False
    )
    
    assert note.content_type == "note"
    assert note.word_count == 342
    print("  ✅ UserNote model works!")
    return note

def test_upload_response():
    """Test ContentUploadResponse model"""
    print("Testing ContentUploadResponse model...")
    response = ContentUploadResponse(
        status="success",
        content_id="img_test_123",
        filename="img_test_123.jpg",
        message="Image uploaded and indexed successfully",
        chunks_created=2,
        indexed=True
    )
    
    assert response.status == "success"
    assert response.chunks_created == 2
    print("  ✅ ContentUploadResponse model works!")
    return response

def test_model_validation():
    """Test that validation works"""
    print("Testing model validation...")
    
    try:
        # This should fail - missing required fields
        UserImage(
            content_id="test",
            title="Test"
        )
        print("  ❌ Validation should have failed!")
        return False
    except Exception as e:
        print(f"  ✅ Validation works! (Expected error: {type(e).__name__})")
        return True

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING MULTIMODAL CONTENT MODELS")
    print("="*60 + "\n")
    
    try:
        # Test each model
        image = test_user_image()
        audio = test_user_audio()
        drawing = test_user_drawing()
        note = test_user_note()
        response = test_upload_response()
        test_model_validation()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        # Print summary
        print("\nModel Summary:")
        print(f"  - UserImage: {image.content_type}, {image.file_size} bytes")
        print(f"  - UserAudio: {audio.content_type}, {audio.duration_seconds}s, {audio.original_format}")
        print(f"  - UserDrawing: {drawing.content_type}, {drawing.file_size} bytes")
        print(f"  - UserNote: {note.content_type}, {note.word_count} words")
        print(f"\nAll 4 content types ready for implementation! 🎉\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

