import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const UserDetailPage = () => {
  const { userId } = useParams()
  const { isAdmin, token, user } = useAuth()
  const navigate = useNavigate()
  const [userDetails, setUserDetails] = useState(null)
  const [currentOrders, setCurrentOrders] = useState([])
  const [pastOrders, setPastOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('current')

  // Determine if viewing own profile or as admin
  const isOwnProfile = userId === user?.user_id || (!userId && user)
  const targetUserId = userId || user?.user_id

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    
    // Check access: must be own profile or admin
    if (userId && userId !== user?.user_id && !isAdmin()) {
      navigate('/')
      return
    }
    
    fetchUserDetails()
  }, [targetUserId])

  const fetchUserDetails = async () => {
    setLoading(true)
    setError(null)
    try {
      // Admin can view any user, regular users use their own endpoint
      const endpoint = isAdmin() && userId 
        ? `${API_BASE_URL}/admin/users/${targetUserId}`
        : `${API_BASE_URL}/profile/${targetUserId || user?.user_id}`
      
      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUserDetails(response.data.user)
      setCurrentOrders(response.data.current_orders || [])
      setPastOrders(response.data.past_orders || [])
    } catch (err) {
      console.error('Failed to fetch user details:', err)
      setError(err.response?.data?.detail || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const statusColors = {
      delivered: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return statusColors[status] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-4">Loading profile...</p>
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
          onClick={() => navigate(isAdmin() ? '/admin' : '/')}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          ← Go Back
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Back Button */}
      <button
        onClick={() => navigate(isAdmin() && !isOwnProfile ? '/admin' : '/')}
        className="mb-6 flex items-center text-blue-600 hover:text-blue-800"
      >
        <span className="mr-2">←</span> {isAdmin() && !isOwnProfile ? 'Back to Admin Dashboard' : 'Back to Home'}
      </button>

      {/* Admin Badge */}
      {isAdmin() && !isOwnProfile && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-blue-800 text-sm font-semibold">👤 Viewing as Admin</p>
        </div>
      )}

      {/* User Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center mb-6">
          <div className="h-20 w-20 rounded-full bg-blue-500 flex items-center justify-center text-white text-3xl font-bold">
            {userDetails?.name ? userDetails.name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="ml-6">
            <h1 className="text-3xl font-bold text-gray-900">
              {userDetails?.name || 'Unknown User'}
              {isOwnProfile && <span className="text-xl text-gray-500 ml-2">(You)</span>}
            </h1>
            <p className="text-gray-600">{userDetails?.email || 'No email'}</p>
            <div className="mt-2">
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                userDetails?.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
              }`}>
                {userDetails?.role ? userDetails.role.toUpperCase() : 'CUSTOMER'}
              </span>
            </div>
          </div>
        </div>

        {/* User Stats */}
        <div className="grid grid-cols-4 gap-4 pt-6 border-t">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{currentOrders.length + pastOrders.length}</p>
            <p className="text-sm text-gray-600">Total Orders</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{currentOrders.length}</p>
            <p className="text-sm text-gray-600">Current Orders</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{pastOrders.length}</p>
            <p className="text-sm text-gray-600">Past Orders</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">
              ${(currentOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0) + 
                 pastOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0)).toFixed(2)}
            </p>
            <p className="text-sm text-gray-600">Total Spent</p>
          </div>
        </div>

        {/* User Info */}
        <div className="mt-6 pt-6 border-t">
          <h3 className="font-semibold text-gray-700 mb-3">Account Information</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">User ID:</span>
              <span className="ml-2 font-mono">{userDetails?.user_id || 'N/A'}</span>
            </div>
            <div>
              <span className="text-gray-600">Joined:</span>
              <span className="ml-2">
                {userDetails?.created_at ? new Date(userDetails.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Status:</span>
              <span className="ml-2">
                <span className={`inline-block px-2 py-1 rounded-full text-xs ${
                  userDetails?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {userDetails?.is_active ? 'ACTIVE' : 'INACTIVE'}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Orders Tabs */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex space-x-4 mb-6 border-b">
          <button
            onClick={() => setActiveTab('current')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'current'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Current Orders ({currentOrders.length})
          </button>
          <button
            onClick={() => setActiveTab('past')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'past'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Past Orders ({pastOrders.length})
          </button>
        </div>

        {/* Current Orders */}
        {activeTab === 'current' && (
          <div className="space-y-4">
            {currentOrders.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No current orders
              </div>
            ) : (
              currentOrders.map(order => (
                <div 
                  key={order.order_id} 
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/orders/${order.order_id}`)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-bold">Order #{order.order_id?.substring(0, 8)}</h4>
                      <p className="text-sm text-gray-600">
                        {order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">${order.total_amount?.toFixed(2) || '0.00'}</p>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(order.status)}`}>
                        {order.status ? order.status.toUpperCase() : 'PENDING'}
                      </span>
                    </div>
                  </div>
                  {order.items && order.items.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-sm font-semibold text-gray-700">Items:</p>
                      {order.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between text-sm bg-gray-50 p-2 rounded">
                          <span>{item.name || 'Unknown'}</span>
                          <span className="text-gray-600">{item.quantity}x ${item.price?.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="mt-3 text-right">
                    <span className="text-blue-600 text-sm hover:underline">
                      View Details →
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Past Orders */}
        {activeTab === 'past' && (
          <div className="space-y-4">
            {pastOrders.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No past orders
              </div>
            ) : (
              pastOrders.map(order => (
                <div 
                  key={order.order_id} 
                  className="border rounded-lg p-4 bg-gray-50 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/orders/${order.order_id}`)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-bold">Order #{order.order_id?.substring(0, 8)}</h4>
                      <p className="text-sm text-gray-600">
                        {order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">${order.total_amount?.toFixed(2) || '0.00'}</p>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(order.status)}`}>
                        {order.status ? order.status.toUpperCase() : 'PENDING'}
                      </span>
                    </div>
                  </div>
                  {order.items && order.items.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-sm font-semibold text-gray-700">Items:</p>
                      {order.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between text-sm bg-white p-2 rounded">
                          <span>{item.name || 'Unknown'}</span>
                          <span className="text-gray-600">{item.quantity}x ${item.price?.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="mt-3 text-right">
                    <span className="text-blue-600 text-sm hover:underline">
                      View Details →
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default UserDetailPage
