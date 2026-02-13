import { describe, it, expect, beforeEach } from 'vitest'
import useChatStore from '../store/chatStore'

const resetStore = () => {
  useChatStore.setState({
    messages: [],
    sessionId: null,
    ownerKey: 'guest:test',
    isLoading: false,
    activeRequestId: 0,
    isAssistantOpen: false
  })
}

describe('chat store request lifecycle', () => {
  beforeEach(() => {
    resetStore()
  })

  it('sets loading true on start and false on finish', () => {
    const { startRequest, finishRequest } = useChatStore.getState()

    const id = startRequest()
    expect(useChatStore.getState().isLoading).toBe(true)

    finishRequest(id)
    expect(useChatStore.getState().isLoading).toBe(false)
  })

  it('ignores finish for stale request id', () => {
    const { startRequest, finishRequest } = useChatStore.getState()

    const first = startRequest()
    const second = startRequest()

    finishRequest(first)
    expect(useChatStore.getState().isLoading).toBe(true)

    finishRequest(second)
    expect(useChatStore.getState().isLoading).toBe(false)
  })
})
