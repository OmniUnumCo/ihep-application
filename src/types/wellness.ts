export interface HealthMetric {
  id: string
  userId: string
  type: 'weight' | 'blood_pressure' | 'heart_rate' | 'steps' | 'sleep' | 'medication_adherence' | 'mood' | 'cd4_count' | 'viral_load'
  value: number | string
  unit: string
  recordedAt: Date
  notes?: string
}

export interface VitalSigns {
  bloodPressure?: {
    systolic: number
    diastolic: number
    unit: 'mmHg'
  }
  heartRate?: {
    value: number
    unit: 'bpm'
  }
  temperature?: {
    value: number
    unit: 'F' | 'C'
  }
  oxygenSaturation?: {
    value: number
    unit: '%'
  }
  recordedAt: Date
}

export interface MedicationAdherence {
  id: string
  userId: string
  medicationName: string
  dosage: string
  frequency: string
  adherenceRate: number // percentage
  missedDoses: number
  period: 'daily' | 'weekly' | 'monthly'
  lastTaken?: Date
}

export interface WellnessGoal {
  id: string
  userId: string
  type: 'exercise' | 'nutrition' | 'medication' | 'sleep' | 'mental_health' | 'custom'
  title: string
  description?: string
  targetValue: number
  currentValue: number
  unit: string
  startDate: Date
  targetDate: Date
  status: 'active' | 'completed' | 'paused'
  progress: number // percentage
}

export interface HealthSummary {
  userId: string
  latestVitals?: VitalSigns
  recentMetrics: HealthMetric[]
  medicationAdherence?: MedicationAdherence[]
  activeGoals: WellnessGoal[]
  overallWellnessScore?: number
}
