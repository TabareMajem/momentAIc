import { create } from 'zustand';
import { api } from '../lib/api';
import type { ChatMessage, AgentType } from '../types';
import { v4 as uuidv4 } from 'uuid';

interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  currentAgent: AgentType;
  currentStartupId: string | null;
  setCurrentAgent: (agent: AgentType) => void;
  setCurrentStartupId: (id: string | null) => void;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessionId: null,
  isLoading: false,
  currentAgent: 'orchestrator',
  currentStartupId: null,

  setCurrentAgent: (agent) => set({ currentAgent: agent }),

  setCurrentStartupId: (id) => set({ currentStartupId: id }),

  sendMessage: async (content) => {
    const { currentAgent, currentStartupId, messages, sessionId } = get();

    // Add user message immediately
    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date()
    };

    set({ messages: [...messages, userMsg], isLoading: true });

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));

      // Create a placeholder assistant message
      const assistantMsgId = uuidv4();
      const placeholderMsg: ChatMessage = {
        id: assistantMsgId,
        role: 'assistant',
        content: '', // Empty start
        timestamp: new Date(),
        isStreaming: true
      };

      set({
        messages: [...get().messages, placeholderMsg],
        isLoading: true // Keep loading true while streaming starts? Or false to remove spinner?
        // Actually, for streaming, we usually remove spinner and show cursor. 
        // Let's keep isLoading=true for the initial connection, then false once first token arrives?
        // Simpler: isLoading=true means "waiting for response OR streaming".
        // But UI shows spinner if isLoading. We want to hide spinner if content > 0.
      });

      await api.streamChatWithAgent({
        message: content,
        agent_type: currentAgent,
        startup_id: currentStartupId || undefined,
        session_id: sessionId || undefined,
        conversation_history: history
      }, (token) => {
        // onToken: Update the specific message in store
        set((state) => {
          const newMessages = [...state.messages];
          const msgIndex = newMessages.findIndex(m => m.id === assistantMsgId);
          if (msgIndex !== -1) {
            newMessages[msgIndex] = {
              ...newMessages[msgIndex],
              content: newMessages[msgIndex].content + token,
              isStreaming: true
            };
          }
          return { messages: newMessages, isLoading: false }; // Stop spinner on first token
        });
      }, (fullText) => {
        // onComplete
        set((state) => {
          const newMessages = [...state.messages];
          const msgIndex = newMessages.findIndex(m => m.id === assistantMsgId);
          if (msgIndex !== -1) {
            newMessages[msgIndex] = {
              ...newMessages[msgIndex],
              isStreaming: false
            };
          }
          return { messages: newMessages, isLoading: false };
        });
      }, (err) => {
        // onError
        set({ isLoading: false });
        console.error('Stream error', err);
      });

    } catch (error) {
      console.error('Chat failed', error);
      set({ isLoading: false });
    }
  },

  clearChat: () => set({ messages: [], sessionId: null })
}));