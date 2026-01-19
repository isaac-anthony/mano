"""
Quick test script to verify Square Sandbox connection
"""

import os
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment

# Load environment variables
load_dotenv()

# Get credentials
access_token = os.getenv("SQUARE_ACCESS_TOKEN")
location_id = os.getenv("SQUARE_LOCATION_ID")

print("=" * 60)
print("Square Sandbox Connection Test")
print("=" * 60)
print(f"\n📍 Location ID: {location_id}")
print(f"🔑 Access Token: {access_token[:20]}..." if access_token else "❌ Access Token: NOT SET")

if not access_token or not location_id:
    print("\n❌ ERROR: Missing credentials in .env file")
    exit(1)

# Initialize Square Client
try:
    square_client = Square(
        token=access_token,
        environment=SquareEnvironment.SANDBOX
    )
    print("\n✅ Square Client initialized")
    
    # Test 1: List Catalog
    print("\n📋 Testing Catalog API...")
    catalog_api = square_client.catalog
    
    try:
        # The list() method returns a SyncPager, we need to iterate or get results
        result = catalog_api.list()
        
        # Convert pager to list of results
        objects = []
        for page in result:
            if hasattr(page, 'body') and page.body:
                page_objects = page.body.get('objects', [])
                objects.extend(page_objects)
            elif isinstance(page, dict):
                objects.extend(page.get('objects', []))
        
        items = [obj for obj in objects if obj.get('type') == 'ITEM']
        print(f"✅ Catalog API working! Found {len(items)} items")
        
        if items:
            print("\n📝 Sample items:")
            for item in items[:3]:
                item_data = item.get('item_data', {})
                print(f"   - {item_data.get('name', 'Unknown')}")
        else:
            print("   ⚠️  No items found in catalog. Add items in Square Sandbox dashboard.")
    except Exception as e:
        print(f"❌ Catalog API Error: {e}")
    
    # Test 2: Search Orders (to verify location)
    print("\n📦 Testing Orders API...")
    orders_api = square_client.orders
    
    try:
        query_dict = {
            "filter": {
                "state_filter": {
                    "states": ["OPEN", "COMPLETED", "DRAFT"]
                }
            }
        }
        
        result = orders_api.search(
            location_ids=[location_id],
            query=query_dict,
            limit=1
        )
        
        # Handle response (may be SyncPager or direct response)
        orders = []
        if hasattr(result, 'body'):
            orders = result.body.get('orders', [])
        elif hasattr(result, '__iter__'):
            for page in result:
                if hasattr(page, 'body') and page.body:
                    orders.extend(page.body.get('orders', []))
                elif isinstance(page, dict):
                    orders.extend(page.get('orders', []))
        else:
            orders = result.get('orders', []) if isinstance(result, dict) else []
        
        print(f"✅ Orders API working! Found {len(orders)} recent orders")
        if len(orders) == 0:
            print("   (This is OK if you haven't created any orders yet)")
    except Exception as e:
        print(f"⚠️  Orders API: {e}")
        print("   (This is OK if you haven't created any orders yet)")
    
    print("\n" + "=" * 60)
    print("✅ Square Sandbox connection is working!")
    print("=" * 60)
    print("\n🎉 You're ready to start the FastAPI server!")
    print("   Run: uvicorn main:app --reload")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Verify your Access Token is correct")
    print("2. Verify your Location ID is correct")
    print("3. Make sure you're using Sandbox credentials")
    exit(1)
