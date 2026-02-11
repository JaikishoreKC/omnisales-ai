import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const OrderDetailPage = () => {
  const { orderId } = useParams()
  const { token, user, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    fetchOrderDetails()
  }, [orderId])

  const fetchOrderDetails = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`${API_BASE_URL}/orders/${orderId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setOrder(response.data)
    } catch (err) {
      console.error('Failed to fetch order details:', err)
      setError(err.response?.data?.detail || 'Failed to load order details')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      delivered: 'text-green-600',
      pending: 'text-yellow-600',
      processing: 'text-blue-600',
      shipped: 'text-purple-600',
      cancelled: 'text-red-600'
    }
    return colors[status] || 'text-gray-600'
  }

  const getStatusBadge = (status) => {
    const colors = {
      delivered: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getProgressPercentage = (status) => {
    const progress = {
      pending: 25,
      processing: 50,
      shipped: 75,
      delivered: 100,
      cancelled: 0
    }
    return progress[status] || 0
  }

  const getProgressSteps = (status) => {
    const steps = [
      { name: 'Order Placed', key: 'pending', icon: '📦' },
      { name: 'Processing', key: 'processing', icon: '⚙️' },
      { name: 'Shipped', key: 'shipped', icon: '🚚' },
      { name: 'Delivered', key: 'delivered', icon: '✅' }
    ]

    if (status === 'cancelled') {
      return steps.map(step => ({ ...step, completed: false, active: false }))
    }

    const statusOrder = ['pending', 'processing', 'shipped', 'delivered']
    const currentIndex = statusOrder.indexOf(status)

    return steps.map((step, index) => ({
      ...step,
      completed: index < currentIndex,
      active: index === currentIndex
    }))
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-4">Loading order details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
          {error}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          ← Go Back
        </button>
      </div>
    )
  }

  const progressSteps = getProgressSteps(order.status)
  const progressPercentage = getProgressPercentage(order.status)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="mb-6 flex items-center text-blue-600 hover:text-blue-800"
      >
        <span className="mr-2">←</span> Back
      </button>

      {/* Order Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Order #{order.order_id?.substring(0, 8)}</h1>
            <p className="text-gray-600 mt-1">
              Placed on {order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-blue-600">
              ${order.total_amount?.toFixed(2) || '0.00'}
            </p>
            <span className={`inline-block mt-2 px-4 py-2 rounded-full text-sm font-medium ${getStatusBadge(order.status)}`}>
              {order.status ? order.status.toUpperCase() : 'PENDING'}
            </span>
          </div>
        </div>

        {/* Shipping Progress Bar */}
        {order.status !== 'cancelled' && (
          <div className="mt-8">
            <div className="relative">
              {/* Progress Line */}
              <div className="absolute top-8 left-0 w-full h-2 bg-gray-200 rounded-full">
                <div 
                  className="h-full bg-blue-600 rounded-full transition-all duration-1000 ease-in-out"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>

              {/* Progress Steps */}
              <div className="relative flex justify-between">
                {progressSteps.map((step, index) => (
                  <div key={index} className="flex flex-col items-center" style={{ width: '25%' }}>
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl mb-3 transition-all duration-500 ${
                      step.completed 
                        ? 'bg-blue-600 text-white shadow-lg scale-110' 
                        : step.active 
                        ? 'bg-blue-500 text-white shadow-lg animate-pulse scale-110' 
                        : 'bg-gray-200 text-gray-400'
                    }`}>
                      {step.icon}
                    </div>
                    <p className={`text-sm font-medium text-center ${
                      step.completed || step.active ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Cancelled Status */}
        {order.status === 'cancelled' && (
          <div className="mt-8 p-4 bg-red-50 border-l-4 border-red-600 rounded">
            <p className="text-red-800 font-semibold">❌ This order has been cancelled</p>
          </div>
        )}
      </div>

      {/* Order Details Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Shipping Address */}
        {order.shipping_address && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">📍</span> Shipping Address
            </h2>
            <div className="space-y-2 text-gray-700">
              <p className="font-semibold">{order.shipping_address.name}</p>
              <p>{order.shipping_address.email}</p>
              <p>{order.shipping_address.phone}</p>
              <div className="pt-2 mt-2 border-t">
                <p>{order.shipping_address.address}</p>
                <p>
                  {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.zip}
                </p>
                <p>{order.shipping_address.country || 'USA'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Order Summary */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <span className="mr-2">💰</span> Order Summary
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between text-gray-700">
              <span>Subtotal:</span>
              <span className="font-medium">
                ${((order.total_amount || 0) / 1.08).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-gray-700">
              <span>Tax (8%):</span>
              <span className="font-medium">
                ${((order.total_amount || 0) * 0.08 / 1.08).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-gray-700">
              <span>Shipping:</span>
              <span className="font-medium text-green-600">FREE</span>
            </div>
            <div className="pt-3 mt-3 border-t flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span className="text-blue-600">${order.total_amount?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="pt-3 mt-3 border-t text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Payment Status:</span>
                <span className="font-medium text-green-600">PAID ✓</span>
              </div>
              <div className="flex justify-between mt-2">
                <span>Order ID:</span>
                <span className="font-mono text-xs">{order.order_id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Order Items */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <span className="mr-2">📦</span> Order Items ({order.items?.length || 0})
        </h2>
        <div className="space-y-4">
          {order.items && order.items.length > 0 ? (
            order.items.map((item, index) => (
              <div key={index} className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50 transition">
                <div className="flex-shrink-0 w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center text-3xl">
                  📦
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{item.name || 'Unknown Product'}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Product ID: {item.product_id?.substring(0, 8) || 'N/A'}
                  </p>
                  <p className="text-sm text-gray-600">
                    Quantity: <span className="font-medium">{item.quantity || 1}</span>
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">
                    ${item.price ? item.price.toFixed(2) : '0.00'}
                  </p>
                  <p className="text-sm text-gray-600">
                    Subtotal: ${((item.price || 0) * (item.quantity || 1)).toFixed(2)}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">No items in this order</p>
          )}
        </div>
      </div>

      {/* Admin Actions (if admin) */}
      {isAdmin() && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
          <p className="text-blue-800 font-semibold mb-2">👤 Admin View</p>
          <p className="text-sm text-blue-700">
            User ID: <span className="font-mono">{order.user_id}</span>
          </p>
          <button
            onClick={() => navigate(`/profile/${order.user_id}`)}
            className="mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View Customer Profile →
          </button>
        </div>
      )}
    </div>
  )
}

export default OrderDetailPage
