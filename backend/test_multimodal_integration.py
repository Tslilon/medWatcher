"""
Integration test for multimodal content system
Tests the full pipeline: ContentProcessor → MultimodalIndexer → ChromaDB
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from content_processor import ContentProcessor
from multimodal_indexer import MultimodalIndexer


def test_note_full_pipeline():
    """Test complete pipeline for a note"""
    print("\n" + "="*70)
    print("TESTING MULTIMODAL INTEGRATION - NOTE")
    print("="*70 + "\n")
    
    try:
        # Step 1: Process note
        print("STEP 1: Processing note...")
        processor = ContentProcessor()
        
        text_content = """
# Acute MI Management

## STEMI Protocol
- Aspirin 325mg
- Dual antiplatelet therapy
- Primary PCI within 90 minutes
- Consider fibrinolysis if PCI delay > 120 min

## Post-MI Care
- Beta-blockers
- ACE inhibitors
- Statins
- Cardiac rehab referral
        """.strip()
        
        metadata, chunks, filename = processor.process_note(
            text_content=text_content,
            title="Acute MI Management Protocol",
            tags=["cardiology", "emergency", "protocols"],
            is_markdown=True
        )
        
        print(f"✅ Note processed:")
        print(f"   - Filename: {filename}")
        print(f"   - Content ID: {metadata['content_id']}")
        print(f"   - Chunks: {len(chunks)}")
        print(f"   - Word count: {metadata['word_count']}")
        
        # Step 2: Index content
        print("\nSTEP 2: Indexing content...")
        indexer = MultimodalIndexer()
        
        success = indexer.index_content(
            metadata=metadata,
            chunks=chunks,
            content_type="note",
            filename=filename
        )
        
        if success:
            print("\n" + "="*70)
            print("✅ INTEGRATION TEST PASSED!")
            print("="*70)
            print(f"\nContent Summary:")
            print(f"  Content ID: {metadata['content_id']}")
            print(f"  Type: note")
            print(f"  Title: {metadata['title']}")
            print(f"  Chunks: {len(chunks)}")
            print(f"  Indexed: ✅")
            print(f"  GCS Upload: ✅")
            print(f"  ChromaDB: ✅")
            print(f"\nYou can now:")
            print(f"  1. Search for 'MI management' or 'STEMI' in the web interface")
            print(f"  2. Content will appear in search results")
            print(f"  3. Click refresh button to sync on deployed server")
            print()
            return 0
        else:
            print("\n❌ INTEGRATION TEST FAILED: Indexing failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_drawing_full_pipeline():
    """Test complete pipeline for a drawing"""
    print("\n" + "="*70)
    print("TESTING MULTIMODAL INTEGRATION - DRAWING")
    print("="*70 + "\n")
    
    try:
        # Create minimal PNG
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
        
        # Step 1: Process drawing
        print("STEP 1: Processing drawing...")
        processor = ContentProcessor()
        
        metadata, chunks, filename = processor.process_drawing(
            drawing_data=minimal_png,
            caption="ECG showing ST elevation in leads II, III, aVF (inferior STEMI)",
            tags=["ecg", "cardiology", "STEMI"]
        )
        
        print(f"✅ Drawing processed:")
        print(f"   - Filename: {filename}")
        print(f"   - Content ID: {metadata['content_id']}")
        print(f"   - Chunks: {len(chunks)}")
        
        # Step 2: Index content
        print("\nSTEP 2: Indexing content...")
        indexer = MultimodalIndexer()
        
        success = indexer.index_content(
            metadata=metadata,
            chunks=chunks,
            content_type="drawing",
            filename=filename
        )
        
        if success:
            print("\n" + "="*70)
            print("✅ INTEGRATION TEST PASSED!")
            print("="*70)
            print(f"\nContent Summary:")
            print(f"  Content ID: {metadata['content_id']}")
            print(f"  Type: drawing")
            print(f"  Caption: {metadata['caption']}")
            print(f"  Chunks: {len(chunks)}")
            print(f"  Indexed: ✅")
            print()
            return 0
        else:
            print("\n❌ INTEGRATION TEST FAILED: Indexing failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Test note
    result1 = test_note_full_pipeline()
    
    # Test drawing
    result2 = test_drawing_full_pipeline()
    
    # Overall result
    if result1 == 0 and result2 == 0:
        print("\n" + "="*70)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("="*70)
        print("\nReady for Phase 3: Frontend UI")
        print()
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

