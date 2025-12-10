import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getHealthSummary,
  getHealthMetrics,
  addHealthMetric,
  getVitalSigns,
  getMedicationAdherence,
  getWellnessGoals,
  createWellnessGoal,
  updateWellnessGoal,
} from '@/lib/api/wellness'
import { HealthMetric, WellnessGoal } from '@/types/wellness'

export function useHealthSummary(userId: string) {
  return useQuery({
    queryKey: ['healthSummary', userId],
    queryFn: () => getHealthSummary(userId),
    enabled: !!userId,
  })
}

export function useHealthMetrics(userId: string, type?: string) {
  return useQuery({
    queryKey: ['healthMetrics', userId, type],
    queryFn: () => getHealthMetrics(userId, type),
    enabled: !!userId,
  })
}

export function useAddHealthMetric() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Omit<HealthMetric, 'id' | 'recordedAt'>) => addHealthMetric(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['healthMetrics', variables.userId] })
      queryClient.invalidateQueries({ queryKey: ['healthSummary', variables.userId] })
    },
  })
}

export function useVitalSigns(userId: string) {
  return useQuery({
    queryKey: ['vitalSigns', userId],
    queryFn: () => getVitalSigns(userId),
    enabled: !!userId,
  })
}

export function useMedicationAdherence(userId: string) {
  return useQuery({
    queryKey: ['medicationAdherence', userId],
    queryFn: () => getMedicationAdherence(userId),
    enabled: !!userId,
  })
}

export function useWellnessGoals(userId: string) {
  return useQuery({
    queryKey: ['wellnessGoals', userId],
    queryFn: () => getWellnessGoals(userId),
    enabled: !!userId,
  })
}

export function useCreateWellnessGoal() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Omit<WellnessGoal, 'id' | 'progress'>) => createWellnessGoal(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['wellnessGoals', variables.userId] })
      queryClient.invalidateQueries({ queryKey: ['healthSummary', variables.userId] })
    },
  })
}

export function useUpdateWellnessGoal() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<WellnessGoal> }) =>
      updateWellnessGoal(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['wellnessGoals', data.userId] })
      queryClient.invalidateQueries({ queryKey: ['healthSummary', data.userId] })
    },
  })
}
