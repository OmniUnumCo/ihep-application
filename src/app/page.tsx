'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { Heart, ArrowRight, CheckCircle2, Users, Shield, Sparkles } from 'lucide-react'
import { healthConditions, supportNeeds } from '@/lib/constants/conditions'

export default function LandingPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [selectedConditions, setSelectedConditions] = useState<string[]>([])
  const [selectedSupport, setSelectedSupport] = useState<string[]>([])
  const [showSurvey, setShowSurvey] = useState(false)

  const handleConditionToggle = (conditionId: string) => {
    setSelectedConditions((prev) =>
      prev.includes(conditionId)
        ? prev.filter((id) => id !== conditionId)
        : [...prev, conditionId]
    )
  }

  const handleSupportToggle = (supportId: string) => {
    setSelectedSupport((prev) =>
      prev.includes(supportId) ? prev.filter((id) => id !== supportId) : [...prev, supportId]
    )
  }

  const handleSubmitSurvey = () => {
    // In production, save the survey results to the backend
    router.push('/dashboard')
  }

  if (session) {
    router.push('/dashboard')
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Heart className="h-8 w-8 text-red-500" />
              <span className="text-xl font-bold gradient-text">IHEP</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link href="/auth/signup">
                <Button className="gradient-primary">Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      {!showSurvey && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold gradient-text mb-6">
              Integrated Health
              <br />
              Empowerment Program
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              A comprehensive platform that combines cutting-edge healthcare technology with compassionate
              support to empower your wellness journey
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="gradient-primary" onClick={() => setShowSurvey(true)}>
                Take Our Health Assessment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Link href="/auth/signup">
                <Button size="lg" variant="outline">
                  Create Free Account
                </Button>
              </Link>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <Card className="apple-card text-center">
              <CardContent className="pt-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 flex items-center justify-center">
                  <Heart className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold mb-2">Personalized Care</h3>
                <p className="text-gray-600">
                  AI-powered digital twin technology creates a personalized health model just for you
                </p>
              </CardContent>
            </Card>

            <Card className="apple-card text-center">
              <CardContent className="pt-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-100 flex items-center justify-center">
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold mb-2">Community Support</h3>
                <p className="text-gray-600">
                  Connect with healthcare providers and support groups who understand your journey
                </p>
              </CardContent>
            </Card>

            <Card className="apple-card text-center">
              <CardContent className="pt-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                  <Shield className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-bold mb-2">Secure & Private</h3>
                <p className="text-gray-600">
                  Your health data is protected with enterprise-grade security and encryption
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Benefits */}
          <Card className="apple-card">
            <CardHeader>
              <CardTitle className="text-2xl text-center flex items-center justify-center">
                <Sparkles className="h-6 w-6 mr-2 text-yellow-500" />
                What You'll Get
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  'Digital twin health visualization',
                  'AI-powered wellness recommendations',
                  'Medication adherence tracking',
                  'Provider directory and appointments',
                  'Educational resources and curriculum',
                  'Mental health support',
                  'Community connection tools',
                  '24/7 health monitoring',
                ].map((benefit, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Health Assessment Survey */}
      {showSurvey && (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <Button
            variant="ghost"
            onClick={() => setShowSurvey(false)}
            className="mb-6"
          >
            ← Back
          </Button>

          <Card className="apple-card">
            <CardHeader>
              <CardTitle className="text-2xl">Health Assessment</CardTitle>
              <p className="text-gray-600 mt-2">
                Help us personalize your experience by sharing what matters most to you
              </p>
            </CardHeader>
            <CardContent className="space-y-8">
              {/* Health Conditions */}
              <div>
                <Label className="text-lg font-medium mb-4 block">
                  What health conditions are you managing? (Select all that apply)
                </Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {healthConditions.map((condition) => (
                    <div key={condition.id} className="flex items-center space-x-3">
                      <Checkbox
                        id={condition.id}
                        checked={selectedConditions.includes(condition.id)}
                        onCheckedChange={() => handleConditionToggle(condition.id)}
                      />
                      <Label
                        htmlFor={condition.id}
                        className="text-sm font-normal cursor-pointer flex-1"
                      >
                        {condition.name}
                        <Badge variant="outline" className="ml-2 text-xs">
                          {condition.category}
                        </Badge>
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Support Needs */}
              <div>
                <Label className="text-lg font-medium mb-4 block">
                  What type of support are you looking for? (Select all that apply)
                </Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {supportNeeds.map((support) => (
                    <div key={support.id} className="flex items-center space-x-3">
                      <Checkbox
                        id={support.id}
                        checked={selectedSupport.includes(support.id)}
                        onCheckedChange={() => handleSupportToggle(support.id)}
                      />
                      <Label
                        htmlFor={support.id}
                        className="text-sm font-normal cursor-pointer flex-1"
                      >
                        <span className="mr-2">{support.icon}</span>
                        {support.name}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-4 pt-6">
                <Button
                  onClick={handleSubmitSurvey}
                  className="flex-1 gradient-primary"
                  disabled={selectedConditions.length === 0 && selectedSupport.length === 0}
                >
                  Continue to Dashboard
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
                <Link href="/auth/signup" className="flex-1">
                  <Button variant="outline" className="w-full">
                    Sign Up First
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600 text-sm">
            <p>&copy; 2025 Integrated Health Empowerment Program. All rights reserved.</p>
            <p className="mt-2">Empowering wellness through technology and compassion.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
