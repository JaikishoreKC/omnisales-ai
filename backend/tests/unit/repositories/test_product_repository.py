"""
Unit tests for Product Repository
Tests product database operations
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.product_repository import (
    find_products,
    find_product_by_name,
    get_product_by_id
)


class TestProductRepository:
    """Test product repository database operations"""
    
    @pytest.mark.asyncio
    async def test_find_products_with_filter(self):
        """Test finding products with query filter"""
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[
            {"product_id": "P001", "name": "Product 1"},
            {"product_id": "P002", "name": "Product 2"}
        ])
        
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find.return_value = mock_cursor
            
            result = await find_products({"category": "electronics"}, limit=5)
            
            assert len(result) == 2
            assert result[0]["product_id"] == "P001"
            mock_db.return_value.products.find.assert_called_once_with({"category": "electronics"})
    
    @pytest.mark.asyncio
    async def test_find_products_empty_result(self):
        """Test finding products returns empty list when none match"""
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find.return_value = mock_cursor
            
            result = await find_products({"category": "nonexistent"})
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_find_product_by_name_exact_match(self):
        """Test finding product by exact name match"""
        mock_product = {
            "product_id": "P001",
            "name": "Nike Air Max",
            "price": 120.00
        }
        
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find_one = AsyncMock(return_value=mock_product)
            
            result = await find_product_by_name("Nike Air Max")
            
            assert result is not None
            assert result["name"] == "Nike Air Max"
            # Verify regex search was used
            call_args = mock_db.return_value.products.find_one.call_args[0][0]
            assert "$regex" in call_args["name"]
    
    @pytest.mark.asyncio
    async def test_find_product_by_name_partial_match(self):
        """Test finding product by partial/keyword match"""
        with patch('app.repositories.product_repository.get_database') as mock_db:
            # First call returns None (no exact match), second returns keyword match
            mock_db.return_value.products.find_one = AsyncMock(side_effect=[
                None,  # No exact match
                {"product_id": "P001", "name": "Adidas Essential T-Shirt"}  # Keyword match
            ])
            
            result = await find_product_by_name("adidas shirt")
            
            assert result is not None
            assert "Adidas" in result["name"]
            assert "Shirt" in result["name"]
            # Should have been called twice (exact then keyword)
            assert mock_db.return_value.products.find_one.call_count == 2
    
    @pytest.mark.asyncio
    async def test_find_product_by_name_not_found(self):
        """Test finding non-existent product"""
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find_one = AsyncMock(return_value=None)
            
            result = await find_product_by_name("NonExistent Product")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_find_product_by_name_case_insensitive(self):
        """Test that name search is case-insensitive"""
        mock_product = {"product_id": "P001", "name": "Nike Shoes"}
        
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find_one = AsyncMock(return_value=mock_product)
            
            result = await find_product_by_name("NIKE SHOES")
            
            assert result is not None
            # Verify case-insensitive flag was used
            call_args = mock_db.return_value.products.find_one.call_args[0][0]
            assert call_args["name"]["$options"] == "i"
    
    @pytest.mark.asyncio
    async def test_find_product_by_name_multiple_keywords(self):
        """Test finding product with multiple keywords"""
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find_one = AsyncMock(side_effect=[
                None,  # No exact match
                {"product_id": "P001", "name": "Nike Running Shoes"}  # Keyword match
            ])
            
            result = await find_product_by_name("nike shoes")
            
            # Should use lookahead pattern for multiple keywords
            assert mock_db.return_value.products.find_one.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_found(self):
        """Test getting product by ID when exists"""
        mock_product = {
            "product_id": "P001",
            "name": "Test Product",
            "price": 99.99
        }
        
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find_one = AsyncMock(return_value=mock_product)
            
            result = await get_product_by_id("P001")
            
            assert result is not None
            assert result["product_id"] == "P001"
            mock_db.return_value.products.find_one.assert_called_once_with({"product_id": "P001"})
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self):
        """Test getting product by ID when doesn't exist"""
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find_one = AsyncMock(return_value=None)
            
            result = await get_product_by_id("NONEXISTENT")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_find_products_respects_limit(self):
        """Test that find_products respects the limit parameter"""
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[{"product_id": f"P{i}"} for i in range(3)])
        
        with patch('app.repositories.product_repository.get_database') as mock_db:
            mock_db.return_value.products.find.return_value = mock_cursor
            
            await find_products({}, limit=3)
            
            mock_cursor.limit.assert_called_once_with(3)
            mock_cursor.to_list.assert_called_once_with(length=3)
