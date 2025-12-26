// app/api/ai/chat/route.ts
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const token = request.headers.get('Authorization')?.replace('Bearer ', '');
  const body = await request.json();
  
  if (!token) {
    return new Response(JSON.stringify({ error: 'No authorization token' }), {
      status: 401,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
  
  const chatApiUrl = process.env.CHAT_API_URL || 'http://localhost:8082';
  
  try {
    const response = await fetch(`${chatApiUrl}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    
    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Chat service unavailable',
      message: 'I apologize, but I encountered an error processing your message. Please try again in a moment.'
    }), {
      status: 503,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}
