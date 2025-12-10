'use client'

import { useEffect, useRef } from 'react'
import { Bot } from 'lucide-react'

interface DigitalTwinCanvasProps {
  className?: string
}

export function DigitalTwinCanvas({ className = '' }: DigitalTwinCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Placeholder for 3D visualization initialization
    // In production, this would use Three.js or similar for 3D rendering
  }, [])

  return (
    <div
      ref={canvasRef}
      className={`aspect-video bg-gradient-to-br from-slate-900 to-blue-900 rounded-lg relative overflow-hidden ${className}`}
    >
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center text-white">
          <Bot className="h-16 w-16 mx-auto mb-4 animate-pulse" />
          <p className="text-lg font-medium">3D Health Model</p>
          <p className="text-sm text-gray-300 mt-2">
            Interactive visualization will render here
          </p>
        </div>
      </div>
      {/* Animated particles effect */}
      <div className="absolute inset-0 opacity-30">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          ></div>
        ))}
      </div>
    </div>
  )
}
