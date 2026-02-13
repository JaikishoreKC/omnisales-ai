import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { getGuestSessionId } from '../utils/session'

const MAX_MESSAGES = 200
const OWNER_KEY_STORAGE = 'omnisales-chat-owner-key'

const getOwnerScopedKey = () => {
  const ownerKey = localStorage.getItem(OWNER_KEY_STORAGE)
  return ownerKey ? `omnisales-chat-storage:${ownerKey}` : 'omnisales-chat-storage:guest'
}

const ownerScopedStorage = {
  getItem: () => localStorage.getItem(getOwnerScopedKey()),
  setItem: (_key, value) => localStorage.setItem(getOwnerScopedKey(), value),
  removeItem: () => localStorage.removeItem(getOwnerScopedKey())
}

const normalizeMessage = (message) => {
  if (!message || typeof message !== 'object') {
    return message
  }

  if (message.content === undefined && message.text !== undefined) {
    return { ...message, content: message.text }
  }

  return message
}

const useChatStore = create(
  persist(
    (set, get) => ({
      // State
      messages: [],
      sessionId: null,
      ownerKey: `guest:${getGuestSessionId()}`,
      isLoading: false,
      activeRequestId: 0,
      isAssistantOpen: false,

      // Initialize session
      initializeSession: () => {
        const existingSessionId = get().sessionId
        if (!existingSessionId) {
          const newSessionId = getGuestSessionId()
          set({ sessionId: newSessionId, ownerKey: `guest:${newSessionId}` })
          localStorage.setItem(OWNER_KEY_STORAGE, `guest:${newSessionId}`)
          return newSessionId
        }
        return existingSessionId
      },

      // Force set session ID (used on auth changes)
      setSessionId: (sessionId) => set({ sessionId }),

      setOwnerKey: (ownerKey) => {
        if (ownerKey) {
          localStorage.setItem(OWNER_KEY_STORAGE, ownerKey)
        }
        set({ ownerKey })
      },

      // Add a new message (append-only)
      addMessage: (message) => {
        set((state) => ({
          messages: [...state.messages, {
            ...message,
            id: Date.now() + Math.random(), // Unique ID
            timestamp: message.timestamp || new Date().toISOString()
          }].slice(-MAX_MESSAGES)
        }))
      },

      // Set loading state
      setLoading: (isLoading) => set({ isLoading }),

      // Request lifecycle helpers (prevents stale loading state)
      startRequest: () => {
        const nextId = get().activeRequestId + 1
        set({ activeRequestId: nextId, isLoading: true })
        return nextId
      },

      finishRequest: (requestId) => {
        if (get().activeRequestId === requestId) {
          set({ isLoading: false })
        }
      },

      // Clear all messages (reset conversation)
      clearMessages: (source = 'user') => {
        set((state) => ({ messages: [], sessionId: null, ownerKey: state.ownerKey }))
      },

      // Get session ID (create if doesn't exist)
      getSessionId: () => {
        const { sessionId, initializeSession } = get()
        return sessionId || initializeSession()
      },

      // Hydrate from storage (already handled by persist middleware)
      // But we can force a manual sync if needed
      syncFromStorage: () => {
        // The persist middleware handles this automatically
        // This is a no-op but kept for API consistency
      },

      // Replace messages safely (used when loading from backend)
      setMessages: (messages, options = {}) => {
        const { force = false, source = 'unknown' } = options
        const nextMessages = Array.isArray(messages)
          ? messages.map(normalizeMessage).slice(-MAX_MESSAGES)
          : []

        set((state) => {
          if (!force && nextMessages.length === 0 && state.messages.length > 0) {
            return { messages: state.messages }
          }

          return { messages: nextMessages }
        })
      },

      // Hydrate messages by merging with existing state
      hydrateMessages: (messages, source = 'storage') => {
        const nextMessages = Array.isArray(messages)
          ? messages.map(normalizeMessage).slice(-MAX_MESSAGES)
          : []

        set((state) => {
          if (nextMessages.length === 0) {
            if (state.messages.length > 0) {
              return { messages: state.messages }
            }
            return { messages: [] }
          }

          const seen = new Set(
            state.messages.map((m) => m.id || `${m.timestamp || ''}-${m.role}-${m.content}`)
          )
          const merged = [...state.messages]

          nextMessages.forEach((m) => {
            const key = m.id || `${m.timestamp || ''}-${m.role}-${m.content}`
            if (!seen.has(key)) {
              merged.push(m)
              seen.add(key)
            }
          })

          return { messages: merged.slice(-MAX_MESSAGES) }
        })
      },

      // Assistant control functions
      openAssistant: () => set({ isAssistantOpen: true }),
      closeAssistant: () => set({ isAssistantOpen: false }),
      toggleAssistant: () => set((state) => ({ isAssistantOpen: !state.isAssistantOpen })),

      // Send contextual message and open assistant
      sendContextMessage: async (contextMessage, callback) => {
        // Open assistant first
        set({ isAssistantOpen: true })
        
        // Add user message
        const userMessage = {
          role: 'user',
          content: contextMessage,
          source: 'context-action'
        }
        
        get().addMessage(userMessage)
        const requestId = get().startRequest()
        
        // Call the API (callback provided by component)
        if (callback) {
          try {
            await callback(contextMessage)
          } catch (error) {
            console.error('Error sending context message:', error)
          } finally {
            get().finishRequest(requestId)
          }
        } else {
          get().finishRequest(requestId)
        }
      },
    }),
    {
      name: 'omnisales-chat-storage', // logical key; storage handles per-owner key
      storage: createJSONStorage(() => ownerScopedStorage),
      version: 1,
      // Only persist messages and sessionId, not isLoading or isAssistantOpen
      partialize: (state) => ({
        messages: state.messages,
        sessionId: state.sessionId,
        ownerKey: state.ownerKey
      }),
      merge: (persistedState, currentState) => {
        const persistedMessages = Array.isArray(persistedState?.messages)
          ? persistedState.messages
          : []
        const currentMessages = Array.isArray(currentState?.messages)
          ? currentState.messages
          : []

        const persistedOwner = persistedState?.ownerKey
        const currentOwner = currentState?.ownerKey
        const canUsePersisted = persistedOwner && currentOwner && persistedOwner === currentOwner

        let messages = currentMessages
        if (canUsePersisted && persistedMessages.length > 0) {
          const seen = new Set(
            currentMessages.map((m) => m.id || `${m.timestamp || ''}-${m.role}-${m.content}`)
          )
          messages = [...currentMessages]
          persistedMessages.forEach((m) => {
            const key = m.id || `${m.timestamp || ''}-${m.role}-${m.content}`
            if (!seen.has(key)) {
              messages.push(m)
              seen.add(key)
            }
          })
          messages = messages.slice(-MAX_MESSAGES)
        }

        const sessionId = canUsePersisted
          ? (persistedState?.sessionId || currentState?.sessionId)
          : currentState?.sessionId

        return {
          ...currentState,
          ...persistedState,
          ownerKey: currentOwner || persistedOwner,
          sessionId,
          messages
        }
      },
      onRehydrateStorage: () => (state, error) => {
        if (error) {
          console.error('[chatStore] Rehydrate error:', error)
          return
        }
      }
    }
  )
)

export default useChatStore
