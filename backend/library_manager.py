"""
Library Manager - CRUD operations for all content sources
"""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from models import ContentSource, HarrisonSource, IndependentPDFSource, PersonalNote, LibraryStats
from vector_store import ChromaVectorStore
import uuid

class LibraryManager:
    """Manage all content sources in the medWatcher system"""
    
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.data_dir = Path("../data")
        if not self.data_dir.exists():
            self.data_dir = Path("data")
        
        self.notes_dir = self.data_dir / "personal_notes"
        self.notes_chunks_dir = self.data_dir / "processed" / "personal_note_chunks"
        self.pdfs_dir = self.data_dir / "independant_pdfs"
        self.pdf_chunks_dir = self.data_dir / "processed" / "independent_chunks"
        self.harrison_chunks_dir = self.data_dir / "processed" / "chunks"
        
        # Create directories if they don't exist
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.notes_chunks_dir.mkdir(parents=True, exist_ok=True)
    
    def get_all_sources(self, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all content sources
        
        Args:
            source_type: Filter by type ('harrison', 'independent_pdf', 'personal_note', or None for all)
        
        Returns:
            List of content source dictionaries
        """
        sources = []
        
        # Get Harrison's (static reference)
        if source_type is None or source_type == "harrison":
            harrison_source = self._get_harrison_source()
            if harrison_source:
                sources.append(harrison_source)
        
        # Get independent PDFs
        if source_type is None or source_type == "independent_pdf":
            pdf_sources = self._get_pdf_sources()
            sources.extend(pdf_sources)
        
        # Get personal notes
        if source_type is None or source_type == "personal_note":
            note_sources = self._get_note_sources()
            sources.extend(note_sources)
        
        return sources
    
    def _get_harrison_source(self) -> Optional[Dict[str, Any]]:
        """Get Harrison's source information"""
        if not self.harrison_chunks_dir.exists():
            return None
        
        # Count chunks
        chunk_files = list(self.harrison_chunks_dir.glob("*.json"))
        if not chunk_files:
            return None
        
        # Load first chunk to get metadata
        with open(chunk_files[0], 'r') as f:
            sample_chunk = json.load(f)
        
        # Calculate total stats
        total_words = 0
        for chunk_file in chunk_files:
            with open(chunk_file, 'r') as f:
                chunk = json.load(f)
                total_words += chunk.get('word_count', 0)
        
        return {
            "id": "harrison_medical",
            "type": "harrison",
            "title": "Harrison's Principles of Internal Medicine (21st Edition)",
            "created_at": datetime(2022, 1, 1).isoformat(),  # Publication date
            "updated_at": datetime(2022, 1, 1).isoformat(),
            "word_count": total_words,
            "is_indexed": True,
            "total_chapters": len(chunk_files),
            "total_pages": 13299,
            "metadata": {
                "publisher": "McGraw Hill Education",
                "edition": "21st",
                "year": 2022
            }
        }
    
    def _get_pdf_sources(self) -> List[Dict[str, Any]]:
        """Get all independent PDF sources"""
        sources = []
        
        if not self.pdf_chunks_dir.exists():
            return sources
        
        # Group chunks by PDF
        pdf_chunks = {}
        for chunk_file in self.pdf_chunks_dir.glob("*.json"):
            if chunk_file.name == "summary.json":
                continue
            
            with open(chunk_file, 'r') as f:
                chunk = json.load(f)
            
            pdf_filename = chunk.get('pdf_filename')
            if not pdf_filename:
                continue
            
            if pdf_filename not in pdf_chunks:
                pdf_chunks[pdf_filename] = []
            pdf_chunks[pdf_filename].append(chunk)
        
        # Create source entry for each PDF
        for pdf_filename, chunks in pdf_chunks.items():
            first_chunk = chunks[0]
            
            # Get file stats
            pdf_path = self.pdfs_dir / pdf_filename
            file_size = pdf_path.stat().st_size if pdf_path.exists() else 0
            created_at = datetime.fromtimestamp(pdf_path.stat().st_ctime) if pdf_path.exists() else datetime.now()
            
            # Calculate total words
            total_words = sum(chunk.get('word_count', 0) for chunk in chunks)
            
            sources.append({
                "id": f"pdf_{pdf_filename}",
                "type": "independent_pdf",
                "title": first_chunk.get('pdf_name', pdf_filename),
                "created_at": created_at.isoformat(),
                "updated_at": created_at.isoformat(),
                "word_count": total_words,
                "is_indexed": True,
                "filename": pdf_filename,
                "pdf_path": str(pdf_path),
                "total_pages": first_chunk.get('total_pages', len(chunks) * 5),
                "file_size": file_size,
                "metadata": {
                    "chunks": len(chunks)
                }
            })
        
        return sources
    
    def _get_note_sources(self) -> List[Dict[str, Any]]:
        """Get all personal note sources"""
        sources = []
        
        if not self.notes_dir.exists():
            return sources
        
        for note_file in self.notes_dir.glob("*.json"):
            with open(note_file, 'r') as f:
                note_data = json.load(f)
            
            sources.append({
                "id": note_data['note_id'],
                "type": "personal_note",
                "title": note_data['title'],
                "created_at": note_data['created_at'],
                "updated_at": note_data['updated_at'],
                "word_count": note_data['word_count'],
                "is_indexed": note_data.get('is_indexed', False),
                "note_id": note_data['note_id'],
                "content": note_data['content'],
                "tags": note_data.get('tags', []),
                "linked_sources": note_data.get('linked_sources', []),
                "is_public": note_data.get('is_public', False),
                "metadata": note_data.get('metadata', {})
            })
        
        return sources
    
    def get_source_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific content source by ID"""
        all_sources = self.get_all_sources()
        for source in all_sources:
            if source['id'] == source_id:
                return source
        return None
    
    def delete_source(self, source_id: str) -> Dict[str, str]:
        """
        Delete a content source
        
        Args:
            source_id: ID of the source to delete
        
        Returns:
            Status dictionary
        """
        source = self.get_source_by_id(source_id)
        if not source:
            return {"status": "error", "message": "Source not found"}
        
        source_type = source['type']
        
        # Cannot delete Harrison's
        if source_type == "harrison":
            return {"status": "error", "message": "Cannot delete Harrison's textbook"}
        
        try:
            if source_type == "independent_pdf":
                self._delete_pdf_source(source)
            elif source_type == "personal_note":
                self._delete_note_source(source)
            
            return {"status": "success", "message": f"Deleted {source['title']}"}
        except Exception as e:
            return {"status": "error", "message": f"Error deleting source: {str(e)}"}
    
    def _delete_pdf_source(self, source: Dict[str, Any]):
        """Delete a PDF source"""
        pdf_filename = source['filename']
        
        # Delete PDF file
        pdf_path = self.pdfs_dir / pdf_filename
        if pdf_path.exists():
            pdf_path.unlink()
        
        # Delete chunks
        for chunk_file in self.pdf_chunks_dir.glob(f"*{pdf_filename}*.json"):
            chunk_file.unlink()
        
        # Remove from vector store
        self.vector_store.delete_by_metadata('pdf_filename', pdf_filename)
    
    def _delete_note_source(self, source: Dict[str, Any]):
        """Delete a personal note"""
        note_id = source['note_id']
        
        # Delete note file
        note_file = self.notes_dir / f"{note_id}.json"
        if note_file.exists():
            note_file.unlink()
        
        # Delete chunk
        chunk_file = self.notes_chunks_dir / f"{note_id}.json"
        if chunk_file.exists():
            chunk_file.unlink()
        
        # Remove from vector store
        self.vector_store.delete_by_id(note_id)
    
    def get_library_stats(self) -> LibraryStats:
        """Get statistics about the library"""
        sources = self.get_all_sources()
        
        harrison_count = sum(1 for s in sources if s['type'] == 'harrison')
        pdf_count = sum(1 for s in sources if s['type'] == 'independent_pdf')
        note_count = sum(1 for s in sources if s['type'] == 'personal_note')
        
        total_words = sum(s['word_count'] for s in sources)
        total_indexed = self.vector_store.count_documents()
        
        # Calculate storage used
        storage_mb = 0.0
        if self.pdfs_dir.exists():
            storage_mb += sum(f.stat().st_size for f in self.pdfs_dir.glob("*.pdf")) / (1024 * 1024)
        if self.notes_dir.exists():
            storage_mb += sum(f.stat().st_size for f in self.notes_dir.glob("*.json")) / (1024 * 1024)
        
        # Get last updated
        last_updated = datetime.now()
        if sources:
            dates = [datetime.fromisoformat(s['updated_at']) for s in sources]
            last_updated = max(dates)
        
        return LibraryStats(
            total_sources=len(sources),
            harrison_chapters=harrison_count,
            independent_pdfs=pdf_count,
            personal_notes=note_count,
            total_words=total_words,
            total_indexed=total_indexed,
            last_updated=last_updated,
            storage_used_mb=round(storage_mb, 2)
        )
    
    def search_library(self, query: str, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search library sources by title or content
        
        Args:
            query: Search query
            source_type: Filter by type
        
        Returns:
            List of matching sources
        """
        sources = self.get_all_sources(source_type)
        query_lower = query.lower()
        
        matching = []
        for source in sources:
            # Search in title
            if query_lower in source['title'].lower():
                matching.append(source)
                continue
            
            # Search in content for notes
            if source['type'] == 'personal_note':
                if query_lower in source['content'].lower():
                    matching.append(source)
                    continue
            
            # Search in tags for notes
            if source['type'] == 'personal_note':
                if any(query_lower in tag.lower() for tag in source.get('tags', [])):
                    matching.append(source)
        
        return matching

