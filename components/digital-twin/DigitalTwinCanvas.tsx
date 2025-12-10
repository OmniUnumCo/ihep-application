// components/digital-twin/DigitalTwinCanvas.tsx (Complete Implementation)
'use client';

import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface DigitalTwinCanvasProps {
  healthScore: number;
  heartRate: number;
  viralLoad?: number;
  cd4Count?: number;
}

export function DigitalTwinCanvas({ healthScore, heartRate, viralLoad, cd4Count }: DigitalTwinCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const humanoidRef = useRef<THREE.Mesh | null>(null);
  const animationRef = useRef<number>(0);

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
    renderer.setClearColor(0x000000, 0);
    rendererRef.current = renderer;
    canvasRef.current.appendChild(renderer.domElement);

    // Create simplified humanoid form with body parts
    const group = new THREE.Group();
    
    // Head
    const headGeometry = new THREE.SphereGeometry(0.3, 16, 16);
    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0x00ff88,
      emissive: 0x00ff88,
      emissiveIntensity: 0.3,
      transparent: true,
      opacity: 0.7,
    });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.8;
    group.add(head);

    // Body
    const bodyGeometry = new THREE.CapsuleGeometry(0.4, 1.2, 16, 32);
    const bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x00ff88,
      emissive: 0x00ff88,
      emissiveIntensity: 0.3,
      transparent: true,
      opacity: 0.6,
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.6;
    group.add(body);

    // Arms
    const armGeometry = new THREE.CapsuleGeometry(0.15, 0.8, 16, 16);
    const armMaterial = new THREE.MeshStandardMaterial({
      color: 0x00ff88,
      emissive: 0x00ff88,
      emissiveIntensity: 0.2,
      transparent: true,
      opacity: 0.5,
    });

    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.6, 0.8, 0);
    leftArm.rotation.z = Math.PI / 6;
    group.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.6, 0.8, 0);
    rightArm.rotation.z = -Math.PI / 6;
    group.add(rightArm);

    // Legs
    const legGeometry = new THREE.CapsuleGeometry(0.2, 1.0, 16, 16);
    const legMaterial = new THREE.MeshStandardMaterial({
      color: 0x00ff88,
      emissive: 0x00ff88,
      emissiveIntensity: 0.2,
      transparent: true,
      opacity: 0.5,
    });

    const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
    leftLeg.position.set(-0.2, -0.7, 0);
    group.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
    rightLeg.position.set(0.2, -0.7, 0);
    group.add(rightLeg);

    humanoidRef.current = group;
    scene.add(group);

    // Add ambient and point lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(2, 2, 2);
    scene.add(pointLight);

    const backLight = new THREE.PointLight(0x4444ff, 0.5);
    backLight.position.set(-2, 1, -2);
    scene.add(backLight);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      if (humanoidRef.current) {
        // Rotate entire figure slowly
        humanoidRef.current.rotation.y += 0.002;
        
        // Pulsate based on heart rate
        const normalizedHR = Math.max(0, Math.min(1, (heartRate - 40) / 80));
        const pulseSpeed = 0.5 + normalizedHR * 2;
        const pulseScale = 1 + Math.sin(Date.now() * 0.001 * pulseSpeed * Math.PI * 2) * 0.03;
        humanoidRef.current.scale.set(pulseScale, pulseScale, pulseScale);
        
        // Adjust color based on health score
        humanoidRef.current.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            const material = child.material as THREE.MeshStandardMaterial;
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
            
            // Adjust opacity based on viral load if available
            if (viralLoad !== undefined) {
              const opacityFactor = Math.max(0.3, 1 - (viralLoad / 1000));
              material.opacity = opacityFactor;
            }
          }
        });
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
      cancelAnimationFrame(animationRef.current);
      if (canvasRef.current && rendererRef.current?.domElement) {
        canvasRef.current.removeChild(rendererRef.current.domElement);
      }
      rendererRef.current?.dispose();
    };
  }, []);

  // Update properties when health metrics change
  useEffect(() => {
    // Properties are updated in the animation loop
  }, [healthScore, heartRate, viralLoad, cd4Count]);

  return (
    <div 
      ref={canvasRef} 
      className="w-full h-96 bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-lg backdrop-blur-sm border border-blue-500/30"
    />
  );
}
