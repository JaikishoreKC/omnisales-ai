import { sendChatMessage, getChatHistory } from '../services/api'
import { getChatUserId } from './session'
import { getChatErrorMessage } from './chatMessages'

export const sendChatWithStore = async ({
  message,
  user,
  source,
  getSessionId,
  startRequest,
  finishRequest,
  addMessage,
  getStoreState,
  setMessages
}) => {
  const requestId = startRequest()
  const storeState = getStoreState()
  const expectedSessionId = user?.user_id ? `user_${user.user_id}` : getSessionId()
  if (storeState.sessionId !== expectedSessionId) {
    storeState.setSessionId(expectedSessionId)
  }
  if (user?.user_id) {
    storeState.setOwnerKey(`user:${user.user_id}`)
  } else {
    storeState.setOwnerKey(`guest:${expectedSessionId}`)
  }
  const sessionId = expectedSessionId
  const contextKey = storeState.ownerKey
  const userId = getChatUserId(user)

  try {
    const response = await sendChatMessage({
      user_id: userId,
      session_id: sessionId,
      message,
      channel: 'web'
    })

    const latest = getStoreState()
    if (latest.sessionId !== sessionId || latest.ownerKey !== contextKey) {
      return
    }

    if (response?.reply) {
      addMessage({
        role: 'assistant',
        content: response.reply,
        agent: response?.agent_used,
        actions: response?.actions,
        source
      })
    } else if (typeof setMessages === 'function') {
      const token = localStorage.getItem('token')
      const history = await getChatHistory({ token, sessionId, limit: 200 })
      const latestAfter = getStoreState()
      if (latestAfter.sessionId === sessionId && latestAfter.ownerKey === contextKey) {
        setMessages(history?.messages || [], { force: true, source: 'chat-sync' })
      }
    } else {
      addMessage({
        role: 'assistant',
        content: 'Sorry, I could not generate a response right now.',
        source
      })
    }
  } catch (error) {
    const errorMessage = {
      role: 'assistant',
      content: getChatErrorMessage(error?.status),
      source
    }
    const latest = getStoreState()
    if (latest.sessionId === sessionId && latest.ownerKey === contextKey) {
      addMessage(errorMessage)
    }
  } finally {
    finishRequest(requestId)
  }
}
