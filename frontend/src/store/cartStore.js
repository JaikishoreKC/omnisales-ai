import { create } from 'zustand'
import { getCart, addCartItem, updateCartItem, removeCartItem, clearCart as clearCartApi } from '../services/api'

const CART_UPDATED_KEY = 'omnisales-cart-updated'

const notifyCartUpdated = () => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(CART_UPDATED_KEY, Date.now().toString())
  }
}

const useCartStore = create((set, get) => ({
  cartItems: [],
  isLoading: false,
  ownerKey: null,

  setOwnerKey: (ownerKey) => set({ ownerKey }),

  setCartItems: (items) => set({ cartItems: Array.isArray(items) ? items : [] }),

  loadCart: async ({ token, sessionId }) => {
    set({ isLoading: true })
    try {
      const data = token
        ? await getCart({ token })
        : await getCart({ sessionId })
      set({ cartItems: Array.isArray(data?.items) ? data.items : [] })
    } finally {
      set({ isLoading: false })
    }
  },

  addToCart: async (product, quantity, { token, sessionId }) => {
    if (!product?.product_id) {
      throw new Error('Invalid product_id')
    }
    const safeQuantity = Number(quantity)
    if (!Number.isFinite(safeQuantity) || safeQuantity <= 0) {
      throw new Error('Invalid quantity')
    }
    const data = await addCartItem(
      { product_id: product.product_id, quantity: safeQuantity },
      token ? { token } : { sessionId }
    )
    if (Array.isArray(data?.items)) {
      set({ cartItems: data.items })
    } else {
      await get().loadCart(token ? { token } : { sessionId })
    }
    notifyCartUpdated()
  },

  removeFromCart: async (productId, { token, sessionId }) => {
    if (!productId) {
      throw new Error('Invalid product_id')
    }
    const data = await removeCartItem(
      productId,
      token ? { token } : { sessionId }
    )
    if (Array.isArray(data?.items)) {
      set({ cartItems: data.items })
    } else {
      await get().loadCart(token ? { token } : { sessionId })
    }
    notifyCartUpdated()
  },

  updateQuantity: async (productId, quantity, { token, sessionId }) => {
    if (!productId) {
      throw new Error('Invalid product_id')
    }
    const safeQuantity = Number(quantity)
    if (!Number.isFinite(safeQuantity) || safeQuantity <= 0) {
      throw new Error('Invalid quantity')
    }
    const data = await updateCartItem(
      { product_id: productId, quantity: safeQuantity },
      token ? { token } : { sessionId }
    )
    if (Array.isArray(data?.items)) {
      set({ cartItems: data.items })
    } else {
      await get().loadCart(token ? { token } : { sessionId })
    }
    notifyCartUpdated()
  },

  clearCart: async ({ token, sessionId }) => {
    await clearCartApi(token ? { token } : { sessionId })
    await get().loadCart(token ? { token } : { sessionId })
    notifyCartUpdated()
  },

  getCartTotal: () => {
    const items = get().cartItems
    return items.reduce((total, item) => {
      const price = Number(item.price) || 0
      const qty = Number(item.quantity) || 0
      return total + price * qty
    }, 0)
  },

  getCartCount: () => {
    const items = get().cartItems
    return items.reduce((count, item) => count + (Number(item.quantity) || 0), 0)
  }
}))

export default useCartStore