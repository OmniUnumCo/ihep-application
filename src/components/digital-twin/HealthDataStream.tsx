'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity } from 'lucide-react'

interface HealthDataPoint {
  timestamp: Date
  type: string
  value: string
}

export function HealthDataStream() {
  const mockData: HealthDataPoint[] = [
    { timestamp: new Date(), type: 'Heart Rate', value: '72 bpm' },
    { timestamp: new Date(Date.now() - 60000), type: 'Blood Pressure', value: '120/80 mmHg' },
    { timestamp: new Date(Date.now() - 120000), type: 'Steps', value: '8,432' },
  ]

  return (
    <Card className="apple-card">
      <CardHeader>
        <CardTitle className="flex items-center text-sm">
          <Activity className="h-4 w-4 mr-2" />
          Real-time Health Data
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {mockData.map((data, index) => (
            <div key={index} className="flex justify-between items-center text-sm py-2 border-b last:border-0">
              <div>
                <p className="font-medium">{data.type}</p>
                <p className="text-xs text-gray-600">
                  {data.timestamp.toLocaleTimeString()}
                </p>
              </div>
              <span className="font-medium">{data.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
