'use client'

import { useSession } from 'next-auth/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Activity, Calendar, Heart, TrendingUp } from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const { data: session } = useSession()
  const displayName = (() => {
    const user: any = session?.user
    const fullName = [user?.firstName, user?.lastName].filter(Boolean).join(' ').trim()
    return fullName || user?.username || user?.email || 'User'
  })()

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">
          Welcome back, {displayName}
        </h1>
        <p className="text-gray-600 mt-2">
          Here's an overview of your health and wellness
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Wellness Score</CardTitle>
            <Heart className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85%</div>
            <p className="text-xs text-gray-600">+2% from last week</p>
          </CardContent>
        </Card>

        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Goals</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-gray-600">2 on track</p>
          </CardContent>
        </Card>

        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming Appointments</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-gray-600">Next: Tomorrow 2 PM</p>
          </CardContent>
        </Card>

        <Card className="apple-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Medication Adherence</CardTitle>
            <Activity className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">95%</div>
            <p className="text-xs text-gray-600">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="apple-card">
          <CardHeader>
            <CardTitle>Recent Health Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Blood Pressure</span>
                <span className="font-medium">120/80 mmHg</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Heart Rate</span>
                <span className="font-medium">72 bpm</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Weight</span>
                <span className="font-medium">165 lbs</span>
              </div>
              <Link href="/dashboard/wellness">
                <Button variant="outline" className="w-full mt-4">
                  View All Metrics
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card className="apple-card">
          <CardHeader>
            <CardTitle>Upcoming Appointments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">Dr. Sarah Johnson</p>
                  <p className="text-sm text-gray-600">Follow-up Consultation</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">Tomorrow</p>
                  <p className="text-sm text-gray-600">2:00 PM</p>
                </div>
              </div>
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">Dr. Michael Chen</p>
                  <p className="text-sm text-gray-600">Lab Work</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">Next Week</p>
                  <p className="text-sm text-gray-600">10:30 AM</p>
                </div>
              </div>
              <Link href="/dashboard/calendar">
                <Button variant="outline" className="w-full mt-4">
                  View Calendar
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/dashboard/providers">
              <Button variant="outline" className="w-full">
                Find a Provider
              </Button>
            </Link>
            <Link href="/dashboard/calendar">
              <Button variant="outline" className="w-full">
                Schedule Appointment
              </Button>
            </Link>
            <Link href="/dashboard/digital-twin">
              <Button variant="outline" className="w-full">
                View Digital Twin
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
