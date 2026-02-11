import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useConfirm } from '../context/ConfirmContext'
import { useToast } from '../context/ToastContext'
import {
  getProductsByQuery,
  getAdminOrders,
  getAdminUsers,
  createAdminProduct,
  deleteAdminProduct,
  updateAdminProduct
} from '../services/api'

const AdminPage = () => {
  const { isAdmin, token } = useAuth()
  const { confirm } = useConfirm()
  const { success, error: showError } = useToast()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('products')
  const [products, setProducts] = useState([])
  const [orders, setOrders] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showAddProduct, setShowAddProduct] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchQueryOrders, setSearchQueryOrders] = useState('')
  const [searchQueryUsers, setSearchQueryUsers] = useState('')
  const [selectedProducts, setSelectedProducts] = useState([])
  
  // Pagination state
  const [productsPage, setProductsPage] = useState(1)
  const [ordersPage, setOrdersPage] = useState(1)
  const [usersPage, setUsersPage] = useState(1)
  const itemsPerPage = 10
  
  // Total counts from backend
  const [productsTotal, setProductsTotal] = useState(0)
  const [ordersTotal, setOrdersTotal] = useState(0)
  const [usersTotal, setUsersTotal] = useState(0)

  // Filtering and sorting state
  const [productCategory, setProductCategory] = useState('all')
  const [productStockFilter, setProductStockFilter] = useState('all')
  const [productSortBy, setProductSortBy] = useState('name')
  const [productSortOrder, setProductSortOrder] = useState('asc')
  
  const [orderStatusFilter, setOrderStatusFilter] = useState('all')
  const [orderSortBy, setOrderSortBy] = useState('created_at')
  const [orderSortOrder, setOrderSortOrder] = useState('desc')
  
  const [userRoleFilter, setUserRoleFilter] = useState('all')
  const [userSortBy, setUserSortBy] = useState('created_at')
  const [userSortOrder, setUserSortOrder] = useState('desc')


  const [newProduct, setNewProduct] = useState({
    name: '',
    category: 'electronics',
    price: '',
    stock: ''
  })

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/')
      return
    }
    fetchData()
  }, [activeTab, productsPage, ordersPage, usersPage, productCategory, productStockFilter, productSortBy, productSortOrder, orderStatusFilter, orderSortBy, orderSortOrder, userRoleFilter, userSortBy, userSortOrder])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      if (activeTab === 'products') {
        const skip = (productsPage - 1) * itemsPerPage
        const params = new URLSearchParams({
          limit: itemsPerPage,
          skip: skip,
          sort_by: productSortBy,
          sort_order: productSortOrder
        })
        if (productCategory !== 'all') params.append('category', productCategory)
        if (productStockFilter !== 'all') params.append('stock_filter', productStockFilter)
        
        const data = await getProductsByQuery(params.toString())
        setProducts(data.products || [])
        setProductsTotal(data.total || 0)
      } else if (activeTab === 'orders') {
        const skip = (ordersPage - 1) * itemsPerPage
        const params = new URLSearchParams({
          limit: itemsPerPage,
          skip: skip,
          sort_by: orderSortBy,
          sort_order: orderSortOrder
        })
        if (orderStatusFilter !== 'all') params.append('status', orderStatusFilter)
        
        const data = await getAdminOrders(params.toString(), token)
        setOrders(data.orders || [])
        setOrdersTotal(data.total || 0)
      } else if (activeTab === 'users') {
        const skip = (usersPage - 1) * itemsPerPage
        const params = new URLSearchParams({
          limit: itemsPerPage,
          skip: skip,
          sort_by: userSortBy,
          sort_order: userSortOrder
        })
        if (userRoleFilter !== 'all') params.append('role', userRoleFilter)
        
        const data = await getAdminUsers(params.toString(), token)
        setUsers(data.users || [])
        setUsersTotal(data.total || 0)
      }
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setError(err.message || 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const handleAddProduct = async (e) => {
    e.preventDefault()
    try {
      await createAdminProduct({
        ...newProduct,
        price: parseFloat(newProduct.price),
        stock: parseInt(newProduct.stock)
      }, token)
      setShowAddProduct(false)
      setNewProduct({ name: '', category: 'electronics', price: '', stock: '' })
      success('Product added successfully!')
      fetchData()
    } catch (err) {
      console.error('Failed to add product:', err)
      showError(err.message || 'Failed to add product')
    }
  }

  const handleDeleteProduct = async (productId) => {
    const confirmed = await confirm({
      title: 'Delete Product',
      message: 'Are you sure you want to delete this product? This action cannot be undone.',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      type: 'danger'
    })
    
    if (!confirmed) return
    
    try {
      await deleteAdminProduct(productId, token)
      success('Product deleted successfully!')
      fetchData()
    } catch (err) {
      console.error('Failed to delete product:', err)
      showError(err.message || 'Failed to delete product')
    }
  }

  const handleUpdateStock = async (productId, newStock) => {
    try {
      await updateAdminProduct(productId, { stock: parseInt(newStock) }, token)
      success('Stock updated successfully!')
      fetchData()
    } catch (err) {
      console.error('Failed to update stock:', err)
      showError(err.message || 'Failed to update stock')
    }
  }

  const handleSelectProduct = (productId) => {
    setSelectedProducts(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    )
  }

  const handleSelectAll = () => {
    if (selectedProducts.length === filteredProducts.length) {
      setSelectedProducts([])
    } else {
      setSelectedProducts(filteredProducts.map(p => p.product_id))
    }
  }

  const handleDeleteSelected = async () => {
    if (!selectedProducts.length) return
    
    const confirmed = await confirm({
      title: 'Delete Multiple Products',
      message: `Are you sure you want to delete ${selectedProducts.length} product(s)? This action cannot be undone.`,
      confirmText: 'Delete All',
      cancelText: 'Cancel',
      type: 'danger'
    })
    
    if (!confirmed) return
    
    try {
      await Promise.all(
        selectedProducts.map(productId => deleteAdminProduct(productId, token))
      )
      setSelectedProducts([])
      success(`Successfully deleted ${selectedProducts.length} product(s)!`)
      fetchData()
    } catch (err) {
      console.error('Failed to delete products:', err)
      showError(err.message || 'Failed to delete some products')
    }
  }

  // Filter products based on search query (client-side, filters current page only)
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Filter orders based on search query (client-side, filters current page only)
  const filteredOrders = orders.filter(order => {
    const searchLower = searchQueryOrders.toLowerCase()
    const orderId = (order.order_id || '').toLowerCase()
    const userName = (order.shipping_address?.name || order.shipping_address?.fullName || '').toLowerCase()
    const email = (order.shipping_address?.email || '').toLowerCase()
    const status = (order.status || '').toLowerCase()
    
    return orderId.includes(searchLower) || 
           userName.includes(searchLower) || 
           email.includes(searchLower) ||
           status.includes(searchLower)
  })

  // Filter users based on search query (client-side, filters current page only)
  const filteredUsers = users.filter(user => {
    const searchLower = searchQueryUsers.toLowerCase()
    const name = (user.name || '').toLowerCase()
    const email = (user.email || '').toLowerCase()
    const userId = (user.user_id || '').toLowerCase()
    
    return name.includes(searchLower) || 
           email.includes(searchLower) ||
           userId.includes(searchLower)
  })

  // Pagination calculations using server-side totals
  const totalProductsPages = Math.ceil(productsTotal / itemsPerPage)
  const totalOrdersPages = Math.ceil(ordersTotal / itemsPerPage)
  const totalUsersPages = Math.ceil(usersTotal / itemsPerPage)


  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

      {/* Tabs */}
      <div className="flex space-x-4 mb-8 border-b">
        <button
          onClick={() => setActiveTab('products')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'products'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Products
        </button>
        <button
          onClick={() => setActiveTab('orders')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'orders'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Orders
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'users'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Users
        </button>
      </div>

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Products Management</h2>
            <div className="flex space-x-3">
              {selectedProducts.length > 0 && (
                <button
                  onClick={handleDeleteSelected}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                >
                  Delete Selected ({selectedProducts.length})
                </button>
              )}
              <button
                onClick={() => setShowAddProduct(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                + Add Product
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search products by name or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filters and Sorting */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-gray-700">Filters & Sorting</h3>
              <button
                onClick={() => {
                  setProductCategory('all')
                  setProductStockFilter('all')
                  setProductSortBy('name')
                  setProductSortOrder('asc')
                  setProductsPage(1)
                }}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Reset Filters
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={productCategory}
                onChange={(e) => {
                  setProductCategory(e.target.value)
                  setProductsPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Categories</option>
                <option value="electronics">Electronics</option>
                <option value="shirts">Shirts</option>
                <option value="shoes">Shoes</option>
                <option value="jeans">Jeans</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Stock Status</label>
              <select
                value={productStockFilter}
                onChange={(e) => {
                  setProductStockFilter(e.target.value)
                  setProductsPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Stock Levels</option>
                <option value="in_stock">In Stock (&gt;10)</option>
                <option value="low_stock">Low Stock (1-10)</option>
                <option value="out_of_stock">Out of Stock</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={productSortBy}
                onChange={(e) => {
                  setProductSortBy(e.target.value)
                  setProductsPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="name">Name</option>
                <option value="price">Price</option>
                <option value="stock">Stock</option>
                <option value="category">Category</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Order</label>
              <select
                value={productSortOrder}
                onChange={(e) => {
                  setProductSortOrder(e.target.value)
                  setProductsPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="asc">Ascending (A-Z, Low-High)</option>
                <option value="desc">Descending (Z-A, High-Low)</option>
              </select>
            </div>
          </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 mt-2">Loading products...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {/* Add Product Modal */}
          {showAddProduct && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-8 max-w-md w-full">
                <h3 className="text-xl font-bold mb-4">Add New Product</h3>
                <form onSubmit={handleAddProduct} className="space-y-4">
                  <input
                    type="text"
                    placeholder="Product Name"
                    value={newProduct.name}
                    onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                  <select
                    value={newProduct.category}
                    onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="electronics">Electronics</option>
                    <option value="shirts">Shirts</option>
                    <option value="shoes">Shoes</option>
                    <option value="jeans">Jeans</option>
                  </select>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Price"
                    value={newProduct.price}
                    onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="number"
                    placeholder="Stock"
                    value={newProduct.stock}
                    onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                    >
                      Add Product
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowAddProduct(false)}
                      className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Products Table */}
          {!loading && !error && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedProducts.length === filteredProducts.length && filteredProducts.length > 0}
                        onChange={handleSelectAll}
                        className="rounded"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredProducts.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                        {searchQuery ? 'No products found matching your search' : 'No products available'}
                      </td>
                    </tr>
                  ) : (
                    filteredProducts.map(product => (
                      <tr key={product.product_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <input
                            type="checkbox"
                            checked={selectedProducts.includes(product.product_id)}
                            onChange={() => handleSelectProduct(product.product_id)}
                            className="rounded"
                          />
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{product.name}</td>
                        <td className="px-6 py-4 text-sm text-gray-600 capitalize">{product.category}</td>
                        <td className="px-6 py-4 text-sm text-gray-900">${product.price}</td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            defaultValue={product.stock}
                            onBlur={(e) => handleUpdateStock(product.product_id, e.target.value)}
                            className="w-20 px-2 py-1 border rounded"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => handleDeleteProduct(product.product_id)}
                            className="text-red-600 hover:underline text-sm"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Products Pagination Controls */}
          {!loading && productsTotal > itemsPerPage && (
            <div className="mt-6 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setProductsPage(1)}
                  disabled={productsPage === 1}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  First
                </button>
                <button
                  onClick={() => setProductsPage(prev => Math.max(1, prev - 1))}
                  disabled={productsPage === 1}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                {/* Page Numbers */}
                <div className="flex space-x-1">
                  {[...Array(Math.min(5, totalProductsPages))].map((_, idx) => {
                    let pageNum
                    if (totalProductsPages <= 5) {
                      pageNum = idx + 1
                    } else if (productsPage <= 3) {
                      pageNum = idx + 1
                    } else if (productsPage >= totalProductsPages - 2) {
                      pageNum = totalProductsPages - 4 + idx
                    } else {
                      pageNum = productsPage - 2 + idx
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setProductsPage(pageNum)}
                        className={`px-3 py-2 border rounded-lg ${
                          productsPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>

                <button
                  onClick={() => setProductsPage(prev => Math.min(totalProductsPages, prev + 1))}
                  disabled={productsPage === totalProductsPages}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
                <button
                  onClick={() => setProductsPage(totalProductsPages)}
                  disabled={productsPage === totalProductsPages}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Last
                </button>
              </div>
              
              {/* Results Summary */}
              <div className="text-sm text-gray-600">
                Showing {((productsPage - 1) * itemsPerPage) + 1} - {Math.min(productsPage * itemsPerPage, productsTotal)} of {productsTotal} products
              </div>
            </div>
          )}
        </div>
      )}

      {/* Orders Tab */}
      {activeTab === 'orders' && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Orders Management</h2>

          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search orders by order ID, customer name, email, or status..."
              value={searchQueryOrders}
              onChange={(e) => setSearchQueryOrders(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filters and Sorting */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-gray-700">Filters & Sorting</h3>
              <button
                onClick={() => {
                  setOrderStatusFilter('all')
                  setOrderSortBy('created_at')
                  setOrderSortOrder('desc')
                  setOrdersPage(1)
                }}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Reset Filters
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={orderStatusFilter}
                onChange={(e) => {
                  setOrderStatusFilter(e.target.value)
                  setOrdersPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={orderSortBy}
                onChange={(e) => {
                  setOrderSortBy(e.target.value)
                  setOrdersPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Order Date</option>
                <option value="total_amount">Total Amount</option>
                <option value="status">Status</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Order</label>
              <select
                value={orderSortOrder}
                onChange={(e) => {
                  setOrderSortOrder(e.target.value)
                  setOrdersPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="desc">Newest First / Highest Amount</option>
                <option value="asc">Oldest First / Lowest Amount</option>
              </select>
            </div>
          </div>
        </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 mt-2">Loading orders...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {/* Orders List */}
          {!loading && !error && (
            <>
              <div className="space-y-4">
                {filteredOrders.length === 0 ? (
                  <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                    {searchQueryOrders ? 'No orders found matching your search' : 'No orders found'}
                  </div>
                ) : (
                  filteredOrders.map(order => (
                    <div 
                      key={order.order_id} 
                      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
                      onClick={() => navigate(`/orders/${order.order_id}`)}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-bold text-lg">Order #{order.order_id?.substring(0, 8) || 'N/A'}</h3>
                          <p className="text-sm text-gray-600">
                            {order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A'}
                          </p>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-blue-600 text-lg">
                            ${order.total_amount ? order.total_amount.toFixed(2) : '0.00'}
                          </span>
                          <div className="mt-1">
                            <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                              order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              order.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                              order.status === 'shipped' ? 'bg-purple-100 text-purple-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {order.status ? order.status.toUpperCase() : 'PENDING'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Compact Summary */}
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Customer:</span>
                          <p className="font-medium">{order.shipping_address?.name || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="text-gray-600">Items:</span>
                          <p className="font-medium">{order.items?.length || 0} products</p>
                        </div>
                        <div>
                          <span className="text-gray-600">User ID:</span>
                          <p className="font-mono text-xs">{order.user_id?.substring(0, 8) || 'N/A'}</p>
                        </div>
                      </div>

                      <div className="mt-3 text-right">
                        <span className="text-blue-600 text-sm font-medium hover:underline">
                          View Full Details →
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Pagination Controls */}
              {ordersTotal > itemsPerPage && (
                <div className="mt-6 flex justify-center items-center space-x-4">
                  <button
                    onClick={() => setOrdersPage(1)}
                    disabled={ordersPage === 1}
                    className={`px-4 py-2 rounded-lg ${
                      ordersPage === 1
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    ⇤ First
                  </button>
                  <button
                    onClick={() => setOrdersPage(prev => Math.max(1, prev - 1))}
                    disabled={ordersPage === 1}
                    className={`px-4 py-2 rounded-lg ${
                      ordersPage === 1
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    ← Previous
                  </button>
                  
                  <div className="flex items-center space-x-2">
                    {Array.from({ length: Math.min(5, totalOrdersPages) }, (_, i) => {
                      let pageNum
                      if (totalOrdersPages <= 5) {
                        pageNum = i + 1
                      } else if (ordersPage <= 3) {
                        pageNum = i + 1
                      } else if (ordersPage >= totalOrdersPages - 2) {
                        pageNum = totalOrdersPages - 4 + i
                      } else {
                        pageNum = ordersPage - 2 + i
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setOrdersPage(pageNum)}
                          className={`px-3 py-1 rounded ${
                            ordersPage === pageNum
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                  </div>

                  <button
                    onClick={() => setOrdersPage(prev => Math.min(totalOrdersPages, prev + 1))}
                    disabled={ordersPage === totalOrdersPages}
                    className={`px-4 py-2 rounded-lg ${
                      ordersPage === totalOrdersPages
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    Next →
                  </button>
                  <button
                    onClick={() => setOrdersPage(totalOrdersPages)}
                    disabled={ordersPage === totalOrdersPages}
                    className={`px-4 py-2 rounded-lg ${
                      ordersPage === totalOrdersPages
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    Last ⇥
                  </button>
                </div>
              )}

              {/* Results Summary */}
              {ordersTotal > 0 && (
                <p className="text-center text-sm text-gray-600 mt-4">
                  Showing {((ordersPage - 1) * itemsPerPage) + 1} - {Math.min(ordersPage * itemsPerPage, ordersTotal)} of {ordersTotal} orders
                </p>
              )}
            </>
          )}
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Users Management</h2>

          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search users by name, email, or user ID..."
              value={searchQueryUsers}
              onChange={(e) => setSearchQueryUsers(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filters and Sorting */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-gray-700">Filters & Sorting</h3>
              <button
                onClick={() => {
                  setUserRoleFilter('all')
                  setUserSortBy('created_at')
                  setUserSortOrder('desc')
                  setUsersPage(1)
                }}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Reset Filters
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
              <select
                value={userRoleFilter}
                onChange={(e) => {
                  setUserRoleFilter(e.target.value)
                  setUsersPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Roles</option>
                <option value="admin">Admin</option>
                <option value="customer">Customer</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={userSortBy}
                onChange={(e) => {
                  setUserSortBy(e.target.value)
                  setUsersPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Join Date</option>
                <option value="name">Name</option>
                <option value="email">Email</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Order</label>
              <select
                value={userSortOrder}
                onChange={(e) => {
                  setUserSortOrder(e.target.value)
                  setUsersPage(1)
                }}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="desc">Newest First / Z-A</option>
                <option value="asc">Oldest First / A-Z</option>
              </select>
            </div>
          </div>
        </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 mt-2">Loading users...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {/* Users List */}
          {!loading && !error && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                        {searchQueryUsers ? 'No users found matching your search' : 'No users found'}
                      </td>
                    </tr>
                  ) : (
                    filteredUsers.map(user => (
                      <tr 
                        key={user.user_id} 
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => navigate(`/admin/users/${user.user_id}`)}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                              {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">{user.name || 'Unknown'}</p>
                              <p className="text-xs text-gray-500">ID: {user.user_id?.substring(0, 8)}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{user.email || 'N/A'}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                            user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {user.role ? user.role.toUpperCase() : 'CUSTOMER'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/admin/users/${user.user_id}`)
                            }}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View Details →
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Users Pagination Controls */}
          {!loading && usersTotal > itemsPerPage && (
            <div className="mt-6 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setUsersPage(1)}
                  disabled={usersPage === 1}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  First
                </button>
                <button
                  onClick={() => setUsersPage(prev => Math.max(1, prev - 1))}
                  disabled={usersPage === 1}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                {/* Page Numbers */}
                <div className="flex space-x-1">
                  {[...Array(Math.min(5, totalUsersPages))].map((_, idx) => {
                    let pageNum
                    if (totalUsersPages <= 5) {
                      pageNum = idx + 1
                    } else if (usersPage <= 3) {
                      pageNum = idx + 1
                    } else if (usersPage >= totalUsersPages - 2) {
                      pageNum = totalUsersPages - 4 + idx
                    } else {
                      pageNum = usersPage - 2 + idx
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setUsersPage(pageNum)}
                        className={`px-3 py-2 border rounded-lg ${
                          usersPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>

                <button
                  onClick={() => setUsersPage(prev => Math.min(totalUsersPages, prev + 1))}
                  disabled={usersPage === totalUsersPages}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
                <button
                  onClick={() => setUsersPage(totalUsersPages)}
                  disabled={usersPage === totalUsersPages}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Last
                </button>
              </div>
              
              {/* Results Summary */}
              <div className="text-sm text-gray-600">
                Showing {((usersPage - 1) * itemsPerPage) + 1} - {Math.min(usersPage * itemsPerPage, usersTotal)} of {usersTotal} users
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AdminPage
