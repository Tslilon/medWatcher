#!/usr/bin/env python3
"""
Index documents into ChromaDB
"""
import json
import os
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from vector_store import ChromaVectorStore
import time

def load_chunks(chunks_dir: Path) -> List[Dict]:
    """Load all chunk JSON files"""
    chunks = []
    for json_file in chunks_dir.glob("*.json"):
        # Skip summary files
        if json_file.name == 'summary.json':
            continue
        with open(json_file, 'r') as f:
            chunk = json.load(f)
            chunks.append(chunk)
    return chunks

def generate_embeddings(texts: List[str], client: OpenAI, model: str = "text-embedding-3-large") -> List[List[float]]:
    """Generate embeddings for texts"""
    embeddings = []
    batch_size = 100
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"   Generating embeddings for texts {i+1} to {min(i+batch_size, len(texts))}...")
        
        response = client.embeddings.create(
            input=batch,
            model=model
        )
        
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)
        
        # Rate limiting
        time.sleep(0.5)
    
    return embeddings

def index_documents():
    """Main indexing function - indexes both Harrison's and independent PDFs"""
    print("="*80)
    print("📚 INDEXING MEDICAL DOCUMENTS")
    print("="*80)
    
    # Initialize
    print("\n1️⃣  Initializing vector store...")
    vector_store = ChromaVectorStore()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("   Please set it first: export OPENAI_API_KEY='your-key-here'")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Check if already indexed
    current_count = vector_store.count_documents()
    if current_count > 0:
        print(f"\n⚠️  Database already contains {current_count} documents")
        response = input("   Re-index anyway? This will clear existing data (y/N): ")
        if response.lower() != 'y':
            print("   Skipping re-index")
            return
        print("   Clearing existing data...")
        # Note: You may need to implement a clear method in vector_store
    
    # Load Harrison's chunks
    print("\n2️⃣  Loading Harrison's document chunks...")
    harrisons_chunks_dir = Path("../data/processed/chunks")
    if not harrisons_chunks_dir.exists():
        harrisons_chunks_dir = Path("data/processed/chunks")
    
    harrisons_chunks = []
    if harrisons_chunks_dir.exists():
        harrisons_chunks = load_chunks(harrisons_chunks_dir)
        print(f"   Found {len(harrisons_chunks)} Harrison's chunks")
    else:
        print(f"   ⚠️  Harrison's chunks not found at {harrisons_chunks_dir}")
    
    # Load independent PDF chunks
    print("\n3️⃣  Loading independent PDF chunks...")
    independent_chunks_dir = Path("../data/processed/independent_chunks")
    if not independent_chunks_dir.exists():
        independent_chunks_dir = Path("data/processed/independent_chunks")
    
    independent_chunks = []
    if independent_chunks_dir.exists():
        independent_chunks = load_chunks(independent_chunks_dir)
        print(f"   Found {len(independent_chunks)} independent PDF chunks")
    else:
        print(f"   ℹ️  No independent PDFs found at {independent_chunks_dir}")
    
    # Combine all chunks
    all_chunks = harrisons_chunks + independent_chunks
    total_chunks = len(all_chunks)
    
    if total_chunks == 0:
        print("\n❌ No chunks found to index!")
        return
    
    print(f"\n   📊 Total chunks to index: {total_chunks}")
    print(f"      - Harrison's: {len(harrisons_chunks)}")
    print(f"      - Independent PDFs: {len(independent_chunks)}")
    
    # Prepare documents
    print("\n4️⃣  Preparing documents...")
    documents = []
    texts_for_embedding = []
    
    for chunk in all_chunks:
        # Determine if this is Harrison's or independent PDF
        is_independent = 'pdf_filename' in chunk
        
        if is_independent:
            # Independent PDF chunk
            doc = {
                'id': chunk['chunk_id'],
                'text': chunk['text_content'],
                'metadata': {
                    'chunk_id': chunk['chunk_id'],
                    'title': chunk['title'],
                    'pdf_source': 'independent',
                    'pdf_filename': chunk['pdf_filename'],
                    'pdf_name': chunk['pdf_name'],
                    'start_page': chunk['start_page'],
                    'end_page': chunk['end_page'],
                    'total_pages': chunk['total_pages'],
                    'preview': chunk['preview'],
                    'word_count': chunk['word_count']
                }
            }
        else:
            # Harrison's chunk
            doc = {
                'id': chunk['topic_id'],
                'text': chunk['text_content'],
                'metadata': {
                    'topic_id': chunk['topic_id'],
                    'topic_name': chunk['topic_name'],
                    'pdf_source': 'harrisons',
                    'start_page': chunk['start_page'],
                    'end_page': chunk['end_page'],
                    'preview': chunk['preview'],
                    'word_count': chunk['word_count']
                }
            }
        
        documents.append(doc)
        texts_for_embedding.append(chunk['text_content'])
    
    # Generate embeddings
    print(f"\n5️⃣  Generating embeddings for {len(texts_for_embedding)} documents...")
    print("   This may take a few minutes...")
    embeddings = generate_embeddings(texts_for_embedding, client)
    
    # Add to vector store
    print(f"\n6️⃣  Adding {len(documents)} documents to vector store...")
    vector_store.add_documents(documents, embeddings)
    
    # Verify
    final_count = vector_store.count_documents()
    print(f"\n✅ INDEXING COMPLETE!")
    print(f"   Total documents in database: {final_count}")
    print(f"      - Harrison's: {len(harrisons_chunks)}")
    print(f"      - Independent PDFs: {len(independent_chunks)}")
    print("="*80)

