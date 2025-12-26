// app/page.tsx - Main Landing Page Component
'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { Users, BookOpen, Activity, Shield, Brain, Menu, X, ChevronRight, Phone, Mail, MapPin, Clock, Heart, Sparkles, Calendar } from 'lucide-react';

// Main App Component
export default function HomePage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeModal, setActiveModal] = useState<'login' | 'signup' | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-lime-50">
      {/* Navigation Header */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-lg shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <Image
                src="/assets/logo.png"
                alt="IHEP Logo"
                width={40}
                height={40}
                className="h-10 w-10"
              />
              <span className="text-xl font-bold bg-gradient-to-r from-green-700 to-emerald-600 bg-clip-text text-transparent">
                IHEP
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#home" className="text-gray-700 hover:text-green-700 transition">Home</a>
              <a href="#features" className="text-gray-700 hover:text-green-700 transition">Features</a>
              <a href="#digital-twin" className="text-gray-700 hover:text-green-700 transition">Digital Twin</a>
              <a href="#about" className="text-gray-700 hover:text-green-700 transition">About</a>
              <a href="#contact" className="text-gray-700 hover:text-green-700 transition">Contact</a>
              <button
                onClick={() => setActiveModal('login')}
                className="px-4 py-2 text-green-700 hover:text-green-800 font-medium transition"
              >
                Sign In
              </button>
              <button
                onClick={() => setActiveModal('signup')}
                className="px-6 py-2 bg-gradient-to-r from-green-700 to-emerald-600 text-white rounded-full hover:shadow-lg transition"
              >
                Register
              </button>
            </div>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-2 space-y-2">
              <a href="#home" className="block py-2 text-gray-700">Home</a>
              <a href="#features" className="block py-2 text-gray-700">Features</a>
              <a href="#digital-twin" className="block py-2 text-gray-700">Digital Twin</a>
              <a href="#about" className="block py-2 text-gray-700">About</a>
              <a href="#contact" className="block py-2 text-gray-700">Contact</a>
              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => {
                    setActiveModal('login');
                    setIsMobileMenuOpen(false);
                  }}
                  className="flex-1 py-2 border border-green-700 text-green-700 rounded-lg font-medium"
                >
                  Sign In
                </button>
                <button
                  onClick={() => {
                    setActiveModal('signup');
                    setIsMobileMenuOpen(false);
                  }}
                  className="flex-1 py-2 bg-gradient-to-r from-green-700 to-emerald-600 text-white rounded-lg"
                >
                  Register
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section id="home" className="py-20 px-4">
        <div className="container mx-auto max-w-7xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-green-800 to-emerald-600 bg-clip-text text-transparent">
                Comprehensive Aftercare Through Digital Innovation
              </h1>
              <p className="text-lg text-gray-600">
                Empowering your recovery journey with cutting-edge digital twin technology,
                personalized care management, and integrated support systems for lasting wellness.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => setActiveModal('signup')}
                  className="px-8 py-3 bg-gradient-to-r from-green-700 to-emerald-600 text-white rounded-full hover:shadow-xl transition"
                >
                  Get Started
                </button>
                <button className="px-8 py-3 border-2 border-green-700 text-green-700 rounded-full hover:bg-green-50 transition">
                  Learn About Digital Twins
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white/90 backdrop-blur-lg rounded-3xl shadow-2xl p-8">
                <div className="space-y-4">
                  <div className="h-40 bg-gradient-to-r from-green-400 to-emerald-400 rounded-2xl opacity-30 animate-pulse"></div>
                  <h3 className="text-xl font-bold text-center text-green-800">4-Twin Digital Ecosystem</h3>
                  <p className="text-center text-gray-600">Personalized health modeling for your unique care journey</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-16 px-4 bg-white/70 backdrop-blur-lg">
        <div className="container mx-auto max-w-7xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-green-800">Comprehensive Care Platform</h2>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            Your complete solution for aftercare management and personalized wellness support
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Calendar, title: 'Dynamic Calendar', desc: 'Manage telehealth appointments, group meetings, and medication schedules all in one place.' },
              { icon: Activity, title: 'Wellness Monitoring', desc: 'Track your health metrics, medication adherence, and care plan progress in real-time.' },
              { icon: BookOpen, title: 'Resource Hub', desc: 'Access educational materials, support groups, community programs, and latest research.' },
              { icon: Brain, title: 'Digital Twin Tech', desc: 'Revolutionary personalized care modeling using AI-powered health simulations.' },
              { icon: Users, title: 'Financial Empowerment', desc: 'Tools and resources to help you achieve financial stability during your care journey.' },
              { icon: Shield, title: 'HIPAA Compliant', desc: 'Full PHI/PPI protection with end-to-end encryption and enterprise security.' }
            ].map((feature, idx) => (
              <div key={idx} className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition cursor-pointer border border-green-100">
                <feature.icon className="h-12 w-12 text-green-700 mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-green-800">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Digital Twin Section */}
      <section id="digital-twin" className="py-16 px-4 bg-gradient-to-r from-green-100 to-emerald-100">
        <div className="container mx-auto max-w-7xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl md:text-4xl font-bold text-green-800">4-Twin Digital Ecosystem</h2>
              <h3 className="text-xl text-amber-600 font-semibold">Personalized Care Through AI Simulation</h3>
              <p className="text-gray-600">
                Our revolutionary digital twin platform creates virtual models across four key dimensions
                of your wellbeing, allowing us to optimize your care journey with precision and insight.
              </p>
              <div className="space-y-3">
                <h4 className="font-semibold text-green-700">Integrated Care Features</h4>
                {[
                  'Health Twin: Real-time wellness monitoring and predictions',
                  'Financial Twin: Resource optimization and empowerment tools',
                  'Social Twin: Community connections and support networks',
                  'Care Twin: Treatment tracking and provider coordination'
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <ChevronRight className="h-5 w-5 text-green-600" />
                    <span className="text-gray-700">{item}</span>
                  </div>
                ))}
              </div>
              <button className="px-8 py-3 bg-gradient-to-r from-green-700 to-emerald-600 text-white rounded-full hover:shadow-xl transition">
                Explore Digital Twin Program
              </button>
            </div>
            <div className="flex justify-center">
              <div className="relative w-64 h-64 md:w-80 md:h-80">
                <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-pulse opacity-30"></div>
                <div className="absolute inset-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full animate-pulse opacity-40"></div>
                <div className="absolute inset-8 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full animate-pulse opacity-50"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-16 px-4 bg-white/70 backdrop-blur-lg">
        <div className="container mx-auto max-w-7xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-green-800">About IHEP</h2>
          <p className="text-center text-gray-600 mb-12 max-w-3xl mx-auto">
            The Integrated Health Empowerment Program is a comprehensive aftercare management platform
            designed to support individuals managing chronic conditions on their path to wellness.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                <Heart className="h-8 w-8 text-green-700" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-green-800">Patient-Centered</h3>
              <p className="text-gray-600">Built around your unique health journey with personalized care pathways.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 flex items-center justify-center">
                <Sparkles className="h-8 w-8 text-amber-600" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-green-800">Innovation-Driven</h3>
              <p className="text-gray-600">Leveraging AI and digital twin technology for better outcomes.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                <Users className="h-8 w-8 text-green-700" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-green-800">Community-Focused</h3>
              <p className="text-gray-600">Connecting you with support networks and resources for holistic care.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="bg-green-900 text-white py-12 px-4">
        <div className="container mx-auto max-w-7xl">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">IHEP</h3>
              <p className="text-green-200">Pioneering the future of aftercare through digital innovation and integrated support.</p>
              <div className="flex space-x-2 mt-4">
                <span className="px-3 py-1 bg-green-800 rounded text-sm">HIPAA</span>
                <span className="px-3 py-1 bg-green-800 rounded text-sm">PHI</span>
                <span className="px-3 py-1 bg-green-800 rounded text-sm">PPI</span>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-green-200">
                <li><a href="#about" className="hover:text-white transition">About Us</a></li>
                <li><a href="#contact" className="hover:text-white transition">Contact</a></li>
                <li><a href="#privacy" className="hover:text-white transition">Privacy Policy</a></li>
                <li><a href="#terms" className="hover:text-white transition">Terms & Conditions</a></li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-green-200">
                <li><a href="#education" className="hover:text-white transition">Patient Education</a></li>
                <li><a href="#support" className="hover:text-white transition">Support Groups</a></li>
                <li><a href="#programs" className="hover:text-white transition">Community Programs</a></li>
                <li><a href="#faq" className="hover:text-white transition">FAQ</a></li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-green-200">
                <li className="flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>support@ihep.care</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Phone className="h-4 w-4" />
                  <span>1-800-IHEP-CARE</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>24/7 Telehealth</span>
                </li>
                <li className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>Multiple Locations</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-green-800 mt-8 pt-8 text-center text-green-200">
            <p>© 2024 IHEP - Integrated Health Empowerment Program. All rights reserved. Protected Health Information secured under HIPAA compliance.</p>
          </div>
        </div>
      </footer>

      {/* Login Modal */}
      {activeModal === 'login' && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 md:p-8 w-full max-w-md relative">
            <h2 className="text-2xl font-bold mb-6 text-green-800">Sign In</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Email</label>
                <input type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Password</label>
                <input type="password" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent" />
              </div>
              <button type="submit" className="w-full py-3 bg-gradient-to-r from-green-700 to-emerald-600 text-white rounded-lg hover:shadow-lg transition">
                Sign In
              </button>
            </form>
            <p className="text-center mt-4 text-gray-600">
              Do not have an account?{' '}
              <button onClick={() => setActiveModal('signup')} className="text-green-700 font-medium hover:underline">
                Register
              </button>
            </p>
            <button
              onClick={() => setActiveModal(null)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>
      )}

      {/* Signup Modal */}
      {activeModal === 'signup' && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 md:p-8 w-full max-w-md max-h-[90vh] overflow-y-auto relative">
            <h2 className="text-2xl font-bold mb-6 text-green-800">Create Account</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Full Name</label>
                <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Email</label>
                <input type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Password</label>
                <input type="password" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Phone</label>
                <input type="tel" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600 focus:border-transparent" />
              </div>
              <div className="flex items-start space-x-2">
                <input type="checkbox" className="mt-1 accent-green-600" />
                <span className="text-sm text-gray-600">I agree to Terms of Service, Privacy Policy, and HIPAA Authorization</span>
              </div>
              <button type="submit" className="w-full py-3 bg-gradient-to-r from-green-700 to-emerald-600 text-white rounded-lg hover:shadow-lg transition">
                Create Account
              </button>
            </form>
            <p className="text-center mt-4 text-gray-600">
              Already have an account?{' '}
              <button onClick={() => setActiveModal('login')} className="text-green-700 font-medium hover:underline">
                Sign In
              </button>
            </p>
            <button
              onClick={() => setActiveModal(null)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
