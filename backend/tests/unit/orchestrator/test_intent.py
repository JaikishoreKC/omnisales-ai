"""
Unit tests for Intent Detection
Tests intent classification logic
"""
import pytest
from app.orchestrator.intent import detect_intent


class TestIntentDetection:
    """Test intent detection from user messages"""
    
    def test_recommendation_intent(self):
        """Test recommendation intent detection"""
        messages = [
            "recommend me a laptop",
            "suggest some shoes",
            "what are the best phones?",
            "help me find a gift",
            "show me popular items",
            "looking for electronics"
        ]
        for msg in messages:
            assert detect_intent(msg) == "recommendation", f"Failed for: {msg}"
    
    def test_inventory_intent(self):
        """Test inventory checking intent"""
        messages = [
            "is this available?",
            "do you have Nike shoes?",
            "check stock for iPhone",
            "any left in stock?",
            "what's available?"
        ]
        for msg in messages:
            assert detect_intent(msg) == "inventory", f"Failed for: {msg}"
    
    def test_cart_intent(self):
        """Test cart management intent"""
        messages = [
            "add to cart",
            "put this in my cart",
            "I want to add this to cart",  # Fixed: need cart context
            "I'll take it and add to cart",  # Fixed: need cart context
            "view my cart",
            "show cart",
            "remove from cart",
            "clear cart",
            "I want Nike shoes too",  # Edge case with 'too'
            "Add Adidas shirt also"   # Edge case with 'also'
        ]
        for msg in messages:
            assert detect_intent(msg) == "cart", f"Failed for: {msg}"
    
    def test_payment_intent(self):
        """Test payment/checkout intent"""
        messages = [
            "buy this",
            "I want to purchase",
            "checkout",
            "pay now",
            "proceed to payment"
        ]
        for msg in messages:
            assert detect_intent(msg) == "payment", f"Failed for: {msg}"
    
    def test_tracking_intent(self):
        """Test order tracking intent"""
        messages = [
            "track my order",
            "where is my order?",
            "delivery status",
            "is it shipped?",
            "order status for #12345",
            "when will it arrive?"
        ]
        for msg in messages:
            assert detect_intent(msg) == "tracking", f"Failed for: {msg}"
    
    def test_loyalty_intent(self):
        """Test loyalty program intent"""
        # Note: Current implementation only detects loyalty via offer/coupon/deal keywords
        messages = [
            "show me offers",
            "available coupons",
            "what deals do you have?"
        ]
        for msg in messages:
            assert detect_intent(msg) == "loyalty", f"Failed for: {msg}"
    
    def test_loyalty_priority_over_recommendation(self):
        """Test that offer/coupon/deal keywords trigger loyalty, not recommendation"""
        # These should go to loyalty, not recommendation
        assert detect_intent("Show me available offers") == "loyalty"
        assert detect_intent("What coupons do you have?") == "loyalty"
        assert detect_intent("Any deals today?") == "loyalty"
    
    def test_post_purchase_intent(self):
        """Test post-purchase support intent"""
        messages = [
            "return this order",
            "I want a refund",
            "exchange this item",
            "cancel my order",
            "I have a complaint",
            "report an issue",
            "this is broken",
            "wrong item delivered",
            "damaged product"
        ]
        for msg in messages:
            assert detect_intent(msg) == "post_purchase", f"Failed for: {msg}"
    
    def test_general_intent(self):
        """Test general/fallback intent"""
        messages = [
            "hello",
            "hi there",
            "what's up?",
            "tell me a joke",
            "random question",
            "xyz abc 123"  # Nonsense
        ]
        for msg in messages:
            assert detect_intent(msg) == "general", f"Failed for: {msg}"
    
    def test_empty_message(self):
        """Test empty message returns general"""
        assert detect_intent("") == "general"
        assert detect_intent("   ") == "general"
    
    def test_none_message(self):
        """Test None message returns general"""
        assert detect_intent(None) == "general"
    
    def test_case_insensitive(self):
        """Test that detection is case-insensitive"""
        assert detect_intent("RECOMMEND A LAPTOP") == "recommendation"
        assert detect_intent("Track My Order") == "tracking"
        assert detect_intent("ADD TO CART") == "cart"
    
    def test_mixed_keywords_priority(self):
        """Test that priority keywords take precedence"""
        # Cart keywords should be detected even with other words
        assert detect_intent("I want to add Nike shoes to cart") == "cart"
        assert detect_intent("Help me find shoes and add to cart") == "cart"
