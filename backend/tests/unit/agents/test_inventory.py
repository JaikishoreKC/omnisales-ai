"""
Unit tests for Inventory Agent
Tests stock checking functionality
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.inventory import check_stock


class TestInventoryAgent:
    """Test inventory agent stock checking"""
    
    @pytest.mark.asyncio
    async def test_check_stock_found(self):
        """Test successful stock check for existing product"""
        mock_product = {
            "product_id": "P001",
            "name": "Nike Air Max",
            "category": "shoes",
            "price": 120.00,
            "stock": 15
        }
        
        with patch('app.agents.inventory.find_product_by_name', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_product
            
            result = await check_stock("Nike Air Max")
            
            assert result is not None
            assert result["product"]["name"] == "Nike Air Max"
            assert result["stock"] == 15
            assert result["product"]["price"] == 120.00
            mock_find.assert_called_once_with("Nike Air Max")
    
    @pytest.mark.asyncio
    async def test_check_stock_not_found(self):
        """Test stock check for non-existent product"""
        with patch('app.agents.inventory.find_product_by_name', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await check_stock("NonExistent Product")
            
            assert result is None
            mock_find.assert_called_once_with("NonExistent Product")
    
    @pytest.mark.asyncio
    async def test_check_stock_empty_name(self):
        """Test stock check with empty product name"""
        result = await check_stock("")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_check_stock_none_name(self):
        """Test stock check with None as product name"""
        result = await check_stock(None)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_check_stock_out_of_stock(self):
        """Test stock check for out-of-stock product"""
        mock_product = {
            "product_id": "P002",
            "name": "Adidas Shirt",
            "category": "clothing",
            "price": 45.00,
            "stock": 0
        }
        
        with patch('app.agents.inventory.find_product_by_name', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_product
            
            result = await check_stock("Adidas Shirt")
            
            assert result is not None
            assert result["stock"] == 0
    
    @pytest.mark.asyncio
    async def test_check_stock_missing_stock_field(self):
        """Test handling product without stock field"""
        mock_product = {
            "product_id": "P003",
            "name": "Test Product",
            "category": "test",
            "price": 10.00
            # No stock field
        }
        
        with patch('app.agents.inventory.find_product_by_name', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_product
            
            result = await check_stock("Test Product")
            
            assert result is not None
            assert result["stock"] == 0  # Default to 0
