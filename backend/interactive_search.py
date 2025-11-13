#!/usr/bin/env python3
"""
Interactive CLI for Harrison's Medical RAG System
Test natural language queries and get page numbers
"""
from vector_store import ChromaVectorStore, EmbeddingGenerator
from typing import List, Dict
import sys

class HarrisonsSearch:
    """Interactive search interface for Harrison's"""
    
    def __init__(self):
        print("\n🏥 Initializing Harrison's Medical RAG System...")
        self.vector_store = ChromaVectorStore()
        self.generator = EmbeddingGenerator()
        print("✅ System ready!\n")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search for relevant topics"""
        
        # Generate query embedding
        query_embedding = self.generator.generate_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Format results
        formatted_results = []
        
        if results['ids'] and results['ids'][0]:
            for doc_id, metadata, distance in zip(
                results['ids'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                relevance = 1 - distance
                
                # Only include relevant results (relevance > 0.3)
                if relevance < -0.5:  # Distance-based filtering
                    continue
                
                formatted_results.append({
                    'topic_id': metadata['topic_id'],
                    'topic_name': metadata['topic_name'],
                    'start_page': metadata['start_page'],
                    'end_page': metadata['end_page'],
                    'pages': f"{metadata['start_page']}-{metadata['end_page']}",
                    'preview': metadata['preview'],
                    'relevance': relevance,
                    'tables': metadata.get('has_tables', '').split(',') if metadata.get('has_tables') else [],
                    'figures': metadata.get('has_figures', '').split(',') if metadata.get('has_figures') else []
                })
        
        return formatted_results
    
    def display_results(self, results: List[Dict]):
        """Display search results in a nice format"""
        
        if not results:
            print("❌ No relevant results found. Try rephrasing your query.")
            return
        
        print(f"\n📊 Found {len(results)} relevant sections:\n")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['topic_name']}")
            print(f"    📄 Pages: {result['pages']}")
            print(f"    📈 Relevance: {result['relevance']:.3f}")
            print(f"    💬 {result['preview'][:100]}...")
            
            if result['tables']:
                tables_list = [t.strip() for t in result['tables'] if t.strip()]
                if tables_list:
                    print(f"    📊 Tables: {', '.join(tables_list[:3])}")
            
            if result['figures']:
                figures_list = [f.strip() for f in result['figures'] if f.strip()]
                if figures_list:
                    print(f"    🖼️  Figures: {', '.join(figures_list[:3])}")
        
        print("\n" + "="*80)
    
    def get_user_selection(self, results: List[Dict]) -> Dict:
        """Let user select a result"""
        
        while True:
            try:
                selection = input(f"\n👉 Select a result [1-{len(results)}] (or 'q' to query again): ").strip()
                
                if selection.lower() == 'q':
                    return None
                
                index = int(selection) - 1
                
                if 0 <= index < len(results):
                    return results[index]
                else:
                    print(f"❌ Please enter a number between 1 and {len(results)}")
            
            except ValueError:
                print("❌ Please enter a valid number or 'q'")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
    
    def display_selection(self, result: Dict):
        """Display detailed information about selected topic"""
        
        print("\n" + "="*80)
        print("✅ SELECTED TOPIC")
        print("="*80)
        print(f"\n📚 Topic: {result['topic_name']}")
        print(f"📄 Pages: {result['start_page']} to {result['end_page']}")
        print(f"📖 Total pages in section: {result['end_page'] - result['start_page'] + 1}")
        
        if result['tables']:
            tables_list = [t.strip() for t in result['tables'] if t.strip()]
            if tables_list:
                print(f"\n📊 Tables referenced:")
                for table in tables_list:
                    print(f"   - {table}")
        
        if result['figures']:
            figures_list = [f.strip() for f in result['figures'] if f.strip()]
            if figures_list:
                print(f"\n🖼️  Figures referenced:")
                for figure in figures_list:
                    print(f"   - {figure}")
        
        print(f"\n💡 Preview:")
        print(f"   {result['preview']}")
        
        print("\n" + "="*80)
        print(f"\n🎯 ACTION: Open Harrison's PDF to pages {result['start_page']}-{result['end_page']}")
        print("="*80 + "\n")
    
    def run(self):
        """Main interactive loop"""
        
        print("="*80)
        print("🏥 HARRISON'S MEDICAL RAG - INTERACTIVE SEARCH")
        print("="*80)
        print("\nAsk me anything about internal medicine!")
        print("Examples:")
        print("  - What is the workup for hyponatremia?")
        print("  - How to treat acute myocardial infarction?")
        print("  - Pneumonia antibiotic selection")
        print("  - Diabetes management guidelines")
        print("\nType 'quit' or 'exit' to leave\n")
        
        while True:
            try:
                # Get query
                query = input("🔍 Your question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Harrison's Medical RAG!")
                    break
                
                # Search
                print(f"\n🔎 Searching Harrison's for: '{query}'...")
                results = self.search(query, top_k=10)
                
                # Display results
                self.display_results(results)
                
                if not results:
                    continue
                
                # Let user select
                selected = self.get_user_selection(results)
                
                if selected:
                    self.display_selection(selected)
                
                print("\n" + "-"*80 + "\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Entry point"""
    try:
        search = HarrisonsSearch()
        search.run()
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

