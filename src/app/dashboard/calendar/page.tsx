'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar as CalendarIcon, Plus, Clock, MapPin, User } from 'lucide-react'

export default function CalendarPage() {
  const [selectedDate, setSelectedDate] = useState(new Date())

  const upcomingAppointments = [
    {
      id: '1',
      title: 'Follow-up Consultation',
      provider: 'Dr. Sarah Johnson',
      specialty: 'Internal Medicine',
      date: 'Tomorrow',
      time: '2:00 PM',
      duration: '30 min',
      location: 'Main Clinic, Room 203',
      type: 'In-Person',
    },
    {
      id: '2',
      title: 'Lab Work',
      provider: 'Dr. Michael Chen',
      specialty: 'Laboratory',
      date: 'Next Week, Monday',
      time: '10:30 AM',
      duration: '15 min',
      location: 'Lab Building, 2nd Floor',
      type: 'In-Person',
    },
    {
      id: '3',
      title: 'Therapy Session',
      provider: 'Lisa Martinez, LCSW',
      specialty: 'Mental Health',
      date: 'Next Week, Wednesday',
      time: '4:00 PM',
      duration: '60 min',
      location: 'Virtual',
      type: 'Telehealth',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Calendar & Appointments</h1>
          <p className="text-gray-600 mt-2">Manage your healthcare schedule</p>
        </div>
        <Button className="gradient-primary">
          <Plus className="h-4 w-4 mr-2" />
          New Appointment
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Widget */}
        <Card className="apple-card lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center">
              <CalendarIcon className="h-5 w-5 mr-2" />
              Calendar
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Simplified calendar - in production, use a proper calendar component */}
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600 mb-2">January 2025</div>
                <div className="grid grid-cols-7 gap-1 text-xs">
                  {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, i) => (
                    <div key={i} className="text-center font-medium text-gray-600 p-2">
                      {day}
                    </div>
                  ))}
                  {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                    <div
                      key={day}
                      className={`text-center p-2 rounded cursor-pointer hover:bg-gray-100 ${
                        day === 15 ? 'bg-blue-500 text-white hover:bg-blue-600' : ''
                      } ${[16, 22].includes(day) ? 'bg-blue-100' : ''}`}
                    >
                      {day}
                    </div>
                  ))}
                </div>
              </div>
              <div className="text-xs text-gray-600 space-y-1">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded bg-blue-500 mr-2"></div>
                  <span>Today</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded bg-blue-100 mr-2"></div>
                  <span>Has appointments</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Upcoming Appointments */}
        <Card className="apple-card lg:col-span-2">
          <CardHeader>
            <CardTitle>Upcoming Appointments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingAppointments.map((appointment) => (
                <div
                  key={appointment.id}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-medium text-lg">{appointment.title}</h4>
                      <p className="text-sm text-gray-600 flex items-center mt-1">
                        <User className="h-3 w-3 mr-1" />
                        {appointment.provider} • {appointment.specialty}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        appointment.type === 'Telehealth'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {appointment.type}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center text-gray-600">
                      <CalendarIcon className="h-4 w-4 mr-2" />
                      <span>{appointment.date}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Clock className="h-4 w-4 mr-2" />
                      <span>
                        {appointment.time} ({appointment.duration})
                      </span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>{appointment.location}</span>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" className="flex-1">
                      Reschedule
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      Cancel
                    </Button>
                    {appointment.type === 'Telehealth' && (
                      <Button size="sm" className="flex-1 gradient-primary">
                        Join Video Call
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Past Appointments */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle>Past Appointments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-3 border-b">
              <div>
                <p className="font-medium">Routine Checkup</p>
                <p className="text-sm text-gray-600">Dr. Sarah Johnson</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">Jan 8, 2025</p>
                <Button variant="link" size="sm" className="p-0 h-auto">
                  View Notes
                </Button>
              </div>
            </div>
            <div className="flex justify-between items-center py-3 border-b">
              <div>
                <p className="font-medium">Viral Load Test</p>
                <p className="text-sm text-gray-600">Dr. Michael Chen</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">Dec 15, 2024</p>
                <Button variant="link" size="sm" className="p-0 h-auto">
                  View Results
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
