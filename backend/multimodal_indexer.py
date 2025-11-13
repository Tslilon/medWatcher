"""
Multimodal Content Indexer
Handles saving multimodal content chunks to ChromaDB and GCS
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
from vector_store import ChromaVectorStore, EmbeddingGenerator
from gcs_helper import upload_to_gcs, upload_directory_to_gcs


class MultimodalIndexer:
    """Index multimodal content into ChromaDB and GCS"""
    
    def __init__(self, data_dir: Path = None):
        """Initialize indexer with vector store and embedding generator"""
        if data_dir is None:
            # Auto-detect: Cloud Run vs local
            if Path("/app/data").exists():
                self.data_dir = Path("/app/data")
            else:
                self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # Initialize vector store and embedding generator
        self.vector_store = ChromaVectorStore()
        self.embedding_generator = EmbeddingGenerator()
        
        print(f"✅ MultimodalIndexer initialized (data_dir: {self.data_dir})")
    
    def _get_chunks_dir(self, content_type: str) -> Path:
        """Get the chunks directory for a content type"""
        type_map = {
            "image": "user_images_chunks",
            "audio": "user_audio_chunks",
            "drawing": "user_drawings_chunks",
            "note": "user_notes_chunks"
        }
        
        if content_type not in type_map:
            raise ValueError(f"Invalid content_type: {content_type}")
        
        return self.data_dir / "processed" / type_map[content_type]
    
    def _get_content_dir(self, content_type: str) -> Path:
        """Get the content directory for a content type"""
        type_map = {
            "image": "user_images",
            "audio": "user_audio",
            "drawing": "user_drawings",
            "note": "user_notes"
        }
        
        if content_type not in type_map:
            raise ValueError(f"Invalid content_type: {content_type}")
        
        return self.data_dir / "processed" / type_map[content_type]
    
    def _get_gcs_paths(self, content_type: str) -> Tuple[str, str]:
        """Get GCS paths for content and chunks"""
        type_map = {
            "image": ("processed/user_images", "processed/user_images_chunks"),
            "audio": ("processed/user_audio", "processed/user_audio_chunks"),
            "drawing": ("processed/user_drawings", "processed/user_drawings_chunks"),
            "note": ("processed/user_notes", "processed/user_notes_chunks")
        }
        
        return type_map[content_type]
    
    def save_chunks_to_disk(
        self,
        chunks: List[Dict],
        content_type: str
    ) -> bool:
        """
        Save chunks to disk as JSON files
        
        Args:
            chunks: List of chunk dictionaries
            content_type: Type of content (image, audio, drawing, note)
            
        Returns:
            True if successful
        """
        try:
            chunks_dir = self._get_chunks_dir(content_type)
            chunks_dir.mkdir(parents=True, exist_ok=True)
            
            # Save each chunk as a separate JSON file
            for chunk in chunks:
                chunk_id = chunk['chunk_id']
                chunk_file = chunks_dir / f"{chunk_id}.json"
                
                with open(chunk_file, 'w') as f:
                    json.dump(chunk, f, indent=2)
            
            print(f"   ✅ Saved {len(chunks)} chunk(s) to disk: {chunks_dir.name}/")
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving chunks to disk: {e}")
            return False
    
    def index_chunks_to_chromadb(
        self,
        chunks: List[Dict],
        content_type: str
    ) -> bool:
        """
        Index chunks into ChromaDB with embeddings
        
        Args:
            chunks: List of chunk dictionaries
            content_type: Type of content
            
        Returns:
            True if successful
        """
        try:
            print(f"   🔍 Generating embeddings for {len(chunks)} chunk(s)...")
            
            # Extract texts for embedding
            texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_generator.generate_embeddings_batch(texts)
            
            # Prepare documents for ChromaDB
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    'id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'metadata': {
                        'content_id': chunk['content_id'],
                        'content_type': chunk['content_type'],
                        'title': chunk['metadata']['title'],
                        'filename': chunk['metadata']['filename'],
                        'source': 'user_content',  # Distinguish from Harrison's
                        # Add type-specific metadata
                        **{k: str(v) if not isinstance(v, str) else v 
                           for k, v in chunk['metadata'].items() 
                           if k not in ['title', 'filename']}
                    }
                }
                documents.append(doc)
            
            # Add to ChromaDB
            self.vector_store.add_documents(documents, embeddings)
            
            print(f"   ✅ Indexed {len(chunks)} chunk(s) into ChromaDB")
            return True
            
        except Exception as e:
            print(f"   ❌ Error indexing to ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_summary_json(
        self,
        metadata: Dict,
        chunks: List[Dict],
        content_type: str
    ) -> bool:
        """
        Update summary.json with new content metadata
        
        Args:
            metadata: Content metadata
            chunks: List of chunks
            content_type: Type of content
            
        Returns:
            True if successful
        """
        try:
            chunks_dir = self._get_chunks_dir(content_type)
            summary_file = chunks_dir / "summary.json"
            
            # Load existing summary or create new
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
            else:
                summary = {
                    'content_type': content_type,
                    'total_items': 0,
                    'total_chunks': 0,
                    'items': []
                }
            
            # Add new item
            summary['items'].append({
                'content_id': metadata['content_id'],
                'title': metadata['title'],
                'filename': metadata['filename'],
                'created_at': metadata['created_at'],
                'chunks': len(chunks),
                'file_size': metadata['file_size'],
                'tags': metadata.get('tags', [])
            })
            
            # Update totals
            summary['total_items'] = len(summary['items'])
            summary['total_chunks'] = sum(item['chunks'] for item in summary['items'])
            
            # Save summary
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"   ✅ Updated summary.json ({summary['total_items']} items, {summary['total_chunks']} chunks)")
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating summary.json: {e}")
            return False
    
    def upload_to_gcs(
        self,
        content_type: str,
        filename: str
    ) -> bool:
        """
        Upload content file and chunks to GCS
        
        Args:
            content_type: Type of content
            filename: Filename of the content
            
        Returns:
            True if successful
        """
        try:
            from gcs_helper import check_gcs_available
            
            if not check_gcs_available():
                print(f"   ⚠️ GCS not available, skipping upload")
                return False
            
            content_gcs_path, chunks_gcs_path = self._get_gcs_paths(content_type)
            
            # Upload content file
            content_dir = self._get_content_dir(content_type)
            content_file = content_dir / filename
            
            if content_file.exists():
                if upload_to_gcs(str(content_file), f"{content_gcs_path}/{filename}"):
                    print(f"   ✅ Uploaded content to GCS: {content_gcs_path}/{filename}")
                else:
                    print(f"   ⚠️ Failed to upload content to GCS")
            
            # Upload chunks directory
            chunks_dir = self._get_chunks_dir(content_type)
            if upload_directory_to_gcs(str(chunks_dir), chunks_gcs_path):
                print(f"   ✅ Uploaded chunks to GCS: {chunks_gcs_path}/")
            else:
                print(f"   ⚠️ Failed to upload chunks to GCS")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error uploading to GCS: {e}")
            return False
    
    def upload_chromadb_to_gcs(self) -> bool:
        """
        Upload ChromaDB to GCS (for multi-container sync)
        Uses threading to avoid HTTP timeout
        
        Returns:
            True if successful
        """
        try:
            import threading
            from gcs_helper import check_gcs_available
            
            if not check_gcs_available():
                print(f"   ⚠️ GCS not available, skipping ChromaDB upload")
                return False
            
            print(f"   ☁️ Uploading ChromaDB to GCS (for other containers)...")
            print(f"      ⏳ This may take 30-60 seconds for large ChromaDB...")
            
            # Find ChromaDB directory
            if Path("/app/data/chroma_db").exists():
                chroma_dir = Path("/app/data/chroma_db")
            else:
                chroma_dir = self.data_dir / "chroma_db"
            
            # BLOCKING upload (wait for completion)
            upload_success = [False]
            
            def upload_chromadb():
                upload_success[0] = upload_directory_to_gcs(str(chroma_dir), "chroma_db")
            
            upload_thread = threading.Thread(target=upload_chromadb)
            upload_thread.daemon = False  # NOT daemon - we want to wait
            upload_thread.start()
            upload_thread.join(timeout=90)  # 90 second timeout
            
            if upload_thread.is_alive():
                print(f"      ⚠️ ChromaDB upload taking longer than 90 seconds!")
                print(f"      ⚠️ Continuing in background, but refresh may not work immediately")
                return False
            elif upload_success[0]:
                print(f"      ✅ ChromaDB uploaded to GCS!")
                
                # Create version marker
                version_marker = f"{int(time.time())}"
                version_file = chroma_dir.parent / "version.txt"
                version_file.write_text(version_marker)
                upload_to_gcs(str(version_file), "version.txt")
                print(f"      ✅ Version marker updated: {version_marker}")
                
                return True
            else:
                print(f"      ⚠️ ChromaDB upload failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error uploading ChromaDB to GCS: {e}")
            return False
    
    def index_content(
        self,
        metadata: Dict,
        chunks: List[Dict],
        content_type: str,
        filename: str
    ) -> bool:
        """
        Complete indexing pipeline: save, index, upload
        
        Args:
            metadata: Content metadata
            chunks: List of chunks
            content_type: Type of content
            filename: Content filename
            
        Returns:
            True if successful
        """
        print(f"\n🔄 Indexing {content_type} content...")
        
        # Step 1: Save chunks to disk
        if not self.save_chunks_to_disk(chunks, content_type):
            return False
        
        # Step 2: Update summary.json
        if not self.update_summary_json(metadata, chunks, content_type):
            return False
        
        # Step 3: Index into ChromaDB
        if not self.index_chunks_to_chromadb(chunks, content_type):
            return False
        
        # Step 4: Upload to GCS
        if not self.upload_to_gcs(content_type, filename):
            print(f"   ⚠️ GCS upload failed, but content is indexed locally")
        
        # Step 5: Upload ChromaDB to GCS
        if not self.upload_chromadb_to_gcs():
            print(f"   ⚠️ ChromaDB upload failed, refresh button may not work immediately")
        
        # Step 6: Reload search engine singleton
        print(f"   🔄 Reloading search engine...")
        try:
            import hierarchical_search
            hierarchical_search._search_engine = None  # Reset singleton
            from hierarchical_search import get_search_engine
            search_engine = get_search_engine()
            doc_count = search_engine.vector_store.count_documents()
            print(f"      ✅ Search engine reloaded ({doc_count} documents)")
        except Exception as e:
            print(f"   ⚠️ Warning: Could not reload search engine: {e}")
        
        print(f"✅ {content_type.capitalize()} content indexed successfully!")
        return True

