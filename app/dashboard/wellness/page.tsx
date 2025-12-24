// app/dashboard/wellness/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { Card } from '@/components/ui/Card';
import { HealthChart } from '@/components/dashboard/HealthChart';
import { useHealthData } from '@/lib/hooks/useHealthData';

interface WellnessMetrics {
  heartRate: number;
  bloodPressureSystolic: number;
  bloodPressureDiastolic: number;
  oxygenSaturation: number;
  temperature: number;
  lastUpdated: string;
}

export default function WellnessPage() {
  const { user } = useAuth();
  const { metrics, loading, error, refreshMetrics } = useHealthData();
  const [filteredMetrics, setFilteredMetrics] = useState<WellnessMetrics | null>(null);

  // Simple Kalman filter implementation for smoothing sensor data
  useEffect(() => {
    if (!metrics) return;

    // Initialize filter state if not already done
    if (!filteredMetrics) {
      setFilteredMetrics(metrics);
      return;
    }

    // Simplified Kalman filter: blend previous estimate with new measurement
    // Process noise Q = 0.01, measurement noise R = 0.1
    const alpha = 0.3; // Kalman gain approximation for this noise ratio
    
    const smoothed: WellnessMetrics = {
      heartRate: alpha * metrics.heartRate + (1 - alpha) * filteredMetrics.heartRate,
      bloodPressureSystolic: alpha * metrics.bloodPressureSystolic + (1 - alpha) * filteredMetrics.bloodPressureSystolic,
      bloodPressureDiastolic: alpha * metrics.bloodPressureDiastolic + (1 - alpha) * filteredMetrics.bloodPressureDiastolic,
      oxygenSaturation: alpha * metrics.oxygenSaturation + (1 - alpha) * filteredMetrics.oxygenSaturation,
      temperature: alpha * metrics.temperature + (1 - alpha) * filteredMetrics.temperature,
      lastUpdated: metrics.lastUpdated,
    };

    setFilteredMetrics(smoothed);
  }, [metrics]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(refreshMetrics, 30000);
    return () => clearInterval(interval);
  }, [refreshMetrics]);

  if (loading) return <div className="flex justify-center items-center h-screen">Loading wellness data...</div>;
  if (error) return <div className="text-red-500">Error loading wellness data: {error}</div>;
  if (!filteredMetrics) return null;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Wellness Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card title="Heart Rate">
          <div className="text-4xl font-bold">{Math.round(filteredMetrics.heartRate)} <span className="text-lg">bpm</span></div>
          <HealthChart 
            dataType="heartRate" 
            currentValue={filteredMetrics.heartRate}
            normalRange={[60, 100]}
          />
        </Card>

        <Card title="Blood Pressure">
          <div className="text-4xl font-bold">
            {Math.round(filteredMetrics.bloodPressureSystolic)}/
            {Math.round(filteredMetrics.bloodPressureDiastolic)}
            <span className="text-lg ml-2">mmHg</span>
          </div>
          <HealthChart 
            dataType="bloodPressure" 
            currentValue={filteredMetrics.bloodPressureSystolic}
            normalRange={[90, 120]}
          />
        </Card>

        <Card title="Oxygen Saturation">
          <div className="text-4xl font-bold">{Math.round(filteredMetrics.oxygenSaturation)}<span className="text-lg">%</span></div>
          <HealthChart 
            dataType="oxygenSaturation" 
            currentValue={filteredMetrics.oxygenSaturation}
            normalRange={[95, 100]}
          />
        </Card>

        <Card title="Body Temperature">
          <div className="text-4xl font-bold">{filteredMetrics.temperature.toFixed(1)}<span className="text-lg">°F</span></div>
          <HealthChart 
            dataType="temperature" 
            currentValue={filteredMetrics.temperature}
            normalRange={[97.0, 99.0]}
          />
        </Card>
      </div>

      <div className="text-sm text-gray-500">
        Last updated: {new Date(filteredMetrics.lastUpdated).toLocaleString()}
      </div>
    </div>
  );
}