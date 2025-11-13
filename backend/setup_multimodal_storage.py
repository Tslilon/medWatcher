"""
Setup script for multimodal content storage on GCS
Creates all necessary directories and initializes summary.json files

Run with: python setup_multimodal_storage.py
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

GCS_BUCKET = "harrisons-rag-data-flingoos"

# Directory structure to create
DIRECTORIES = [
    "processed/user_images",
    "processed/user_images_chunks",
    "processed/user_notes",
    "processed/user_notes_chunks",
    "processed/user_drawings",
    "processed/user_drawings_chunks",
    "processed/user_audio",
    "processed/user_audio_chunks",
]

# Summary.json templates
SUMMARY_TEMPLATES = {
    "user_images_chunks": {
        "total_images": 0,
        "total_chunks": 0,
        "images": []
    },
    "user_notes_chunks": {
        "total_notes": 0,
        "total_chunks": 0,
        "notes": []
    },
    "user_drawings_chunks": {
        "total_drawings": 0,
        "total_chunks": 0,
        "drawings": []
    },
    "user_audio_chunks": {
        "total_audio": 0,
        "total_chunks": 0,
        "audio": []
    }
}

def check_gsutil():
    """Check if gsutil is installed"""
    try:
        result = subprocess.run(
            ["gsutil", "version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def create_gcs_directory(directory: str):
    """Create a directory on GCS by uploading a placeholder file"""
    print(f"  Creating: gs://{GCS_BUCKET}/{directory}/")
    
    # Create a temporary placeholder file
    placeholder = Path("/tmp/.keep")
    placeholder.write_text("# This file ensures the directory exists")
    
    # Upload to GCS
    cmd = [
        "gsutil",
        "cp",
        str(placeholder),
        f"gs://{GCS_BUCKET}/{directory}/.keep"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"    ✅ Created")
        return True
    else:
        print(f"    ❌ Failed: {result.stderr}")
        return False

def create_summary_json(chunks_dir: str, template: dict):
    """Create initial summary.json file"""
    print(f"  Creating summary.json in: {chunks_dir}/")
    
    # Create temporary summary file
    summary_path = Path("/tmp/summary.json")
    summary_path.write_text(json.dumps(template, indent=2))
    
    # Upload to GCS
    cmd = [
        "gsutil",
        "cp",
        str(summary_path),
        f"gs://{GCS_BUCKET}/processed/{chunks_dir}/summary.json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"    ✅ Created summary.json")
        return True
    else:
        print(f"    ❌ Failed: {result.stderr}")
        return False

def verify_directories():
    """Verify all directories exist"""
    print("\n📋 Verifying directory structure...")
    
    cmd = [
        "gsutil",
        "ls",
        f"gs://{GCS_BUCKET}/processed/"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ Current GCS structure:")
        print(result.stdout)
        return True
    else:
        print(f"\n❌ Verification failed: {result.stderr}")
        return False

def setup_local_directories():
    """Create local directories for development/container"""
    print("\n📁 Creating local directory structure...")
    
    base_path = Path("../data/processed")
    
    local_dirs = [
        "user_images",
        "user_images_chunks",
        "user_notes",
        "user_notes_chunks",
        "user_drawings",
        "user_drawings_chunks",
        "user_audio",
        "user_audio_chunks",
    ]
    
    for dir_name in local_dirs:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")
    
    # Create local summary.json files
    for chunks_dir, template in SUMMARY_TEMPLATES.items():
        summary_path = base_path / chunks_dir / "summary.json"
        summary_path.write_text(json.dumps(template, indent=2))
        print(f"  ✅ Created: {summary_path}")
    
    print("\n✅ Local directories ready!")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🗄️  MULTIMODAL CONTENT STORAGE SETUP")
    print("="*70 + "\n")
    
    # Check prerequisites
    print("1️⃣  Checking prerequisites...")
    if not check_gsutil():
        print("❌ gsutil not found! Please install Google Cloud SDK")
        exit(1)
    print("  ✅ gsutil found")
    
    # Create GCS directories
    print("\n2️⃣  Creating GCS directories...")
    success_count = 0
    for directory in DIRECTORIES:
        if create_gcs_directory(directory):
            success_count += 1
    
    print(f"\n  Created {success_count}/{len(DIRECTORIES)} directories")
    
    # Create summary.json files
    print("\n3️⃣  Creating summary.json files...")
    for chunks_dir, template in SUMMARY_TEMPLATES.items():
        create_summary_json(chunks_dir, template)
    
    # Verify
    verify_directories()
    
    # Setup local directories
    setup_local_directories()
    
    print("\n" + "="*70)
    print("✅ STORAGE SETUP COMPLETE!")
    print("="*70)
    print("\nReady for multimodal content:")
    print("  📷 Images  → gs://{}/processed/user_images/".format(GCS_BUCKET))
    print("  📝 Notes   → gs://{}/processed/user_notes/".format(GCS_BUCKET))
    print("  ✏️  Drawings → gs://{}/processed/user_drawings/".format(GCS_BUCKET))
    print("  🎤 Audio   → gs://{}/processed/user_audio/".format(GCS_BUCKET))
    print("\n")

