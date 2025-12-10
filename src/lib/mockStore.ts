import bcrypt from 'bcrypt'

export type MockUser = {
  id: number
  username: string
  password: string
  email: string
  firstName: string
  lastName: string
  role: string
  profilePicture?: string
  phone?: string
  preferredContactMethod?: string
  createdAt: Date
}

class InMemoryUserStore {
  private users: MockUser[] = []
  private nextId = 1

  constructor() {
    // Seed a demo user for local logins
    // Use 12 rounds for stronger protection (OWASP 2024 recommendation)
    const seedPassword = bcrypt.hashSync('password123', 12)
    this.users.push({
      id: this.nextId++,
      username: 'demo',
      password: seedPassword,
      email: 'demo@example.com',
      firstName: 'Demo',
      lastName: 'User',
      role: 'patient',
      createdAt: new Date(),
    })
  }

  async getUserByUsername(username: string) {
    return this.users.find((u) => u.username === username) ?? null
  }

  async getUserByEmail(email: string) {
    return this.users.find((u) => u.email === email) ?? null
  }

  async createUser(data: Omit<MockUser, 'id' | 'createdAt'>) {
    const user: MockUser = {
      ...data,
      id: this.nextId++,
      createdAt: new Date(),
    }
    this.users.push(user)
    return user
  }
}

export const mockStore = new InMemoryUserStore()
