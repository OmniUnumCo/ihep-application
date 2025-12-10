'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface HealthChartProps {
  title: string
  data?: any[]
  height?: number
}

export function HealthChart({ title, data = [], height = 200 }: HealthChartProps) {
  // Placeholder for chart visualization
  // In production, use recharts or similar library

  return (
    <Card className="apple-card">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg flex items-center justify-center"
          style={{ height: `${height}px` }}
        >
          <div className="text-center text-gray-400">
            <p className="text-sm">Chart visualization</p>
            <p className="text-xs mt-1">Data visualization will appear here</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
