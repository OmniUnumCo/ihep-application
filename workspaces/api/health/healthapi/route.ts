// app/api/health/[...healthapi]/route.ts
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const token = request.headers.get('Authorization')?.replace('Bearer ', '');
  
  if (!token) {
    return new Response(JSON.stringify({ error: 'No authorization token' }), {
      status: 401,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
  
  const healthApiUrl = process.env.HEALTH_API_URL || 'http://localhost:8081';
  const path = request.nextUrl.pathname.replace('/api/health', '');
  
  try {
    const response = await fetch(`${healthApiUrl}${path}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    const data = await response.json();
    
    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Health service unavailable' }), {
      status: 503,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}

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
  
  const healthApiUrl = process.env.HEALTH_API_URL || 'http://localhost:8081';
  const path = request.nextUrl.pathname.replace('/api/health', '');
  
  try {
    const response = await fetch(`${healthApiUrl}${path}`, {
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
    return new Response(JSON.stringify({ error: 'Health service unavailable' }), {
      status: 503,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}
