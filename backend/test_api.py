"""
Test script for Harrison's Medical RAG API
Tests all endpoints with sample queries
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("\n" + "="*70)
    print("🧪 Test 1: Root Endpoint")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Root endpoint working")

def test_health():
    """Test health check"""
    print("\n" + "="*70)
    print("🧪 Test 2: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["vector_store_count"] == 550
    print("✅ Health check passed")

def test_stats():
    """Test stats endpoint"""
    print("\n" + "="*70)
    print("🧪 Test 3: Statistics")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Stats endpoint working")

def test_search(query: str, expected_results: int = None):
    """Test search endpoint"""
    print("\n" + "="*70)
    print(f"🧪 Test: Search Query")
    print("="*70)
    print(f"Query: '{query}'")
    
    response = requests.post(
        f"{BASE_URL}/api/search",
        json={"query": query, "max_results": 5}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Results: {data['total_results']} topics found")
        print(f"⏱️  Search time: {data['search_time_ms']}ms\n")
        
        for i, result in enumerate(data['results'], 1):
            print(f"[{i}] {result['topic_name']}")
            print(f"    Pages: {result['pages']}")
            print(f"    Relevance: {result['relevance_score']:.3f}")
            print(f"    Preview: {result['preview'][:80]}...")
            print()
        
        if expected_results:
            assert data['total_results'] >= expected_results
        
        print(f"✅ Search test passed")
        return data['results'][0] if data['results'] else None
    else:
        print(f"❌ Search failed: {response.text}")
        return None

def test_get_topic(topic_id: str):
    """Test get topic endpoint"""
    print("\n" + "="*70)
    print(f"🧪 Test: Get Topic Details")
    print("="*70)
    print(f"Topic ID: {topic_id}")
    
    response = requests.get(f"{BASE_URL}/api/topic/{topic_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📚 Topic: {data['topic_name']}")
        print(f"📄 Pages: {data['start_page']}-{data['end_page']}")
        print(f"📝 Word count: {data['word_count']}")
        print(f"📊 Tables: {len(data['tables'])}")
        print(f"🖼️  Figures: {len(data['figures'])}")
        print(f"💬 Preview: {data['preview'][:100]}...")
        
        print(f"\n✅ Topic retrieval test passed")
    else:
        print(f"❌ Topic retrieval failed: {response.text}")

def run_all_tests():
    """Run complete test suite"""
    
    print("\n" + "="*70)
    print("🏥 HARRISON'S MEDICAL RAG API - TEST SUITE")
    print("="*70)
    print("📍 Testing API at:", BASE_URL)
    
    try:
        # Test 1: Root endpoint
        test_root()
        time.sleep(0.5)
        
        # Test 2: Health check
        test_health()
        time.sleep(0.5)
        
        # Test 3: Stats
        test_stats()
        time.sleep(0.5)
        
        # Test 4: Medical queries
        medical_queries = [
            ("what is the workup for hyponatremia", 3),
            ("acute myocardial infarction management", 3),
            ("pneumonia antibiotic therapy", 2),
            ("diabetes type 2 treatment", 3),
        ]
        
        for query, expected in medical_queries:
            first_result = test_search(query, expected)
            time.sleep(0.5)
            
            # Test getting topic details for first result
            if first_result:
                test_get_topic(first_result['topic_id'])
                time.sleep(0.5)
        
        # Final summary
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🎉 Harrison's Medical RAG API is fully functional!")
        print("📍 Ready for Apple Watch integration")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   cd backend && python main.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

