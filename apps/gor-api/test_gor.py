#!/usr/bin/env python3
"""
Test script for GOR API components
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_gor_service():
    """Test the GOR Service"""
    print("🧪 Testing GOR Service...")
    
    try:
        from services.gor_service import GORService
        
        # Initialize service
        gor_service = GORService()
        
        # Wait for initialization
        await asyncio.sleep(1)
        
        print("✅ GOR Service initialized successfully")
        
        # Test stats
        stats = await gor_service.get_registry_stats()
        print(f"📊 Registry stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ GOR Service test failed: {e}")
        return False

async def test_embedding_service():
    """Test the Embedding Service"""
    print("🧪 Testing Embedding Service...")
    
    try:
        from services.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        
        # Test mock embedding
        test_text = "pizza italian restaurant"
        embedding = await embedding_service.get_embedding(test_text)
        
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        print(f"📝 Test text: '{test_text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding Service test failed: {e}")
        return False

async def test_search_service():
    """Test the Search Service"""
    print("🧪 Testing Search Service...")
    
    try:
        from services.gor_service import GORService
        from services.search_service import SearchService
        
        gor_service = GORService()
        search_service = SearchService(gor_service)
        
        print("✅ Search Service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Search Service test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting GOR API Tests...\n")
    
    tests = [
        test_gor_service(),
        test_embedding_service(),
        test_search_service()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n📋 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Test {i+1} failed with exception: {result}")
        elif result:
            print(f"✅ Test {i+1} passed")
            passed += 1
        else:
            print(f"❌ Test {i+1} failed")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GOR API is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
