import React from 'react'

const ProductCard = ({ product }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex flex-col space-y-2">
        <h3 className="font-semibold text-gray-900 text-sm">{product.name}</h3>
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-blue-600">
            ${product.price.toFixed(2)}
          </span>
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
            {product.category}
          </span>
        </div>
      </div>
    </div>
  )
}

export default ProductCard
