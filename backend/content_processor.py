"""
Content Processor for Multimodal Content
Handles images, audio, drawings, and text notes

Features:
- Image: OCR, format conversion (HEIC → JPEG)
- Audio: Transcription (Whisper), format conversion (→ MP3)
- Drawing: Optional OCR
- Note: Text chunking
"""
import os
import re
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from uuid import uuid4
from datetime import datetime

# Image processing
try:
    from PIL import Image
    import pytesseract
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️ PIL/pytesseract not available - OCR disabled")

# HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_AVAILABLE = True
except ImportError:
    HEIF_AVAILABLE = False
    print("⚠️ pillow-heif not available - HEIC support disabled")

# Audio processing
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("⚠️ pydub not available - audio conversion disabled")


class ContentProcessor:
    """Process multimodal content for RAG indexing"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize content processor
        
        Args:
            data_dir: Base data directory (default: ../data or /app/data)
        """
        if data_dir is None:
            # Auto-detect: Cloud Run vs local
            if Path("/app/data").exists():
                self.data_dir = Path("/app/data")
            else:
                self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # Content directories
        self.images_dir = self.data_dir / "processed/user_images"
        self.images_chunks_dir = self.data_dir / "processed/user_images_chunks"
        
        self.notes_dir = self.data_dir / "processed/user_notes"
        self.notes_chunks_dir = self.data_dir / "processed/user_notes_chunks"
        
        self.drawings_dir = self.data_dir / "processed/user_drawings"
        self.drawings_chunks_dir = self.data_dir / "processed/user_drawings_chunks"
        
        self.audio_dir = self.data_dir / "processed/user_audio"
        self.audio_chunks_dir = self.data_dir / "processed/user_audio_chunks"
        
        # Ensure directories exist
        for dir_path in [
            self.images_dir, self.images_chunks_dir,
            self.notes_dir, self.notes_chunks_dir,
            self.drawings_dir, self.drawings_chunks_dir,
            self.audio_dir, self.audio_chunks_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ ContentProcessor initialized (data_dir: {self.data_dir})")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text[:50]
    
    def _generate_content_id(self, content_type: str) -> str:
        """Generate unique content ID"""
        timestamp = int(time.time())
        random_hex = uuid4().hex[:8]
        return f"{content_type}_{timestamp}_{random_hex}"
    
    def _create_preview(self, text: str, max_length: int = 200) -> str:
        """Create preview from text"""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."
    
    def _chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    # ========================================================================
    # Image Processing
    # ========================================================================
    
    def process_image(
        self,
        image_data: bytes,
        filename: str,
        caption: Optional[str] = None,
        tags: Optional[List[str]] = None,
        perform_ocr: bool = True
    ) -> Tuple[Dict, List[Dict], str]:
        """
        Process an image file
        
        Args:
            image_data: Raw image bytes
            filename: Original filename
            caption: Optional caption
            tags: Optional tags
            perform_ocr: Whether to perform OCR
            
        Returns:
            (metadata, chunks, saved_filename)
        """
        print(f"📷 Processing image: {filename}")
        
        if not PILLOW_AVAILABLE:
            raise RuntimeError("PIL not available - cannot process images")
        
        # Generate ID and filename
        content_id = self._generate_content_id("image")
        original_ext = filename.split('.')[-1].lower()
        
        # Auto-detect format, convert HEIC to JPEG
        if original_ext in ['heic', 'heif']:
            if not HEIF_AVAILABLE:
                raise RuntimeError("HEIC support not available - install pillow-heif")
            saved_ext = 'jpg'
            print("  🔄 Converting HEIC to JPEG...")
        else:
            saved_ext = original_ext if original_ext in ['jpg', 'jpeg', 'png', 'webp'] else 'jpg'
        
        saved_filename = f"{content_id}.{saved_ext}"
        saved_path = self.images_dir / saved_filename
        
        # Save image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if saving as JPEG
        if saved_ext in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        img.save(saved_path, quality=85, optimize=True)
        file_size = saved_path.stat().st_size
        
        print(f"  ✅ Saved: {saved_filename} ({file_size} bytes)")
        
        # Perform OCR
        ocr_text = ""
        if perform_ocr:
            try:
                print("  🔍 Performing OCR...")
                ocr_text = pytesseract.image_to_string(img)
                ocr_text = ocr_text.strip()
                print(f"  ✅ OCR complete ({len(ocr_text)} chars)")
            except Exception as e:
                print(f"  ⚠️ OCR failed: {e}")
        
        # Combine caption and OCR text
        full_text = ""
        if caption:
            full_text += caption + "\n\n"
        if ocr_text:
            full_text += ocr_text
        
        if not full_text.strip():
            full_text = f"Image: {filename}"
        
        # Create chunks
        text_chunks = self._chunk_text(full_text, chunk_size=500)
        chunks = []
        
        for i, chunk_text in enumerate(text_chunks, 1):
            chunk = {
                "chunk_id": f"image_{self._slugify(content_id)}_chunk{i}",
                "content_id": content_id,
                "content_type": "image",
                "text": chunk_text,
                "preview": self._create_preview(chunk_text),
                "metadata": {
                    "title": caption or filename,
                    "filename": saved_filename,
                    "caption": caption,
                    "tags": tags or [],
                    "has_ocr": bool(ocr_text),
                    "original_format": original_ext,
                    "file_size": file_size
                }
            }
            chunks.append(chunk)
        
        # Metadata
        metadata = {
            "content_id": content_id,
            "content_type": "image",
            "title": caption or filename,
            "filename": saved_filename,
            "caption": caption,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "file_size": file_size,
            "has_ocr": bool(ocr_text),
            "ocr_text": ocr_text if ocr_text else None,
            "original_format": original_ext,
            "chunks": len(chunks)
        }
        
        print(f"  ✅ Created {len(chunks)} chunk(s)")
        
        return metadata, chunks, saved_filename
    
    # ========================================================================
    # Audio Processing
    # ========================================================================
    
    def process_audio(
        self,
        audio_data: bytes,
        filename: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        transcribe: bool = True
    ) -> Tuple[Dict, List[Dict], str]:
        """
        Process an audio file
        
        Args:
            audio_data: Raw audio bytes
            filename: Original filename
            title: Optional title
            description: Optional description
            tags: Optional tags
            transcribe: Whether to transcribe (requires OpenAI API)
            
        Returns:
            (metadata, chunks, saved_filename)
        """
        print(f"🎤 Processing audio: {filename}")
        
        if not PYDUB_AVAILABLE:
            raise RuntimeError("pydub not available - cannot process audio")
        
        # Generate ID
        content_id = self._generate_content_id("audio")
        original_ext = filename.split('.')[-1].lower()
        
        # Save original temporarily
        temp_path = Path(f"/tmp/{content_id}_original.{original_ext}")
        temp_path.write_bytes(audio_data)
        
        # Convert to MP3
        print(f"  🔄 Converting {original_ext.upper()} to MP3...")
        
        try:
            # Load audio (supports: webm, mp4, m4a, aac, caf, wav, ogg)
            if original_ext in ['webm', 'mp4', 'm4a', 'aac', 'caf', 'wav', 'ogg']:
                audio = AudioSegment.from_file(str(temp_path), format=original_ext)
            else:
                # Try auto-detect
                audio = AudioSegment.from_file(str(temp_path))
            
            # Get duration
            duration_seconds = len(audio) / 1000.0
            
            # Export as MP3
            saved_filename = f"{content_id}.mp3"
            saved_path = self.audio_dir / saved_filename
            audio.export(str(saved_path), format='mp3', bitrate='128k')
            
            file_size = saved_path.stat().st_size
            print(f"  ✅ Converted to MP3: {saved_filename} ({duration_seconds:.1f}s, {file_size} bytes)")
            
        except Exception as e:
            print(f"  ⚠️ Conversion failed: {e}")
            # Use original file
            saved_filename = f"{content_id}.{original_ext}"
            saved_path = self.audio_dir / saved_filename
            saved_path.write_bytes(audio_data)
            file_size = len(audio_data)
            duration_seconds = 0
        
        # Transcribe using OpenAI Whisper API
        transcription = ""
        if transcribe:
            try:
                print("  🎙️ Transcribing audio with Whisper API...")
                from openai import OpenAI
                import os
                
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    print("  ⚠️  No OpenAI API key found - skipping transcription")
                else:
                    client = OpenAI(api_key=api_key)
                    
                    # Open the audio file for transcription
                    # Add medical context prompt for better accuracy
                    medical_prompt = (
                        "This is a medical recording made by a doctor in the hospital emergency room. "
                        "The recording contains medical terminology, patient notes, clinical observations, "
                        "diagnoses, treatment plans, and medical procedures. "
                        "Common terms include medication names, anatomical terms, lab values, and medical abbreviations."
                    )
                    
                    with open(temp_path, 'rb') as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            response_format="text",
                            prompt=medical_prompt  # Provide medical context
                        )
                        transcription = transcript.strip()
                        
                    if transcription:
                        print(f"  ✅ Transcribed: {len(transcription)} characters")
                    else:
                        print("  ⚠️  Transcription returned empty")
                        
            except Exception as e:
                print(f"  ⚠️  Transcription failed: {e}")
                transcription = ""
        
        # Combine title + description + transcription
        full_text = ""
        if title:
            full_text += title + "\n\n"
        if description:
            full_text += description + "\n\n"
        if transcription:
            full_text += transcription
        
        if not full_text.strip():
            full_text = f"Audio: {filename}"
        
        # Create chunks
        text_chunks = self._chunk_text(full_text, chunk_size=500)
        chunks = []
        
        for i, chunk_text in enumerate(text_chunks, 1):
            chunk = {
                "chunk_id": f"audio_{self._slugify(content_id)}_chunk{i}",
                "content_id": content_id,
                "content_type": "audio",
                "text": chunk_text,
                "preview": self._create_preview(chunk_text),
                "metadata": {
                    "title": title or filename,
                    "filename": saved_filename,
                    "description": description,
                    "tags": tags or [],
                    "duration_seconds": duration_seconds,
                    "has_transcription": bool(transcription),
                    "original_format": original_ext,
                    "file_size": file_size
                }
            }
            chunks.append(chunk)
        
        # Metadata
        metadata = {
            "content_id": content_id,
            "content_type": "audio",
            "title": title or filename,
            "filename": saved_filename,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "file_size": file_size,
            "duration_seconds": duration_seconds,
            "has_transcription": bool(transcription),
            "transcription": transcription if transcription else None,
            "original_format": original_ext,
            "chunks": len(chunks)
        }
        
        print(f"  ✅ Created {len(chunks)} chunk(s)")
        
        # Cleanup temp file
        if temp_path.exists():
            temp_path.unlink()
        
        return metadata, chunks, saved_filename
    
    # ========================================================================
    # Drawing Processing
    # ========================================================================
    
    def process_drawing(
        self,
        drawing_data: bytes,
        caption: Optional[str] = None,
        tags: Optional[List[str]] = None,
        perform_ocr: bool = False
    ) -> Tuple[Dict, List[Dict], str]:
        """
        Process a canvas drawing (PNG)
        
        Args:
            drawing_data: Raw PNG bytes
            caption: Optional caption
            tags: Optional tags
            perform_ocr: Whether to perform OCR
            
        Returns:
            (metadata, chunks, saved_filename)
        """
        print(f"✏️ Processing drawing")
        
        # Generate ID and save
        content_id = self._generate_content_id("drawing")
        saved_filename = f"{content_id}.png"
        saved_path = self.drawings_dir / saved_filename
        saved_path.write_bytes(drawing_data)
        
        file_size = len(drawing_data)
        print(f"  ✅ Saved: {saved_filename} ({file_size} bytes)")
        
        # Optional OCR
        ocr_text = ""
        if perform_ocr and PILLOW_AVAILABLE:
            try:
                print("  🔍 Performing OCR...")
                import io
                img = Image.open(io.BytesIO(drawing_data))
                ocr_text = pytesseract.image_to_string(img).strip()
                print(f"  ✅ OCR complete ({len(ocr_text)} chars)")
            except Exception as e:
                print(f"  ⚠️ OCR failed: {e}")
        
        # Combine caption and OCR
        full_text = ""
        if caption:
            full_text += caption + "\n\n"
        if ocr_text:
            full_text += ocr_text
        
        if not full_text.strip():
            full_text = f"Drawing: {saved_filename}"
        
        # Create chunks
        text_chunks = self._chunk_text(full_text, chunk_size=500)
        chunks = []
        
        for i, chunk_text in enumerate(text_chunks, 1):
            chunk = {
                "chunk_id": f"drawing_{self._slugify(content_id)}_chunk{i}",
                "content_id": content_id,
                "content_type": "drawing",
                "text": chunk_text,
                "preview": self._create_preview(chunk_text),
                "metadata": {
                    "title": caption or "Drawing",
                    "filename": saved_filename,
                    "caption": caption,
                    "tags": tags or [],
                    "has_ocr": bool(ocr_text),
                    "file_size": file_size
                }
            }
            chunks.append(chunk)
        
        # Metadata
        metadata = {
            "content_id": content_id,
            "content_type": "drawing",
            "title": caption or "Drawing",
            "filename": saved_filename,
            "caption": caption,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "file_size": file_size,
            "has_ocr": bool(ocr_text),
            "ocr_text": ocr_text if ocr_text else None,
            "chunks": len(chunks)
        }
        
        print(f"  ✅ Created {len(chunks)} chunk(s)")
        
        return metadata, chunks, saved_filename
    
    # ========================================================================
    # Note Processing
    # ========================================================================
    
    def process_note(
        self,
        text_content: str,
        title: str,
        tags: Optional[List[str]] = None,
        is_markdown: bool = False
    ) -> Tuple[Dict, List[Dict], str]:
        """
        Process a text note
        
        Args:
            text_content: Note text
            title: Note title
            tags: Optional tags
            is_markdown: Whether content is markdown
            
        Returns:
            (metadata, chunks, saved_filename)
        """
        print(f"📝 Processing note: {title}")
        
        # Generate ID and save
        content_id = self._generate_content_id("note")
        ext = 'md' if is_markdown else 'txt'
        saved_filename = f"{content_id}.{ext}"
        saved_path = self.notes_dir / saved_filename
        saved_path.write_text(text_content, encoding='utf-8')
        
        file_size = len(text_content.encode('utf-8'))
        word_count = len(text_content.split())
        print(f"  ✅ Saved: {saved_filename} ({word_count} words)")
        
        # Create chunks
        text_chunks = self._chunk_text(text_content, chunk_size=1000)
        chunks = []
        
        for i, chunk_text in enumerate(text_chunks, 1):
            chunk = {
                "chunk_id": f"note_{self._slugify(content_id)}_chunk{i}",
                "content_id": content_id,
                "content_type": "note",
                "text": chunk_text,
                "preview": self._create_preview(chunk_text),
                "metadata": {
                    "title": title,
                    "filename": saved_filename,
                    "tags": tags or [],
                    "word_count": word_count,
                    "is_markdown": is_markdown,
                    "file_size": file_size
                }
            }
            chunks.append(chunk)
        
        # Metadata
        metadata = {
            "content_id": content_id,
            "content_type": "note",
            "title": title,
            "filename": saved_filename,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "file_size": file_size,
            "word_count": word_count,
            "is_markdown": is_markdown,
            "chunks": len(chunks)
        }
        
        print(f"  ✅ Created {len(chunks)} chunk(s)")
        
        return metadata, chunks, saved_filename


# Add missing import
import io

