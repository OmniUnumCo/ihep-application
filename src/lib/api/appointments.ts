import { Appointment, AppointmentWithDetails, AppointmentRequest } from '@/types/appointment'

export async function getAppointments(userId: string): Promise<AppointmentWithDetails[]> {
  const response = await fetch(`/api/appointments?userId=${userId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch appointments')
  }

  return response.json()
}

export async function getUpcomingAppointments(userId: string): Promise<AppointmentWithDetails[]> {
  const response = await fetch(`/api/appointments/upcoming?userId=${userId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch upcoming appointments')
  }

  return response.json()
}

export async function getAppointmentById(id: string): Promise<AppointmentWithDetails> {
  const response = await fetch(`/api/appointments/${id}`)

  if (!response.ok) {
    throw new Error('Failed to fetch appointment')
  }

  return response.json()
}

export async function createAppointment(data: AppointmentRequest): Promise<Appointment> {
  const response = await fetch('/api/appointments', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'Failed to create appointment')
  }

  return response.json()
}

export async function updateAppointment(id: string, data: Partial<Appointment>): Promise<Appointment> {
  const response = await fetch(`/api/appointments/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'Failed to update appointment')
  }

  return response.json()
}

export async function cancelAppointment(id: string): Promise<void> {
  const response = await fetch(`/api/appointments/${id}/cancel`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error('Failed to cancel appointment')
  }
}
