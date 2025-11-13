"""
Unit tests for ContentProcessor
Run with: pytest tests/test_content_processor_unit.py -v
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from content_processor import ContentProcessor


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup after tests
    shutil.rmtree(temp_dir)


@pytest.fixture
def processor(temp_data_dir):
    """Create a ContentProcessor instance for testing"""
    return ContentProcessor(data_dir=temp_data_dir)


class TestProcessorInitialization:
    """Test ContentProcessor initialization"""
    
    def test_processor_init(self, processor, temp_data_dir):
        """Test that processor initializes correctly"""
        assert processor.data_dir == temp_data_dir
        assert processor.images_dir.exists()
        assert processor.audio_dir.exists()
        assert processor.drawings_dir.exists()
        assert processor.notes_dir.exists()
    
    def test_directory_creation(self, processor):
        """Test that all required directories are created"""
        required_dirs = [
            processor.images_dir,
            processor.images_chunks_dir,
            processor.notes_dir,
            processor.notes_chunks_dir,
            processor.drawings_dir,
            processor.drawings_chunks_dir,
            processor.audio_dir,
            processor.audio_chunks_dir
        ]
        
        for dir_path in required_dirs:
            assert dir_path.exists()
            assert dir_path.is_dir()


class TestHelperMethods:
    """Test helper methods"""
    
    def test_slugify(self, processor):
        """Test text slugification"""
        test_cases = [
            ("Test File.pdf", "test_filepdf"),
            ("My Document 123", "my_document_123"),
            ("Special!@#$%Chars", "specialchars"),
            ("Multiple   Spaces", "multiple_spaces"),
            ("UPPERCASE", "uppercase"),
        ]
        
        for input_text, expected in test_cases:
            result = processor._slugify(input_text)
            assert result == expected, f"Failed for '{input_text}'"
    
    def test_generate_content_id(self, processor):
        """Test content ID generation"""
        for content_type in ["image", "audio", "drawing", "note"]:
            content_id = processor._generate_content_id(content_type)
            
            assert content_id.startswith(f"{content_type}_")
            parts = content_id.split('_')
            assert len(parts) == 3  # type_timestamp_random
            assert parts[1].isdigit()  # timestamp
            assert len(parts[2]) == 8  # random hex
    
    def test_generate_unique_ids(self, processor):
        """Test that generated IDs are unique"""
        ids = set()
        for _ in range(100):
            content_id = processor._generate_content_id("test")
            assert content_id not in ids
            ids.add(content_id)
    
    def test_create_preview(self, processor):
        """Test preview creation"""
        # Short text
        short = "This is short"
        assert processor._create_preview(short, 100) == short
        
        # Long text
        long = "This is a very long text. " * 20
        preview = processor._create_preview(long, 50)
        assert len(preview) <= 55  # 50 + "..."
        assert preview.endswith("...")
    
    def test_chunk_text(self, processor):
        """Test text chunking"""
        # Short text - no chunking needed
        short = "Short text"
        chunks = processor._chunk_text(short, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == short
        
        # Long text - multiple chunks
        long = "Sentence. " * 100
        chunks = processor._chunk_text(long, chunk_size=50, overlap=10)
        assert len(chunks) > 1
        
        # Check overlap works
        for i in range(len(chunks) - 1):
            # Some overlap should exist
            assert len(chunks[i]) > 0
            assert len(chunks[i+1]) > 0


class TestNoteProcessing:
    """Test note processing"""
    
    def test_process_simple_note(self, processor):
        """Test processing a simple text note"""
        text = "This is a test note about hyponatremia management."
        title = "Test Note"
        
        metadata, chunks, filename = processor.process_note(
            text_content=text,
            title=title,
            tags=["test", "electrolytes"]
        )
        
        # Check metadata
        assert metadata['content_type'] == 'note'
        assert metadata['title'] == title
        assert metadata['word_count'] > 0
        assert metadata['is_markdown'] == False
        assert 'test' in metadata['tags']
        
        # Check chunks
        assert len(chunks) > 0
        assert all(chunk['content_type'] == 'note' for chunk in chunks)
        assert all('chunk_id' in chunk for chunk in chunks)
        
        # Check file saved
        saved_path = processor.notes_dir / filename
        assert saved_path.exists()
        assert saved_path.read_text() == text
    
    def test_process_markdown_note(self, processor):
        """Test processing markdown note"""
        text = "# Title\n\n## Section\n\nContent here."
        title = "Markdown Note"
        
        metadata, chunks, filename = processor.process_note(
            text_content=text,
            title=title,
            is_markdown=True
        )
        
        assert metadata['is_markdown'] == True
        assert filename.endswith('.md')
    
    def test_process_long_note(self, processor):
        """Test processing long note (multiple chunks)"""
        # Create a long text that will be chunked
        text = "This is a sentence. " * 100  # ~2000 chars
        
        metadata, chunks, filename = processor.process_note(
            text_content=text,
            title="Long Note"
        )
        
        # Should create multiple chunks for long text
        if len(text) > 1000:
            assert len(chunks) > 1
        
        # All chunks should have proper structure
        for chunk in chunks:
            assert 'chunk_id' in chunk
            assert 'text' in chunk
            assert 'preview' in chunk
            assert 'metadata' in chunk


class TestDrawingProcessing:
    """Test drawing processing"""
    
    @pytest.fixture
    def minimal_png(self):
        """Create minimal valid PNG data"""
        # 1x1 pixel PNG
        return bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0x60, 0x00, 0x00, 0x00,
            0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC, 0x33, 0x00,
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
            0x42, 0x60, 0x82
        ])
    
    def test_process_drawing(self, processor, minimal_png):
        """Test processing a drawing"""
        metadata, chunks, filename = processor.process_drawing(
            drawing_data=minimal_png,
            caption="ECG interpretation",
            tags=["ecg", "cardiology"]
        )
        
        # Check metadata
        assert metadata['content_type'] == 'drawing'
        assert metadata['caption'] == "ECG interpretation"
        assert 'ecg' in metadata['tags']
        assert metadata['file_size'] == len(minimal_png)
        
        # Check chunks
        assert len(chunks) > 0
        assert all(chunk['content_type'] == 'drawing' for chunk in chunks)
        
        # Check file saved
        saved_path = processor.drawings_dir / filename
        assert saved_path.exists()
        assert saved_path.read_bytes() == minimal_png
        assert filename.endswith('.png')
    
    def test_drawing_without_caption(self, processor, minimal_png):
        """Test drawing without caption still creates valid chunks"""
        metadata, chunks, filename = processor.process_drawing(
            drawing_data=minimal_png
        )
        
        assert len(chunks) > 0
        assert chunks[0]['text']  # Should have default text


class TestChunkStructure:
    """Test that chunks have correct structure"""
    
    def test_chunk_required_fields(self, processor):
        """Test that all chunks have required fields"""
        text = "Test note content"
        metadata, chunks, _ = processor.process_note(
            text_content=text,
            title="Test"
        )
        
        required_fields = ['chunk_id', 'content_id', 'content_type', 'text', 'preview', 'metadata']
        
        for chunk in chunks:
            for field in required_fields:
                assert field in chunk, f"Missing field: {field}"
            
            # Metadata should be a dict with required fields
            assert isinstance(chunk['metadata'], dict)
            assert 'title' in chunk['metadata']
            assert 'filename' in chunk['metadata']
    
    def test_chunk_ids_unique(self, processor):
        """Test that chunk IDs are unique"""
        text = "Long text. " * 200  # Force multiple chunks
        metadata, chunks, _ = processor.process_note(
            text_content=text,
            title="Test"
        )
        
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs not unique"


class TestContentIdConsistency:
    """Test content ID consistency across chunks"""
    
    def test_all_chunks_same_content_id(self, processor):
        """Test that all chunks from same content have same content_id"""
        text = "Long note. " * 200
        metadata, chunks, _ = processor.process_note(
            text_content=text,
            title="Test"
        )
        
        if len(chunks) > 1:
            content_ids = [chunk['content_id'] for chunk in chunks]
            assert all(cid == content_ids[0] for cid in content_ids)
            assert content_ids[0] == metadata['content_id']


class TestFileManagement:
    """Test file saving and management"""
    
    def test_files_saved_to_correct_directories(self, processor):
        """Test that files are saved to correct directories"""
        # Note
        _, _, note_file = processor.process_note(
            text_content="Test",
            title="Test Note"
        )
        assert (processor.notes_dir / note_file).exists()
        
        # Drawing
        minimal_png = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0x60, 0x00, 0x00, 0x00,
            0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC, 0x33, 0x00,
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
            0x42, 0x60, 0x82
        ])
        _, _, drawing_file = processor.process_drawing(drawing_data=minimal_png)
        assert (processor.drawings_dir / drawing_file).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

