import type { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { mockStore } from '@/lib/mockStore'
import bcrypt from 'bcryptjs'

export const authOptions: NextAuthOptions = {
  secret: process.env.SESSION_SECRET,
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) return null
        const user = await mockStore.getUserByUsername(credentials.username)
        if (!user) return null
        const ok = await bcrypt.compare(credentials.password, user.password)
        if (!ok) return null
        return {
          id: String(user.id),
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
          profilePicture: user.profilePicture ?? undefined,
          phone: user.phone ?? undefined,
          preferredContactMethod: user.preferredContactMethod ?? undefined
        } as any
      }
    })
  ],
  session: { strategy: 'jwt', maxAge: 30 * 60 },
  pages: { signIn: '/login' },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role
        token.username = (user as any).username
        token.firstName = (user as any).firstName
        token.lastName = (user as any).lastName
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        ;(session.user as any).id = token.sub!
        ;(session.user as any).role = token.role as string
        ;(session.user as any).username = token.username as string
        ;(session.user as any).firstName = token.firstName as string
        ;(session.user as any).lastName = token.lastName as string
      }
      return session
    }
  }
}
