// components/digital-twin/DigitalTwinCanvas.tsx
'use client';

import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface DigitalTwinCanvasProps {
  healthScore: number; // 0-100 aggregate health score
  heartRate: number;
}

export function DigitalTwinCanvas({ healthScore, heartRate }: DigitalTwinCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const humanoidRef = useRef<THREE.Mesh | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize Three.js scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    
    const camera = new THREE.PerspectiveCamera(
      75,
      canvasRef.current.clientWidth / canvasRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(canvasRef.current.clientWidth, canvasRef.current.clientHeight);
    rendererRef.current = renderer;
    canvasRef.current.appendChild(renderer.domElement);

    // Create simplified humanoid form
    const geometry = new THREE.CapsuleGeometry(0.5, 2, 32, 32);
    const material = new THREE.MeshStandardMaterial({
      color: 0x00ff88,
      emissive: 0x00ff88,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.8,
    });
    
    const humanoid = new THREE.Mesh(geometry, material);
    humanoidRef.current = humanoid;
    scene.add(humanoid);

    // Add ambient and point lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(2, 2, 2);
    scene.add(pointLight);

    // Animation loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      
      if (humanoidRef.current) {
        // Rotate humanoid
        humanoidRef.current.rotation.y += 0.005;
        
        // Pulsate based on heart rate
        // Normalize heart rate to 0-1 range (assuming 40-120 bpm range)
        const normalizedHR = Math.max(0, Math.min(1, (heartRate - 40) / 80));
        const pulseSpeed = 0.5 + normalizedHR * 2; // 0.5 to 2.5 Hz
        const pulseScale = 1 + Math.sin(Date.now() * 0.001 * pulseSpeed * Math.PI * 2) * 0.05;
        humanoidRef.current.scale.set(pulseScale, pulseScale, pulseScale);
        
        // Change color based on health score
        const material = humanoidRef.current.material as THREE.MeshStandardMaterial;
        if (healthScore >= 80) {
          material.color.setHex(0x00ff88); // Green for good health
          material.emissive.setHex(0x00ff88);
        } else if (healthScore >= 50) {
          material.color.setHex(0xffaa00); // Orange for moderate health
          material.emissive.setHex(0xffaa00);
        } else {
          material.color.setHex(0xff3300); // Red for poor health
          material.emissive.setHex(0xff3300);
        }
      }
      
      renderer.render(scene, camera);
    };
    animate();

    // Handle window resize
    const handleResize = () => {
      if (!canvasRef.current || !rendererRef.current) return;
      
      const width = canvasRef.current.clientWidth;
      const height = canvasRef.current.clientHeight;
      
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (canvasRef.current && rendererRef.current) {
        canvasRef.current.removeChild(rendererRef.current.domElement);
      }
      rendererRef.current?.dispose();
    };
  }, []);

  // Update humanoid properties when health metrics change
  useEffect(() => {
    // Health score and heart rate changes are handled in the animation loop
  }, [healthScore, heartRate]);

  return (
    <div 
      ref={canvasRef} 
      className="w-full h-96 bg-gradient-to-br from-blue-900 to-purple-900 rounded-lg"
    />
  );
}