"""
Vector Store for Harrison's Medical RAG
Generates embeddings and stores them in ChromaDB for semantic search
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables
load_dotenv()

class EmbeddingGenerator:
    """Generate embeddings using OpenAI"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        print(f"✅ Initialized embedding generator with model: {self.model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        
        response = self.client.embeddings.create(
            model=self.model,
            input=text[:8000]  # Limit text length
        )
        
        return response.data[0].embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings", unit="batch"):
            batch = texts[i:i + batch_size]
            
            # Limit text length for each item
            batch = [text[:8000] for text in batch]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings


class ChromaVectorStore:
    """ChromaDB implementation for vector storage"""
    
    def __init__(self, collection_name: str = "harrisons_medical"):
        super().__init__()
        
        # Initialize ChromaDB
        # Check if running in Cloud Run or locally
        if Path("/app/data/chroma_db").exists():
            # Running in Cloud Run
            persist_dir = Path("/app/data/chroma_db")
        elif Path("chroma_db").exists():
            # Running locally (backend directory)
            persist_dir = Path("chroma_db")
        else:
            # Fallback to original path
            persist_dir = Path("../data/chroma_db")
        
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Loaded existing collection: {collection_name}")
            print(f"   Current document count: {self.collection.count()}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Harrison's Principles of Internal Medicine - 21st Edition"}
            )
            print(f"✅ Created new collection: {collection_name}")
    
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """Add documents with embeddings to collection"""
        
        ids = [doc['id'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        
        # ChromaDB expects lists of strings for metadata values
        # Convert lists to comma-separated strings
        for metadata in metadatas:
            if 'has_tables' in metadata and isinstance(metadata['has_tables'], list):
                metadata['has_tables'] = ','.join(metadata['has_tables']) if metadata['has_tables'] else ''
            if 'has_figures' in metadata and isinstance(metadata['has_figures'], list):
                metadata['has_figures'] = ','.join(metadata['has_figures']) if metadata['has_figures'] else ''
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
        
        print(f"✅ Added {len(documents)} documents to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 10, filter_dict: Optional[Dict] = None):
        """Search for similar documents"""
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict if filter_dict else None
        )
        
        return results
    
    def count_documents(self) -> int:
        """Get total document count"""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection"""
        self.client.delete_collection(name=self.collection.name)
        print(f"✅ Deleted collection: {self.collection.name}")


def load_processed_topics(processed_dir: str = "../data/processed") -> List[Dict]:
    """Load all processed topics from chunks directory"""
    
    chunks_dir = Path(processed_dir) / "chunks"
    
    if not chunks_dir.exists():
        raise FileNotFoundError(f"Chunks directory not found: {chunks_dir}")
    
    topics = []
    
    for topic_file in sorted(chunks_dir.glob("*.json")):
        with open(topic_file, 'r') as f:
            topic_data = json.load(f)
            topics.append(topic_data)
    
    print(f"✅ Loaded {len(topics)} topics from {chunks_dir}")
    return topics


def prepare_documents_for_indexing(topics: List[Dict]) -> List[Dict]:
    """Convert topics to documents ready for vector store"""
    
    documents = []
    
    for topic in topics:
        # Create combined text for embedding
        # Include topic name for better semantic matching
        embedding_text = f"{topic['topic_name']}\n\n{topic['text_content']}"
        
        doc = {
            'id': topic['topic_id'],
            'text': embedding_text[:8000],  # Limit text length
            'metadata': {
                'topic_id': topic['topic_id'],
                'topic_name': topic['topic_name'],
                'start_page': topic['start_page'],
                'end_page': topic['end_page'],
                'preview': topic['preview'],
                'word_count': topic['word_count'],
                'has_tables': topic['has_tables'],
                'has_figures': topic['has_figures'],
            }
        }
        
        documents.append(doc)
    
    print(f"✅ Prepared {len(documents)} documents for indexing")
    return documents


def index_documents():
    """Main function to index all documents"""
    
    print("\n" + "="*70)
    print("🚀 STARTING VECTOR DATABASE INDEXING")
    print("="*70 + "\n")
    
    # Load processed topics
    print("📖 Step 1: Loading processed topics...")
    topics = load_processed_topics()
    
    # Prepare documents
    print("\n📝 Step 2: Preparing documents...")
    documents = prepare_documents_for_indexing(topics)
    
    # Generate embeddings
    print("\n🧠 Step 3: Generating embeddings...")
    print(f"   Using OpenAI {os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')}")
    print(f"   Estimated cost: ~$0.30-0.50")
    print(f"   Processing {len(documents)} documents...\n")
    
    generator = EmbeddingGenerator()
    texts = [doc['text'] for doc in documents]
    embeddings = generator.generate_embeddings_batch(texts)
    
    # Initialize vector store
    print("\n💾 Step 4: Storing in vector database...")
    vector_store = ChromaVectorStore()
    
    # Add documents
    vector_store.add_documents(documents, embeddings)
    
    # Verify
    count = vector_store.count_documents()
    
    print("\n" + "="*70)
    print("✅ INDEXING COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   Total documents indexed: {count}")
    print(f"   Vector dimensions: 3,072 (text-embedding-3-large)")
    print(f"   Database location: data/chroma_db/")
    print(f"\n🎯 Next step: Run hierarchical search tests")
    print("="*70 + "\n")
    
    return vector_store


if __name__ == "__main__":
    try:
        vector_store = index_documents()
        print("✅ Vector database ready for search!")
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        import traceback
        traceback.print_exc()

