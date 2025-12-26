'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Search,
  BookOpen,
  FileText,
  Video,
  Users,
  ExternalLink,
  Heart,
  Pill,
  Brain,
  DollarSign,
  Filter
} from 'lucide-react';

type ResourceCategory = 'all' | 'education' | 'support' | 'financial' | 'mental-health';

interface Resource {
  id: string;
  title: string;
  description: string;
  category: ResourceCategory;
  type: 'article' | 'video' | 'guide' | 'program' | 'group';
  url?: string;
  readTime?: string;
  tags: string[];
  featured?: boolean;
}

const mockResources: Resource[] = [
  {
    id: '1',
    title: 'Understanding Your Viral Load Results',
    description: 'A comprehensive guide to interpreting your lab results and what they mean for your health.',
    category: 'education',
    type: 'article',
    readTime: '5 min read',
    tags: ['Lab Results', 'Viral Load', 'CD4'],
    featured: true,
  },
  {
    id: '2',
    title: 'U=U: The Science of Undetectable',
    description: 'Learn about the scientific evidence behind Undetectable = Untransmittable and what it means for you.',
    category: 'education',
    type: 'video',
    readTime: '12 min watch',
    tags: ['U=U', 'Treatment', 'Prevention'],
    featured: true,
  },
  {
    id: '3',
    title: 'Medication Adherence Tips',
    description: 'Practical strategies to help you stay on track with your antiretroviral therapy.',
    category: 'education',
    type: 'guide',
    readTime: '8 min read',
    tags: ['Medication', 'Adherence', 'ART'],
  },
  {
    id: '4',
    title: 'HIV+ Support Group',
    description: 'Connect with others living with HIV in a supportive, confidential environment.',
    category: 'support',
    type: 'group',
    tags: ['Support', 'Community', 'Peer'],
  },
  {
    id: '5',
    title: 'Ryan White HIV/AIDS Program',
    description: 'Federal program providing HIV-related services to low-income individuals.',
    category: 'financial',
    type: 'program',
    url: 'https://ryanwhite.hrsa.gov',
    tags: ['Financial Aid', 'Insurance', 'Services'],
  },
  {
    id: '6',
    title: 'AIDS Drug Assistance Program (ADAP)',
    description: 'State program providing HIV medications to eligible individuals without insurance.',
    category: 'financial',
    type: 'program',
    tags: ['Medication Assistance', 'ADAP', 'Financial'],
  },
  {
    id: '7',
    title: 'Mental Health and HIV',
    description: 'Understanding the connection between HIV and mental health, and resources available.',
    category: 'mental-health',
    type: 'article',
    readTime: '7 min read',
    tags: ['Mental Health', 'Depression', 'Anxiety'],
  },
  {
    id: '8',
    title: 'Counseling Services',
    description: 'Free confidential counseling for individuals living with HIV.',
    category: 'mental-health',
    type: 'program',
    tags: ['Counseling', 'Therapy', 'Support'],
  },
];

const categories: { value: ResourceCategory; label: string; icon: typeof BookOpen }[] = [
  { value: 'all', label: 'All Resources', icon: BookOpen },
  { value: 'education', label: 'Education', icon: FileText },
  { value: 'support', label: 'Support Groups', icon: Users },
  { value: 'financial', label: 'Financial Aid', icon: DollarSign },
  { value: 'mental-health', label: 'Mental Health', icon: Brain },
];

const getTypeIcon = (type: Resource['type']) => {
  switch (type) {
    case 'video':
      return Video;
    case 'guide':
      return BookOpen;
    case 'group':
      return Users;
    case 'program':
      return Heart;
    default:
      return FileText;
  }
};

export default function ResourcesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<ResourceCategory>('all');

  const filteredResources = mockResources.filter((resource) => {
    const matchesSearch =
      resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      resource.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      resource.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory =
      selectedCategory === 'all' || resource.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const featuredResources = filteredResources.filter((r) => r.featured);
  const regularResources = filteredResources.filter((r) => !r.featured);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="p-2 text-white/70 hover:text-white transition-colors rounded-lg hover:bg-white/10"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white">Resources</h1>
              <p className="text-purple-300 text-sm">Educational content and support</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-300" />
          <input
            type="text"
            placeholder="Search resources, topics, or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-300 focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => setSelectedCategory(value)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                selectedCategory === value
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/5 text-purple-300 hover:bg-white/10'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Featured Resources */}
        {featuredResources.length > 0 && (
          <section className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Featured</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {featuredResources.map((resource) => {
                const TypeIcon = getTypeIcon(resource.type);
                return (
                  <div
                    key={resource.id}
                    className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-xl border border-purple-500/30 p-6 hover:border-purple-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2 bg-purple-500/30 rounded-lg">
                        <TypeIcon className="w-5 h-5 text-purple-400" />
                      </div>
                      {resource.readTime && (
                        <span className="text-purple-300 text-sm">{resource.readTime}</span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{resource.title}</h3>
                    <p className="text-purple-300 text-sm mb-4">{resource.description}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {resource.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-white/10 rounded-full text-xs text-purple-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <button className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors">
                      {resource.type === 'video' ? 'Watch Now' : 'Read More'}
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* All Resources */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">
            {selectedCategory === 'all' ? 'All Resources' : categories.find((c) => c.value === selectedCategory)?.label}
          </h2>

          {regularResources.length === 0 && featuredResources.length === 0 ? (
            <div className="text-center py-12">
              <Filter className="w-12 h-12 text-purple-300 mx-auto mb-4" />
              <p className="text-purple-300">No resources found matching your search.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {regularResources.map((resource) => {
                const TypeIcon = getTypeIcon(resource.type);
                return (
                  <div
                    key={resource.id}
                    className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 p-5 hover:border-purple-500/50 transition-colors group"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2 bg-purple-500/20 rounded-lg group-hover:bg-purple-500/30 transition-colors">
                        <TypeIcon className="w-4 h-4 text-purple-400" />
                      </div>
                      <span className="text-xs text-purple-300 capitalize">{resource.type}</span>
                    </div>
                    <h3 className="font-semibold text-white mb-2">{resource.title}</h3>
                    <p className="text-purple-300 text-sm mb-3 line-clamp-2">
                      {resource.description}
                    </p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {resource.tags.slice(0, 2).map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-white/10 rounded text-xs text-purple-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="flex items-center justify-between">
                      {resource.readTime && (
                        <span className="text-xs text-purple-400">{resource.readTime}</span>
                      )}
                      {resource.url ? (
                        <a
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1"
                        >
                          Visit <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <button className="text-sm text-purple-400 hover:text-purple-300">
                          Learn More
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Help Section */}
        <section className="mt-8 bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <Pill className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">Need Immediate Assistance?</h3>
              <p className="text-purple-300 text-sm mb-4">
                If you need help with medication, financial assistance, or have questions about your care,
                our team is here to help.
              </p>
              <div className="flex flex-wrap gap-3">
                <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors">
                  Contact Care Coordinator
                </button>
                <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors">
                  24/7 Helpline: 1-800-XXX-XXXX
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
