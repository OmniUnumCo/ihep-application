'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { DigitalTwinState } from '@/types';

interface DigitalTwinCanvasProps {
  userId: string;
  state: DigitalTwinState;
  interactive?: boolean;
  showTrajectory?: boolean;
  showPredictions?: boolean;
  onStateChange?: (state: DigitalTwinState) => void;
}

export function DigitalTwinCanvas({
  userId,
  state,
  interactive = true,
  showTrajectory = true,
  showPredictions = false,
  onStateChange,
}: DigitalTwinCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const avatarRef = useRef<THREE.Mesh | null>(null);
  const trajectoryRef = useRef<THREE.Line | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      initializeScene();
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize Digital Twin');
      setLoading(false);
    }

    return () => {
      cleanup();
    };
  }, []);

  useEffect(() => {
    if (!sceneRef.current || !state) return;
    updateDigitalTwin(state);
  }, [state]);

  const initializeScene = () => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    scene.fog = new THREE.Fog(0x0a0a0a, 10, 50);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(5, 5, 5);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Controls
    if (interactive) {
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.screenSpacePanning = false;
      controls.minDistance = 2;
      controls.maxDistance = 20;
      controlsRef.current = controls;
    }

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    scene.add(directionalLight);

    // Grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Axes helper (for development)
    if (process.env.NODE_ENV === 'development') {
      const axesHelper = new THREE.AxesHelper(5);
      scene.add(axesHelper);
    }

    // Create avatar mesh
    createAvatar();

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);
      
      if (controlsRef.current) {
        controlsRef.current.update();
      }

      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    animate();

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  };

  const createAvatar = () => {
    if (!sceneRef.current) return;

    // Avatar geometry - sphere representing patient
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    
    // Material with health-based color
    const material = new THREE.MeshPhongMaterial({
      color: 0x3b82f6, // Default blue
      emissive: 0x3b82f6,
      emissiveIntensity: 0.2,
      shininess: 100,
      transparent: true,
      opacity: 0.9,
    });

    const avatar = new THREE.Mesh(geometry, material);
    avatar.castShadow = true;
    avatar.receiveShadow = true;
    avatarRef.current = avatar;
    sceneRef.current.add(avatar);

    // Add pulsing animation
    const pulse = () => {
      if (!avatarRef.current) return;
      const scale = 1 + Math.sin(Date.now() * 0.002) * 0.05;
      avatarRef.current.scale.set(scale, scale, scale);
    };
    setInterval(pulse, 16); // ~60fps
  };

  const updateDigitalTwin = (newState: DigitalTwinState) => {
    if (!avatarRef.current || !sceneRef.current) return;

    // Update position from manifold projection
    const [x, y, z] = newState.visualizationState.position;
    avatarRef.current.position.set(x, y, z);

    // Update color based on health score
    const [r, g, b] = newState.visualizationState.color;
    const material = avatarRef.current.material as THREE.MeshPhongMaterial;
    material.color.setRGB(r, g, b);
    material.emissive.setRGB(r * 0.5, g * 0.5, b * 0.5);

    // Update size
    const size = newState.visualizationState.size;
    avatarRef.current.scale.setScalar(size);

    // Update opacity
    material.opacity = newState.visualizationState.opacity;

    // Update trajectory
    if (showTrajectory && newState.trajectory.length > 0) {
      updateTrajectory(newState.trajectory);
    }

    // Update predictions
    if (showPredictions && newState.predictions.length > 0) {
      updatePredictions(newState.predictions);
    }
  };

  const updateTrajectory = (trajectory: typeof state.trajectory) => {
    if (!sceneRef.current) return;

    // Remove old trajectory
    if (trajectoryRef.current) {
      sceneRef.current.remove(trajectoryRef.current);
    }

    // Create new trajectory line
    const points = trajectory.map(t => 
      new THREE.Vector3(t.visualPosition[0], t.visualPosition[1], t.visualPosition[2])
    );

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0x888888,
      linewidth: 2,
      transparent: true,
      opacity: 0.5,
    });

    const line = new THREE.Line(geometry, material);
    trajectoryRef.current = line;
    sceneRef.current.add(line);
  };

  const updatePredictions = (predictions: typeof state.predictions) => {
    if (!sceneRef.current) return;

    // Clear old predictions
    sceneRef.current.children
      .filter(child => (child as any).isPrediction)
      .forEach(child => sceneRef.current!.remove(child));

    // Add prediction spheres
    predictions.forEach((prediction, index) => {
      const geometry = new THREE.SphereGeometry(0.3, 16, 16);
      const material = new THREE.MeshPhongMaterial({
        color: 0xffaa00,
        transparent: true,
        opacity: prediction.confidence * 0.5,
        wireframe: true,
      });

      const sphere = new THREE.Mesh(geometry, material);
      
      // Position prediction (simplified - would use actual predicted state)
      const offset = (index + 1) * 1.5;
      sphere.position.copy(avatarRef.current!.position);
      sphere.position.y += offset;
      
      (sphere as any).isPrediction = true;
      sceneRef.current!.add(sphere);
    });
  };

  const cleanup = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    if (controlsRef.current) {
      controlsRef.current.dispose();
    }

    if (rendererRef.current) {
      rendererRef.current.dispose();
      if (containerRef.current && rendererRef.current.domElement) {
        containerRef.current.removeChild(rendererRef.current.domElement);
      }
    }

    if (sceneRef.current) {
      sceneRef.current.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
    }
  };

  if (loading) {
    return (
      <div className="dt-canvas-loading">
        <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full" />
        <p className="mt-4 text-muted-foreground">Initializing Digital Twin...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dt-canvas-loading">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="dt-canvas-container w-full h-full">
      {/* Controls overlay */}
      {interactive && (
        <div className="absolute top-4 left-4 bg-background/80 backdrop-blur-sm rounded-lg p-3 text-sm space-y-2">
          <p className="font-medium">Controls:</p>
          <p>Left mouse: Rotate</p>
          <p>Right mouse: Pan</p>
          <p>Scroll: Zoom</p>
        </div>
      )}
      
      {/* Health metrics overlay */}
      <div className="absolute top-4 right-4 bg-background/80 backdrop-blur-sm rounded-lg p-3 text-sm">
        <p className="font-medium mb-2">Health Metrics</p>
        <p>Dimension: {state.dimension}D → 3D</p>
        <p>Distortion: {(state.manifold.distortion * 100).toFixed(2)}%</p>
        <p className="text-xs text-muted-foreground mt-2">
          δ ≤ {state.manifold.distortion.toFixed(4)}
        </p>
      </div>
    </div>
  );
}
