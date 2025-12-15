'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Bot, Activity, Brain, Heart, TrendingUp, Zap, Eye } from 'lucide-react'

export default function DigitalTwinPage() {
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)

  const healthSystems = [
    { id: 'immune', name: 'Immune System', status: 85, icon: Zap, color: 'text-blue-500' },
    { id: 'cardiovascular', name: 'Cardiovascular', status: 92, icon: Heart, color: 'text-red-500' },
    { id: 'nervous', name: 'Nervous System', status: 78, icon: Brain, color: 'text-purple-500' },
    { id: 'metabolic', name: 'Metabolic', status: 88, icon: Activity, color: 'text-green-500' },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text flex items-center">
          <Bot className="h-8 w-8 mr-3" />
          Digital Twin Visualization
        </h1>
        <p className="text-gray-600 mt-2">
          Real-time simulation of your health data and predicted outcomes
        </p>
      </div>

      {/* Overall Health Score */}
      <Card className="apple-card bg-gradient-to-br from-blue-50 to-purple-50">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1 text-center md:text-left">
              <h3 className="text-lg font-medium text-gray-600 mb-2">Overall Health Index</h3>
              <div className="text-5xl font-bold gradient-text mb-2">86%</div>
              <p className="text-sm text-gray-600">
                Your digital twin indicates excellent health trends
              </p>
            </div>
            <div className="w-48 h-48 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white relative">
              <div className="absolute inset-4 rounded-full bg-white/20 backdrop-blur-sm"></div>
              <div className="relative">
                <Bot className="h-24 w-24" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3D Visualization Placeholder */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center">
              <Eye className="h-5 w-5 mr-2" />
              Interactive Health Model
            </span>
            <Button variant="outline" size="sm">
              Fullscreen
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="aspect-video bg-gradient-to-br from-slate-900 to-blue-900 rounded-lg relative overflow-hidden">
            {/* Placeholder for 3D visualization */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <Bot className="h-16 w-16 mx-auto mb-4 animate-pulse" />
                <p className="text-lg font-medium">3D Health Model</p>
                <p className="text-sm text-gray-300 mt-2">
                  Interactive visualization of your body systems
                </p>
                <Button className="mt-4 gradient-primary">
                  Explore Model
                </Button>
              </div>
            </div>
            {/* Animated particles effect */}
            <div className="absolute inset-0 opacity-30">
              {Array.from({ length: 20 }).map((_, i) => (
                <div
                  key={i}
                  className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                    animationDelay: `${Math.random() * 2}s`,
                  }}
                ></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Status Overview */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle>Body Systems Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {healthSystems.map((system) => (
              <div
                key={system.id}
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  selectedSystem === system.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedSystem(system.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <system.icon className={`h-6 w-6 mr-3 ${system.color}`} />
                    <h4 className="font-medium">{system.name}</h4>
                  </div>
                  <span className="text-2xl font-bold">{system.status}%</span>
                </div>
                <Progress value={system.status} className="h-2" />
                <div className="mt-2 flex items-center text-sm text-gray-600">
                  <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                  <span>Trending positive</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analysis Tabs */}
      <Tabs defaultValue="predictions" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="predictions" className="space-y-6">
          <Card className="apple-card">
            <CardHeader>
              <CardTitle>Health Predictions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-l-4 border-green-500 bg-green-50 p-4 rounded">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-green-900">Positive Outlook</h4>
                      <p className="text-sm text-green-700 mt-1">
                        Based on current trends, your CD4 count is predicted to remain in healthy range
                      </p>
                    </div>
                    <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">95% confidence</span>
                  </div>
                </div>

                <div className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-blue-900">Weight Goal Progress</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        At current pace, you're likely to reach your target weight in 6 weeks
                      </p>
                    </div>
                    <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">88% confidence</span>
                  </div>
                </div>

                <div className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-yellow-900">Sleep Pattern Alert</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        Consider improving sleep consistency to optimize immune function
                      </p>
                    </div>
                    <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded">72% confidence</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card className="apple-card">
            <CardHeader>
              <CardTitle>30-Day Health Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Placeholder for charts - in production, use recharts or similar */}
                <div>
                  <h4 className="font-medium mb-3">Medication Adherence</h4>
                  <div className="h-32 bg-gradient-to-r from-green-100 to-green-200 rounded-lg flex items-end justify-around p-4">
                    {Array.from({ length: 30 }).map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-green-600 rounded-t"
                        style={{ height: `${70 + Math.random() * 30}%` }}
                      ></div>
                    ))}
                  </div>
                  <p className="text-sm text-gray-600 mt-2">Average: 95% • Trend: ↗ Improving</p>
                </div>

                <div>
                  <h4 className="font-medium mb-3">Activity Level</h4>
                  <div className="h-32 bg-gradient-to-r from-blue-100 to-blue-200 rounded-lg flex items-end justify-around p-4">
                    {Array.from({ length: 30 }).map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-blue-600 rounded-t"
                        style={{ height: `${50 + Math.random() * 50}%` }}
                      ></div>
                    ))}
                  </div>
                  <p className="text-sm text-gray-600 mt-2">Average: 8,432 steps • Trend: → Stable</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <Card className="apple-card">
            <CardHeader>
              <CardTitle>Personalized Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-4 p-4 bg-blue-50 rounded-lg">
                  <Activity className="h-6 w-6 text-blue-500 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h4 className="font-medium">Increase Cardiovascular Activity</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Adding 15 minutes of moderate exercise could improve your cardiovascular score by 5%
                    </p>
                    <Button size="sm" variant="outline" className="mt-2">
                      View Exercise Plans
                    </Button>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 bg-purple-50 rounded-lg">
                  <Brain className="h-6 w-6 text-purple-500 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h4 className="font-medium">Mindfulness Practice</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Daily meditation could help reduce stress markers and improve overall wellness
                    </p>
                    <Button size="sm" variant="outline" className="mt-2">
                      Start Guided Meditation
                    </Button>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 bg-green-50 rounded-lg">
                  <Heart className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h4 className="font-medium">Nutrition Optimization</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Your digital twin suggests increasing vitamin D intake for immune support
                    </p>
                    <Button size="sm" variant="outline" className="mt-2">
                      View Nutrition Guide
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* AI Insights */}
      <Card className="apple-card border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bot className="h-5 w-5 mr-2 text-purple-600" />
            AI-Powered Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 mb-4">
            Your digital twin has analyzed 30 days of health data and identified key patterns that could
            enhance your wellness journey. The simulation suggests maintaining current medication adherence
            while focusing on sleep quality and stress management for optimal outcomes.
          </p>
          <Button variant="outline" className="w-full">
            Chat with AI Health Assistant
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
