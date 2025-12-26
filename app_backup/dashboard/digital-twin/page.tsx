'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Activity, Heart, Pill, TrendingUp, RefreshCw } from 'lucide-react';
import { DigitalTwinCanvas } from '@/components/digital-twin/DigitalTwinCanvas';

interface HealthData {
  cd4Count: number;
  viralLoad: number;
  heartRate: number;
  healthScore: number;
  adherence: number;
  lastUpdate: string;
}

const mockHealthData: HealthData = {
  cd4Count: 650,
  viralLoad: 20, // < 50 = undetectable
  heartRate: 72,
  healthScore: 85,
  adherence: 98,
  lastUpdate: new Date().toISOString(),
};

export default function DigitalTwinPage() {
  const [healthData] = useState<HealthData>(mockHealthData);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsRefreshing(false);
  };

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
              <h1 className="text-2xl font-bold text-white">Digital Twin</h1>
              <p className="text-purple-300 text-sm">Your personalized health visualization</p>
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Sync Data
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Digital Twin Visualization */}
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <h2 className="text-lg font-semibold text-white">3D Health Visualization</h2>
                <p className="text-sm text-purple-300">
                  Real-time representation of your health state
                </p>
              </div>
              <div className="p-4">
                <DigitalTwinCanvas
                  healthScore={healthData.healthScore}
                  heartRate={healthData.heartRate}
                  viralLoad={healthData.viralLoad}
                  cd4Count={healthData.cd4Count}
                />
              </div>
              <div className="p-4 border-t border-white/10 flex items-center justify-between text-sm">
                <span className="text-purple-300">
                  Last updated: {new Date(healthData.lastUpdate).toLocaleString()}
                </span>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-green-400">Live</span>
                </div>
              </div>
            </div>
          </div>

          {/* Health Metrics Panel */}
          <div className="space-y-4">
            {/* CD4 Count */}
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Activity className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">CD4 Count</h3>
                  <p className="text-purple-300 text-sm">Immune function</p>
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-white">{healthData.cd4Count}</span>
                <span className="text-purple-300">cells/uL</span>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <span className="text-green-400 text-sm">+50 from last month</span>
              </div>
            </div>

            {/* Viral Load */}
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Heart className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">Viral Load</h3>
                  <p className="text-purple-300 text-sm">Viral control</p>
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-white">
                  {healthData.viralLoad < 50 ? 'Undetectable' : healthData.viralLoad}
                </span>
              </div>
              <div className="mt-3">
                <span className="inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                  U=U Protected
                </span>
              </div>
            </div>

            {/* Medication Adherence */}
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-500/20 rounded-lg">
                  <Pill className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">Adherence</h3>
                  <p className="text-purple-300 text-sm">Medication compliance</p>
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-white">{healthData.adherence}%</span>
              </div>
              <div className="mt-3 w-full bg-white/10 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                  style={{ width: `${healthData.adherence}%` }}
                />
              </div>
            </div>

            {/* Health Score */}
            <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
              <h3 className="text-white font-medium mb-2">Overall Health Score</h3>
              <div className="flex items-center justify-between">
                <span className="text-5xl font-bold text-white">{healthData.healthScore}</span>
                <div className="text-right">
                  <span className="text-green-400 text-lg font-medium">Excellent</span>
                  <p className="text-purple-300 text-sm">Top 15% of users</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Research Participation */}
        <div className="mt-8 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl p-6 border border-purple-500/20">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-white mb-2">Research Participation</h3>
              <p className="text-purple-300 text-sm mb-4 max-w-2xl">
                Your digital twin contributes to medical research while maintaining complete privacy.
                Federated learning ensures your data never leaves your device.
              </p>
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                Learn About Research Impact
              </button>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-purple-400">98.7%</div>
              <div className="text-xs text-purple-300">Model Accuracy</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
