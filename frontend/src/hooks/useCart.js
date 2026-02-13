import { useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import { getGuestSessionId } from '../utils/session'
import { clearCart as clearCartApi } from '../services/api'
import useCartStore from '../store/cartStore'

const CART_UPDATED_KEY = 'omnisales-cart-updated'

export const useCart = () => {
  const { isAuthenticated, token } = useAuth()
  const guestSessionId = getGuestSessionId()
  const contextRef = useRef('')
  const {
    cartItems,
    setOwnerKey,
    loadCart,
    addToCart: storeAddToCart,
    removeFromCart: storeRemoveFromCart,
    updateQuantity: storeUpdateQuantity,
    clearCart: storeClearCart,
    getCartTotal,
    getCartCount
  } = useCartStore()

  const getContextKey = useCallback(() => {
    if (isAuthenticated) {
      return `user:${token || 'unknown'}`
    }
    return `guest:${guestSessionId}`
  }, [isAuthenticated, token, guestSessionId])

  useEffect(() => {
    contextRef.current = getContextKey()
    setOwnerKey(contextRef.current)
  }, [getContextKey])

  const refreshCart = useCallback(async () => {
    const contextKey = getContextKey()
    if (contextRef.current !== contextKey) {
      return
    }
    await loadCart(isAuthenticated ? { token } : { sessionId: guestSessionId })
  }, [isAuthenticated, token, guestSessionId, getContextKey, loadCart])

  const emitCartUpdated = useCallback(() => {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('cart:updated'))
    }
  }, [])

  useEffect(() => {
    let isActive = true

    const syncCart = async () => {
      try {
        const contextKey = getContextKey()
        if (isAuthenticated) {
          await clearCartApi({ sessionId: guestSessionId })
          if (isActive && contextRef.current === contextKey) {
            await refreshCart()
          }
        } else if (isActive && contextRef.current === contextKey) {
          await refreshCart()
        }
      } catch (error) {
        console.error('Failed to sync cart:', error)
      }
    }

    syncCart()

    return () => {
      isActive = false
    }
  }, [isAuthenticated, token, guestSessionId, refreshCart])

  useEffect(() => {
    const handleStorage = (event) => {
      if (event.key === CART_UPDATED_KEY) {
        refreshCart().catch((error) => {
          console.error('Failed to refresh cart:', error)
        })
      }
    }

    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [refreshCart])

  const addToCart = async (product, quantity = 1) => {
    const contextKey = getContextKey()
    if (contextRef.current !== contextKey) {
      return
    }
    await storeAddToCart(product, quantity, isAuthenticated ? { token } : { sessionId: guestSessionId })
  }

  const removeFromCart = async (productId) => {
    const contextKey = getContextKey()
    if (contextRef.current !== contextKey) {
      return
    }
    await storeRemoveFromCart(productId, isAuthenticated ? { token } : { sessionId: guestSessionId })
  }

  const updateQuantity = async (productId, newQuantity) => {
    const contextKey = getContextKey()
    if (contextRef.current !== contextKey) {
      return
    }
    await storeUpdateQuantity(productId, newQuantity, isAuthenticated ? { token } : { sessionId: guestSessionId })
  }

  const clearCart = async () => {
    const contextKey = getContextKey()
    if (contextRef.current !== contextKey) {
      return
    }
    await storeClearCart(isAuthenticated ? { token } : { sessionId: guestSessionId })
  }

  return {
    cartItems,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartTotal,
    getCartCount
  }
}
