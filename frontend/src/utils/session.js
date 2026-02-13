const GUEST_SESSION_KEY = 'guest_session_id'

export const getGuestSessionId = () => {
  const existing = localStorage.getItem(GUEST_SESSION_KEY)
  if (existing) {
    return existing
  }
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
  localStorage.setItem(GUEST_SESSION_KEY, sessionId)
  return sessionId
}

export const getChatSessionId = (user) => {
  if (user?.user_id) {
    return `user_${user.user_id}`
  }
  return getGuestSessionId()
}

export const getChatUserId = (user) => {
  if (user?.user_id) {
    return user.user_id
  }
  return `guest_${getGuestSessionId()}`
}
