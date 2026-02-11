import React, { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProductById } from '../services/api'
import { useCart } from '../hooks/useCart'
import { useToast } from '../context/ToastContext'
import useChatStore from '../store/chatStore'
import { sendChatMessage } from '../services/api'

const ProductDetailPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { cartItems, addToCart, updateQuantity } = useCart()
  const { success } = useToast()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [quantity, setQuantity] = useState(1)
  const [isSendingToAI, setIsSendingToAI] = useState(false)
  
  // Chat store for AI assistant
  const openAssistant = useChatStore((state) => state.openAssistant)
  const addMessage = useChatStore((state) => state.addMessage)
  const setLoadingChat = useChatStore((state) => state.setLoading)
  const getSessionId = useChatStore((state) => state.getSessionId)
  
  // Check if product is already in cart
  const cartItem = useMemo(
    () => cartItems.find(item => item.product_id === id),
    [cartItems, id]
  )
  
  // Sync quantity with cart when product is loaded
  useEffect(() => {
    if (cartItem) {
      console.log('📦 Product found in cart, syncing quantity:', cartItem.quantity)
      setQuantity(cartItem.quantity)
    } else {
      console.log('🆕 Product not in cart, resetting quantity to 1')
      setQuantity(1)
    }
  }, [cartItem])

  useEffect(() => {
    const fetchProduct = async () => {
      console.log('🔍 Fetching product with ID:', id)
      setLoading(true)
      setError(null)
      setProduct(null) // Clear previous product
      try {
        const data = await getProductById(id)
        console.log('✅ Product loaded:', data)
        setProduct(data)
      } catch (err) {
        console.error('❌ Error fetching product:', err)
        setError('Product not found')
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      fetchProduct()
    }
  }, [id])

  const handleAddToCart = () => {
    if (cartItem) {
      // Update existing cart item
      updateQuantity(product.product_id, quantity)
      success(`Updated ${product.name} quantity to ${quantity}!`)
    } else {
      // Add new item to cart
      addToCart(product, quantity)
      success(`Added ${quantity} × ${product.name} to cart!`)
    }
  }

  const handleBuyNow = () => {
    if (cartItem) {
      updateQuantity(product.product_id, quantity)
    } else {
      addToCart(product, quantity)
    }
    success(`Added ${quantity} × ${product.name} to cart!`)
    navigate('/cart')
  }

  const handleChatWithAI = async () => {
    if (!product || isSendingToAI) return

    setIsSendingToAI(true)

    // Build contextual message
    const contextMessage = `I'm viewing this product and would like your help:

Product: ${product.name}
Category: ${product.category}
Price: $${product.price}
Stock: ${product.stock} available
Rating: ${product.rating || 4.5}/5 stars
${product.description ? `Description: ${product.description}` : ''}

Please provide detailed information, comparisons with similar products, buying advice, and answer any questions I might have about this product.`

    console.log('🤖 Opening AI assistant with product context')
    
    // Open assistant immediately
    openAssistant()
    
    // Add system context message
    addMessage({
      role: 'system',
      content: '📦 Product context loaded. How can I help you with this product?',
      source: 'context-action'
    })
    
    // Add user's contextual message
    addMessage({
      role: 'user',
      content: contextMessage,
      source: 'product-page'
    })
    
    // Send to backend
    setLoadingChat(true)
    try {
      const sessionId = getSessionId()
      const response = await sendChatMessage({
        user_id: 'user_' + Math.random().toString(36).substr(2, 9),
        session_id: sessionId,
        message: contextMessage,
        channel: 'web'
      })

      // Add assistant response
      addMessage({
        role: 'assistant',
        content: response.reply,
        agent: response.agent_used,
        actions: response.actions,
        source: 'product-page'
      })
    } catch (error) {
      console.error('Error sending product context:', error)
      const status = error?.status
      const fallbackMessage = status === 429
        ? 'We are getting a lot of requests. Please try again shortly.'
        : status === 401
        ? 'Chat is unavailable. Missing or invalid API key.'
        : 'I received your product inquiry. How can I assist you?'
      addMessage({
        role: 'assistant',
        content: fallbackMessage,
        source: 'product-page'
      })
    } finally {
      setLoadingChat(false)
      setIsSendingToAI(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div className="w-full h-96 bg-gray-200 rounded-lg"></div>
            <div className="space-y-4">
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          {error || 'Product Not Found'}
        </h1>
        <button
          onClick={() => navigate('/products')}
          className="text-blue-600 hover:underline"
        >
          ← Back to Products
        </button>
      </div>
    )
  }

  // MOVED AFTER NULL CHECK - Use product image or generate placeholder
  const productImage = product.image || `https://via.placeholder.com/600x600?text=${encodeURIComponent(product.name.split(' ').slice(0, 2).join(' '))}`
  // Use product rating or default to 4.5
  const rating = product.rating || 4.5
  // Generate consistent review count based on product ID (using deterministic hash)
  const hashCode = product.product_id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const reviews = 50 + (hashCode % 450)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="mb-6 text-sm text-gray-600">
        <button onClick={() => navigate('/')} className="hover:text-blue-600 hover:underline">
          Home
        </button>
        <span className="mx-2">›</span>
        <button onClick={() => navigate('/products')} className="hover:text-blue-600 hover:underline">
          Products
        </button>
        <span className="mx-2">›</span>
        <button 
          onClick={() => navigate(`/products?category=${product.category}`)} 
          className="hover:text-blue-600 hover:underline capitalize"
        >
          {product.category}
        </button>
        <span className="mx-2">›</span>
        <span className="text-gray-900">{product.name}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Product Images */}
        <div>
          <div className="bg-white rounded-lg p-8 shadow-md">
            <img
              src={productImage}
              alt={product.name}
              className="w-full h-auto rounded-lg"
              onError={(e) => {
                e.target.onerror = null // Prevent infinite loop
                e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="600" height="600"%3E%3Crect width="600" height="600" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="48" fill="%239ca3af"%3E📦%3C/text%3E%3C/svg%3E'
              }}
            />
          </div>
        </div>

        {/* Product Info */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>

          {/* Rating */}
          <div className="flex items-center space-x-2 mb-4">
            <div className="flex text-yellow-400">
              {'⭐'.repeat(Math.floor(rating))}
            </div>
            <span className="text-gray-600">
              {rating.toFixed(1)} ({reviews} reviews)
            </span>
          </div>

          {/* Price */}
          <div className="mb-6">
            <span className="text-4xl font-bold text-gray-900">${product.price}</span>
            <span className="ml-2 text-sm text-gray-500">Free shipping</span>
          </div>

          {/* Stock */}
          <div className="mb-6">
            {product.stock > 0 ? (
              <span className="text-green-600 font-medium">
                ✓ In Stock ({product.stock} available)
              </span>
            ) : (
              <span className="text-red-600 font-medium">✗ Out of Stock</span>
            )}
          </div>

          {/* Description */}
          <p className="text-gray-700 mb-6">
            {product.description || `Premium quality ${product.category}. Perfect for everyday use with excellent durability and style.`}
          </p>

          {/* Quantity */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-10 h-10 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                −
              </button>
              <span className="text-xl font-semibold w-12 text-center">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                className="w-10 h-10 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                +
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-4 mb-8">
            <button
              onClick={handleAddToCart}
              disabled={product.stock === 0}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {cartItem ? 'Update Cart' : 'Add to Cart'}
            </button>
            <button
              onClick={handleBuyNow}
              disabled={product.stock === 0}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Buy Now
            </button>
          </div>

          {/* Product Details */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Product Details</h3>
            <dl className="space-y-2">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <dt className="text-gray-600">Category</dt>
                <dd className="text-gray-900 font-medium capitalize">{product.category}</dd>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <dt className="text-gray-600">Product ID</dt>
                <dd className="text-gray-900 font-medium">{product.product_id.substring(0, 8)}...</dd>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <dt className="text-gray-600">Availability</dt>
                <dd className="text-gray-900 font-medium">{product.stock > 0 ? 'In Stock' : 'Out of Stock'}</dd>
              </div>
              <div className="flex justify-between py-2">
                <dt className="text-gray-600">Shipping</dt>
                <dd className="text-green-600 font-medium">Free</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      {/* Ask AI Banner */}
      <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-2">Have Questions About This Product?</h2>
        <p className="mb-4">Ask our AI assistant for detailed information, comparisons, or recommendations!</p>
        <button 
          onClick={handleChatWithAI}
          disabled={isSendingToAI}
          className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSendingToAI ? '⏳ Opening Assistant...' : '💬 Chat with AI'}
        </button>
      </div>
    </div>
  )
}

export default ProductDetailPage
