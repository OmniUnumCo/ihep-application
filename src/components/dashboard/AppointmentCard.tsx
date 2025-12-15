'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar, Clock, MapPin, User } from 'lucide-react'

interface Appointment {
  id: string
  title: string
  provider: string
  date: string
  time: string
  location: string
  type?: 'In-Person' | 'Telehealth'
}

interface AppointmentCardProps {
  appointment: Appointment
  onReschedule?: () => void
  onCancel?: () => void
  onJoinCall?: () => void
}

export function AppointmentCard({
  appointment,
  onReschedule,
  onCancel,
  onJoinCall
}: AppointmentCardProps) {
  return (
    <Card className="apple-card">
      <CardContent className="pt-6">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h4 className="font-medium text-lg">{appointment.title}</h4>
            <p className="text-sm text-gray-600 flex items-center mt-1">
              <User className="h-3 w-3 mr-1" />
              {appointment.provider}
            </p>
          </div>
          {appointment.type && (
            <span
              className={`px-2 py-1 text-xs rounded-full ${
                appointment.type === 'Telehealth'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-blue-100 text-blue-700'
              }`}
            >
              {appointment.type}
            </span>
          )}
        </div>

        <div className="space-y-2 text-sm mb-4">
          <div className="flex items-center text-gray-600">
            <Calendar className="h-4 w-4 mr-2" />
            <span>{appointment.date}</span>
          </div>
          <div className="flex items-center text-gray-600">
            <Clock className="h-4 w-4 mr-2" />
            <span>{appointment.time}</span>
          </div>
          <div className="flex items-center text-gray-600">
            <MapPin className="h-4 w-4 mr-2" />
            <span>{appointment.location}</span>
          </div>
        </div>

        <div className="flex gap-2">
          {onReschedule && (
            <Button variant="outline" size="sm" className="flex-1" onClick={onReschedule}>
              Reschedule
            </Button>
          )}
          {onCancel && (
            <Button variant="outline" size="sm" className="flex-1" onClick={onCancel}>
              Cancel
            </Button>
          )}
          {appointment.type === 'Telehealth' && onJoinCall && (
            <Button size="sm" className="flex-1 gradient-primary" onClick={onJoinCall}>
              Join Call
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
