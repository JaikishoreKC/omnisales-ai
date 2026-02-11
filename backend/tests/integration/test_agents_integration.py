"""
Comprehensive test script for all OmniSales AI agents
Tests all 8 agents with the seeded test data
"""
import os
import requests
import json
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_INTEGRATION") != "1",
    reason="Live integration test requires running backend and seeded data"
)

BASE_URL = "http://localhost:8000"
API_KEY = "CxFn1QSd0rRCQWieaf_e7pJiPrESsIaPqaYRHgUPpDs"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Test users from seed data
USERS = {
    "gold": "customer_123",      # 2500 points, Gold tier
    "silver": "customer_456",    # 750 points, Silver tier
    "bronze": "customer_789"     # 150 points, Bronze tier
}

# Test orders from seed data
ORDERS = {
    "delivered": "12345",        # Can test returns
    "shipped": "12346",          # Can test tracking
    "processing": "ORD-789",
    "pending": "67890",          # Can test refund
    "cancelled": "ORDER999"
}


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def send_message(message, user_id="customer_123", session_id="test_session"):
    """Send a message to the chat endpoint"""
    payload = {
        "message": message,
        "user_id": user_id,
        "session_id": session_id
    }
    
    print(f"\n📨 Message: \"{message}\"")
    print(f"   User: {user_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            headers=HEADERS,
            json=payload,
            timeout=180  # Increased to 180s to match Ollama timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent: {data.get('agent_used')}")
            print(f"💬 Reply: {data.get('reply')[:150]}...")
            
            if data.get('actions'):
                print(f"🔧 Actions: {json.dumps(data['actions'], indent=2)}")
            
            return data
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None


def test_inventory_agent():
    """Test Agent 1: Inventory Management"""
    print_section("TEST 1: INVENTORY AGENT")
    
    print("\n--- Test 1.1: Check product availability ---")
    send_message("Do you have Nike shoes?")
    
    print("\n--- Test 1.2: Search by brand ---")
    send_message("Show me Apple products")
    
    print("\n--- Test 1.3: Search by category ---")
    send_message("What laptops do you have?")


def test_recommendation_agent():
    """Test Agent 2: Recommendation Engine"""
    print_section("TEST 2: RECOMMENDATION AGENT")
    
    print("\n--- Test 2.1: General recommendation ---")
    send_message("I need a new phone")
    
    print("\n--- Test 2.2: Budget-based recommendation ---")
    send_message("Suggest something under $100")
    
    print("\n--- Test 2.3: Category recommendation ---")
    send_message("Recommend some shoes")


def test_cart_agent():
    """Test Agent 3: Cart Management"""
    print_section("TEST 3: CART MANAGEMENT")
    
    session = "cart_test_session"
    
    print("\n--- Test 3.1: Add to cart ---")
    send_message("Add the Adidas shirt to cart", session_id=session)
    
    print("\n--- Test 3.2: View cart ---")
    send_message("Show my cart", session_id=session)
    
    print("\n--- Test 3.3: Add another item ---")
    send_message("I want the Nike shoes too", session_id=session)
    
    print("\n--- Test 3.4: Remove item ---")
    send_message("Remove the shirt from cart", session_id=session)
    
    print("\n--- Test 3.5: Clear cart ---")
    send_message("Clear my cart", session_id=session)


def test_tracking_agent():
    """Test Agent 4: Order Tracking"""
    print_section("TEST 4: ORDER TRACKING")
    
    print("\n--- Test 4.1: Track delivered order ---")
    send_message(f"Track order {ORDERS['delivered']}", user_id=USERS['gold'])
    
    print("\n--- Test 4.2: Track shipped order ---")
    send_message(f"Where is my order {ORDERS['shipped']}?", user_id=USERS['gold'])
    
    print("\n--- Test 4.3: Track with short ID ---")
    send_message(f"Track order #{ORDERS['processing']}", user_id=USERS['silver'])


def test_loyalty_agent():
    """Test Agent 5: Loyalty Program"""
    print_section("TEST 5: LOYALTY PROGRAM")
    
    print("\n--- Test 5.1: Check points (Gold user) ---")
    send_message("How many points do I have?", user_id=USERS['gold'])
    
    print("\n--- Test 5.2: Check loyalty tier ---")
    send_message("What's my loyalty status?", user_id=USERS['gold'])
    
    print("\n--- Test 5.3: Check offers ---")
    send_message("Show me available offers", user_id=USERS['silver'])
    
    print("\n--- Test 5.4: Redeem points ---")
    send_message("Redeem 500 points", user_id=USERS['gold'])


def test_payment_agent():
    """Test Agent 6: Payment Processing"""
    print_section("TEST 6: PAYMENT PROCESSING")
    
    # First add items to cart
    session = "payment_test_session"
    print("\n--- Setup: Add items to cart ---")
    send_message("Add the Adidas shirt", session_id=session)
    
    print("\n--- Test 6.1: Checkout ---")
    send_message("Checkout", user_id=USERS['gold'], session_id=session)
    
    print("\n--- Test 6.2: Process payment ---")
    send_message("Pay with credit card", user_id=USERS['gold'], session_id=session)


def test_post_purchase_agent():
    """Test Agent 7: Post-Purchase Support"""
    print_section("TEST 7: POST-PURCHASE SUPPORT")
    
    print("\n--- Test 7.1: Initiate return ---")
    send_message(f"Return order {ORDERS['delivered']}", user_id=USERS['gold'])
    
    print("\n--- Test 7.2: Request refund ---")
    send_message(f"Refund order {ORDERS['pending']}", user_id=USERS['silver'])
    
    print("\n--- Test 7.3: Report issue ---")
    send_message(f"Report issue with order {ORDERS['shipped']}", user_id=USERS['gold'])


def test_general_agent():
    """Test Agent 8: General Support"""
    print_section("TEST 8: GENERAL SUPPORT")
    
    print("\n--- Test 8.1: Greeting ---")
    send_message("Hello!")
    
    print("\n--- Test 8.2: Help request ---")
    send_message("I need help")
    
    print("\n--- Test 8.3: General question ---")
    send_message("What can you do?")


def run_all_tests():
    """Run all agent tests"""
    print("\n" + "="*60)
    print("  OMNISALES AI - COMPREHENSIVE AGENT TEST SUITE")
    print("="*60)
    print(f"\n🔗 Testing endpoint: {BASE_URL}")
    print(f"🔑 Using API Key: {API_KEY[:20]}...")
    
    try:
        # Test in order of importance
        test_inventory_agent()
        test_recommendation_agent()
        test_cart_agent()
        test_tracking_agent()
        test_loyalty_agent()
        test_payment_agent()
        test_post_purchase_agent()
        test_general_agent()
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\n📊 Summary:")
        print("   • Inventory Agent - Product search & availability")
        print("   • Recommendation Agent - Personalized suggestions")
        print("   • Cart Management - Add/view/remove items")
        print("   • Order Tracking - Track orders by ID")
        print("   • Loyalty Program - Points & offers")
        print("   • Payment Processing - Checkout & pay")
        print("   • Post-Purchase - Returns, refunds, issues")
        print("   • General Support - Help & information")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {str(e)}")


def run_quick_test():
    """Run a quick test of key features"""
    print("\n" + "="*60)
    print("  QUICK TEST - Key Agent Features")
    print("="*60)
    
    tests = [
        ("Inventory", "Do you have shirts?"),
        ("Recommendation", "Suggest a laptop"),
        ("Cart", "Add Adidas shirt to cart"),
        ("Tracking", f"Track order {ORDERS['delivered']}"),
        ("Loyalty", "How many points do I have?"),
    ]
    
    for agent_name, message in tests:
        print(f"\n[{agent_name}]")
        send_message(message, user_id=USERS['gold'])


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_all_tests()
