import { useState, useEffect } from 'react'

const CART_STORAGE_KEY = 'cart'

export const useCart = () => {
  const [cartItems, setCartItems] = useState(() => {
    // Initialize state from localStorage
    const savedCart = localStorage.getItem(CART_STORAGE_KEY)
    if (savedCart) {
      try {
        return JSON.parse(savedCart)
      } catch (error) {
        console.error('Failed to load cart:', error)
        localStorage.removeItem(CART_STORAGE_KEY)
        return []
      }
    }
    return []
  })

  // Listen for cart changes from other components/tabs
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === CART_STORAGE_KEY) {
        console.log('🔄 Cart updated from storage event')
        if (e.newValue) {
          try {
            const newCart = JSON.parse(e.newValue)
            // Only update if cart actually changed
            setCartItems(prev => {
              if (JSON.stringify(prev) === JSON.stringify(newCart)) {
                return prev // No change, return same reference to prevent re-render
              }
              return newCart
            })
          } catch (error) {
            console.error('Failed to parse cart from storage event:', error)
          }
        } else {
          setCartItems([])
        }
      }
    }

    // Listen for storage events (changes from other tabs)
    window.addEventListener('storage', handleStorageChange)

    // Custom event for same-window updates
    const handleCustomCartUpdate = (e) => {
      console.log('🔄 Cart updated from custom event')
      const savedCart = localStorage.getItem(CART_STORAGE_KEY)
      if (savedCart) {
        try {
          const newCart = JSON.parse(savedCart)
          // Only update if cart actually changed (prevent infinite loop)
          setCartItems(prev => {
            if (JSON.stringify(prev) === JSON.stringify(newCart)) {
              return prev // No change, return same reference to prevent re-render
            }
            return newCart
          })
        } catch (error) {
          console.error('Failed to parse cart:', error)
        }
      } else {
        setCartItems(prev => prev.length === 0 ? prev : [])
      }
    }

    window.addEventListener('cartUpdated', handleCustomCartUpdate)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('cartUpdated', handleCustomCartUpdate)
    }
  }, [])

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems))
    // Dispatch custom event to notify other useCart instances in the same window
    window.dispatchEvent(new CustomEvent('cartUpdated', { detail: cartItems }))
  }, [cartItems])

  const addToCart = (product, quantity = 1) => {
    console.log('🛒 Adding to cart:', { product, quantity })
    
    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.product_id === product.product_id)
      
      if (existingItem) {
        console.log('📦 Item already in cart, updating quantity')
        const updatedItems = prevItems.map(item =>
          item.product_id === product.product_id
            ? { ...item, quantity: Math.min(item.quantity + quantity, product.stock) }
            : item
        )
        console.log('✅ Cart updated:', updatedItems)
        return updatedItems
      }
      
      console.log('🆕 Adding new item to cart')
      const newItems = [...prevItems, { ...product, quantity }]
      console.log('✅ Cart updated:', newItems)
      return newItems
    })
  }

  const removeFromCart = (productId) => {
    console.log('🗑️ Removing from cart:', productId)
    setCartItems(prevItems => {
      const newItems = prevItems.filter(item => item.product_id !== productId)
      console.log('✅ Cart after removal:', newItems)
      return newItems
    })
  }

  const updateQuantity = (productId, newQuantity) => {
    console.log('🔄 Updating quantity:', { productId, newQuantity })
    
    if (newQuantity < 1) {
      removeFromCart(productId)
      return
    }
    
    setCartItems(prevItems => {
      const newItems = prevItems.map(item =>
        item.product_id === productId
          ? { ...item, quantity: Math.min(newQuantity, item.stock) }
          : item
      )
      console.log('✅ Cart after quantity update:', newItems)
      return newItems
    })
  }

  const clearCart = () => {
    setCartItems([])
    localStorage.removeItem(CART_STORAGE_KEY)
  }

  const getCartTotal = () => {
    return cartItems.reduce((total, item) => total + item.price * item.quantity, 0)
  }

  const getCartCount = () => {
    return cartItems.reduce((count, item) => count + item.quantity, 0)
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
