#!/usr/bin/env python3
"""
Demo script to show search functionality
"""
from interactive_search import HarrisonsSearch

def demo():
    """Demo the search with sample query"""
    
    # Initialize
    search = HarrisonsSearch()
    
    # Test query
    test_query = "what is the workup for hyponatremia"
    
    print("="*80)
    print("🧪 DEMO: Testing with sample query")
    print("="*80)
    print(f"\n🔍 Query: '{test_query}'\n")
    
    # Search
    results = search.search(test_query, top_k=5)
    
    # Display
    search.display_results(results)
    
    if results:
        print("\n💡 In the interactive mode, you would now select one of these options.")
        print("   Let's automatically select the first one as an example:\n")
        
        # Show selection
        search.display_selection(results[0])

if __name__ == "__main__":
    demo()

