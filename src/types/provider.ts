export interface Provider {
  id: string
  userId: string
  firstName: string
  lastName: string
  title: string // Dr., RN, NP, etc.
  specialty: string
  licenseNumber: string
  email: string
  phone: string
  bio?: string
  yearsOfExperience?: number
  languages?: string[]
  acceptingNewPatients: boolean
  rating?: number
  reviewCount?: number
  availableHours?: {
    day: string
    startTime: string
    endTime: string
  }[]
  location?: {
    facilityName: string
    address: string
    city: string
    state: string
    zipCode: string
  }
  createdAt: Date
  updatedAt: Date
}

export interface ProviderSearchFilters {
  specialty?: string
  acceptingNewPatients?: boolean
  language?: string
  minRating?: number
  city?: string
  state?: string
}
