'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Activity,
  Calendar,
  Users,
  BookOpen,
  Heart,
  TrendingUp,
  Bell,
  Settings
} from 'lucide-react';

interface HealthMetric {
  label: string;
  value: string;
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'alert';
}

const healthMetrics: HealthMetric[] = [
  { label: 'CD4 Count', value: '650 cells/uL', trend: 'up', status: 'good' },
  { label: 'Viral Load', value: 'Undetectable', trend: 'stable', status: 'good' },
  { label: 'Adherence', value: '98%', trend: 'up', status: 'good' },
  { label: 'Next Appointment', value: 'Jan 15', trend: 'stable', status: 'good' },
];

const quickActions = [
  { href: '/dashboard/digital-twin', icon: Activity, label: 'Digital Twin', description: 'View your health visualization' },
  { href: '/dashboard/wellness', icon: Heart, label: 'Wellness', description: 'Track health metrics' },
  { href: '/dashboard/calendar', icon: Calendar, label: 'Calendar', description: 'Manage appointments' },
  { href: '/dashboard/providers', icon: Users, label: 'Providers', description: 'Your care team' },
  { href: '/dashboard/resources', icon: BookOpen, label: 'Resources', description: 'Educational content' },
];

export default function DashboardPage() {
  const [notifications] = useState(3);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-purple-300 text-sm">Welcome back</p>
          </div>
          <div className="flex items-center gap-4">
            <button className="relative p-2 text-white/70 hover:text-white transition-colors">
              <Bell className="w-6 h-6" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-pink-500 rounded-full text-xs flex items-center justify-center">
                  {notifications}
                </span>
              )}
            </button>
            <button className="p-2 text-white/70 hover:text-white transition-colors">
              <Settings className="w-6 h-6" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Health Metrics Summary */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Health Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {healthMetrics.map((metric) => (
              <div
                key={metric.label}
                className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-purple-300 text-sm">{metric.label}</span>
                  <TrendingUp
                    className={`w-4 h-4 ${
                      metric.trend === 'up'
                        ? 'text-green-400'
                        : metric.trend === 'down'
                        ? 'text-red-400'
                        : 'text-yellow-400'
                    }`}
                  />
                </div>
                <p className="text-2xl font-bold text-white">{metric.value}</p>
                <span
                  className={`inline-block mt-2 px-2 py-1 rounded-full text-xs ${
                    metric.status === 'good'
                      ? 'bg-green-500/20 text-green-400'
                      : metric.status === 'warning'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {metric.status === 'good' ? 'On Track' : metric.status === 'warning' ? 'Attention' : 'Action Needed'}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <Link
                key={action.href}
                href={action.href}
                className="group bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:border-purple-500/50 hover:bg-white/10 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-purple-500/20 rounded-lg group-hover:bg-purple-500/30 transition-colors">
                    <action.icon className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{action.label}</h3>
                    <p className="text-sm text-purple-300">{action.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Recent Activity */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
          <div className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 divide-y divide-white/10">
            {[
              { text: 'Lab results uploaded', time: '2 hours ago', type: 'success' },
              { text: 'Appointment confirmed for Jan 15', time: '1 day ago', type: 'info' },
              { text: 'Medication reminder set', time: '2 days ago', type: 'info' },
              { text: 'Wellness check completed', time: '3 days ago', type: 'success' },
            ].map((activity, index) => (
              <div key={index} className="p-4 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      activity.type === 'success' ? 'bg-green-400' : 'bg-blue-400'
                    }`}
                  />
                  <span className="text-white">{activity.text}</span>
                </div>
                <span className="text-purple-300 text-sm">{activity.time}</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
