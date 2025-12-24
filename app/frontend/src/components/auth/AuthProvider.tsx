'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, Session } from '@/types';
import { apiClient } from '@/lib/api/client';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSession();
  }, []);

  useEffect(() => {
    if (!session) return;

    // Calculate time until expiration (refresh 5 minutes before)
    const expiresAt = new Date(session.expiresAt);
    const now = new Date();
    const timeUntilRefresh = expiresAt.getTime() - now.getTime() - 5 * 60 * 1000;

    if (timeUntilRefresh > 0) {
      const timer = setTimeout(() => {
        refreshSession();
      }, timeUntilRefresh);

      return () => clearTimeout(timer);
    } else {
      refreshSession();
    }
  }, [session]);

  const checkSession = async () => {
    try {
      const response = await apiClient.get<Session>('/auth/session');
      if (response.success && response.data) {
        setSession(response.data);
        setUser(response.data.user);
      }
    } catch (error) {
      console.error('Session check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await apiClient.post<Session>('/auth/signin', {
        email,
        password,
      });

      if (response.success && response.data) {
        setSession(response.data);
        setUser(response.data.user);
        
        // Store tokens securely
        localStorage.setItem('accessToken', response.data.accessToken);
        localStorage.setItem('refreshToken', response.data.refreshToken);
      } else {
        throw new Error(response.error?.message || 'Sign in failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    setLoading(true);
    try {
      await apiClient.post('/auth/signout');
    } catch (error) {
      console.error('Sign out error:', error);
    } finally {
      setUser(null);
      setSession(null);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setLoading(false);
    }
  };

  const refreshSession = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<Session>('/auth/refresh', {
        refreshToken,
      });

      if (response.success && response.data) {
        setSession(response.data);
        setUser(response.data.user);
        localStorage.setItem('accessToken', response.data.accessToken);
        localStorage.setItem('refreshToken', response.data.refreshToken);
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('Session refresh failed:', error);
      await signOut();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        signIn,
        signOut,
        refreshSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
