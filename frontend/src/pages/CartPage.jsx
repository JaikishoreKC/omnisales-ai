import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../hooks/useCart'
import { useAuth } from '../context/AuthContext'
import { useConfirm } from '../context/ConfirmContext'
import { useToast } from '../context/ToastContext'
import useChatStore from '../store/chatStore'
import { sendChatMessage } from '../services/api'

const CartPage = () => {
  const navigate = useNavigate()
  const { cartItems, updateQuantity, removeFromCart, getCartTotal } = useCart()
  const { isAuthenticated } = useAuth()
  const { confirm } = useConfirm()
  const { success } = useToast()
  const [isSendingToAI, setIsSendingToAI] = useState(false)
  
  // Chat store for AI assistant
  const openAssistant = useChatStore((state) => state.openAssistant)
  const addMessage = useChatStore((state) => state.addMessage)
  const setLoadingChat = useChatStore((state) => state.setLoading)
  const getSessionId = useChatStore((state) => state.getSessionId)

  // Debug: Log cart items
  console.log('🛒 CartPage - cartItems:', cartItems)
  console.log('🛒 CartPage - cartItems.length:', cartItems.length)

  const subtotal = getCartTotal()
  const shipping = subtotal > 0 ? 0 : 0 // Free shipping
  const tax = subtotal * 0.08 // 8% tax
  const total = subtotal + shipping + tax

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate('/login')
    } else {
      navigate('/checkout')
    }
  }

  const handleRemoveFromCart = async (productId, productName) => {
    const confirmed = await confirm({
      title: 'Remove Item',
      message: `Are you sure you want to remove "${productName}" from your cart?`,
      confirmText: 'Remove',
      cancelText: 'Keep',
      type: 'danger'
    })
    
    if (confirmed) {
      removeFromCart(productId)
      success('Item removed from cart')
    }
  }

  const handleAskAIForHelp = async () => {
    if (cartItems.length === 0) {
      success('Add some items to your cart first!')
      return
    }

    if (isSendingToAI) return
    setIsSendingToAI(true)

    // Build cart summary
    const itemsList = cartItems.map(item => 
      `- ${item.name} x${item.quantity} ($${item.price} each = $${(item.price * item.quantity).toFixed(2)})`
    ).join('\\n')
    
    const subtotal = getCartTotal()
    const tax = subtotal * 0.08
    const total = subtotal + tax

    const contextMessage = `I need help with my shopping cart:

Cart Items (${cartItems.length} items):
${itemsList}

Cart Summary:
- Subtotal: $${subtotal.toFixed(2)}
- Tax (8%): $${tax.toFixed(2)}
- Total: $${total.toFixed(2)}
- Shipping: FREE

Please help me with:
- Product recommendations or alternatives
- Checkout process guidance
- Answers to questions about these items
- Ways to save or bundle deals
- Any concerns about my cart`

    console.log('🛒 Opening AI assistant with cart context')
    
    // Open assistant immediately
    openAssistant()
    
    // Add system context message
    addMessage({
      role: 'system',
      content: '🛒 Cart summary loaded. How can I assist you with your purchase?',
      source: 'context-action'
    })
    
    // Add user's contextual message
    addMessage({
      role: 'user',
      content: contextMessage,
      source: 'cart-page'
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
        source: 'cart-page'
      })
    } catch (error) {
      console.error('Error sending cart context:', error)
      const status = error?.status
      const fallbackMessage = status === 429
        ? 'We are getting a lot of requests. Please try again shortly.'
        : status === 401
        ? 'Chat is unavailable. Missing or invalid API key.'
        : 'I can see your cart contents. How can I help you with your purchase decision?'
      addMessage({
        role: 'assistant',
        content: fallbackMessage,
        source: 'cart-page'
      })
    } finally {
      setLoadingChat(false)
      setIsSendingToAI(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

      {cartItems.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-6xl mb-4">🛒</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
          <p className="text-gray-600 mb-6">Add some products to get started!</p>
          <button
            onClick={() => navigate('/products')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md">
              {cartItems.map((item) => (
                <div
                  key={item.product_id}
                  className="flex items-center p-6 border-b border-gray-200 last:border-0"
                >
                  {/* Product Image */}
                  <img
                    src={item.image || `https://via.placeholder.com/80x80?text=${encodeURIComponent(item.name.split(' ').slice(0, 2).join(' '))}`}
                    alt={item.name}
                    className="w-20 h-20 object-cover rounded-lg mr-4 cursor-pointer hover:opacity-80 transition"
                    onClick={() => navigate(`/products/${item.product_id}`)}
                    onError={(e) => {
                      // Use a simple colored background as final fallback
                      e.target.onerror = null // Prevent infinite loop
                      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect width="80" height="80" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3E📦%3C/text%3E%3C/svg%3E'
                    }}
                  />

                  {/* Product Info */}
                  <div className="flex-1">
                    <h3 
                      className="font-semibold text-gray-900 mb-1 cursor-pointer hover:text-blue-600 transition"
                      onClick={() => navigate(`/products/${item.product_id}`)}
                    >
                      {item.name}
                    </h3>
                    <p className="text-gray-600 text-sm mb-2">${item.price}</p>

                    {/* Quantity Controls */}
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                        className="w-8 h-8 border border-gray-300 rounded hover:bg-gray-100"
                      >
                        −
                      </button>
                      <span className="text-gray-900 font-medium w-8 text-center">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                        className="w-8 h-8 border border-gray-300 rounded hover:bg-gray-100"
                      >
                        +
                      </button>
                      <button
                        onClick={() => handleRemoveFromCart(item.product_id, item.name)}
                        className="ml-4 text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {/* Item Total */}
                  <div className="text-right">
                    <p className="text-xl font-bold text-gray-900">
                      ${(item.price * item.quantity).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Continue Shopping */}
            <button
              onClick={() => navigate('/products')}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Continue Shopping
            </button>
          </div>

          {/* Order Summary */}
          <div>
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal ({cartItems.length} items)</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span className="text-green-600 font-medium">FREE</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span>${tax.toFixed(2)}</span>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4 mb-6">
                <div className="flex justify-between text-xl font-bold text-gray-900">
                  <span>Total</span>
                  <span>${total.toFixed(2)}</span>
                </div>
              </div>

              <button 
                onClick={handleCheckout}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition mb-3"
              >
                Proceed to Checkout
              </button>

              <button 
                onClick={handleAskAIForHelp}
                disabled={isSendingToAI}
                className="w-full border-2 border-blue-600 text-blue-600 py-3 rounded-lg font-semibold hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSendingToAI ? '⏳ Opening Assistant...' : '💬 Ask AI for Help'}
              </button>

              {/* Trust Badges */}
              <div className="mt-6 pt-6 border-t border-gray-200 space-y-2 text-sm text-gray-600">
                <div className="flex items-center">
                  <span className="mr-2">🔒</span>
                  <span>Secure checkout</span>
                </div>
                <div className="flex items-center">
                  <span className="mr-2">🚚</span>
                  <span>Free shipping on all orders</span>
                </div>
                <div className="flex items-center">
                  <span className="mr-2">↩️</span>
                  <span>30-day return policy</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CartPage
