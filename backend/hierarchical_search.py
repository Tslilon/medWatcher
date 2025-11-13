"""
Hierarchical search implementation for Harrison's RAG
Provides semantic search across medical topics
"""
import time
from typing import List, Dict, Optional
import json
from pathlib import Path
from vector_store import ChromaVectorStore, EmbeddingGenerator
from models import TopicResult

class HierarchicalSearch:
    """Implements semantic search across Harrison's medical content"""
    
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.generator = EmbeddingGenerator()
        self.hierarchy = self._load_hierarchy()
        print("✅ Hierarchical search initialized")
    
    def _load_hierarchy(self) -> Dict:
        """Load complete hierarchy for metadata"""
        hierarchy_file = Path("../data/processed/complete_hierarchy.json")
        
        if not hierarchy_file.exists():
            print("⚠️  Hierarchy file not found, continuing without detailed hierarchy")
            return {"parts": []}
        
        with open(hierarchy_file, 'r') as f:
            return json.load(f)
    
    def search(self, query: str, max_results: int = 10, min_relevance: float = -1.0) -> tuple[List[TopicResult], int]:
        """
        Semantic search across Harrison's
        
        Args:
            query: Natural language medical query
            max_results: Maximum number of results to return
            min_relevance: Minimum relevance threshold (distance-based, typically negative)
        
        Returns:
            Tuple of (list of TopicResult objects, search time in ms)
        """
        
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.generator.generate_embedding(query)
        
        # Search vector store
        raw_results = self.vector_store.search(
            query_embedding,
            top_k=max_results * 2  # Get more to filter
        )
        
        # Convert to TopicResult objects
        results = []
        
        if raw_results['ids'] and raw_results['ids'][0]:
            for doc_id, metadata, distance in zip(
                raw_results['ids'][0],
                raw_results['metadatas'][0],
                raw_results['distances'][0]
            ):
                # Calculate relevance score (convert distance to 0-1 range)
                # ChromaDB uses L2 distance, smaller = more similar
                # We'll accept all results and let the user decide
                relevance = max(0, 1 - (distance / 2))  # Normalize distance
                
                # Parse metadata
                tables_str = metadata.get('has_tables', '')
                figures_str = metadata.get('has_figures', '')
                
                tables = [t.strip() for t in tables_str.split(',') if t.strip()] if tables_str else []
                figures = [f.strip() for f in figures_str.split(',') if f.strip()] if figures_str else []
                
                # Check if this is an independent PDF or Harrison's
                pdf_source = metadata.get('pdf_source', 'harrisons')
                is_independent = pdf_source == 'independent'
                
                # Build hierarchy string
                if is_independent:
                    # For independent PDFs, use the PDF name as hierarchy
                    pdf_name = metadata.get('pdf_name', 'Independent PDF')
                    hierarchy = f"📄 {pdf_name}"
                    topic_id = metadata.get('chunk_id', doc_id)
                    topic_name = metadata.get('title', 'Document')
                else:
                    # For Harrison's, use the normal hierarchy
                    topic_id = metadata.get('topic_id', doc_id)
                    topic_name = metadata.get('topic_name', 'Chapter')
                    hierarchy = self._build_hierarchy_string(topic_id, topic_name)
                
                result = TopicResult(
                    topic_id=topic_id,
                    topic_name=topic_name,
                    hierarchy=hierarchy,
                    preview=metadata.get('preview', ''),
                    pages=f"{metadata['start_page']}-{metadata['end_page']}",
                    start_page=metadata['start_page'],
                    end_page=metadata['end_page'],
                    relevance_score=round(relevance, 3),  # 0-1 range
                    tables=tables,
                    figures=figures,
                    pdf_source=pdf_source,
                    pdf_filename=metadata.get('pdf_filename', ''),
                    pdf_name=metadata.get('pdf_name', '')
                )
                
                results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit to max_results
        results = results[:max_results]
        
        search_time = int((time.time() - start_time) * 1000)
        
        return results, search_time
    
    def _build_hierarchy_string(self, topic_id: str, topic_name: str) -> str:
        """Build human-readable hierarchy string"""
        
        # Parse topic_id: part4_ch81_cancer_of_the_skin
        parts = topic_id.split('_')
        
        if len(parts) < 2:
            return topic_name
        
        # Extract part and chapter numbers
        part_match = parts[0].replace('part', '')
        chapter_match = parts[1].replace('ch', '')
        
        # Try to find full names from hierarchy
        for part in self.hierarchy.get('parts', []):
            if str(part.get('part_number')) == part_match:
                part_name = part.get('part_name', f'Part {part_match}')
                # Simplify long part names
                if len(part_name) > 50:
                    part_name = f"Part {part_match}"
                return f"{part_name} > {topic_name}"
        
        return f"Part {part_match} > {topic_name}"
    
    def get_topic_details(self, topic_id: str) -> Optional[Dict]:
        """Get full details for a specific topic"""
        
        # Check Cloud Run location first, then local
        cloud_chunks = Path(f"/app/data/processed/chunks/{topic_id}.json")
        local_chunks = Path(f"../data/processed/chunks/{topic_id}.json")
        
        topic_file = cloud_chunks if cloud_chunks.exists() else local_chunks
        
        if not topic_file.exists():
            return None
        
        with open(topic_file, 'r') as f:
            return json.load(f)


# Global instance (singleton pattern)
_search_engine = None

def get_search_engine() -> HierarchicalSearch:
    """Get or create search engine instance (singleton)"""
    global _search_engine
    
    if _search_engine is None:
        _search_engine = HierarchicalSearch()
    
    return _search_engine

