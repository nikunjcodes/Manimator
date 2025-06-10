interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: 'pending' | 'generating' | 'completed' | 'error';
  animationUrl?: string;
}

interface GenerateAnimationResponse {
  message: string;
  animationUrl?: string;
  error?: string;
}

class ChatService {
  private baseUrl = 'http://localhost:5000/api';

  async sendMessage(message: string, token: string): Promise<GenerateAnimationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to generate animation');
      }

      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getChatHistory(token: string): Promise<ChatMessage[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/history`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch chat history');
      }

      return data.messages;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  }
}

export const chatService = new ChatService();
export type { ChatMessage, GenerateAnimationResponse }; 