import { create } from 'zustand'

export const useStore = create((set) => ({
  currentConversationId: null,
  setCurrentConversationId: (id) => set({ currentConversationId: id }),
  
  user: null,
  setUser: (user) => set({ user }),
  
  conversations: [],
  setConversations: (conversations) => set({ conversations }),
}))
