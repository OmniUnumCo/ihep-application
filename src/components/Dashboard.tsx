'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CalendarDays, Users, BookOpen, Heart, Award, MessageSquare } from 'lucide-react'
import Link from 'next/link'

export function Dashboard() {
  const { data: session, status } = useSession()

  const { data: upcomingEvents } = useQuery({
    queryKey: ['/api/events'],
    enabled: !!session
  })

  const { data: userStats } = useQuery<{ totalPoints?: number }>({
    queryKey: ['/api/users/stats'],
    enabled: !!session
  })

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <h1 className="text-4xl font-bold gradient-text mb-6">Welcome to Health Insight Ventures</h1>
            <p className="text-xl text-gray-600 mb-8">Your comprehensive digital health platform</p>
            <div className="space-x-4">
              <Link href="/login">
                <Button className="btn-glossy px-8 py-3">Log In</Button>
              </Link>
              <Link href="/register">
                <Button className="gradient-primary px-8 py-3">Sign Up</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold gradient-text">Welcome back, {session.user.firstName}!</h1>
          <p className="text-gray-600 mt-2">Here's your health dashboard overview</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Upcoming Appointments */}
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Upcoming Appointments</CardTitle>
              <div className="icon-3d icon-calendar">
                <CalendarDays className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">Next: Tomorrow 2:00 PM</p>
            </CardContent>
          </Card>

          {/* Community Activity */}
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Community Activity</CardTitle>
              <div className="icon-3d icon-community">
                <Users className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground">New messages</p>
            </CardContent>
          </Card>

          {/* Health Resources */}
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Health Resources</CardTitle>
              <div className="icon-3d icon-resources">
                <BookOpen className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">45</div>
              <p className="text-xs text-muted-foreground">Available resources</p>
            </CardContent>
          </Card>

          {/* Wellness Score */}
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Wellness Score</CardTitle>
              <div className="icon-3d icon-health">
                <Heart className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">85%</div>
              <p className="text-xs text-muted-foreground">+5% from last week</p>
            </CardContent>
          </Card>

          {/* Health Points */}
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Health Points</CardTitle>
              <div className="icon-3d icon-resources">
                <Award className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats?.totalPoints || 0}</div>
              <p className="text-xs text-muted-foreground">Total earned</p>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="apple-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
              <div className="icon-3d">
                <MessageSquare className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-muted-foreground">Actions this week</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link href="/appointments">
              <Button className="btn-glossy w-full h-16 flex flex-col items-center justify-center space-y-1">
                <CalendarDays className="h-5 w-5" />
                <span className="text-sm">Book Appointment</span>
              </Button>
            </Link>
            <Link href="/community">
              <Button className="btn-glossy w-full h-16 flex flex-col items-center justify-center space-y-1">
                <Users className="h-5 w-5" />
                <span className="text-sm">Join Community</span>
              </Button>
            </Link>
            <Link href="/resources">
              <Button className="btn-glossy w-full h-16 flex flex-col items-center justify-center space-y-1">
                <BookOpen className="h-5 w-5" />
                <span className="text-sm">Find Resources</span>
              </Button>
            </Link>
            <Link href="/wellness">
              <Button className="btn-glossy w-full h-16 flex flex-col items-center justify-center space-y-1">
                <Heart className="h-5 w-5" />
                <span className="text-sm">Wellness Tips</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
