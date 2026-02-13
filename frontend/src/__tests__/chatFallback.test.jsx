import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, beforeEach, expect, vi } from 'vitest'
import ChatPage from '../pages/ChatPage'
import CartPage from '../pages/CartPage'
import ProductDetailPage from '../pages/ProductDetailPage'
import { sendChatMessage, getProductById } from '../services/api'
import useChatStore from '../store/chatStore'

vi.mock('../services/api', () => ({
  sendChatMessage: vi.fn(),
  getProductById: vi.fn()
}))

vi.mock('../components/MessageBubble', () => ({
  default: ({ message }) => <div>{message.content}</div>
}))

vi.mock('../context/ConfirmContext', () => ({
  useConfirm: () => ({ confirm: vi.fn().mockResolvedValue(true) })
}))

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 'u1' }, isAuthenticated: true, token: 't1' })
}))

vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() })
}))

vi.mock('../hooks/useCart', () => ({
  useCart: () => ({
    cartItems: [
      { product_id: 'p1', name: 'Widget', price: 10, quantity: 1 }
    ],
    updateQuantity: vi.fn(),
    removeFromCart: vi.fn(),
    addToCart: vi.fn(),
    getCartTotal: () => 10
  })
}))

vi.mock('../utils/session', () => ({
  getChatSessionId: () => 's1',
  getChatUserId: () => 'u1',
  getGuestSessionId: () => 'g1'
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useParams: () => ({ id: 'p1' })
  }
})

vi.mock('../store/chatStore', () => {
  const baseState = () => ({
    messages: [],
    sessionId: 's1',
    ownerKey: 'guest:s1',
    isLoading: false,
    activeRequestId: 0,
    isAssistantOpen: false
  })

  let state = baseState()
  let api = {}

  const rebuildApi = () => {
    api = {
      addMessage: vi.fn((message) => {
        state.messages.push(message)
      }),
      startRequest: vi.fn(() => {
        state.activeRequestId += 1
        state.isLoading = true
        return state.activeRequestId
      }),
      finishRequest: vi.fn((requestId) => {
        if (state.activeRequestId === requestId) {
          state.isLoading = false
        }
      }),
      getSessionId: vi.fn(() => state.sessionId),
      setSessionId: vi.fn((sessionId) => {
        state.sessionId = sessionId
      }),
      openAssistant: vi.fn(),
      closeAssistant: vi.fn()
    }
  }

  rebuildApi()

  const useChatStore = (selector) => {
    const current = { ...state, ...api }
    return selector ? selector(current) : current
  }

  useChatStore.getState = () => ({ ...state, ...api })
  useChatStore.__reset = () => {
    state = baseState()
    rebuildApi()
  }

  return { default: useChatStore }
})

const findMessageCall = (calls, expected) =>
  calls.some(([message]) => message?.content === expected)

beforeEach(() => {
  vi.clearAllMocks()
  useChatStore.__reset()
})

describe('Chat fallback paths', () => {
  it('adds a fallback message in ChatPage on error', async () => {
    sendChatMessage.mockRejectedValue({ status: 429 })

    render(<ChatPage />)

    fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
      target: { value: 'Hello' }
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => {
      const calls = useChatStore.getState().addMessage.mock.calls
      expect(
        findMessageCall(
          calls,
          'We are getting a lot of requests. Please wait a moment and try again.'
        )
      ).toBe(true)
    })
  })

  it('adds a fallback message in CartPage on error', async () => {
    sendChatMessage.mockRejectedValue({ status: 429 })

    render(<CartPage />)

    fireEvent.click(screen.getByRole('button', { name: /ask ai for help/i }))

    await waitFor(() => {
      const calls = useChatStore.getState().addMessage.mock.calls
      expect(
        findMessageCall(
          calls,
          'We are getting a lot of requests. Please try again shortly.'
        )
      ).toBe(true)
    })
  })

  it('adds a fallback message in ProductDetailPage on error', async () => {
    sendChatMessage.mockRejectedValue({ status: 401 })
    getProductById.mockResolvedValue({
      product_id: 'p1',
      name: 'Widget',
      category: 'tools',
      price: 10,
      stock: 5,
      rating: 4.5,
      description: 'Test product'
    })

    render(<ProductDetailPage />)

    const chatButton = await screen.findByRole('button', { name: /chat with ai/i })
    fireEvent.click(chatButton)

    await waitFor(() => {
      const calls = useChatStore.getState().addMessage.mock.calls
      expect(
        findMessageCall(
          calls,
          'Chat is unavailable. Missing or invalid API key.'
        )
      ).toBe(true)
    })
  })
})
