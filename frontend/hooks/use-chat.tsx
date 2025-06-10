"use client"

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuth } from './use-auth';
import { chatService, type ChatMessage } from '../services/chat-service';
import { v4 as uuidv4 } from 'uuid';

interface ChatContextType {
  messages: ChatMessage[];
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { user, isAuthenticated } = useAuth();

  // Load chat history when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      const token = localStorage.getItem('auth_token');
      if (token) {
        loadChatHistory(token);
      }
    }
  }, [isAuthenticated, user]);

  const loadChatHistory = async (token: string) => {
    try {
      const history = await chatService.getChatHistory(token);
      setMessages(history);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!isAuthenticated || !user) {
      throw new Error('Must be authenticated to send messages');
    }

    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
      status: 'pending'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatService.sendMessage(content, token);

      // Add assistant's response
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        status: 'completed',
        animationUrl: response.animationUrl
      };

      setMessages(prev => {
        const updatedMessages = prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, status: 'completed' as const }
            : msg
        );
        return [...updatedMessages, assistantMessage];
      });

    } catch (error) {
      // Update user message status to error
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id 
          ? { ...msg, status: 'error' as const }
          : msg
      ));

      // Add error message
      const errorMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while generating the animation. Please try again.',
        timestamp: new Date(),
        status: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return (
    <ChatContext.Provider value={{
      messages,
      isLoading,
      sendMessage,
      clearMessages
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
} 