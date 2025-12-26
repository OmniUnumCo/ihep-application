// app/api/auth/[...nextauth]/route.ts
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Proxy to Cloud Run Auth API
  const authApiUrl = process.env.AUTH_API_URL || 'http://localhost:8080';
  
  try {
    const response = await fetch(`${authApiUrl}/auth${request.nextUrl.pathname.replace('/api/auth', '')}`, {
      method: 'POST',
      headers: {
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
    return new Response(JSON.stringify({ error: 'Authentication service unavailable' }), {
      status: 503,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}

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
  
  const authApiUrl = process.env.AUTH_API_URL || 'http://localhost:8080';
  
  try {
    const response = await fetch(`${authApiUrl}/auth/validate`, {
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
    return new Response(JSON.stringify({ error: 'Authentication service unavailable' }), {
      status: 503,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}
