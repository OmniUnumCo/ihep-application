import { HealthMetric, VitalSigns, MedicationAdherence, WellnessGoal, HealthSummary } from '@/types/wellness'

export async function getHealthSummary(userId: string): Promise<HealthSummary> {
  const response = await fetch(`/api/wellness/summary?userId=${userId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch health summary')
  }

  return response.json()
}

export async function getHealthMetrics(userId: string, type?: string): Promise<HealthMetric[]> {
  const params = new URLSearchParams({ userId })
  if (type) params.append('type', type)

  const response = await fetch(`/api/wellness/metrics?${params.toString()}`)

  if (!response.ok) {
    throw new Error('Failed to fetch health metrics')
  }

  return response.json()
}

export async function addHealthMetric(data: Omit<HealthMetric, 'id' | 'recordedAt'>): Promise<HealthMetric> {
  const response = await fetch('/api/wellness/metrics', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'Failed to add health metric')
  }

  return response.json()
}

export async function getVitalSigns(userId: string): Promise<VitalSigns[]> {
  const response = await fetch(`/api/wellness/vitals?userId=${userId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch vital signs')
  }

  return response.json()
}

export async function getMedicationAdherence(userId: string): Promise<MedicationAdherence[]> {
  const response = await fetch(`/api/wellness/medications?userId=${userId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch medication adherence')
  }

  return response.json()
}

export async function getWellnessGoals(userId: string): Promise<WellnessGoal[]> {
  const response = await fetch(`/api/wellness/goals?userId=${userId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch wellness goals')
  }

  return response.json()
}

export async function createWellnessGoal(data: Omit<WellnessGoal, 'id' | 'progress'>): Promise<WellnessGoal> {
  const response = await fetch('/api/wellness/goals', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'Failed to create wellness goal')
  }

  return response.json()
}

export async function updateWellnessGoal(id: string, data: Partial<WellnessGoal>): Promise<WellnessGoal> {
  const response = await fetch(`/api/wellness/goals/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'Failed to update wellness goal')
  }

  return response.json()
}
