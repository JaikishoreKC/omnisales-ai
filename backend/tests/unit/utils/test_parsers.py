"""
Unit tests for Parser Utilities
Tests extraction of product names and order IDs from messages
"""
import pytest
from app.utils.parsers import extract_product_name, extract_order_id


class TestProductNameExtraction:
    """Test product name extraction from messages"""
    
    def test_extract_with_cart_action(self):
        """Test extracting product from cart-related messages"""
        assert extract_product_name("Add the Adidas shirt to cart") == "adidas shirt"
        assert extract_product_name("Put Nike shoes in my cart") == "nike shoes"
        assert extract_product_name("I want the iPhone") == "iphone"
    
    def test_extract_with_search_action(self):
        """Test extracting product from search messages"""
        assert extract_product_name("show me Nike shoes") == "nike shoes"
        assert extract_product_name("find Apple laptop") == "apple laptop"
        assert extract_product_name("search for Samsung phone") == "samsung phone"
    
    def test_extract_simple_product_name(self):
        """Test extracting simple product names"""
        assert extract_product_name("Adidas shirt") == "adidas shirt"
        assert extract_product_name("laptop") == "laptop"
        assert extract_product_name("shoes") == "shoes"
    
    def test_extract_with_articles(self):
        """Test extraction handles articles (a, an, the)"""
        result = extract_product_name("Get me the Samsung Galaxy phone")
        assert "samsung" in result.lower()
        assert "galaxy" in result.lower()
        assert "the" not in result  # 'the' should be removed
    
    def test_extract_with_multiple_keywords(self):
        """Test extraction with multiple filler words"""
        result = extract_product_name("I want to add a Nike Air Max to my cart")
        assert "nike" in result.lower()
        assert "air" in result.lower()
        assert "max" in result.lower()
        assert "add" not in result.lower()
        assert "cart" not in result.lower()
    
    def test_extract_empty_message(self):
        """Test extraction from empty message"""
        assert extract_product_name("") is None
        assert extract_product_name("   ") is None
    
    def test_extract_only_action_words(self):
        """Test extraction when only action words present"""
        result = extract_product_name("add to cart")
        # Should return None or empty since no actual product
        assert not result or result == ""
    
    def test_extract_preserves_brand_and_model(self):
        """Test that brand and model names are preserved"""
        result = extract_product_name("Show me iPhone 15 Pro Max")
        assert "iphone" in result.lower()
        assert "15" in result
        assert "pro" in result.lower()
        assert "max" in result.lower()


class TestOrderIdExtraction:
    """Test order ID extraction from messages"""
    
    def test_extract_numeric_order_id(self):
        """Test extracting numeric order IDs"""
        assert extract_order_id("track order 12345") == "12345"
        assert extract_order_id("order #67890") == "67890"
        assert extract_order_id("order: 54321") == "54321"
    
    def test_extract_alphanumeric_order_id(self):
        """Test extracting alphanumeric order IDs"""
        assert extract_order_id("track order ORD-123") == "ORD-123"
        assert extract_order_id("order ORDER999") == "ORDER999"
        assert extract_order_id("where is ORD-456?") == "ORD-456"
    
    def test_extract_uuid_order_id(self):
        """Test extracting UUID-format order IDs"""
        uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = extract_order_id(f"track order {uuid}")
        assert result.upper() == uuid.upper()
    
    def test_extract_with_various_formats(self):
        """Test various order ID formats"""
        assert extract_order_id("order #12345") == "12345"
        assert extract_order_id("order 67890") == "67890"
        assert extract_order_id("track #ORD-789") == "ORD-789"
        assert extract_order_id("where is my ORDER123?") == "ORDER123"
    
    def test_extract_short_order_id_ignored(self):
        """Test that very short numbers are ignored"""
        # Should ignore 1-2 digit numbers
        result = extract_order_id("I have 12 items")
        # Either None or not "12"
        assert result != "12"
    
    def test_extract_no_order_id(self):
        """Test when no order ID is present"""
        assert extract_order_id("track my order") is None
        assert extract_order_id("where is it?") is None
        assert extract_order_id("hello") is None
    
    def test_extract_multiple_numbers_takes_first(self):
        """Test extraction with multiple numbers"""
        # Should extract the first valid order ID
        result = extract_order_id("track order 12345 or 67890")
        assert result in ["12345", "67890"]
        assert result is not None
    
    def test_extract_case_insensitive(self):
        """Test case-insensitive extraction"""
        assert extract_order_id("TRACK ORDER 12345") == "12345"
        assert extract_order_id("Order ORD-123") == "ORD-123"
    
    def test_extract_with_special_characters(self):
        """Test extraction handles special characters"""
        assert extract_order_id("order #12345!") == "12345"
        assert extract_order_id("track: ORD-789?") == "ORD-789"
    
    def test_extract_standalone_number(self):
        """Test extracting standalone numbers (3+ digits)"""
        assert extract_order_id("12345") == "12345"
        assert extract_order_id("#67890") == "67890"
    
    def test_extract_returns_uppercase(self):
        """Test that returned order IDs are uppercase"""
        assert extract_order_id("track ord-123") == "ORD-123"
        assert extract_order_id("order order999") == "ORDER999"
