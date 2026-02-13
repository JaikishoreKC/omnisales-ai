import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MessageBubble from './MessageBubble'
import useChatStore from '../store/chatStore'
import { shallow } from 'zustand/shallow'
import { useAuth } from '../context/AuthContext'
import { getChatSessionId } from '../utils/session'
import { sendChatWithStore } from '../utils/chatFlow'

const ChatWidget = () => {
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  // Resizing state
  const [size, setSize] = useState(() => {
    const saved = localStorage.getItem('chat-widget-size')
    return saved ? JSON.parse(saved) : { width: 384, height: 600 }
  })
  const [isResizing, setIsResizing] = useState(false)
  const resizeStartRef = useRef({ x: 0, y: 0, width: 0, height: 0 })

  // Use Zustand store for ALL state including isOpen
  const {
    messages,
    isLoading,
    isOpen,
    ownerKey,
    addMessage,
    startRequest,
    finishRequest,
    getSessionId,
    openAssistant,
    closeAssistant,
    setSessionId,
    setMessages
  } = useChatStore(
    (state) => ({
      messages: state.messages,
      isLoading: state.isLoading,
      isOpen: state.isAssistantOpen,
      ownerKey: state.ownerKey,
      addMessage: state.addMessage,
      startRequest: state.startRequest,
      finishRequest: state.finishRequest,
      getSessionId: state.getSessionId,
      openAssistant: state.openAssistant,
      closeAssistant: state.closeAssistant,
      setSessionId: state.setSessionId,
      setMessages: state.setMessages
    }),
    shallow
  )
  const { user } = useAuth()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    setSessionId(getChatSessionId(user))
  }, [user, setSessionId])

  // Auto-focus input when assistant opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])
  
  // Save size to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('chat-widget-size', JSON.stringify(size))
  }, [size])

  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleResizeMove)
      document.removeEventListener('mouseup', handleResizeEnd)
    }
  }, [])
  
  // Resize handlers
  const handleResizeStart = (e, direction) => {
    e.preventDefault()
    e.stopPropagation()
    setIsResizing(true)
    resizeStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height,
      direction
    }
    document.addEventListener('mousemove', handleResizeMove)
    document.addEventListener('mouseup', handleResizeEnd)
  }
  
  const handleResizeMove = (e) => {
    if (!isResizing && !resizeStartRef.current.direction) return
    
    const { x, y, width, height, direction } = resizeStartRef.current
    const deltaX = x - e.clientX // Right side, so negative delta means larger
    const deltaY = e.clientY - y // Bottom, so positive delta means larger
    
    let newWidth = width
    let newHeight = height
    
    if (direction.includes('right')) {
      newWidth = Math.max(320, Math.min(800, width - deltaX))
    }
    if (direction.includes('bottom')) {
      newHeight = Math.max(400, Math.min(900, height + deltaY))
    }
    if (direction.includes('left')) {
      newWidth = Math.max(320, Math.min(800, width + deltaX))
    }
    if (direction.includes('top')) {
      newHeight = Math.max(400, Math.min(900, height - deltaY))
    }
    
    setSize({ width: newWidth, height: newHeight })
  }
  
  const handleResizeEnd = () => {
    setIsResizing(false)
    resizeStartRef.current = { x: 0, y: 0, width: 0, height: 0, direction: '' }
    document.removeEventListener('mousemove', handleResizeMove)
    document.removeEventListener('mouseup', handleResizeEnd)
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: input,
      source: 'floating-widget'
    }

    addMessage(userMessage)
    setInput('')
    await sendChatWithStore({
      message: input,
      user,
      source: 'floating-widget',
      getSessionId,
      ownerKey,
      startRequest,
      finishRequest,
      addMessage,
      getStoreState: useChatStore.getState,
      setMessages
    })
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFullscreen = () => {
    // Messages are already in global store, just navigate
    closeAssistant()
    navigate('/chat')
  }
  
  const handleResetSize = () => {
    setSize({ width: 384, height: 600 })
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={openAssistant}
          className="fixed bottom-6 right-6 w-16 h-16 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 flex items-center justify-center text-2xl z-[9999] animate-bounce"
          aria-label="Open AI Assistant"
          style={{ animationDuration: '2s' }}
        >
          💬
        </button>
      )}

      {/* Chat Widget Window */}
      {isOpen && (
        <div 
          className="fixed bottom-6 right-6 bg-white rounded-lg shadow-2xl flex flex-col z-[9999] border border-gray-200 animate-slideUp"
          style={{ 
            width: `${size.width}px`, 
            height: `${size.height}px`,
            minWidth: '320px',
            minHeight: '400px',
            maxWidth: '800px',
            maxHeight: '900px',
            resize: 'none',
            userSelect: isResizing ? 'none' : 'auto'
          }}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-t-lg flex justify-between items-center">
            <div>
              <h3 className="font-semibold">AI Sales Assistant</h3>
              <p className="text-xs opacity-90">
                {messages.length > 0 ? `${messages.length} messages` : 'Ask me anything!'}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleResetSize}
                className="text-white hover:bg-white/20 rounded-full w-8 h-8 flex items-center justify-center transition"
                title="Reset Size"
              >
                ⊡
              </button>
              <button
                onClick={handleFullscreen}
                className="text-white hover:bg-white/20 rounded-full w-8 h-8 flex items-center justify-center transition"
                title="Fullscreen"
              >
                ⛶
              </button>
              <button
                onClick={closeAssistant}
                className="text-white hover:bg-white/20 rounded-full w-8 h-8 flex items-center justify-center transition"
                aria-label="Close Assistant"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Resize Handles */}
          {/* Corner handles - more visible */}
          <div 
            className="absolute top-0 left-0 w-6 h-6 cursor-nw-resize hover:bg-blue-300 bg-blue-100 opacity-50 hover:opacity-100 transition-opacity rounded-tl-lg"
            onMouseDown={(e) => handleResizeStart(e, 'top-left')}
            title="Resize"
          />
          <div 
            className="absolute top-0 right-0 w-6 h-6 cursor-ne-resize hover:bg-blue-300 bg-blue-100 opacity-50 hover:opacity-100 transition-opacity rounded-tr-lg"
            onMouseDown={(e) => handleResizeStart(e, 'top-right')}
            title="Resize"
          />
          <div 
            className="absolute bottom-0 left-0 w-6 h-6 cursor-sw-resize hover:bg-blue-300 bg-blue-100 opacity-50 hover:opacity-100 transition-opacity"
            onMouseDown={(e) => handleResizeStart(e, 'bottom-left')}
            title="Resize"
          />
          <div 
            className="absolute bottom-0 right-0 w-6 h-6 cursor-se-resize hover:bg-blue-300 bg-blue-100 opacity-50 hover:opacity-100 transition-opacity rounded-br-lg group"
            onMouseDown={(e) => handleResizeStart(e, 'bottom-right')}
            title="Resize"
          >
            <svg 
              className="w-4 h-4 absolute bottom-0.5 right-0.5 text-blue-600 opacity-60 group-hover:opacity-100" 
              fill="currentColor" 
              viewBox="0 0 16 16"
            >
              <path d="M14 14V7h-2v5H7v2h7zM2 2v7h2V4h5V2H2z"/>
            </svg>
          </div>
          
          {/* Edge handles - subtle */}
          <div 
            className="absolute top-0 left-1/2 transform -translate-x-1/2 w-12 h-2 cursor-n-resize hover:bg-blue-200 opacity-0 hover:opacity-70 transition-opacity"
            onMouseDown={(e) => handleResizeStart(e, 'top')}
            title="Resize"
          />
          <div 
            className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-12 h-2 cursor-s-resize hover:bg-blue-200 opacity-0 hover:opacity-70 transition-opacity"
            onMouseDown={(e) => handleResizeStart(e, 'bottom')}
            title="Resize"
          />
          <div 
            className="absolute left-0 top-1/2 transform -translate-y-1/2 w-2 h-12 cursor-w-resize hover:bg-blue-200 opacity-0 hover:opacity-70 transition-opacity"
            onMouseDown={(e) => handleResizeStart(e, 'left')}
            title="Resize"
          />
          <div 
            className="absolute right-0 top-1/2 transform -translate-y-1/2 w-2 h-12 cursor-e-resize hover:bg-blue-200 opacity-0 hover:opacity-70 transition-opacity"
            onMouseDown={(e) => handleResizeStart(e, 'right')}
            title="Resize"
          />

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-8">
                <p className="text-lg mb-2">👋 Hi there!</p>
                <p className="text-sm">I can help you find products, check stock, or answer questions</p>
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

          {/* Input */}
          <div className="border-t p-3">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition text-sm font-medium"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ChatWidget
