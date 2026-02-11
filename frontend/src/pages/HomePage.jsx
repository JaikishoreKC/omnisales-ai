import React from 'react'
import { Link } from 'react-router-dom'

const HomePage = () => {
  const categories = [
    { name: 'Electronics', icon: '💻', color: 'from-blue-500 to-purple-500' },
    { name: 'Clothing', icon: '👕', color: 'from-pink-500 to-red-500' },
    { name: 'Home', icon: '🏠', color: 'from-green-500 to-teal-500' },
    { name: 'Sports', icon: '⚽', color: 'from-orange-500 to-yellow-500' }
  ]

  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Shopping',
      description: 'Get personalized recommendations from our intelligent assistant'
    },
    {
      icon: '💬',
      title: 'Omnichannel Support',
      description: 'Chat with us on Web, WhatsApp, or in-store kiosks'
    },
    {
      icon: '🚚',
      title: 'Fast Delivery',
      description: 'Free shipping on all orders with real-time tracking'
    },
    {
      icon: '🔒',
      title: 'Secure Checkout',
      description: 'Shop with confidence using our encrypted payment system'
    }
  ]

  return (
    <div>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Welcome to OmniSales AI
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            Your Intelligent Shopping Assistant - Shop Smarter with AI
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link
              to="/products"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
            >
              Browse Products
            </Link>
            <Link
              to="/chat"
              className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/10 transition"
            >
              💬 Chat with AI
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Why Shop With Us?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="text-center">
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Categories */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Shop by Category
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {categories.map((category, index) => (
              <Link
                key={index}
                to="/products"
                className={`bg-gradient-to-br ${category.color} text-white rounded-xl p-8 text-center hover:scale-105 transition-transform shadow-lg`}
              >
                <div className="text-5xl mb-3">{category.icon}</div>
                <h3 className="text-xl font-semibold">{category.name}</h3>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Experience AI-Powered Shopping Today
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Get instant product recommendations, check inventory, and complete purchases - all through conversation!
          </p>
          <Link
            to="/chat"
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
          >
            Start Shopping with AI 🚀
          </Link>
        </div>
      </div>
    </div>
  )
}

export default HomePage
