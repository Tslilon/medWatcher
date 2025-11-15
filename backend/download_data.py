#!/usr/bin/env python3
"""
Download RAG data from Google Cloud Storage at startup
"""
import os
import subprocess
from pathlib import Path


def download_from_gcs():
    """Download necessary data files from GCS bucket"""
    
    bucket_name = "harrisons-rag-data-flingoos"
    
    # Create directories
    data_dir = Path("/app/data")
    static_dir = Path("/app/static")
    processed_dir = data_dir / "processed"
    chunks_dir = processed_dir / "chunks"
    independent_chunks_dir = processed_dir / "independent_chunks"
    independent_pdfs_dir = data_dir / "independant_pdfs"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    independent_chunks_dir.mkdir(parents=True, exist_ok=True)
    independent_pdfs_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Checking for RAG data...")
    
    # Check if data already exists (for local caching in Cloud Run)
    pdf_path = static_dir / "harrisons.pdf"
    chroma_path = data_dir / "chroma_db"
    
    if pdf_path.exists() and chroma_path.exists() and chunks_dir.exists() and len(list(chunks_dir.glob("*.json"))) > 500:
        print("✅ Data already exists locally")
        return
    
    print("📥 Downloading data from Google Cloud Storage...")
    
    # Download PDF
    if not pdf_path.exists():
        print("   Downloading harrisons.pdf...")
        subprocess.run([
            "gsutil", "-m", "cp",
            f"gs://{bucket_name}/harrisons.pdf",
            str(pdf_path)
        ], check=True)
        print(f"   ✅ PDF downloaded to {pdf_path}")
    
    # Download ChromaDB (optional - will be created if doesn't exist)
    if not chroma_path.exists():
        print("   Checking for chroma_db in GCS...")
        result = subprocess.run([
            "gsutil", "ls",
            f"gs://{bucket_name}/chroma_db/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Downloading chroma_db...")
            subprocess.run([
                "gsutil", "-m", "cp", "-r",
                f"gs://{bucket_name}/chroma_db",
                str(data_dir)
            ], check=True)
            
            # Fix permissions - make ChromaDB writable
            print("   Setting ChromaDB permissions...")
            subprocess.run([
                "chmod", "-R", "u+w",
                str(chroma_path)
            ], check=True)
            
            print(f"   ✅ ChromaDB downloaded to {chroma_path}")
        else:
            print("   ⚠️  No chroma_db found in GCS - will initialize fresh")
            chroma_path.mkdir(parents=True, exist_ok=True)
    
    # Download Harrison's chunks directory
    if not chunks_dir.exists() or len(list(chunks_dir.glob("*.json"))) < 500:
        print("   Downloading Harrison's chunks...")
        subprocess.run([
            "gsutil", "-m", "cp", "-r",
            f"gs://{bucket_name}/chunks",
            str(processed_dir)
        ], check=True)
        print(f"   ✅ Harrison's chunks downloaded to {chunks_dir}")
    
    # Download independent PDFs
    print("   Checking for independent PDFs...")
    result = subprocess.run([
        "gsutil", "ls",
        f"gs://{bucket_name}/independant_pdfs/"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   Downloading independent PDFs...")
        subprocess.run([
            "gsutil", "-m", "cp", "-r",
            f"gs://{bucket_name}/independant_pdfs/*",
            str(independent_pdfs_dir)
        ], check=True)
        print(f"   ✅ Independent PDFs downloaded to {independent_pdfs_dir}")
    else:
        print("   ℹ️  No independent PDFs found in GCS")
    
    # Download independent PDF chunks
    print("   Checking for independent PDF chunks...")
    result = subprocess.run([
        "gsutil", "ls",
        f"gs://{bucket_name}/processed/independent_chunks/"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   Downloading independent PDF chunks...")
        subprocess.run([
            "gsutil", "-m", "cp", "-r",
            f"gs://{bucket_name}/processed/independent_chunks/*",
            str(independent_chunks_dir)
        ], check=True)
        print(f"   ✅ Independent PDF chunks downloaded to {independent_chunks_dir}")
    else:
        print("   ℹ️  No independent PDF chunks found in GCS")
    
    # Download multimodal content directories (notes, images, drawings, audio)
    print("   Checking for multimodal content...")
    multimodal_types = [
        ("user_notes", "user_notes_chunks"),
        ("user_images", "user_images_chunks"),
        ("user_drawings", "user_drawings_chunks"),
        ("user_audio", "user_audio_chunks")
    ]
    
    for content_type, chunks_type in multimodal_types:
        # Create local directories
        content_dir = processed_dir / content_type
        chunks_dir_local = processed_dir / chunks_type
        content_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir_local.mkdir(parents=True, exist_ok=True)
        
        # Check if content exists in GCS
        result = subprocess.run([
            "gsutil", "ls",
            f"gs://{bucket_name}/processed/{chunks_type}/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   Downloading {content_type}...")
            # Download content files
            subprocess.run([
                "gsutil", "-m", "cp", "-r",
                f"gs://{bucket_name}/processed/{content_type}/*",
                str(content_dir)
            ], capture_output=True)  # Suppress errors if empty
            
            # Download chunks (including summary.json)
            subprocess.run([
                "gsutil", "-m", "cp", "-r",
                f"gs://{bucket_name}/processed/{chunks_type}/*",
                str(chunks_dir_local)
            ], check=True)
            print(f"   ✅ {content_type} downloaded")
        else:
            print(f"   ℹ️  No {content_type} found in GCS")
    
    print("✅ All RAG data ready!")


if __name__ == "__main__":
    try:
        download_from_gcs()
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        exit(1)

