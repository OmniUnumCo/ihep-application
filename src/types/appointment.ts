export interface Appointment {
  id: string
  patientId: string
  providerId: string
  type: 'consultation' | 'follow-up' | 'lab' | 'screening' | 'therapy' | 'other'
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no-show'
  startTime: Date
  endTime: Date
  location?: string
  notes?: string
  createdAt: Date
  updatedAt: Date
}

export interface AppointmentWithDetails extends Appointment {
  patientName: string
  providerName: string
  providerSpecialty?: string
}

export interface AppointmentRequest {
  providerId: string
  type: Appointment['type']
  preferredDate: Date
  preferredTime: 'morning' | 'afternoon' | 'evening'
  reason: string
}
