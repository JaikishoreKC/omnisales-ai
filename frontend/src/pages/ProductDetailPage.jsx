import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProductById } from '../services/api'

const ProductDetailPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [quantity, setQuantity] = useState(1)

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getProductById(id)
        setProduct(data)
      } catch (err) {
        console.error('Error fetching product:', err)
        setError('Product not found')
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id])

  const handleAddToCart = () => {
    alert(`Added ${quantity} × ${product.name} to cart!`)
  }

  const handleBuyNow = () => {
    alert('Proceeding to checkout...')
    navigate('/cart')
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div className="w-full h-96 bg-gray-200 rounded-lg"></div>
            <div className="space-y-4">
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          {error || 'Product Not Found'}
        </h1>
        <button
          onClick={() => navigate('/products')}
          className="text-blue-600 hover:underline"
        >
          ← Back to Products
        </button>
      </div>
    )
  }

  // Generate product image and details
  const productImage = `https://via.placeholder.com/600x600?text=${encodeURIComponent(product.name.split(' ').slice(0, 2).join(' '))}`
  const rating = 4.5 + Math.random()
  const reviews = Math.floor(50 + Math.random() * 500)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="mb-6 text-sm text-gray-600">
        <button onClick={() => navigate('/products')} className="hover:text-blue-600">
          Products
        </button>
        <span className="mx-2">›</span>
        <span>{product.category}</span>
        <span className="mx-2">›</span>
        <span className="text-gray-900">{product.name}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Product Images */}
        <div>
          <div className="bg-white rounded-lg p-8 shadow-md">
            <img
              src={productImage}
              alt={product.name}
              className="w-full h-auto rounded-lg"
            />
          </div>
        </div>

        {/* Product Info */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>

          {/* Rating */}
          <div className="flex items-center space-x-2 mb-4">
            <div className="flex text-yellow-400">
              {'⭐'.repeat(Math.floor(rating))}
            </div>
            <span className="text-gray-600">
              {rating.toFixed(1)} ({reviews} reviews)
            </span>
          </div>

          {/* Price */}
          <div className="mb-6">
            <span className="text-4xl font-bold text-gray-900">${product.price}</span>
            <span className="ml-2 text-sm text-gray-500">Free shipping</span>
          </div>

          {/* Stock */}
          <div className="mb-6">
            {product.stock > 0 ? (
              <span className="text-green-600 font-medium">
                ✓ In Stock ({product.stock} available)
              </span>
            ) : (
              <span className="text-red-600 font-medium">✗ Out of Stock</span>
            )}
          </div>

          {/* Description */}
          <p className="text-gray-700 mb-6">
            Premium quality {product.category} from {product.name.split(' ')[1]} brand.
            Perfect for everyday use with excellent durability and style.
          </p>

          {/* Quantity */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-10 h-10 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                −
              </button>
              <span className="text-xl font-semibold w-12 text-center">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                className="w-10 h-10 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                +
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-4 mb-8">
            <button
              onClick={handleAddToCart}
              disabled={product.stock === 0}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Add to Cart
            </button>
            <button
              onClick={handleBuyNow}
              disabled={product.stock === 0}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Buy Now
            </button>
          </div>

          {/* Product Details */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Product Details</h3>
            <dl className="space-y-2">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <dt className="text-gray-600">Category</dt>
                <dd className="text-gray-900 font-medium capitalize">{product.category}</dd>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <dt className="text-gray-600">Product ID</dt>
                <dd className="text-gray-900 font-medium">{product.product_id.substring(0, 8)}...</dd>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <dt className="text-gray-600">Availability</dt>
                <dd className="text-gray-900 font-medium">{product.stock > 0 ? 'In Stock' : 'Out of Stock'}</dd>
              </div>
              <div className="flex justify-between py-2">
                <dt className="text-gray-600">Shipping</dt>
                <dd className="text-green-600 font-medium">Free</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      {/* Ask AI Banner */}
      <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-2">Have Questions About This Product?</h2>
        <p className="mb-4">Ask our AI assistant for detailed information, comparisons, or recommendations!</p>
        <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
          💬 Chat with AI
        </button>
      </div>
    </div>
  )
}

export default ProductDetailPage
