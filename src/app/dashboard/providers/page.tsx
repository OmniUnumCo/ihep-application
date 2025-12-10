'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Search, MapPin, Star, Calendar, Phone, Mail, CheckCircle2 } from 'lucide-react'

export default function ProvidersPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [specialty, setSpecialty] = useState('all')

  const providers = [
    {
      id: '1',
      name: 'Dr. Sarah Johnson',
      title: 'MD',
      specialty: 'Internal Medicine',
      rating: 4.9,
      reviewCount: 127,
      yearsExperience: 15,
      acceptingNewPatients: true,
      languages: ['English', 'Spanish'],
      location: 'Main Clinic, Downtown',
      distance: '2.3 miles',
      nextAvailable: 'Tomorrow 2:00 PM',
      bio: 'Specializing in HIV care and chronic disease management with a holistic approach.',
    },
    {
      id: '2',
      name: 'Dr. Michael Chen',
      title: 'MD, PhD',
      specialty: 'Infectious Disease',
      rating: 4.8,
      reviewCount: 98,
      yearsExperience: 12,
      acceptingNewPatients: true,
      languages: ['English', 'Mandarin'],
      location: 'University Medical Center',
      distance: '4.1 miles',
      nextAvailable: 'Next Week Mon 10:00 AM',
      bio: 'Expert in HIV treatment and research with focus on latest therapeutic approaches.',
    },
    {
      id: '3',
      name: 'Lisa Martinez',
      title: 'LCSW',
      specialty: 'Mental Health',
      rating: 5.0,
      reviewCount: 84,
      yearsExperience: 8,
      acceptingNewPatients: true,
      languages: ['English', 'Spanish'],
      location: 'Wellness Center',
      distance: '1.8 miles',
      nextAvailable: 'Wed 4:00 PM',
      bio: 'Specialized in therapy for chronic illness, trauma, and wellness support.',
    },
    {
      id: '4',
      name: 'Dr. Jennifer Williams',
      title: 'PharmD',
      specialty: 'Pharmacy',
      rating: 4.9,
      reviewCount: 156,
      yearsExperience: 10,
      acceptingNewPatients: true,
      languages: ['English'],
      location: 'Main Pharmacy',
      distance: '2.5 miles',
      nextAvailable: 'Today 3:00 PM',
      bio: 'Clinical pharmacist specializing in medication therapy management for complex conditions.',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Provider Directory</h1>
        <p className="text-gray-600 mt-2">Find and connect with healthcare professionals</p>
      </div>

      {/* Search and Filters */}
      <Card className="apple-card">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search by name, specialty, or condition..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={specialty} onValueChange={setSpecialty}>
              <SelectTrigger>
                <SelectValue placeholder="All Specialties" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Specialties</SelectItem>
                <SelectItem value="internal">Internal Medicine</SelectItem>
                <SelectItem value="infectious">Infectious Disease</SelectItem>
                <SelectItem value="mental">Mental Health</SelectItem>
                <SelectItem value="pharmacy">Pharmacy</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Provider List */}
      <div className="space-y-6">
        {providers.map((provider) => (
          <Card key={provider.id} className="apple-card hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex flex-col lg:flex-row gap-6">
                {/* Provider Image Placeholder */}
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex-shrink-0 flex items-center justify-center text-white text-2xl font-bold">
                  {provider.name.split(' ').map((n) => n[0]).join('')}
                </div>

                {/* Provider Info */}
                <div className="flex-1">
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-3">
                    <div>
                      <h3 className="text-xl font-bold">
                        {provider.name}, {provider.title}
                      </h3>
                      <p className="text-gray-600">{provider.specialty}</p>
                    </div>
                    <div className="flex items-center mt-2 lg:mt-0">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mr-1" />
                      <span className="font-medium">{provider.rating}</span>
                      <span className="text-sm text-gray-600 ml-1">({provider.reviewCount} reviews)</span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-4">{provider.bio}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm mb-4">
                    <div className="flex items-center text-gray-600">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>
                        {provider.location} ({provider.distance})
                      </span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Calendar className="h-4 w-4 mr-2" />
                      <span>Next available: {provider.nextAvailable}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {provider.acceptingNewPatients && (
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Accepting New Patients
                      </Badge>
                    )}
                    <Badge variant="outline">{provider.yearsExperience} years experience</Badge>
                    {provider.languages.map((lang) => (
                      <Badge key={lang} variant="outline">
                        {lang}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button className="gradient-primary">
                      <Calendar className="h-4 w-4 mr-2" />
                      Book Appointment
                    </Button>
                    <Button variant="outline">
                      <Phone className="h-4 w-4 mr-2" />
                      Call
                    </Button>
                    <Button variant="outline">
                      <Mail className="h-4 w-4 mr-2" />
                      Message
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Emergency Contact */}
      <Card className="apple-card border-2 border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="text-red-700">Emergency Resources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p className="font-medium">If you are experiencing a medical emergency, call 911 immediately.</p>
            <div className="flex items-center justify-between">
              <span>24/7 Crisis Hotline:</span>
              <Button variant="outline" size="sm">
                <Phone className="h-4 w-4 mr-2" />
                1-800-273-8255
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
