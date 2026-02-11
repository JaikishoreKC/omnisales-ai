import React, { useState, useRef, useEffect } from 'react'
import MessageBubble from '../components/MessageBubble'
import { sendChatMessage } from '../services/api'
import useChatStore from '../store/chatStore'
import { useConfirm } from '../context/ConfirmContext'

const ChatPage = () => {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const { confirm } = useConfirm()

  // Use Zustand store instead of local state
  const messages = useChatStore((state) => state.messages)
  const isLoading = useChatStore((state) => state.isLoading)
  const sessionId = useChatStore((state) => state.sessionId)
  const addMessage = useChatStore((state) => state.addMessage)
  const setLoading = useChatStore((state) => state.setLoading)
  const getSessionId = useChatStore((state) => state.getSessionId)
  const clearMessages = useChatStore((state) => state.clearMessages)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: input,
      source: 'chat-page'
    }

    addMessage(userMessage)
    setInput('')
    setLoading(true)

    try {
      const sessionId = getSessionId()
      
      const response = await sendChatMessage({
        user_id: 'user_' + Math.random().toString(36).substr(2, 9),
        session_id: sessionId,
        message: input,
        channel: 'web'
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.reply,
        agent: response.agent_used,
        actions: response.actions,
        source: 'chat-page'
      }

      addMessage(assistantMessage)
    } catch (error) {
      console.error('Error:', error)
      const status = error?.status
      const friendlyMessage = status === 429
        ? 'We are getting a lot of requests. Please wait a moment and try again.'
        : status === 401
        ? 'Chat is unavailable. Missing or invalid API key.'
        : 'Sorry, something went wrong. Please try again.'
      const errorMessage = {
        role: 'assistant',
        content: friendlyMessage,
        source: 'chat-page'
      }
      addMessage(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClearChat = async () => {
    const confirmed = await confirm({
      title: 'Clear Conversation',
      message: 'Are you sure you want to clear the entire conversation? This will also clear the floating widget chat.',
      confirmText: 'Clear All',
      cancelText: 'Cancel',
      type: 'danger'
    })
    
    if (confirmed) {
      clearMessages()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">OmniSales AI Chat</h1>
            <p className="text-sm text-gray-600">
              Your intelligent sales assistant
              {sessionId && <span className="ml-2 text-xs text-gray-400">• Session active</span>}
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
            >
              Clear Chat
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg">Start a conversation</p>
              <p className="text-sm mt-2">Ask about products, check inventory, or track orders</p>
            </div>
          )}

          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="bg-white border-t">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
