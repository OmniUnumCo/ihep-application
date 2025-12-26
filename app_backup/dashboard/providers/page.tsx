'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Search,
  Phone,
  Mail,
  Calendar,
  Star,
  MapPin,
  Clock,
  MessageSquare,
  Video
} from 'lucide-react';

interface Provider {
  id: string;
  name: string;
  title: string;
  specialty: string;
  photo?: string;
  rating: number;
  reviewCount: number;
  location: string;
  availability: string;
  phone: string;
  email: string;
  isPrimary?: boolean;
}

const mockProviders: Provider[] = [
  {
    id: '1',
    name: 'Dr. Sarah Chen',
    title: 'MD, MPH',
    specialty: 'HIV/AIDS Specialist',
    rating: 4.9,
    reviewCount: 127,
    location: 'Main Clinic, 2nd Floor',
    availability: 'Next available: Jan 15',
    phone: '(555) 123-4567',
    email: 'dr.chen@clinic.org',
    isPrimary: true,
  },
  {
    id: '2',
    name: 'Dr. Michael Roberts',
    title: 'MD',
    specialty: 'Internal Medicine',
    rating: 4.8,
    reviewCount: 89,
    location: 'East Wing, Room 105',
    availability: 'Next available: Jan 18',
    phone: '(555) 123-4568',
    email: 'dr.roberts@clinic.org',
  },
  {
    id: '3',
    name: 'James Wilson',
    title: 'PharmD',
    specialty: 'Clinical Pharmacist',
    rating: 4.9,
    reviewCount: 156,
    location: 'Pharmacy Department',
    availability: 'Walk-ins welcome',
    phone: '(555) 123-4569',
    email: 'j.wilson@clinic.org',
  },
  {
    id: '4',
    name: 'Dr. Lisa Martinez',
    title: 'PsyD',
    specialty: 'Clinical Psychologist',
    rating: 4.7,
    reviewCount: 64,
    location: 'Behavioral Health Center',
    availability: 'Next available: Jan 20',
    phone: '(555) 123-4570',
    email: 'dr.martinez@clinic.org',
  },
  {
    id: '5',
    name: 'Amanda Thompson',
    title: 'RN, BSN',
    specialty: 'Care Coordinator',
    rating: 5.0,
    reviewCount: 98,
    location: 'Patient Services',
    availability: 'Available today',
    phone: '(555) 123-4571',
    email: 'a.thompson@clinic.org',
  },
];

export default function ProvidersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>('all');

  const specialties = ['all', ...new Set(mockProviders.map((p) => p.specialty))];

  const filteredProviders = mockProviders.filter((provider) => {
    const matchesSearch =
      provider.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      provider.specialty.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSpecialty =
      selectedSpecialty === 'all' || provider.specialty === selectedSpecialty;
    return matchesSearch && matchesSpecialty;
  });

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
              <h1 className="text-2xl font-bold text-white">Care Team</h1>
              <p className="text-purple-300 text-sm">Your healthcare providers</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-300" />
            <input
              type="text"
              placeholder="Search providers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-300 focus:outline-none focus:border-purple-500"
            />
          </div>
          <select
            value={selectedSpecialty}
            onChange={(e) => setSelectedSpecialty(e.target.value)}
            className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            {specialties.map((specialty) => (
              <option key={specialty} value={specialty} className="bg-slate-900">
                {specialty === 'all' ? 'All Specialties' : specialty}
              </option>
            ))}
          </select>
        </div>

        {/* Primary Provider */}
        {filteredProviders.some((p) => p.isPrimary) && (
          <section className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Primary Provider</h2>
            {filteredProviders
              .filter((p) => p.isPrimary)
              .map((provider) => (
                <div
                  key={provider.id}
                  className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-xl border border-purple-500/30 p-6"
                >
                  <div className="flex flex-col md:flex-row gap-6">
                    <div className="flex-shrink-0">
                      <div className="w-24 h-24 bg-purple-500/30 rounded-full flex items-center justify-center">
                        <span className="text-3xl font-bold text-white">
                          {provider.name.split(' ').map((n) => n[0]).join('')}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-xl font-semibold text-white">
                            {provider.name}, {provider.title}
                          </h3>
                          <p className="text-purple-300">{provider.specialty}</p>
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                          <span className="text-white font-medium">{provider.rating}</span>
                          <span className="text-purple-300">({provider.reviewCount})</span>
                        </div>
                      </div>

                      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="flex items-center gap-2 text-purple-300">
                          <MapPin className="w-4 h-4" />
                          <span>{provider.location}</span>
                        </div>
                        <div className="flex items-center gap-2 text-purple-300">
                          <Clock className="w-4 h-4" />
                          <span>{provider.availability}</span>
                        </div>
                        <div className="flex items-center gap-2 text-purple-300">
                          <Phone className="w-4 h-4" />
                          <span>{provider.phone}</span>
                        </div>
                        <div className="flex items-center gap-2 text-purple-300">
                          <Mail className="w-4 h-4" />
                          <span>{provider.email}</span>
                        </div>
                      </div>

                      <div className="mt-6 flex flex-wrap gap-3">
                        <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
                          <Calendar className="w-4 h-4" />
                          Schedule Appointment
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">
                          <MessageSquare className="w-4 h-4" />
                          Send Message
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">
                          <Video className="w-4 h-4" />
                          Video Call
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </section>
        )}

        {/* All Providers */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">All Providers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredProviders
              .filter((p) => !p.isPrimary)
              .map((provider) => (
                <div
                  key={provider.id}
                  className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 p-6 hover:border-purple-500/50 transition-colors"
                >
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center">
                        <span className="text-xl font-bold text-purple-400">
                          {provider.name.split(' ').map((n) => n[0]).join('')}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-white">
                            {provider.name}, {provider.title}
                          </h3>
                          <p className="text-purple-300 text-sm">{provider.specialty}</p>
                        </div>
                        <div className="flex items-center gap-1 text-sm">
                          <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                          <span className="text-white">{provider.rating}</span>
                        </div>
                      </div>

                      <div className="mt-3 space-y-1 text-sm">
                        <div className="flex items-center gap-2 text-purple-300">
                          <MapPin className="w-3 h-3" />
                          <span className="truncate">{provider.location}</span>
                        </div>
                        <div className="flex items-center gap-2 text-green-400">
                          <Clock className="w-3 h-3" />
                          <span>{provider.availability}</span>
                        </div>
                      </div>

                      <div className="mt-4 flex gap-2">
                        <button className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors">
                          Schedule
                        </button>
                        <button className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors">
                          <Phone className="w-4 h-4" />
                        </button>
                        <button className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors">
                          <Mail className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </section>
      </main>
    </div>
  );
}
