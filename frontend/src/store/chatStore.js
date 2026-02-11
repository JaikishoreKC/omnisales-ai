import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

const useChatStore = create(
  persist(
    (set, get) => ({
      // State
      messages: [],
      sessionId: null,
      isLoading: false,
      isAssistantOpen: false,

      // Initialize session
      initializeSession: () => {
        const existingSessionId = get().sessionId
        if (!existingSessionId) {
          const newSessionId = 'session_' + Date.now()
          set({ sessionId: newSessionId })
          return newSessionId
        }
        return existingSessionId
      },

      // Add a new message (append-only)
      addMessage: (message) => {
        set((state) => ({
          messages: [...state.messages, {
            ...message,
            id: Date.now() + Math.random(), // Unique ID
            timestamp: message.timestamp || new Date().toISOString()
          }]
        }))
      },

      // Set loading state
      setLoading: (isLoading) => set({ isLoading }),

      // Clear all messages (reset conversation)
      clearMessages: (source = 'user') => {
        console.warn('[chatStore] clearMessages from:', source)
        set({ messages: [], sessionId: null })
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
        const nextMessages = Array.isArray(messages) ? messages : []

        set((state) => {
          if (!force && nextMessages.length === 0 && state.messages.length > 0) {
            console.warn('[chatStore] Ignored empty setMessages from:', source)
            return { messages: state.messages }
          }

          console.info('[chatStore] setMessages from:', source, 'length:', nextMessages.length)
          return { messages: nextMessages }
        })
      },

      // Hydrate messages by merging with existing state
      hydrateMessages: (messages, source = 'storage') => {
        const nextMessages = Array.isArray(messages) ? messages : []

        set((state) => {
          if (nextMessages.length === 0) {
            if (state.messages.length > 0) {
              console.warn('[chatStore] Ignored empty hydrateMessages from:', source)
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

          console.info('[chatStore] hydrateMessages from:', source, 'merged length:', merged.length)
          return { messages: merged }
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
        get().setLoading(true)
        
        // Call the API (callback provided by component)
        if (callback) {
          try {
            await callback(contextMessage)
          } catch (error) {
            console.error('Error sending context message:', error)
          } finally {
            get().setLoading(false)
          }
        } else {
          get().setLoading(false)
        }
      },
    }),
    {
      name: 'omnisales-chat-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      version: 1,
      // Only persist messages and sessionId, not isLoading or isAssistantOpen
      partialize: (state) => ({
        messages: state.messages,
        sessionId: state.sessionId
      }),
      merge: (persistedState, currentState) => {
        const persistedMessages = Array.isArray(persistedState?.messages)
          ? persistedState.messages
          : []
        const currentMessages = Array.isArray(currentState?.messages)
          ? currentState.messages
          : []

        const messages = persistedMessages.length > 0
          ? persistedMessages
          : currentMessages

        return {
          ...currentState,
          ...persistedState,
          messages
        }
      },
      onRehydrateStorage: () => (state, error) => {
        if (error) {
          console.error('[chatStore] Rehydrate error:', error)
          return
        }
        if (state?.messages?.length === 0) {
          console.warn('[chatStore] Rehydrated with empty messages')
        } else {
          console.info('[chatStore] Rehydrated messages:', state?.messages?.length || 0)
        }
      }
    }
  )
)

export default useChatStore
