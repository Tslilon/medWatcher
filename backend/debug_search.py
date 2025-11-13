"""
Debug search to see what's happening
"""
from vector_store import ChromaVectorStore, EmbeddingGenerator

def debug():
    print("Initializing...")
    vector_store = ChromaVectorStore()
    generator = EmbeddingGenerator()
    
    query = "hyponatremia"
    print(f"\nQuery: {query}")
    
    # Generate embedding
    query_embedding = generator.generate_embedding(query)
    print(f"Generated embedding (first 5 dims): {query_embedding[:5]}")
    
    # Search
    raw_results = vector_store.search(query_embedding, top_k=5)
    
    print(f"\nRaw results structure:")
    print(f"  IDs: {len(raw_results['ids'][0]) if raw_results['ids'] and raw_results['ids'][0] else 0}")
    print(f"  Distances: {raw_results['distances'][0] if raw_results['distances'] and raw_results['distances'][0] else []}")
    
    if raw_results['ids'] and raw_results['ids'][0]:
        for i, (doc_id, metadata, distance) in enumerate(zip(
            raw_results['ids'][0],
            raw_results['metadatas'][0],
            raw_results['distances'][0]
        ), 1):
            print(f"\nResult {i}:")
            print(f"  ID: {doc_id}")
            print(f"  Distance: {distance}")
            print(f"  Topic: {metadata.get('topic_name', 'N/A')}")
            print(f"  Pages: {metadata.get('start_page', 'N/A')}-{metadata.get('end_page', 'N/A')}")

if __name__ == "__main__":
    debug()

