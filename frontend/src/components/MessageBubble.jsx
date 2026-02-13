import React from 'react'
import PropTypes from 'prop-types'
import ProductCard from './ProductCard'
import { MarkdownText } from '../utils/markdown'

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const content = message.content || message.text || ''
  const actions = Array.isArray(message.actions) ? message.actions : []

  // System messages (context notifications)
  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-full text-xs font-medium">
          {content}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <MarkdownText text={content} className="text-sm whitespace-pre-wrap break-words" />
        {message.agent && (
          <p className="text-xs mt-1 opacity-70">
            Agent: {message.agent}
          </p>
        )}
        {actions.length > 0 && (
          <div className="mt-3 space-y-2">
            {actions.map((action, index) => {
              if (action.type === 'show_products' && Array.isArray(action.data)) {
                const products = action.data.filter(
                  (product) => product && product.product_id
                )
                if (products.length === 0) {
                  return null
                }
                return (
                  <div key={index} className="space-y-2">
                    <p className="text-xs font-semibold opacity-70">Recommended Products:</p>
                    <div className="grid grid-cols-1 gap-2">
                      {products.map((product) => (
                        <ProductCard key={product.product_id} product={product} />
                      ))}
                    </div>
                  </div>
                )
              }
              return null
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageBubble

MessageBubble.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.string,
    agent: PropTypes.string,
    actions: PropTypes.arrayOf(
      PropTypes.shape({
        type: PropTypes.string,
        data: PropTypes.arrayOf(PropTypes.object)
      })
    )
  }).isRequired
}
