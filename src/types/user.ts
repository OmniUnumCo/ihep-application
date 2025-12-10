export interface User {
  id: string
  username: string
  email: string
  firstName: string
  lastName: string
  role: 'patient' | 'provider' | 'admin'
  phone?: string
  preferredContactMethod?: 'email' | 'phone' | 'sms'
  createdAt: Date
  updatedAt: Date
}

export interface UserProfile extends User {
  dateOfBirth?: Date
  gender?: string
  address?: {
    street: string
    city: string
    state: string
    zipCode: string
  }
  emergencyContact?: {
    name: string
    relationship: string
    phone: string
  }
  medicalRecordNumber?: string
  insuranceInfo?: {
    provider: string
    policyNumber: string
    groupNumber?: string
  }
}
