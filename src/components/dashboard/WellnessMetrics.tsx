'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Activity, Heart, TrendingUp } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  unit?: string
  progress?: number
  trend?: 'up' | 'down' | 'stable'
  icon?: React.ReactNode
}

export function MetricCard({ title, value, unit, progress, trend, icon }: MetricCardProps) {
  return (
    <Card className="apple-card">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline">
          <div className="text-2xl font-bold">{value}</div>
          {unit && <span className="ml-1 text-sm text-gray-600">{unit}</span>}
        </div>
        {progress !== undefined && (
          <div className="mt-3">
            <Progress value={progress} className="h-2" />
          </div>
        )}
        {trend && (
          <div className="mt-2 flex items-center text-xs text-gray-600">
            {trend === 'up' && <TrendingUp className="h-3 w-3 mr-1 text-green-500" />}
            <span>{trend === 'up' ? 'Improving' : trend === 'down' ? 'Declining' : 'Stable'}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function WellnessMetrics() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Wellness Score"
        value={85}
        unit="%"
        progress={85}
        trend="up"
        icon={<Heart className="h-4 w-4 text-red-500" />}
      />
      <MetricCard
        title="Active Goals"
        value={3}
        trend="stable"
        icon={<TrendingUp className="h-4 w-4 text-green-500" />}
      />
      <MetricCard
        title="Medication Adherence"
        value={95}
        unit="%"
        progress={95}
        trend="up"
        icon={<Activity className="h-4 w-4 text-purple-500" />}
      />
      <MetricCard
        title="Steps Today"
        value="8,432"
        progress={84}
        trend="up"
        icon={<Activity className="h-4 w-4 text-blue-500" />}
      />
    </div>
  )
}
