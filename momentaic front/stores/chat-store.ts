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
      
      const response = await api.chatWithAgent({
        message: content,
        agent_type: currentAgent,
        startup_id: currentStartupId || undefined,
        session_id: sessionId || undefined,
        conversation_history: history
      });

      const assistantMsg: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response.response,
        agent_used: response.agent_used,
        timestamp: new Date()
      };

      set({ 
        messages: [...get().messages, assistantMsg],
        sessionId: response.session_id,
        isLoading: false
      });
    } catch (error) {
      console.error('Chat failed', error);
      // Add error message if needed
      set({ isLoading: false });
    }
  },

  clearChat: () => set({ messages: [], sessionId: null })
}));