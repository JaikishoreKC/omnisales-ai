import React, { useState, useMemo } from 'react'
import PropTypes from 'prop-types'
import { useCart } from '../hooks/useCart'
import { useToast } from '../context/ToastContext'
import { useNavigate } from 'react-router-dom'

const ProductCard = ({ product }) => {
  if (!product || !product.product_id) {
    return null
  }
  const { cartItems, addToCart, updateQuantity, removeFromCart } = useCart()
  const { success, error } = useToast()
  const navigate = useNavigate()
  const [isAdding, setIsAdding] = useState(false)
  
  // Check if product is in cart and get its quantity
  const cartItem = useMemo(
    () => cartItems.find(item => item.product_id === product.product_id),
    [cartItems, product.product_id]
  )
  const quantityInCart = cartItem?.quantity || 0

  const handleAddToCart = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (product.stock === 0) {
      error('This product is out of stock')
      return
    }
    
    if (isAdding) return // Prevent double clicks
    
    setIsAdding(true)
    
    try {
      await addToCart(product, 1)
      success(`Added ${product.name} to cart!`)
      
      // Re-enable button after 500ms
      setTimeout(() => setIsAdding(false), 500)
    } catch (err) {
      console.error('❌ Failed to add to cart:', err)
      error('Failed to add item to cart')
      setIsAdding(false)
    }
  }
  
  const handleIncreaseQuantity = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (quantityInCart >= product.stock) {
      error('Cannot exceed available stock')
      return
    }
    
    try {
      await updateQuantity(product.product_id, quantityInCart + 1)
    } catch (err) {
      console.error('❌ Failed to update cart:', err)
      error('Failed to update cart')
    }
  }
  
  const handleDecreaseQuantity = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (quantityInCart <= 1) {
      try {
        await removeFromCart(product.product_id)
        success('Removed from cart')
      } catch (err) {
        console.error('❌ Failed to remove item:', err)
        error('Failed to remove item')
      }
    } else {
      try {
        await updateQuantity(product.product_id, quantityInCart - 1)
      } catch (err) {
        console.error('❌ Failed to update cart:', err)
        error('Failed to update cart')
      }
    }
  }

  const handleCardClick = () => {
    navigate(`/products/${product.product_id}`)
  }

  return (
    <div 
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer"
      onClick={handleCardClick}
    >
      {/* Product Image */}
      <div className="relative h-48 bg-gray-200">
        <img
          src={product.image || `https://via.placeholder.com/300x300?text=${encodeURIComponent(product.name.split(' ').slice(0, 2).join(' '))}`}
          alt={product.name || 'Product image'}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.onerror = null
            e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300"%3E%3Crect width="300" height="300" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="32" fill="%239ca3af"%3E%F0%9F%93%A6%3C/text%3E%3C/svg%3E'
          }}
        />
        {product.stock < 10 && product.stock > 0 && (
          <span className="absolute top-2 right-2 bg-orange-500 text-white text-xs px-2 py-1 rounded">
            Only {product.stock} left
          </span>
        )}
        {product.stock === 0 && (
          <span className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
            Out of Stock
          </span>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-1">
          {product.name}
        </h3>
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {product.description || `${product.category || 'Product'} details coming soon.`}
        </p>

        {/* Rating */}
        <div className="flex items-center mb-3">
          <div className="flex text-yellow-400 text-sm">
            {'⭐'.repeat(Math.floor(product.rating || 4.5))}
          </div>
          <span className="ml-1 text-sm text-gray-600">
            {(product.rating || 4.5).toFixed(1)}
          </span>
        </div>

        {/* Price and Cart Controls */}
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-gray-900">
            ${product.price}
          </span>
          
          {quantityInCart > 0 ? (
            /* Quantity Controls */
            <div className="flex items-center space-x-2" onClick={(e) => e.stopPropagation()}>
              <button
                onClick={handleDecreaseQuantity}
                className="w-8 h-8 flex items-center justify-center bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition font-bold"
              >
                −
              </button>
              <span className="w-8 text-center font-bold text-gray-900">
                {quantityInCart}
              </span>
              <button
                onClick={handleIncreaseQuantity}
                disabled={quantityInCart >= product.stock}
                className={`w-8 h-8 flex items-center justify-center rounded-lg transition font-bold ${
                  quantityInCart >= product.stock
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-green-100 text-green-600 hover:bg-green-200'
                }`}
              >
                +
              </button>
            </div>
          ) : (
            /* Add to Cart Button */
            <button
              className={`px-4 py-2 rounded-lg transition text-sm font-medium ${
                product.stock === 0 || isAdding
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
              }`}
              onClick={handleAddToCart}
              disabled={product.stock === 0 || isAdding}
            >
              {isAdding ? '✓ Added!' : product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProductCard

ProductCard.propTypes = {
  product: PropTypes.shape({
    product_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    name: PropTypes.string,
    price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    stock: PropTypes.number,
    image: PropTypes.string,
    description: PropTypes.string,
    category: PropTypes.string,
    rating: PropTypes.number
  }).isRequired
}
