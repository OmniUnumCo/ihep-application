// components/dashboard/HealthChart.tsx
'use client';

import { useEffect, useRef } from 'react';

interface HealthChartProps {
  dataType: string;
  currentValue: number;
  normalRange: [number, number];
  historicalData?: number[];
}

export function HealthChart({ dataType, currentValue, normalRange, historicalData = [] }: HealthChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, width, height);
    
    // Draw normal range
    const [min, max] = normalRange;
    const range = max - min;
    const yMin = height * 0.8;
    const yMax = height * 0.2;
    
    ctx.fillStyle = 'rgba(0, 255, 136, 0.2)';
    const normalTop = yMax + (max - min) * (yMax - yMin) / range;
    const normalBottom = yMax + (max - max) * (yMax - yMin) / range;
    ctx.fillRect(0, normalTop, width, normalBottom - normalTop);
    
    // Draw value indicator
    const valueY = yMax + (max - currentValue) * (yMax - yMin) / range;
    
    // Draw historical data if available
    if (historicalData.length > 1) {
      ctx.strokeStyle = 'rgba(100, 100, 255, 0.6)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      const pointSpacing = width / (historicalData.length - 1);
      historicalData.forEach((value, index) => {
        const x = index * pointSpacing;
        const y = yMax + (max - value) * (yMax - yMin) / range;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
    }
    
    // Draw current value
    ctx.fillStyle = currentValue >= min && currentValue <= max ? '#00ff88' : '#ff3300';
    ctx.beginPath();
    ctx.arc(width - 20, valueY, 6, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw value label
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(currentValue.toFixed(1), width - 30, valueY - 10);

  }, [currentValue, normalRange, historicalData]);

  return (
    <div className="mt-4">
      <canvas 
        ref={canvasRef} 
        width={300} 
        height={100}
        className="w-full"
      />
      <div className="text-xs text-gray-400 mt-1">
        Normal range: {normalRange[0]} - {normalRange[1]}
      </div>
    </div>
  );
}
