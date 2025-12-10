import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getAppointments,
  getUpcomingAppointments,
  getAppointmentById,
  createAppointment,
  updateAppointment,
  cancelAppointment,
} from '@/lib/api/appointments'
import { Appointment, AppointmentRequest } from '@/types/appointment'

export function useAppointments(userId: string) {
  return useQuery({
    queryKey: ['appointments', userId],
    queryFn: () => getAppointments(userId),
    enabled: !!userId,
  })
}

export function useUpcomingAppointments(userId: string) {
  return useQuery({
    queryKey: ['upcomingAppointments', userId],
    queryFn: () => getUpcomingAppointments(userId),
    enabled: !!userId,
  })
}

export function useAppointment(id: string) {
  return useQuery({
    queryKey: ['appointment', id],
    queryFn: () => getAppointmentById(id),
    enabled: !!id,
  })
}

export function useCreateAppointment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: AppointmentRequest) => createAppointment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] })
      queryClient.invalidateQueries({ queryKey: ['upcomingAppointments'] })
    },
  })
}

export function useUpdateAppointment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Appointment> }) =>
      updateAppointment(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] })
      queryClient.invalidateQueries({ queryKey: ['upcomingAppointments'] })
      queryClient.invalidateQueries({ queryKey: ['appointment', variables.id] })
    },
  })
}

export function useCancelAppointment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => cancelAppointment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] })
      queryClient.invalidateQueries({ queryKey: ['upcomingAppointments'] })
    },
  })
}