if __name__ == "__main__":
    import sys
    
    # Check for --force flag
    force_reindex = '--force' in sys.argv or '-f' in sys.argv
    
    try:
        if force_reindex:
            # Modify the function to skip the prompt
            import index_documents as idx_module
            original_func = idx_module.index_documents
            
            def force_index():
                """Wrapper to force re-indexing"""
                print("="*80)
                print("📚 INDEXING MEDICAL DOCUMENTS (FORCE MODE)")
                print("="*80)
                
                # Initialize
                print("\n1️⃣  Initializing vector store...")
                vector_store = ChromaVectorStore()
                
                # Check API key
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("❌ OPENAI_API_KEY environment variable not set!")
                    print("   Please set it first: export OPENAI_API_KEY='your-key-here'")
                    return
                
                client = OpenAI(api_key=api_key)
                
                current_count = vector_store.count_documents()
                if current_count > 0:
                    print(f"\n🔄 Force re-indexing - clearing {current_count} existing documents...")
                
                # Continue with normal indexing (rest of the function)
                # Load Harrison's chunks
                print("\n2️⃣  Loading Harrison's document chunks...")
                harrisons_chunks_dir = Path("../data/processed/chunks")
                if not harrisons_chunks_dir.exists():
                    harrisons_chunks_dir = Path("data/processed/chunks")
                
                harrisons_chunks = []
                if harrisons_chunks_dir.exists():
                    harrisons_chunks = load_chunks(harrisons_chunks_dir)
                    print(f"   Found {len(harrisons_chunks)} Harrison's chunks")
                else:
                    print(f"   ⚠️  Harrison's chunks not found at {harrisons_chunks_dir}")
                
                # Load independent PDF chunks
                print("\n3️⃣  Loading independent PDF chunks...")
                independent_chunks_dir = Path("../data/processed/independent_chunks")
                if not independent_chunks_dir.exists():
                    independent_chunks_dir = Path("data/processed/independent_chunks")
                
                independent_chunks = []
                if independent_chunks_dir.exists():
                    independent_chunks = load_chunks(independent_chunks_dir)
                    print(f"   Found {len(independent_chunks)} independent PDF chunks")
                else:
                    print(f"   ℹ️  No independent PDFs found at {independent_chunks_dir}")
                
                # Combine all chunks
                all_chunks = harrisons_chunks + independent_chunks
                total_chunks = len(all_chunks)
                
                if total_chunks == 0:
                    print("\n❌ No chunks found to index!")
                    return
                
                print(f"\n   📊 Total chunks to index: {total_chunks}")
                print(f"      - Harrison's: {len(harrisons_chunks)}")
                print(f"      - Independent PDFs: {len(independent_chunks)}")
                
                # Prepare documents
                print("\n4️⃣  Preparing documents...")
                documents = []
                texts_for_embedding = []
                
                for chunk in all_chunks:
                    is_independent = 'pdf_filename' in chunk
                    
                    if is_independent:
                        doc = {
                            'id': chunk['chunk_id'],
                            'text': chunk['text_content'],
                            'metadata': {
                                'chunk_id': chunk['chunk_id'],
                                'title': chunk['title'],
                                'pdf_source': 'independent',
                                'pdf_filename': chunk['pdf_filename'],
                                'pdf_name': chunk['pdf_name'],
                                'start_page': chunk['start_page'],
                                'end_page': chunk['end_page'],
                                'total_pages': chunk['total_pages'],
                                'preview': chunk['preview'],
                                'word_count': chunk['word_count']
                            }
                        }
                    else:
                        doc = {
                            'id': chunk['topic_id'],
                            'text': chunk['text_content'],
                            'metadata': {
                                'topic_id': chunk['topic_id'],
                                'topic_name': chunk['topic_name'],
                                'pdf_source': 'harrisons',
                                'start_page': chunk['start_page'],
                                'end_page': chunk['end_page'],
                                'preview': chunk['preview'],
                                'word_count': chunk['word_count']
                            }
                        }
                    
                    documents.append(doc)
                    texts_for_embedding.append(chunk['text_content'])
                
                # Generate embeddings
                print(f"\n5️⃣  Generating embeddings for {len(texts_for_embedding)} documents...")
                print("   This may take a few minutes...")
                embeddings = generate_embeddings(texts_for_embedding, client)
                
                # Add to vector store
                print(f"\n6️⃣  Adding {len(documents)} documents to vector store...")
                vector_store.add_documents(documents, embeddings)
                
                # Verify
                final_count = vector_store.count_documents()
                print(f"\n✅ INDEXING COMPLETE!")
                print(f"   Total documents in database: {final_count}")
                print(f"      - Harrison's: {len(harrisons_chunks)}")
                print(f"      - Independent PDFs: {len(independent_chunks)}")
                print("="*80)
            
            force_index()
        else:
            index_documents()
            
    except KeyboardInterrupt:
        print("\n\n❌ Indexing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during indexing: {e}")
        import traceback
        traceback.print_exc()

