/**
 * Server-side session management utilities
 *
 * This module provides helper functions for accessing the current user session
 * on the server side using NextAuth.
 */

import { getServerSession as nextAuthGetServerSession } from 'next-auth';
import type { Session } from 'next-auth';
import { authOptions } from './options';

/**
 * Get the current server session
 *
 * This function retrieves the current user session on the server side.
 * It should only be used in Server Components, Server Actions, or API routes.
 *
 * @returns The current session or null if not authenticated
 *
 * @example
 * ```typescript
 * import { getServerSession } from '@/lib/auth/session';
 *
 * export default async function Page() {
 *   const session = await getServerSession();
 *
 *   if (!session?.user) {
 *     redirect('/auth/signin');
 *   }
 *
 *   return <div>Welcome {session.user.firstName}!</div>;
 * }
 * ```
 */
export async function getServerSession(): Promise<Session | null> {
  return await nextAuthGetServerSession(authOptions);
}

/**
 * Get the current user from the server session
 *
 * Convenience function that returns just the user object from the session.
 *
 * @returns The current user or null if not authenticated
 *
 * @example
 * ```typescript
 * import { getCurrentUser } from '@/lib/auth/session';
 *
 * export default async function Page() {
 *   const user = await getCurrentUser();
 *
 *   if (!user) {
 *     redirect('/auth/signin');
 *   }
 *
 *   return <div>Welcome {user.firstName}!</div>;
 * }
 * ```
 */
export async function getCurrentUser() {
  const session = await getServerSession();
  return session?.user ?? null;
}

/**
 * Check if the current user is authenticated
 *
 * @returns true if the user is authenticated, false otherwise
 *
 * @example
 * ```typescript
 * import { isAuthenticated } from '@/lib/auth/session';
 *
 * export default async function Page() {
 *   if (!await isAuthenticated()) {
 *     redirect('/auth/signin');
 *   }
 *
 *   return <div>Protected content</div>;
 * }
 * ```
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getServerSession();
  return !!session?.user;
}

/**
 * Require authentication - throws if not authenticated
 *
 * This function checks if the user is authenticated and returns the session.
 * If not authenticated, it throws an error.
 *
 * @returns The current session
 * @throws Error if not authenticated
 *
 * @example
 * ```typescript
 * import { requireAuth } from '@/lib/auth/session';
 *
 * export default async function Page() {
 *   const session = await requireAuth();
 *
 *   // This code only runs if authenticated
 *   return <div>Welcome {session.user.firstName}!</div>;
 * }
 * ```
 */
export async function requireAuth(): Promise<Session> {
  const session = await getServerSession();

  if (!session?.user) {
    throw new Error('Authentication required');
  }

  return session;
}

/**
 * Check if the current user has a specific role
 *
 * @param role - The role to check for
 * @returns true if the user has the specified role, false otherwise
 *
 * @example
 * ```typescript
 * import { hasRole } from '@/lib/auth/session';
 *
 * export default async function AdminPage() {
 *   if (!await hasRole('admin')) {
 *     redirect('/unauthorized');
 *   }
 *
 *   return <div>Admin content</div>;
 * }
 * ```
 */
export async function hasRole(role: string): Promise<boolean> {
  const session = await getServerSession();
  return session?.user?.role === role;
}

/**
 * Require a specific role - throws if user doesn't have the role
 *
 * @param role - The required role
 * @returns The current session
 * @throws Error if user doesn't have the required role
 *
 * @example
 * ```typescript
 * import { requireRole } from '@/lib/auth/session';
 *
 * export default async function AdminPage() {
 *   const session = await requireRole('admin');
 *
 *   // This code only runs if user is an admin
 *   return <div>Admin content</div>;
 * }
 * ```
 */
export async function requireRole(role: string): Promise<Session> {
  const session = await requireAuth();

  if (session.user.role !== role) {
    throw new Error(`Role '${role}' required`);
  }

  return session;
}
