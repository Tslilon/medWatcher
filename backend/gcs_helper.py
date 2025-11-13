"""
Google Cloud Storage Helper
Handles all GCS operations for PDFs, chunks, and ChromaDB
"""
import subprocess
from pathlib import Path
from typing import Optional
import os

GCS_BUCKET = "harrisons-rag-data-flingoos"

def upload_to_gcs(local_path: str, gcs_path: str) -> bool:
    """
    Upload a file to GCS
    
    Args:
        local_path: Local file path
        gcs_path: GCS path (e.g., "independant_pdfs/file.pdf")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["gsutil", "cp", local_path, f"gs://{GCS_BUCKET}/{gcs_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ GCS upload error: {e}")
        return False

def upload_directory_to_gcs(local_dir: str, gcs_dir: str) -> bool:
    """
    Upload a directory to GCS recursively
    
    Args:
        local_dir: Local directory path
        gcs_dir: GCS directory path
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use cp -r instead of rsync to avoid Python compatibility issues on macOS
        # -m for parallel, -r for recursive
        cmd = ["gsutil", "-m", "cp", "-r", local_dir, f"gs://{GCS_BUCKET}/{gcs_dir}/"]
        result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.STDOUT)
        
        # Check if successful (exit code 0 or files already up-to-date)
        if result.returncode == 0 or "already up-to-date" in result.stdout:
            return True
        else:
            print(f"❌ GCS directory upload stderr: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ GCS directory upload error: {e}")
        return False

def delete_from_gcs(gcs_path: str) -> bool:
    """
    Delete a file from GCS
    
    Args:
        gcs_path: GCS path (e.g., "independant_pdfs/file.pdf")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["gsutil", "rm", f"gs://{GCS_BUCKET}/{gcs_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ GCS delete error: {e}")
        return False

def delete_directory_from_gcs(gcs_dir: str, pattern: str = "*") -> bool:
    """
    Delete files matching pattern from GCS directory
    
    Args:
        gcs_dir: GCS directory path
        pattern: File pattern to match (default: all files)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["gsutil", "-m", "rm", f"gs://{GCS_BUCKET}/{gcs_dir}/{pattern}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ GCS directory delete error: {e}")
        return False

def check_gcs_available() -> bool:
    """Check if gsutil is available"""
    try:
        result = subprocess.run(["gsutil", "version"], capture_output=True)
        return result.returncode == 0
    except:
        return False

