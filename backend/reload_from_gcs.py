"""
Reload ChromaDB from GCS on-demand
Used by deployed server to pick up new files without redeploying
"""
import subprocess
from pathlib import Path
import os

def reload_chromadb_from_gcs():
    """
    Download fresh ChromaDB from GCS
    Returns True if successful, False otherwise
    """
    try:
        print("🔄 Reloading ChromaDB from GCS...")
        
        # Determine if we're on Cloud Run or local
        is_cloud = Path("/app/data").exists()
        data_dir = Path("/app/data") if is_cloud else Path("../data")
        
        chroma_dir = data_dir / "chroma_db"
        
        # Remove old ChromaDB
        if chroma_dir.exists():
            import shutil
            shutil.rmtree(chroma_dir)
            print("   🗑️ Removed old ChromaDB")
        
        # Create fresh directory
        chroma_dir.mkdir(parents=True, exist_ok=True)
        
        # Download fresh ChromaDB from GCS (use rsync for cache-busting)
        bucket = "harrisons-rag-data-flingoos"
        # rsync with -d (delete extra files) ensures exact sync, no caching
        cmd = ["gsutil", "-m", "rsync", "-r", "-d", f"gs://{bucket}/chroma_db", str(chroma_dir)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Verify download by checking the main DB file
            db_file = chroma_dir / "chroma.sqlite3"
            if db_file.exists():
                size_mb = db_file.stat().st_size / (1024 * 1024)
                print(f"   ✅ Downloaded fresh ChromaDB from GCS ({size_mb:.1f}MB)")
            else:
                print(f"   ✅ Downloaded fresh ChromaDB from GCS")
            return True
        else:
            print(f"   ❌ Failed to download: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error reloading ChromaDB: {e}")
        return False

def trigger_vector_store_reload():
    """
    Reload the vector store singleton with fresh ChromaDB
    """
    try:
        import hierarchical_search
        from hierarchical_search import get_search_engine
        
        # Reset singleton
        hierarchical_search._search_engine = None
        
        # Create fresh instance (loads from disk)
        search_engine = get_search_engine()
        
        count = search_engine.vector_store.count_documents()
        print(f"   ✅ Vector store reloaded with {count} documents")
        
        return True
    except Exception as e:
        print(f"❌ Error reloading vector store: {e}")
        return False

def full_reload():
    """
    Complete reload: Download from GCS + Reload vector store
    """
    print("\n" + "="*70)
    print("🔄 FULL RELOAD FROM GCS")
    print("="*70)
    
    # Step 1: Download ChromaDB
    if not reload_chromadb_from_gcs():
        return False
    
    # Step 2: Reload vector store
    if not trigger_vector_store_reload():
        return False
    
    print("="*70)
    print("✅ RELOAD COMPLETE!")
    print("="*70 + "\n")
    
    return True

