'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Activity, Heart, TrendingUp, Plus } from 'lucide-react'

export default function WellnessPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('week')

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Wellness Metrics</h1>
          <p className="text-gray-600 mt-2">Track your health journey</p>
        </div>
        <Button className="gradient-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Metric
        </Button>
      </div>

      {/* Overall Wellness Score */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Overall Wellness Score</span>
            <Heart className="h-5 w-5 text-red-500" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-4xl font-bold gradient-text">85%</div>
              <p className="text-sm text-gray-600 mt-1">Great progress this month!</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-green-600 font-medium">+2%</div>
              <p className="text-xs text-gray-600">vs last week</p>
            </div>
          </div>
          <Progress value={85} className="h-3" />
        </CardContent>
      </Card>

      {/* Tabs for different metrics */}
      <Tabs defaultValue="vitals" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="vitals">Vitals</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
          <TabsTrigger value="medication">Medication</TabsTrigger>
          <TabsTrigger value="goals">Goals</TabsTrigger>
        </TabsList>

        {/* Vitals Tab */}
        <TabsContent value="vitals" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">Blood Pressure</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">120/80</span>
                    <span className="text-sm text-gray-600">mmHg</span>
                  </div>
                  <div className="text-sm text-green-600">Normal range</div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Today</span>
                      <span className="font-medium">120/80</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Yesterday</span>
                      <span className="font-medium">118/78</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">2 days ago</span>
                      <span className="font-medium">122/82</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">Heart Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">72</span>
                    <span className="text-sm text-gray-600">bpm</span>
                  </div>
                  <div className="text-sm text-green-600">Normal resting rate</div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Resting</span>
                      <span className="font-medium">72 bpm</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Active</span>
                      <span className="font-medium">98 bpm</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Peak</span>
                      <span className="font-medium">145 bpm</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">Weight</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">165</span>
                    <span className="text-sm text-gray-600">lbs</span>
                  </div>
                  <div className="text-sm text-gray-600">-2 lbs this month</div>
                  <Progress value={67} className="h-2" />
                  <p className="text-xs text-gray-600">Goal: 160 lbs</p>
                </div>
              </CardContent>
            </Card>

            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">CD4 Count</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">650</span>
                    <span className="text-sm text-gray-600">cells/mm³</span>
                  </div>
                  <div className="text-sm text-green-600">Healthy range</div>
                  <div className="text-xs text-gray-600">Last updated: 2 weeks ago</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Activity Tab */}
        <TabsContent value="activity" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">Steps Today</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">8,432</span>
                    <Activity className="h-5 w-5 text-blue-500" />
                  </div>
                  <Progress value={84} className="h-2" />
                  <p className="text-xs text-gray-600">Goal: 10,000 steps</p>
                </div>
              </CardContent>
            </Card>

            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">Active Minutes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">45</span>
                    <span className="text-sm text-gray-600">min</span>
                  </div>
                  <Progress value={75} className="h-2" />
                  <p className="text-xs text-gray-600">Goal: 60 min</p>
                </div>
              </CardContent>
            </Card>

            <Card className="apple-card">
              <CardHeader>
                <CardTitle className="text-lg">Sleep</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-3xl font-bold">7.5</span>
                    <span className="text-sm text-gray-600">hrs</span>
                  </div>
                  <Progress value={94} className="h-2" />
                  <p className="text-xs text-gray-600">Goal: 8 hrs</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Medication Tab */}
        <TabsContent value="medication" className="space-y-6">
          <Card className="apple-card">
            <CardHeader>
              <CardTitle>Medication Adherence</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium">Overall Adherence</span>
                    <span className="text-2xl font-bold text-green-600">95%</span>
                  </div>
                  <Progress value={95} className="h-3" />
                </div>

                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">Antiretroviral Therapy</h4>
                        <p className="text-sm text-gray-600">Once daily</p>
                      </div>
                      <span className="text-sm font-medium text-green-600">100%</span>
                    </div>
                    <Progress value={100} className="h-2" />
                    <p className="text-xs text-gray-600 mt-2">Last taken: Today 8:00 AM</p>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">Vitamin D Supplement</h4>
                        <p className="text-sm text-gray-600">Once daily</p>
                      </div>
                      <span className="text-sm font-medium text-yellow-600">90%</span>
                    </div>
                    <Progress value={90} className="h-2" />
                    <p className="text-xs text-gray-600 mt-2">Last taken: Yesterday 9:00 AM</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Goals Tab */}
        <TabsContent value="goals" className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            <Card className="apple-card">
              <CardHeader>
                <CardTitle>Active Wellness Goals</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium">Reach Target Weight</h4>
                        <p className="text-sm text-gray-600">Current: 165 lbs → Target: 160 lbs</p>
                      </div>
                      <TrendingUp className="h-5 w-5 text-green-500" />
                    </div>
                    <Progress value={67} className="h-2 mb-2" />
                    <p className="text-xs text-gray-600">67% complete • Due: March 31</p>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium">Daily 10K Steps</h4>
                        <p className="text-sm text-gray-600">Maintain 10,000 steps daily</p>
                      </div>
                      <TrendingUp className="h-5 w-5 text-green-500" />
                    </div>
                    <Progress value={84} className="h-2 mb-2" />
                    <p className="text-xs text-gray-600">21/30 days this month</p>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium">Improve Sleep Quality</h4>
                        <p className="text-sm text-gray-600">Average 8 hours per night</p>
                      </div>
                      <TrendingUp className="h-5 w-5 text-yellow-500" />
                    </div>
                    <Progress value={50} className="h-2 mb-2" />
                    <p className="text-xs text-gray-600">50% complete • Due: April 15</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
