// components/calendar/CalendarView.tsx
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';

interface Appointment {
  id: string;
  provider_id: string;
  provider_name: string;
  scheduled_time: string;
  duration: number;
  status: string;
  type: string;
  location: string;
}

interface CommunityEvent {
  id: string;
  name: string;
  date: string;
  time: string;
  duration: number;
  location: string;
  description: string;
  available_spots: number;
  total_spots: number;
}

export function CalendarView() {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [events, setEvents] = useState<CommunityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date());

  useEffect(() => {
    if (user) {
      loadCalendarData();
    }
  }, [user]);

  const loadCalendarData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load appointments
      const appointmentsResponse = await fetch('/api/calendar/appointments', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });
      
      if (appointmentsResponse.ok) {
        const { appointments } = await appointmentsResponse.json();
        setAppointments(appointments);
      }
      
      // Load community events
      const eventsResponse = await fetch('/api/calendar/events');
      if (eventsResponse.ok) {
        const { events } = await eventsResponse.json();
        setEvents(events);
      }
      
    } catch (err) {
      setError('Failed to load calendar data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isDateSelected = (date: Date) => {
    return date.toDateString() === selectedDate.toDateString();
  };

  const renderCalendarDays = () => {
    const today = new Date();
    const days = [];
    
    // Show 14 days starting from today
    for (let i = 0; i < 14; i++) {
      const date = new Date();
      date.setDate(today.getDate() + i);
      days.push(date);
    }
    
    return days.map((date, index) => (
      <div
        key={index}
        className={`p-2 text-center cursor-pointer rounded ${
          isDateSelected(date)
            ? 'bg-blue-600 text-white'
            : 'hover:bg-gray-100'
        }`}
        onClick={() => setSelectedDate(date)}
      >
        <div className="text-sm font-medium">
          {date.toLocaleDateString('en-US', { weekday: 'short' })}
        </div>
        <div className="text-lg">
          {date.getDate()}
        </div>
      </div>
    ));
  };

  const getEventsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    
    const dateAppointments = appointments.filter(apt => 
      new Date(apt.scheduled_time).toISOString().split('T')[0] === dateStr
    );
    
    const dateEvents = events.filter(event => event.date === dateStr);
    
    return [...dateAppointments, ...dateEvents];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  const todayEvents = getEventsForDate(selectedDate);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Your Health Calendar</h2>
      
      {/* Date selector */}
      <div className="grid grid-cols-7 gap-2 mb-6">
        {renderCalendarDays()}
      </div>
      
      {/* Selected date header */}
      <div className="border-b pb-4 mb-6">
        <h3 className="text-xl font-semibold">
          {selectedDate.toLocaleDateString('en-US', { 
            weekday: 'long', 
            month: 'long', 
            day: 'numeric' 
          })}
        </h3>
      </div>
      
      {/* Events list */}
      <div className="space-y-4">
        {todayEvents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No appointments or events scheduled for this day</p>
            <button className="mt-2 text-blue-600 hover:text-blue-800">
              Schedule an appointment
            </button>
          </div>
        ) : (
          todayEvents.map((event: any) => (
            <div 
              key={event.id} 
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              {'provider_id' in event ? (
                // Appointment
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold text-blue-600">
                      {event.type === 'telehealth' ? '📱' : '🏥'} 
                      {' '}{event.provider_name}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {formatDate(event.scheduled_time)}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {event.location}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      event.status === 'scheduled' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {event.status}
                    </span>
                    <button className="block mt-2 text-sm text-blue-600 hover:text-blue-800">
                      View Details
                    </button>
                  </div>
                </div>
              ) : (
                // Community Event
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold text-purple-600">
                      🤝 {event.name}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {event.time} • {event.duration} hours
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {event.location}
                    </p>
                    <p className="text-sm text-gray-600 mt-2">
                      {event.description}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm">
                      <span className="text-gray-500">Spots: </span>
                      <span className="font-medium">
                        {event.available_spots}/{event.total_spots}
                      </span>
                    </div>
                    <button className="mt-2 px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700">
                      Join Event
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* Action buttons */}
      <div className="mt-8 flex space-x-4">
        <button className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors">
          Schedule Appointment
        </button>
        <button className="flex-1 bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors">
          Join Community Event
        </button>
      </div>
    </div>
  );
}
