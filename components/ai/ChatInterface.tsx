// components/ai/ChatInterface.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your IHEP health assistant. I can help you with appointment scheduling, wellness questions, and navigating your health resources. How can I assist you today?',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again in a moment.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              <p className="text-xs mt-1 opacity-70">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Phase 2: Google Cloud Platform Backend Architecture

### Infrastructure Overview

The GCP infrastructure follows a multi-tier architecture with clear separation between the presentation layer, application layer, data layer, and AI services layer. This separation allows independent scaling of each tier based on demand patterns. The architecture enforces Zero Trust principles at every boundary, requiring mutual TLS authentication for all inter-service communication.
```
┌─────────────────────────────────────────────────────────────────┐
│                      Internet / Users                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            Cloud CDN + Cloud Armor (DDoS Protection)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           Global HTTP(S) Load Balancer (SSL Termination)        │
│                    URL Map + Backend Services                    │
└─────┬──────────────────┴────────────────────────┬────────────────┘
      │                                            │
      ▼                                            ▼
┌──────────────────────┐              ┌──────────────────────────┐
│  Cloud Run Service   │              │   Cloud Storage Bucket   │
│   (Next.js App)      │              │   (Static Assets)        │
│  - Auto-scaling      │              │   - Images, Models       │
│  - Serverless        │              └──────────────────────────┘
└──────┬───────────────┘
       │
       │ (Internal requests)
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│               Internal Load Balancer (L7)                        │
└─────┬──────────────┬──────────────┬──────────────┬──────────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────────┐
│Cloud Run  │  │Cloud Run  │  │Cloud Run  │  │   Vertex AI    │
│  Auth API │  │Health API │  │ Chat API  │  │   Endpoints    │
│           │  │           │  │           │  │  (Gemini Pro)  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────────┬───────┘
      │              │              │                   │
      └──────┬───────┴──────┬───────┴───────────────────┘
             │              │
             ▼              ▼
      ┌────────────┐  ┌──────────────────┐
      │ Cloud SQL  │  │ Healthcare API   │
      │(PostgreSQL)│  │  (FHIR Store)    │
      │            │  │   - PHI Data     │
      │ - Users    │  │   - De-ID API    │
      │ - Appts    │  └──────────────────┘
      │ - Providers│
      └──────┬─────┘
             │
             ▼
      ┌────────────┐
      │Memorystore │
      │  (Redis)   │
      │  - Cache   │
      │  - Sessions│
      └────────────┘

     All connections secured with:
     - VPC Service Controls
     - Private Service Connect
     - Mutual TLS (mTLS)
     - Cloud IAM + Workload Identity