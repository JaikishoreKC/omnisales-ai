import React from 'react'
import ProductCard from './ProductCard'
import { MarkdownText } from '../utils/markdown'

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  // System messages (context notifications)
  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-full text-xs font-medium">
          {message.content}
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
        <MarkdownText text={message.content} className="text-sm whitespace-pre-wrap break-words" />
        {message.agent && (
          <p className="text-xs mt-1 opacity-70">
            Agent: {message.agent}
          </p>
        )}
        {message.actions && message.actions.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.actions.map((action, index) => {
              if (action.type === 'show_products' && action.data) {
                return (
                  <div key={index} className="space-y-2">
                    <p className="text-xs font-semibold opacity-70">Recommended Products:</p>
                    <div className="grid grid-cols-1 gap-2">
                      {action.data.map((product, idx) => (
                        <ProductCard key={idx} product={product} />
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
