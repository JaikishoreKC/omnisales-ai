import React, { createContext, useContext, useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import useChatStore from '../store/chatStore'
import { getChatHistory } from '../services/api'
import { getChatSessionId, getGuestSessionId } from '../utils/session'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const wasAuthenticated = useRef(false)

  const clearAuth = (reason = 'unknown') => {
    console.warn('[auth] Clearing auth state:', reason)
    setUser(null)
    setToken(null)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  useEffect(() => {
    // Load user from localStorage on mount
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('token')

    if (storedUser && storedToken) {
      try {
        setUser(JSON.parse(storedUser))
        setToken(storedToken)
      } catch (error) {
        console.error('Failed to parse stored user:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    let isActive = true

    const syncChat = async () => {
      const chatStore = useChatStore.getState()

      if (user && token) {
        const sessionId = getChatSessionId(user)
        chatStore.setSessionId(sessionId)
        chatStore.setOwnerKey(`user:${user.user_id}`)
        chatStore.clearMessages('auth-login')
        try {
          const data = await getChatHistory({ token, sessionId, limit: 200 })
          if (isActive) {
            chatStore.setMessages(data?.messages || [], { force: true, source: 'auth-login' })
          }
        } catch (error) {
          if (error?.status === 401) {
            clearAuth('chat-history-unauthorized')
          } else {
            console.error('Failed to load chat history:', error)
          }
        }
      } else if (wasAuthenticated.current) {
        chatStore.clearMessages('auth-logout')
        const guestSessionId = getGuestSessionId()
        chatStore.setSessionId(guestSessionId)
        chatStore.setOwnerKey(`guest:${guestSessionId}`)
        if (typeof chatStore.persist?.rehydrate === 'function') {
          await chatStore.persist.rehydrate()
        }
      }
    }

    syncChat()
    wasAuthenticated.current = !!user && !!token

    return () => {
      isActive = false
    }
  }, [user, token])

  useEffect(() => {
    const handleStorage = (event) => {
      if (event.key === 'token' || event.key === 'user') {
        const nextToken = localStorage.getItem('token')
        const nextUser = localStorage.getItem('user')

        if (!nextToken || !nextUser) {
          setUser(null)
          setToken(null)
          return
        }

        try {
          setUser(JSON.parse(nextUser))
          setToken(nextToken)
        } catch (error) {
          console.error('Failed to parse synced user:', error)
          setUser(null)
          setToken(null)
        }
      }
    }

    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [])

  useEffect(() => {
    const handleAuthExpired = () => clearAuth('auth-expired-event')
    window.addEventListener('auth:expired', handleAuthExpired)
    return () => window.removeEventListener('auth:expired', handleAuthExpired)
  }, [])

  const login = (userData, authToken) => {
    setUser(userData)
    setToken(authToken)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', authToken)
  }

  const logout = () => {
    clearAuth('user-logout')
    localStorage.removeItem('cart')
  }

  const isAdmin = () => {
    return user?.role === 'admin'
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAdmin,
    isAuthenticated: !!user && !!token
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext

AuthProvider.propTypes = {
  children: PropTypes.node
}
