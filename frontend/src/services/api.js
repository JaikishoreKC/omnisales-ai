import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

const getAuthToken = () => {
  const token = localStorage.getItem('token')
  return token ? token.trim() : ''
}

const buildAuthHeaders = (token) =>
  token ? { Authorization: `Bearer ${token}` } : {}

const buildSessionHeaders = (sessionId) =>
  sessionId ? { 'X-Session-Id': sessionId } : {}

const buildUserTokenHeaders = (token) =>
  token ? { 'X-User-Token': token } : {}

const unwrapApiResponse = (payload) => {
  if (payload && typeof payload === 'object' && Object.prototype.hasOwnProperty.call(payload, 'success')) {
    if (payload.success === false) {
      throw new ApiError(payload.error || payload.message || 'Request failed', payload.status, payload)
    }
    if (payload.data !== undefined && payload.data !== null) {
      return payload.data
    }
  }
  return payload
}

const normalizeError = (error) => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const data = error.response?.data
    const message = data?.error || data?.message || data?.detail || error.message || 'Request failed'
    return new ApiError(message, status, data)
  }
  return new ApiError(error?.message || 'Unexpected error')
}

const request = async (config) => {
  try {
    const response = await api.request(config)
    return unwrapApiResponse(response.data)
  } catch (error) {
    throw normalizeError(error)
  }
}

const emitAuthExpired = () => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth:expired'))
  }
}

const requestWithAuth = async (config, token) => {
  const authToken = token || getAuthToken()
  if (!authToken) {
    throw new ApiError('Authentication required', 401)
  }
  try {
    return await request({
      ...config,
      headers: {
        ...config.headers,
        ...buildAuthHeaders(authToken)
      }
    })
  } catch (error) {
    if (error?.status === 401) {
      emitAuthExpired()
    }
    throw error
  }
}

const requestWithSession = async (config, sessionId) => {
  if (!sessionId) {
    throw new ApiError('session_id is required', 400)
  }
  return request({
    ...config,
    headers: {
      ...config.headers,
      ...buildSessionHeaders(sessionId)
    }
  })
}

const requestWithCartContext = async (config, token, sessionId) => {
  if (token) {
    return requestWithAuth(config, token)
  }
  return requestWithSession(config, sessionId)
}

export const sendChatMessage = async (data) => {
  const authToken = getAuthToken()
  const sessionId = data?.session_id
  return request({
    method: 'post',
    url: '/chat',
    data,
    headers: {
      ...buildUserTokenHeaders(authToken),
      ...buildSessionHeaders(sessionId)
    }
  })
}

export const getChatHistory = async ({ token, sessionId, limit } = {}) => {
  const params = { session_id: sessionId }
  if (limit) {
    params.limit = limit
  }
  if (token) {
    return requestWithAuth({ method: 'get', url: '/chat/history', params }, token)
  }
  return requestWithSession({ method: 'get', url: '/chat/history', params }, sessionId)
}

export const healthCheck = async () => request({ method: 'get', url: '/health' })

export const getProducts = async (params = {}) => {
  const { category, search, limit = 20, skip = 0 } = params
  const queryParams = new URLSearchParams()

  if (category) queryParams.append('category', category)
  if (search) queryParams.append('search', search)
  queryParams.append('limit', limit)
  queryParams.append('skip', skip)

  return request({ method: 'get', url: `/products?${queryParams.toString()}` })
}

export const getProductsByQuery = async (query) =>
  request({ method: 'get', url: `/products?${query}` })

export const getProductById = async (productId) =>
  request({ method: 'get', url: `/products/${productId}` })

export const createReview = async (reviewData, token) =>
  requestWithAuth({ method: 'post', url: '/reviews', data: reviewData }, token)

export const getProductReviews = async (productId) =>
  request({ method: 'get', url: `/reviews/${productId}` })

export const loginUser = async (payload) =>
  request({ method: 'post', url: '/auth/login', data: payload })

export const registerUser = async (payload) =>
  request({ method: 'post', url: '/auth/register', data: payload })

export const requestPasswordReset = async (payload) =>
  request({ method: 'post', url: '/auth/request-reset', data: payload })

export const resetPassword = async (payload) =>
  request({ method: 'post', url: '/auth/reset-password', data: payload })

export const changePassword = async (payload, token) =>
  requestWithAuth({ method: 'post', url: '/auth/change-password', data: payload }, token)

export const getOrders = async (token) =>
  requestWithAuth({ method: 'get', url: '/orders' }, token)

export const getOrderById = async (orderId, token) =>
  requestWithAuth({ method: 'get', url: `/orders/${orderId}` }, token)

export const createOrder = async (payload, token) =>
  requestWithAuth({ method: 'post', url: '/orders', data: payload }, token)

export const getAdminOrders = async (query, token) =>
  requestWithAuth({ method: 'get', url: `/admin/orders?${query}` }, token)

export const getAdminUsers = async (query, token) =>
  requestWithAuth({ method: 'get', url: `/admin/users?${query}` }, token)

export const getAdminUserDetail = async (userId, token) =>
  requestWithAuth({ method: 'get', url: `/admin/users/${userId}` }, token)

export const createAdminProduct = async (payload, token) =>
  requestWithAuth({ method: 'post', url: '/admin/products', data: payload }, token)

export const deleteAdminProduct = async (productId, token) =>
  requestWithAuth({ method: 'delete', url: `/admin/products/${productId}` }, token)

export const updateAdminProduct = async (productId, payload, token) =>
  requestWithAuth({ method: 'patch', url: `/admin/products/${productId}`, data: payload }, token)

export const getProfile = async (userId, token) =>
  requestWithAuth({ method: 'get', url: `/profile/${userId}` }, token)

export const getCart = async ({ token, sessionId } = {}) =>
  requestWithCartContext({ method: 'get', url: '/cart' }, token, sessionId)

export const addCartItem = async (payload, { token, sessionId } = {}) =>
  requestWithCartContext({ method: 'post', url: '/cart/add', data: payload }, token, sessionId)

export const updateCartItem = async (payload, { token, sessionId } = {}) =>
  requestWithCartContext({ method: 'patch', url: '/cart/update', data: payload }, token, sessionId)

export const removeCartItem = async (productId, { token, sessionId } = {}) =>
  requestWithCartContext({ method: 'delete', url: `/cart/remove/${productId}` }, token, sessionId)

export const clearCart = async ({ token, sessionId } = {}) =>
  requestWithCartContext({ method: 'delete', url: '/cart/clear' }, token, sessionId)

export default api
