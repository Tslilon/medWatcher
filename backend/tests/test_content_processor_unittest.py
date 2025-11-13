"""
Unit tests for ContentProcessor (using unittest)
Run with: python run_all_tests.py
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from content_processor import ContentProcessor


class TestProcessorInitialization(unittest.TestCase):
    """Test ContentProcessor initialization"""
    
    @classmethod
    def setUpClass(cls):
        """Create temp directory for all tests"""
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.processor = ContentProcessor(data_dir=cls.temp_dir)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up temp directory"""
        shutil.rmtree(cls.temp_dir)
    
    def test_processor_init(self):
        """Test that processor initializes correctly"""
        self.assertEqual(self.processor.data_dir, self.temp_dir)
        self.assertTrue(self.processor.images_dir.exists())
        self.assertTrue(self.processor.audio_dir.exists())
        self.assertTrue(self.processor.drawings_dir.exists())
        self.assertTrue(self.processor.notes_dir.exists())
    
    def test_directory_creation(self):
        """Test that all required directories are created"""
        required_dirs = [
            self.processor.images_dir,
            self.processor.images_chunks_dir,
            self.processor.notes_dir,
            self.processor.notes_chunks_dir,
            self.processor.drawings_dir,
            self.processor.drawings_chunks_dir,
            self.processor.audio_dir,
            self.processor.audio_chunks_dir
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(dir_path.exists())
            self.assertTrue(dir_path.is_dir())


class TestHelperMethods(unittest.TestCase):
    """Test helper methods"""
    
    @classmethod
    def setUpClass(cls):
        """Create processor for all tests"""
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.processor = ContentProcessor(data_dir=cls.temp_dir)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        shutil.rmtree(cls.temp_dir)
    
    def test_slugify(self):
        """Test text slugification"""
        test_cases = [
            ("Test File.pdf", "test_filepdf"),
            ("My Document 123", "my_document_123"),
            ("Special!@#$%Chars", "specialchars"),
            ("Multiple   Spaces", "multiple_spaces"),
            ("UPPERCASE", "uppercase"),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor._slugify(input_text)
            self.assertEqual(result, expected, f"Failed for '{input_text}'")
    
    def test_generate_content_id(self):
        """Test content ID generation"""
        for content_type in ["image", "audio", "drawing", "note"]:
            content_id = self.processor._generate_content_id(content_type)
            
            self.assertTrue(content_id.startswith(f"{content_type}_"))
            parts = content_id.split('_')
            self.assertEqual(len(parts), 3)  # type_timestamp_random
            self.assertTrue(parts[1].isdigit())  # timestamp
            self.assertEqual(len(parts[2]), 8)  # random hex
    
    def test_generate_unique_ids(self):
        """Test that generated IDs are unique"""
        ids = set()
        for _ in range(100):
            content_id = self.processor._generate_content_id("test")
            self.assertNotIn(content_id, ids)
            ids.add(content_id)
    
    def test_create_preview(self):
        """Test preview creation"""
        # Short text
        short = "This is short"
        self.assertEqual(self.processor._create_preview(short, 100), short)
        
        # Long text
        long = "This is a very long text. " * 20
        preview = self.processor._create_preview(long, 50)
        self.assertLessEqual(len(preview), 55)  # 50 + "..."
        self.assertTrue(preview.endswith("..."))
    
    def test_chunk_text(self):
        """Test text chunking"""
        # Short text - no chunking needed
        short = "Short text"
        chunks = self.processor._chunk_text(short, chunk_size=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short)
        
        # Long text - multiple chunks
        long = "Sentence. " * 100
        chunks = self.processor._chunk_text(long, chunk_size=50, overlap=10)
        self.assertGreater(len(chunks), 1)
        
        # Check all chunks have content (filter out empty strings)
        non_empty_chunks = [c for c in chunks if c.strip()]
        self.assertEqual(len(chunks), len(non_empty_chunks), "Some chunks are empty")


class TestNoteProcessing(unittest.TestCase):
    """Test note processing"""
    
    def setUp(self):
        """Create temp directory for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.processor = ContentProcessor(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_process_simple_note(self):
        """Test processing a simple text note"""
        text = "This is a test note about hyponatremia management."
        title = "Test Note"
        
        metadata, chunks, filename = self.processor.process_note(
            text_content=text,
            title=title,
            tags=["test", "electrolytes"]
        )
        
        # Check metadata
        self.assertEqual(metadata['content_type'], 'note')
        self.assertEqual(metadata['title'], title)
        self.assertGreater(metadata['word_count'], 0)
        self.assertFalse(metadata['is_markdown'])
        self.assertIn('test', metadata['tags'])
        
        # Check chunks
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk['content_type'], 'note')
            self.assertIn('chunk_id', chunk)
        
        # Check file saved
        saved_path = self.processor.notes_dir / filename
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.read_text(), text)
    
    def test_process_markdown_note(self):
        """Test processing markdown note"""
        text = "# Title\n\n## Section\n\nContent here."
        title = "Markdown Note"
        
        metadata, chunks, filename = self.processor.process_note(
            text_content=text,
            title=title,
            is_markdown=True
        )
        
        self.assertTrue(metadata['is_markdown'])
        self.assertTrue(filename.endswith('.md'))
    
    def test_process_long_note(self):
        """Test processing long note (multiple chunks)"""
        # Create a long text that will be chunked
        text = "This is a sentence. " * 100  # ~2000 chars
        
        metadata, chunks, filename = self.processor.process_note(
            text_content=text,
            title="Long Note"
        )
        
        # Should create multiple chunks for long text
        if len(text) > 1000:
            self.assertGreater(len(chunks), 1)
        
        # All chunks should have proper structure
        for chunk in chunks:
            self.assertIn('chunk_id', chunk)
            self.assertIn('text', chunk)
            self.assertIn('preview', chunk)
            self.assertIn('metadata', chunk)


class TestDrawingProcessing(unittest.TestCase):
    """Test drawing processing"""
    
    def setUp(self):
        """Create temp directory for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.processor = ContentProcessor(data_dir=self.temp_dir)
        
        # Create minimal valid PNG data (1x1 pixel)
        self.minimal_png = bytes([
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
    
    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_process_drawing(self):
        """Test processing a drawing"""
        metadata, chunks, filename = self.processor.process_drawing(
            drawing_data=self.minimal_png,
            caption="ECG interpretation",
            tags=["ecg", "cardiology"]
        )
        
        # Check metadata
        self.assertEqual(metadata['content_type'], 'drawing')
        self.assertEqual(metadata['caption'], "ECG interpretation")
        self.assertIn('ecg', metadata['tags'])
        self.assertEqual(metadata['file_size'], len(self.minimal_png))
        
        # Check chunks
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk['content_type'], 'drawing')
        
        # Check file saved
        saved_path = self.processor.drawings_dir / filename
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.read_bytes(), self.minimal_png)
        self.assertTrue(filename.endswith('.png'))
    
    def test_drawing_without_caption(self):
        """Test drawing without caption still creates valid chunks"""
        metadata, chunks, filename = self.processor.process_drawing(
            drawing_data=self.minimal_png
        )
        
        self.assertGreater(len(chunks), 0)
        self.assertTrue(chunks[0]['text'])  # Should have default text


class TestChunkStructure(unittest.TestCase):
    """Test that chunks have correct structure"""
    
    def setUp(self):
        """Create temp directory for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.processor = ContentProcessor(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_chunk_required_fields(self):
        """Test that all chunks have required fields"""
        text = "Test note content"
        metadata, chunks, _ = self.processor.process_note(
            text_content=text,
            title="Test"
        )
        
        required_fields = ['chunk_id', 'content_id', 'content_type', 'text', 'preview', 'metadata']
        
        for chunk in chunks:
            for field in required_fields:
                self.assertIn(field, chunk, f"Missing field: {field}")
            
            # Metadata should be a dict with required fields
            self.assertIsInstance(chunk['metadata'], dict)
            self.assertIn('title', chunk['metadata'])
            self.assertIn('filename', chunk['metadata'])
    
    def test_chunk_ids_unique(self):
        """Test that chunk IDs are unique"""
        text = "Long text. " * 200  # Force multiple chunks
        metadata, chunks, _ = self.processor.process_note(
            text_content=text,
            title="Test"
        )
        
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)), "Chunk IDs not unique")
    
    def test_all_chunks_same_content_id(self):
        """Test that all chunks from same content have same content_id"""
        text = "Long note. " * 200
        metadata, chunks, _ = self.processor.process_note(
            text_content=text,
            title="Test"
        )
        
        if len(chunks) > 1:
            content_ids = [chunk['content_id'] for chunk in chunks]
            for cid in content_ids:
                self.assertEqual(cid, content_ids[0])
            self.assertEqual(content_ids[0], metadata['content_id'])


if __name__ == "__main__":
    unittest.main(verbosity=2)

