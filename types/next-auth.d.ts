import NextAuth from 'next-auth'

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
      username: string
      email: string
      firstName: string
      lastName: string
      role: string
      profilePicture?: string
      phone?: string
      preferredContactMethod?: string
    }
  }

  interface User {
    id: string
    username: string
    email: string
    firstName: string
    lastName: string
    role: string
    profilePicture?: string
    phone?: string
    preferredContactMethod?: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role: string
    username: string
    firstName: string
    lastName: string
  }
}