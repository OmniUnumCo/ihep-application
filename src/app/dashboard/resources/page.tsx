'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BookOpen, Video, FileText, Download, Search, Heart, Brain, Users } from 'lucide-react'

export default function ResourcesPage() {
  const [searchQuery, setSearchQuery] = useState('')

  const educationalResources = [
    {
      id: '1',
      title: 'Why Belief is Medicine—What the Science Shows',
      type: 'Article',
      category: 'Mind-Body Connection',
      duration: '10 min read',
      icon: Brain,
    },
    {
      id: '2',
      title: 'Mindfulness, Optimism, and the Immune System',
      type: 'Video',
      category: 'Wellness',
      duration: '15 min',
      icon: Heart,
    },
    {
      id: '3',
      title: 'How to Build Your Support Network',
      type: 'Guide',
      category: 'Community',
      duration: '8 min read',
      icon: Users,
    },
    {
      id: '4',
      title: 'Simple Rituals for Hope and Gratitude',
      type: 'Workbook',
      category: 'Mind-Body Connection',
      duration: 'Interactive',
      icon: Heart,
    },
    {
      id: '5',
      title: 'Success Stories—When Medicine and Mindset Combine',
      type: 'Article',
      category: 'Inspiration',
      duration: '12 min read',
      icon: Brain,
    },
    {
      id: '6',
      title: 'Daily Toolkit: Journaling, Meditation, Sharing',
      type: 'Workbook',
      category: 'Wellness',
      duration: 'Interactive',
      icon: BookOpen,
    },
  ]

  const toolsAndActivities = [
    {
      id: '1',
      title: 'Hope Journal Template',
      description: 'A structured journaling template to track your journey',
      type: 'PDF',
    },
    {
      id: '2',
      title: 'Mindfulness Practice Audio Script',
      description: 'Guided meditation and mindfulness exercises',
      type: 'Audio',
    },
    {
      id: '3',
      title: 'Group Gratitude Exercise',
      description: 'Activities for support groups and families',
      type: 'PDF',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Educational Resources</h1>
        <p className="text-gray-600 mt-2">
          Empower yourself with knowledge about health, wellness, and healing
        </p>
      </div>

      {/* Search */}
      <Card className="apple-card">
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Resource Categories */}
      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="articles">Articles</TabsTrigger>
          <TabsTrigger value="videos">Videos</TabsTrigger>
          <TabsTrigger value="workbooks">Workbooks</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
        </TabsList>

        {/* All Resources */}
        <TabsContent value="all" className="space-y-6">
          <Card className="apple-card">
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 mr-2" />
                Featured Curriculum
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Healing Mind and Body—The Power of Belief Alongside Medicine
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {educationalResources.map((resource) => (
                  <div key={resource.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center">
                        <resource.icon className="h-5 w-5 mr-2 text-blue-500" />
                        <div>
                          <h4 className="font-medium">{resource.title}</h4>
                          <p className="text-xs text-gray-600 mt-1">
                            {resource.type} • {resource.category}
                          </p>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{resource.duration}</p>
                    <Button variant="outline" size="sm" className="w-full">
                      {resource.type === 'Video' ? 'Watch' : 'Read'}
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Articles */}
        <TabsContent value="articles" className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {educationalResources
              .filter((r) => r.type === 'Article')
              .map((resource) => (
                <Card key={resource.id} className="apple-card">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-lg mb-2">{resource.title}</h4>
                        <p className="text-sm text-gray-600 mb-4">
                          {resource.category} • {resource.duration}
                        </p>
                        <Button variant="outline">Read Article</Button>
                      </div>
                      <FileText className="h-8 w-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        {/* Videos */}
        <TabsContent value="videos" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {educationalResources
              .filter((r) => r.type === 'Video')
              .map((resource) => (
                <Card key={resource.id} className="apple-card">
                  <CardContent className="pt-6">
                    <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg mb-4 flex items-center justify-center">
                      <Video className="h-12 w-12 text-white" />
                    </div>
                    <h4 className="font-medium mb-2">{resource.title}</h4>
                    <p className="text-sm text-gray-600 mb-4">{resource.duration}</p>
                    <Button className="w-full gradient-primary">Watch Video</Button>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        {/* Workbooks */}
        <TabsContent value="workbooks" className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {educationalResources
              .filter((r) => r.type === 'Workbook')
              .map((resource) => (
                <Card key={resource.id} className="apple-card">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-lg mb-2">{resource.title}</h4>
                        <p className="text-sm text-gray-600 mb-4">
                          {resource.category} • {resource.duration}
                        </p>
                        <div className="flex gap-2">
                          <Button variant="outline">Start Workbook</Button>
                          <Button variant="ghost" size="icon">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <BookOpen className="h-8 w-8 text-purple-500" />
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        {/* Tools & Activities */}
        <TabsContent value="tools" className="space-y-6">
          <Card className="apple-card">
            <CardHeader>
              <CardTitle>Tools & Activities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {toolsAndActivities.map((tool) => (
                  <div key={tool.id} className="border rounded-lg p-4 flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{tool.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{tool.description}</p>
                      <span className="inline-block mt-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                        {tool.type}
                      </span>
                    </div>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Additional Resources */}
      <Card className="apple-card">
        <CardHeader>
          <CardTitle>External Resources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <div>
                <p className="font-medium">CDC HIV/AIDS Information</p>
                <p className="text-sm text-gray-600">Official health guidelines and resources</p>
              </div>
              <Button variant="link" size="sm">
                Visit →
              </Button>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <div>
                <p className="font-medium">Mental Health Support</p>
                <p className="text-sm text-gray-600">24/7 crisis support and counseling</p>
              </div>
              <Button variant="link" size="sm">
                Visit →
              </Button>
            </div>
            <div className="flex justify-between items-center py-2">
              <div>
                <p className="font-medium">Community Support Groups</p>
                <p className="text-sm text-gray-600">Connect with others on similar journeys</p>
              </div>
              <Button variant="link" size="sm">
                Visit →
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
