#!/usr/bin/env python3
"""
Standalone script to ingest offers from the demo server into GOR
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    """Ingest offers from demo server"""
    print("🔄 Starting offer ingestion...")
    
    try:
        from gor.services.gor_service import GORService
        
        # Initialize GOR service
        gor_service = GORService()
        
        # Wait for initialization
        print("⏳ Waiting for GOR service to initialize...")
        await asyncio.sleep(2)
        
        # Ingest offers
        result = await gor_service.ingest_offers()
        
        print(f"\n🎉 Ingestion complete!")
        print(f"📊 Total offers found: {result['total']}")
        print(f"✅ Successfully indexed: {result['ingested']}")
        
        if result['ingested'] > 0:
            # Show stats
            stats = await gor_service.get_registry_stats()
            print(f"\n📈 Registry Stats:")
            print(f"   Collection: {stats.get('collection_name', 'N/A')}")
            print(f"   Total offers: {stats.get('total_offers', 'N/A')}")
            print(f"   Vector size: {stats.get('vector_size', 'N/A')}")
            print(f"   Distance metric: {stats.get('distance_metric', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
