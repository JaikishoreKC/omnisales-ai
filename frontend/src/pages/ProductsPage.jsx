import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { getProducts } from '../services/api'
import useChatStore from '../store/chatStore'

const ProductsPage = () => {
  const [searchParams] = useSearchParams()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const pageSize = 20
  const maxPageButtons = 5
  const openAssistant = useChatStore((state) => state.openAssistant)

  const categories = [
    { id: 'all', name: 'All Products', icon: '🛍️' },
    { id: 'electronics', name: 'Electronics', icon: '💻' },
    { id: 'shirts', name: 'Shirts', icon: '👕' },
    { id: 'shoes', name: 'Shoes', icon: '👟' },
    { id: 'jeans', name: 'Jeans', icon: '👖' }
  ]

  const searchQuery = searchParams.get('search') || ''
  const categoryParam = searchParams.get('category') || 'all'

  // Set category from URL on mount
  useEffect(() => {
    if (categoryParam && categoryParam !== selectedCategory) {
      setSelectedCategory(categoryParam)
    }
  }, [categoryParam])

  useEffect(() => {
    setPage(1)
  }, [selectedCategory, searchQuery])

  useEffect(() => {
    let isActive = true

    const fetchProducts = async () => {
      setLoading(true)
      setError(null)
      try {
        const params = {
          limit: pageSize,
          skip: (page - 1) * pageSize
        }
        
        if (selectedCategory !== 'all') {
          params.category = selectedCategory
        }
        
        if (searchQuery) {
          params.search = searchQuery
        }
        
        const data = await getProducts(params)
        if (!isActive) return
        setProducts(data.products || [])
        setTotalPages(data.pages || 1)
        setTotalCount(data.total || 0)
      } catch (err) {
        if (!isActive) return
        console.error('Error fetching products:', err)
        setError('Failed to load products. Please try again.')
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    fetchProducts()
    return () => {
      isActive = false
    }
  }, [selectedCategory, searchQuery, page])

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Our Products</h1>
        <p className="text-gray-600">Discover amazing products with AI-powered assistance</p>
        {searchQuery && (
          <p className="mt-2 text-sm text-blue-600">
            Search results for: &quot;{searchQuery}&quot;
          </p>
        )}
      </div>

      {/* Categories */}
      <div className="mb-8 overflow-x-auto">
        <div className="flex space-x-3 pb-2">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-6 py-3 rounded-lg font-medium transition whitespace-nowrap ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {category.icon} {category.name}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <div key={i} className="bg-white rounded-lg p-4 animate-pulse">
              <div className="w-full h-48 bg-gray-200 rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16 bg-red-50 rounded-lg">
          <p className="text-red-600 text-lg">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 text-blue-600 hover:underline"
          >
            Try Again
          </button>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">No products found</p>
          <p className="text-gray-400 text-sm mt-2">Try a different category or search</p>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
            <span>Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, totalCount)} of {totalCount}</span>
            <span>Page {page} of {totalPages}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map(product => (
              <Link key={product.product_id} to={`/products/${product.product_id}`}>
                <ProductCard product={{
                  ...product,
                  image: product.image || `https://via.placeholder.com/300x300?text=${encodeURIComponent(product.name.split(' ').slice(0, 2).join(' '))}`,
                  rating: product.rating || 4.5,
                  description: product.description || `${product.category} - ${product.name}`
                }} />
              </Link>
            ))}
          </div>
          <div className="mt-8 flex items-center justify-center gap-3">
            <button
              onClick={() => setPage(1)}
              disabled={page === 1}
              className="px-3 py-2 rounded border text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              First
            </button>
            <button
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={page === 1}
              className="px-3 py-2 rounded border text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Prev
            </button>
            {Array.from({ length: Math.min(maxPageButtons, totalPages) }, (_, index) => {
              const halfRange = Math.floor(maxPageButtons / 2)
              const startPage = Math.max(1, Math.min(page - halfRange, totalPages - maxPageButtons + 1))
              const pageNumber = startPage + index
              return (
                <button
                  key={pageNumber}
                  onClick={() => setPage(pageNumber)}
                  className={`px-3 py-2 rounded border text-sm ${
                    pageNumber === page
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {pageNumber}
                </button>
              )
            })}
            <button
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={page >= totalPages}
              className="px-3 py-2 rounded border text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
            <button
              onClick={() => setPage(totalPages)}
              disabled={page >= totalPages}
              className="px-3 py-2 rounded border text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Last
            </button>
          </div>
        </div>
      )}

      {/* Help Banner */}
      <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-2">Need Help Finding Products?</h2>
        <p className="mb-4">Ask our AI assistant! It can help you find exactly what you need.</p>
        <button
          onClick={openAssistant}
          className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
        >
          💬 Chat with AI Assistant
        </button>
      </div>
    </div>
  )
}

export default ProductsPage
