"""
Test script for ContentProcessor
Run with: python test_content_processor.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from content_processor import ContentProcessor

def test_initialization():
    """Test ContentProcessor initialization"""
    print("Testing ContentProcessor initialization...")
    
    try:
        processor = ContentProcessor()
        
        assert processor.images_dir.exists()
        assert processor.audio_dir.exists()
        assert processor.drawings_dir.exists()
        assert processor.notes_dir.exists()
        
        print("  ✅ ContentProcessor initialized successfully")
        print(f"     Data dir: {processor.data_dir}")
        return processor
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        raise

def test_helper_methods(processor):
    """Test helper methods"""
    print("\nTesting helper methods...")
    
    # Test slugify
    slug = processor._slugify("Test File Name.pdf")
    assert slug == "test_file_namepdf"  # Dots are removed, not converted to underscores
    print(f"  ✅ Slugify works: 'Test File Name.pdf' → '{slug}'")
    
    # Test content ID generation
    content_id = processor._generate_content_id("image")
    assert content_id.startswith("image_")
    print(f"  ✅ Content ID generation works: {content_id}")
    
    # Test preview creation
    long_text = "This is a very long text. " * 50
    preview = processor._create_preview(long_text, max_length=50)
    assert len(preview) <= 55  # 50 + "..."
    print(f"  ✅ Preview creation works: {len(long_text)} chars → {len(preview)} chars")
    
    # Test text chunking
    chunks = processor._chunk_text(long_text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    print(f"  ✅ Text chunking works: {len(long_text)} chars → {len(chunks)} chunks")

def test_note_processing(processor):
    """Test note processing"""
    print("\nTesting note processing...")
    
    try:
        text_content = """
# Hyponatremia Management

## Acute Hyponatremia
- Develop over < 48 hours
- Symptomatic: 3% saline bolus
- Rate correction: 4-6 mEq/L in 24h

## Chronic Hyponatremia
- Develop over > 48 hours
- Slower correction required
- Risk: Osmotic demyelination syndrome
        """.strip()
        
        metadata, chunks, filename = processor.process_note(
            text_content=text_content,
            title="Hyponatremia Management",
            tags=["electrolytes", "treatment"],
            is_markdown=True
        )
        
        assert metadata['content_type'] == 'note'
        assert metadata['title'] == 'Hyponatremia Management'
        assert metadata['is_markdown'] == True
        assert metadata['word_count'] > 0
        assert len(chunks) > 0
        assert all(chunk['content_type'] == 'note' for chunk in chunks)
        
        print(f"  ✅ Note processed successfully")
        print(f"     Filename: {filename}")
        print(f"     Word count: {metadata['word_count']}")
        print(f"     Chunks: {len(chunks)}")
        
        # Verify file was saved
        saved_path = processor.notes_dir / filename
        assert saved_path.exists()
        print(f"     File saved: ✅")
        
        return metadata, chunks
        
    except Exception as e:
        print(f"  ❌ Note processing failed: {e}")
        raise

def test_drawing_processing(processor):
    """Test drawing processing (simulated)"""
    print("\nTesting drawing processing...")
    
    try:
        # Create a minimal PNG (1x1 pixel, black)
        # PNG signature + IHDR + IDAT + IEND
        minimal_png = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR length
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x01,  # Width: 1
            0x00, 0x00, 0x00, 0x01,  # Height: 1
            0x08, 0x02, 0x00, 0x00, 0x00,  # 8-bit RGB
            0x90, 0x77, 0x53, 0xDE,  # CRC
            0x00, 0x00, 0x00, 0x0C,  # IDAT length
            0x49, 0x44, 0x41, 0x54,  # IDAT
            0x08, 0xD7, 0x63, 0x60, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01,
            0xE2, 0x21, 0xBC, 0x33,  # CRC
            0x00, 0x00, 0x00, 0x00,  # IEND length
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # CRC
        ])
        
        metadata, chunks, filename = processor.process_drawing(
            drawing_data=minimal_png,
            caption="ECG interpretation - ST elevation",
            tags=["ecg", "cardiology"],
            perform_ocr=False  # Skip OCR for test
        )
        
        assert metadata['content_type'] == 'drawing'
        assert metadata['caption'] == "ECG interpretation - ST elevation"
        assert len(chunks) > 0
        
        print(f"  ✅ Drawing processed successfully")
        print(f"     Filename: {filename}")
        print(f"     File size: {metadata['file_size']} bytes")
        print(f"     Chunks: {len(chunks)}")
        
        # Verify file was saved
        saved_path = processor.drawings_dir / filename
        assert saved_path.exists()
        print(f"     File saved: ✅")
        
        return metadata, chunks
        
    except Exception as e:
        print(f"  ❌ Drawing processing failed: {e}")
        raise

def test_chunk_structure(chunks):
    """Test that chunks have correct structure"""
    print("\nTesting chunk structure...")
    
    required_fields = ['chunk_id', 'content_id', 'content_type', 'text', 'preview', 'metadata']
    
    for chunk in chunks:
        for field in required_fields:
            assert field in chunk, f"Missing field: {field}"
        
        assert isinstance(chunk['metadata'], dict)
        assert 'title' in chunk['metadata']
        assert 'filename' in chunk['metadata']
    
    print(f"  ✅ All {len(chunks)} chunks have correct structure")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING CONTENT PROCESSOR")
    print("="*70 + "\n")
    
    try:
        # Run tests
        processor = test_initialization()
        test_helper_methods(processor)
        
        note_meta, note_chunks = test_note_processing(processor)
        test_chunk_structure(note_chunks)
        
        drawing_meta, drawing_chunks = test_drawing_processing(processor)
        test_chunk_structure(drawing_chunks)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        
        print("\nContent Processor Summary:")
        print(f"  ✅ Helper methods working")
        print(f"  ✅ Note processing working ({len(note_chunks)} chunks)")
        print(f"  ✅ Drawing processing working ({len(drawing_chunks)} chunks)")
        print(f"  ✅ Chunk structure validated")
        print("\nReady for:")
        print("  📷 Image processing (requires PIL + pytesseract)")
        print("  🎤 Audio processing (requires pydub + ffmpeg)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

