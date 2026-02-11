import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY || 'CxFn1QSd0rRCQWieaf_e7pJiPrESsIaPqaYRHgUPpDs'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`
  }
})

export const sendChatMessage = async (data) => {
  const response = await api.post('/chat', data)
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export const getProducts = async (params = {}) => {
  const { category, search, limit = 20, skip = 0 } = params
  const queryParams = new URLSearchParams()
  
  if (category) queryParams.append('category', category)
  if (search) queryParams.append('search', search)
  queryParams.append('limit', limit)
  queryParams.append('skip', skip)
  
  const response = await api.get(`/products?${queryParams.toString()}`)
  return response.data
}

export const getProductById = async (productId) => {
  const response = await api.get(`/products/${productId}`)
  return response.data
}

export default api
