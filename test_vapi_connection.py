"""
Test script to simulate a Vapi tool-call webhook
Tests the connection between Vapi, ngrok, FastAPI, and Square Sandbox
"""

import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NGROK_URL = os.getenv("NGROK_URL", "http://localhost:8000")  # Default to localhost if not set
WEBHOOK_ENDPOINT = f"{NGROK_URL.rstrip('/')}/vapi-webhook"

# Mock order data: 1 Burger and 1 Coke
# NOTE: Replace these with actual Square catalog object IDs from your Sandbox
# You can get these by calling GET /menu on your server
MOCK_BURGER_ITEM_ID = "YOUR_BURGER_VARIATION_ID_HERE"  # Replace with actual ID
MOCK_COKE_ITEM_ID = "YOUR_COKE_VARIATION_ID_HERE"      # Replace with actual ID


def create_mock_tool_call():
    """
    Creates a mock Vapi tool-call payload simulating an order for 1 Burger and 1 Coke
    """
    return {
        "type": "tool-calls",
        "toolCalls": [
            {
                "id": "test-tool-call-123",
                "function": {
                    "name": "place_order",
                    "parameters": {
                        "items": [
                            {
                                "item_id": MOCK_BURGER_ITEM_ID,
                                "quantity": "1",
                                "modifiers": []
                            },
                            {
                                "item_id": MOCK_COKE_ITEM_ID,
                                "quantity": "1",
                                "modifiers": []
                            }
                        ]
                    }
                }
            }
        ]
    }


def get_menu_items():
    """
    Fetches menu items from the server to get actual catalog IDs
    """
    try:
        menu_url = f"{NGROK_URL.rstrip('/')}/menu"
        print(f"\n📋 Fetching menu items from: {menu_url}")
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(menu_url)
            response.raise_for_status()
            menu_items = response.json()
            
            print(f"✅ Found {len(menu_items)} menu items")
            
            # Display first few items for reference
            if menu_items:
                print("\n📝 Sample menu items (use these IDs in your test):")
                for item in menu_items[:5]:
                    print(f"   - {item.get('name', 'Unknown')}: {item.get('id', 'N/A')}")
            
            return menu_items
    except Exception as e:
        print(f"⚠️  Could not fetch menu items: {e}")
        return []


def test_webhook_connection():
    """
    Sends a mock tool-call to the webhook endpoint
    """
    print(f"\n🧪 Testing Vapi Webhook Connection")
    print(f"📍 Endpoint: {WEBHOOK_ENDPOINT}")
    
    # First, try to get menu items to suggest actual IDs
    menu_items = get_menu_items()
    
    # Check if we need to update the item IDs
    if MOCK_BURGER_ITEM_ID == "YOUR_BURGER_VARIATION_ID_HERE":
        print("\n⚠️  WARNING: Using placeholder item IDs!")
        print("   Please update MOCK_BURGER_ITEM_ID and MOCK_COKE_ITEM_ID in this script")
        print("   with actual Square catalog variation IDs from your menu.")
        print("   You can get these by calling GET /menu on your server.\n")
        
        if menu_items:
            print("💡 Suggested IDs from your menu:")
            burger_items = [item for item in menu_items if 'burger' in item.get('name', '').lower()]
            coke_items = [item for item in menu_items if 'coke' in item.get('name', '').lower() or 'cola' in item.get('name', '').lower()]
            
            if burger_items:
                print(f"   Burger: {burger_items[0].get('id')}")
            if coke_items:
                print(f"   Coke: {coke_items[0].get('id')}")
            elif menu_items:
                print(f"   Or use any item ID: {menu_items[0].get('id')}")
    
    # Create mock payload
    payload = create_mock_tool_call()
    
    print(f"\n📤 Sending mock tool-call:")
    print(json.dumps(payload, indent=2))
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                WEBHOOK_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"📥 Response Body:")
                print(json.dumps(response_data, indent=2))
                
                if response.status_code == 200:
                    print("\n✅ SUCCESS! Webhook connection is working!")
                    
                    # Check for tool call responses
                    if "responses" in response_data:
                        for resp in response_data["responses"]:
                            if resp.get("result"):
                                print(f"\n💬 AI Confirmation Message: {resp.get('result')}")
                            if resp.get("error"):
                                print(f"\n❌ Error: {resp.get('error')}")
                    
                    print("\n✅ Next steps:")
                    print("   1. Check your Square Sandbox dashboard for the new order")
                    print("   2. Use GET /orders/recent to verify the order was created")
                    print("   3. Make a real test call through Vapi")
                else:
                    print(f"\n❌ ERROR: Server returned status {response.status_code}")
                    print("   Check your FastAPI server logs for details")
                    
            except json.JSONDecodeError:
                print(f"\n📥 Response Text: {response.text}")
                print("⚠️  Response is not valid JSON")
                
    except httpx.ConnectError:
        print(f"\n❌ CONNECTION ERROR: Could not connect to {WEBHOOK_ENDPOINT}")
        print("   Make sure:")
        print("   1. Your FastAPI server is running (uvicorn main:app --reload)")
        print("   2. ngrok is running and pointing to port 8000")
        print("   3. The NGROK_URL environment variable is set correctly")
        print("   4. Or update NGROK_URL in this script to your ngrok URL")
        
    except httpx.TimeoutException:
        print(f"\n❌ TIMEOUT: Request took too long")
        print("   Check if your server is responding")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")


if __name__ == "__main__":
    print("=" * 60)
    print("Vapi Webhook Connection Test")
    print("=" * 60)
    
    # Check if NGROK_URL is set
    if NGROK_URL == "http://localhost:8000":
        print("\n💡 TIP: Set NGROK_URL environment variable or update it in this script")
        print("   Example: export NGROK_URL=https://abc123.ngrok-free.app")
        print("   Or edit this script and set NGROK_URL directly\n")
    
    test_webhook_connection()
    
    print("\n" + "=" * 60)
