"""
Quick test of the vector search functionality
"""
from vector_store import ChromaVectorStore, EmbeddingGenerator

def test_search():
    """Test vector store search with medical queries"""
    
    print("\n" + "="*70)
    print("🧪 TESTING HARRISON'S RAG SEARCH")
    print("="*70 + "\n")
    
    # Initialize
    vector_store = ChromaVectorStore()
    generator = EmbeddingGenerator()
    
    # Test queries
    test_queries = [
        "basal cell carcinoma skin cancer treatment",
        "acute myocardial infarction heart attack",
        "diabetes mellitus type 2 management",
        "pneumonia antibiotic therapy",
        "hypertension blood pressure treatment"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print('='*70)
        
        # Generate query embedding
        query_embedding = generator.generate_embedding(query)
        
        # Search
        results = vector_store.search(query_embedding, top_k=3)
        
        # Display results
        if results['ids'] and results['ids'][0]:
            for j, (doc_id, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                relevance = 1 - distance
                print(f"\n  Result {j}:")
                print(f"    Topic: {metadata['topic_name']}")
                print(f"    Pages: {metadata['start_page']}-{metadata['end_page']}")
                print(f"    Relevance: {relevance:.3f}")
                print(f"    Preview: {metadata['preview'][:80]}...")
        else:
            print("  No results found")
    
    print("\n" + "="*70)
    print("✅ SEARCH TEST COMPLETE!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_search()

