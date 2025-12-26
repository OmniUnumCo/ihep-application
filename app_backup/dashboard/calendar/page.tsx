'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Plus,
  Clock,
  MapPin,
  User,
  Video,
  Phone
} from 'lucide-react';

interface Appointment {
  id: string;
  title: string;
  date: Date;
  time: string;
  duration: string;
  provider: string;
  location: string;
  type: 'in-person' | 'video' | 'phone';
  status: 'confirmed' | 'pending' | 'cancelled';
}

const mockAppointments: Appointment[] = [
  {
    id: '1',
    title: 'Regular Check-up',
    date: new Date(2025, 0, 15),
    time: '10:00 AM',
    duration: '30 min',
    provider: 'Dr. Sarah Chen',
    location: 'Main Clinic, Room 204',
    type: 'in-person',
    status: 'confirmed',
  },
  {
    id: '2',
    title: 'Lab Work Review',
    date: new Date(2025, 0, 22),
    time: '2:00 PM',
    duration: '15 min',
    provider: 'Dr. Sarah Chen',
    location: 'Video Call',
    type: 'video',
    status: 'confirmed',
  },
  {
    id: '3',
    title: 'Medication Consultation',
    date: new Date(2025, 1, 5),
    time: '11:30 AM',
    duration: '20 min',
    provider: 'Pharmacist James Wilson',
    location: 'Phone Call',
    type: 'phone',
    status: 'pending',
  },
];

const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startingDayOfWeek = firstDayOfMonth.getDay();
  const daysInMonth = lastDayOfMonth.getDate();

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(new Date(year, month + (direction === 'next' ? 1 : -1), 1));
  };

  const getAppointmentsForDate = (date: Date) => {
    return mockAppointments.filter(
      (apt) =>
        apt.date.getFullYear() === date.getFullYear() &&
        apt.date.getMonth() === date.getMonth() &&
        apt.date.getDate() === date.getDate()
    );
  };

  const hasAppointments = (date: Date) => getAppointmentsForDate(date).length > 0;

  const getTypeIcon = (type: Appointment['type']) => {
    switch (type) {
      case 'video':
        return Video;
      case 'phone':
        return Phone;
      default:
        return MapPin;
    }
  };

  const renderCalendarDays = () => {
    const days = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="h-12" />);
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const isToday = new Date().toDateString() === date.toDateString();
      const isSelected = selectedDate?.toDateString() === date.toDateString();
      const hasApts = hasAppointments(date);

      days.push(
        <button
          key={day}
          onClick={() => setSelectedDate(date)}
          className={`h-12 rounded-lg flex flex-col items-center justify-center relative transition-all
            ${isToday ? 'ring-2 ring-purple-500' : ''}
            ${isSelected ? 'bg-purple-500 text-white' : 'hover:bg-white/10 text-white'}
          `}
        >
          <span className="text-sm">{day}</span>
          {hasApts && (
            <span className="absolute bottom-1 w-1.5 h-1.5 bg-pink-500 rounded-full" />
          )}
        </button>
      );
    }

    return days;
  };

  const selectedDateAppointments = selectedDate ? getAppointmentsForDate(selectedDate) : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="p-2 text-white/70 hover:text-white transition-colors rounded-lg hover:bg-white/10"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white">Calendar</h1>
              <p className="text-purple-300 text-sm">Manage your appointments</p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
            <Plus className="w-4 h-4" />
            New Appointment
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Calendar */}
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 p-6">
              {/* Month Navigation */}
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {months[month]} {year}
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigateMonth('prev')}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5 text-white" />
                  </button>
                  <button
                    onClick={() => navigateMonth('next')}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <ChevronRight className="w-5 h-5 text-white" />
                  </button>
                </div>
              </div>

              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {daysOfWeek.map((day) => (
                  <div key={day} className="text-center text-purple-300 text-sm font-medium py-2">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-2">{renderCalendarDays()}</div>
            </div>
          </div>

          {/* Appointments Panel */}
          <div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10">
              <div className="p-4 border-b border-white/10">
                <h3 className="text-lg font-semibold text-white">
                  {selectedDate
                    ? selectedDate.toLocaleDateString('en-US', {
                        weekday: 'long',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'Select a date'}
                </h3>
              </div>

              <div className="p-4 space-y-4">
                {selectedDateAppointments.length === 0 ? (
                  <p className="text-purple-300 text-center py-8">
                    No appointments scheduled
                  </p>
                ) : (
                  selectedDateAppointments.map((apt) => {
                    const TypeIcon = getTypeIcon(apt.type);
                    return (
                      <div
                        key={apt.id}
                        className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-purple-500/50 transition-colors"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <h4 className="font-medium text-white">{apt.title}</h4>
                          <span
                            className={`px-2 py-1 rounded-full text-xs ${
                              apt.status === 'confirmed'
                                ? 'bg-green-500/20 text-green-400'
                                : apt.status === 'pending'
                                ? 'bg-yellow-500/20 text-yellow-400'
                                : 'bg-red-500/20 text-red-400'
                            }`}
                          >
                            {apt.status}
                          </span>
                        </div>

                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2 text-purple-300">
                            <Clock className="w-4 h-4" />
                            <span>
                              {apt.time} ({apt.duration})
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-purple-300">
                            <User className="w-4 h-4" />
                            <span>{apt.provider}</span>
                          </div>
                          <div className="flex items-center gap-2 text-purple-300">
                            <TypeIcon className="w-4 h-4" />
                            <span>{apt.location}</span>
                          </div>
                        </div>

                        <div className="mt-4 flex gap-2">
                          {apt.type === 'video' && (
                            <button className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors">
                              Join Call
                            </button>
                          )}
                          <button className="flex-1 px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors">
                            Reschedule
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Upcoming Appointments */}
            <div className="mt-4 bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Upcoming</h3>
              <div className="space-y-3">
                {mockAppointments.slice(0, 3).map((apt) => (
                  <div
                    key={apt.id}
                    className="flex items-center gap-3 p-3 bg-white/5 rounded-lg"
                  >
                    <div className="text-center">
                      <div className="text-xs text-purple-300">
                        {apt.date.toLocaleDateString('en-US', { month: 'short' })}
                      </div>
                      <div className="text-lg font-bold text-white">
                        {apt.date.getDate()}
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-white text-sm font-medium">{apt.title}</p>
                      <p className="text-purple-300 text-xs">{apt.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
