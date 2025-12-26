'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Calendar as CalendarIcon, Plus, Clock, MapPin, User, X } from 'lucide-react'

export default function CalendarPage() {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showAddModal, setShowAddModal] = useState(false)
  const [appointmentData, setAppointmentData] = useState({
    title: '',
    provider: '',
    date: '',
    time: '',
    duration: '30',
    type: 'in-person',
    location: '',
    notes: ''
  })

  const handleAddAppointment = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Save appointment to database
    console.log('Adding appointment:', appointmentData)
    setShowAddModal(false)
    setAppointmentData({
      title: '',
      provider: '',
      date: '',
      time: '',
      duration: '30',
      type: 'in-person',
      location: '',
      notes: ''
    })
  }

  // Get current month's appointment days
  const getAppointmentDay = (dayOffset: number) => {
    const date = new Date()
    date.setDate(date.getDate() + dayOffset)
    return date.getDate()
  }

  const upcomingAppointments = [
    {
      id: '1',
      title: 'Follow-up Consultation',
      provider: 'Dr. Sarah Johnson',
      specialty: 'Internal Medicine',
      date: 'Tomorrow',
      day: getAppointmentDay(1),
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
      date: 'Next Monday',
      day: getAppointmentDay(7),
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
      date: 'Next Wednesday',
      day: getAppointmentDay(9),
      time: '4:00 PM',
      duration: '60 min',
      location: 'Virtual',
      type: 'Telehealth',
    },
  ]

  // Get appointments for a specific day
  const getAppointmentsForDay = (day: number) => {
    return upcomingAppointments.filter(apt => apt.day === day)
  }

  // Get all days that have appointments
  const appointmentDays = upcomingAppointments.map(apt => apt.day)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Calendar & Appointments</h1>
          <p className="text-gray-600 mt-2">Manage your healthcare schedule</p>
        </div>
        <Button className="gradient-primary" onClick={() => setShowAddModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Appointment
        </Button>
      </div>

      {/* Add Appointment Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto relative">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Schedule New Appointment</h2>
            <form onSubmit={handleAddAppointment} className="space-y-4">
              <div>
                <Label htmlFor="appt-title">Appointment Title</Label>
                <Input
                  id="appt-title"
                  value={appointmentData.title}
                  onChange={(e) => setAppointmentData({ ...appointmentData, title: e.target.value })}
                  placeholder="e.g., Follow-up Consultation"
                  className="mt-1"
                  required
                />
              </div>
              <div>
                <Label htmlFor="appt-provider">Provider</Label>
                <Select
                  value={appointmentData.provider}
                  onValueChange={(v) => setAppointmentData({ ...appointmentData, provider: v })}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="dr-sarah-johnson">Dr. Sarah Johnson - Internal Medicine</SelectItem>
                    <SelectItem value="dr-michael-chen">Dr. Michael Chen - Laboratory</SelectItem>
                    <SelectItem value="lisa-martinez">Lisa Martinez, LCSW - Mental Health</SelectItem>
                    <SelectItem value="dr-james-wilson">Dr. James Wilson - Cardiology</SelectItem>
                    <SelectItem value="other">Other Provider</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="appt-date">Date</Label>
                  <Input
                    id="appt-date"
                    type="date"
                    value={appointmentData.date}
                    onChange={(e) => setAppointmentData({ ...appointmentData, date: e.target.value })}
                    className="mt-1"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="appt-time">Time</Label>
                  <Input
                    id="appt-time"
                    type="time"
                    value={appointmentData.time}
                    onChange={(e) => setAppointmentData({ ...appointmentData, time: e.target.value })}
                    className="mt-1"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="appt-duration">Duration</Label>
                  <Select
                    value={appointmentData.duration}
                    onValueChange={(v) => setAppointmentData({ ...appointmentData, duration: v })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 minutes</SelectItem>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="45">45 minutes</SelectItem>
                      <SelectItem value="60">1 hour</SelectItem>
                      <SelectItem value="90">1.5 hours</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="appt-type">Appointment Type</Label>
                  <Select
                    value={appointmentData.type}
                    onValueChange={(v) => setAppointmentData({ ...appointmentData, type: v })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="in-person">In-Person</SelectItem>
                      <SelectItem value="telehealth">Telehealth</SelectItem>
                      <SelectItem value="phone">Phone Call</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="appt-location">Location</Label>
                <Input
                  id="appt-location"
                  value={appointmentData.location}
                  onChange={(e) => setAppointmentData({ ...appointmentData, location: e.target.value })}
                  placeholder={appointmentData.type === 'telehealth' ? 'Video link will be provided' : 'e.g., Main Clinic, Room 203'}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="appt-notes">Notes (Optional)</Label>
                <Textarea
                  id="appt-notes"
                  value={appointmentData.notes}
                  onChange={(e) => setAppointmentData({ ...appointmentData, notes: e.target.value })}
                  placeholder="Any additional information for the appointment..."
                  className="mt-1"
                  rows={3}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button type="submit" className="flex-1 gradient-primary">
                  Schedule Appointment
                </Button>
              </div>
            </form>
            <button
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

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
              {/* Interactive calendar */}
              <div className="text-center">
                <div className="flex items-center justify-between mb-3">
                  <button
                    onClick={() => {
                      const newDate = new Date(selectedDate)
                      newDate.setMonth(newDate.getMonth() - 1)
                      setSelectedDate(newDate)
                    }}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    &lt;
                  </button>
                  <div className="text-sm font-medium text-gray-700">
                    {selectedDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
                  </div>
                  <button
                    onClick={() => {
                      const newDate = new Date(selectedDate)
                      newDate.setMonth(newDate.getMonth() + 1)
                      setSelectedDate(newDate)
                    }}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    &gt;
                  </button>
                </div>
                <div className="grid grid-cols-7 gap-1 text-xs">
                  {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, i) => (
                    <div key={i} className="text-center font-medium text-gray-600 p-2">
                      {day}
                    </div>
                  ))}
                  {(() => {
                    const year = selectedDate.getFullYear()
                    const month = selectedDate.getMonth()
                    const firstDay = new Date(year, month, 1).getDay()
                    const daysInMonth = new Date(year, month + 1, 0).getDate()
                    const today = new Date()
                    const isCurrentMonth = today.getMonth() === month && today.getFullYear() === year
                    const todayDate = today.getDate()

                    const cells = []
                    // Empty cells for days before the first day of the month
                    for (let i = 0; i < firstDay; i++) {
                      cells.push(<div key={`empty-${i}`} className="p-2"></div>)
                    }
                    // Days of the month
                    for (let day = 1; day <= daysInMonth; day++) {
                      const isToday = isCurrentMonth && day === todayDate
                      const isSelected = selectedDate.getDate() === day && selectedDate.getMonth() === month
                      const hasAppointment = appointmentDays.includes(day)

                      cells.push(
                        <button
                          key={day}
                          onClick={() => {
                            const newDate = new Date(year, month, day)
                            setSelectedDate(newDate)
                          }}
                          className={`text-center p-2 rounded-full transition-colors ${
                            isToday
                              ? 'bg-green-600 text-white hover:bg-green-700'
                              : isSelected
                              ? 'bg-green-100 text-green-800 font-medium ring-2 ring-green-500'
                              : hasAppointment
                              ? 'bg-blue-500 text-white hover:bg-blue-600'
                              : 'hover:bg-gray-100'
                          }`}
                        >
                          {day}
                        </button>
                      )
                    }
                    return cells
                  })()}
                </div>
              </div>
              <div className="text-xs text-gray-600 space-y-1">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-600 mr-2"></div>
                  <span>Today</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-100 ring-2 ring-green-500 mr-2"></div>
                  <span>Selected</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                  <span>Has appointments</span>
                </div>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm font-medium mb-2">
                  Selected: {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                </p>
                {getAppointmentsForDay(selectedDate.getDate()).length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-blue-600">Appointments on this day:</p>
                    {getAppointmentsForDay(selectedDate.getDate()).map((apt) => (
                      <div key={apt.id} className="bg-blue-50 border border-blue-200 rounded-lg p-2">
                        <p className="font-medium text-sm">{apt.title}</p>
                        <p className="text-xs text-gray-600">{apt.time} - {apt.provider}</p>
                        <p className="text-xs text-gray-500">{apt.location}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500">No appointments on this day</p>
                )}
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
