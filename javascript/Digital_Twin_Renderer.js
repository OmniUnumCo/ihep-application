/**
 * React component wrapper for IHEP Digital Twin Renderer
 * 
 * This integrates the three.js rendering engine into your Next.js application
 * with proper lifecycle management and React hooks.
 */

import { useEffect, useRef, useState } from 'react';
import IHEPDigitalTwinRenderer from './IHEPDigitalTwinRenderer';

export default function DigitalTwinViewer({ usdScenePath, onPatientSelect }) {
    // Ref to container DOM element
    const containerRef = useRef(null);
    
    // Ref to renderer instance
    const rendererRef = useRef(null);
    
    // State for viewer controls
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [animationSpeed, setAnimationSpeed] = useState(1.0);
    const [selectedPatient, setSelectedPatient] = useState(null);
    
    // Initialize renderer on mount
    useEffect(() => {
        if (!containerRef.current) return;
        
        console.log('Initializing Digital Twin Viewer');
        
        // Create renderer instance
        const renderer = new IHEPDigitalTwinRenderer(
            containerRef.current,
            {
                enableMorphogenetics: true,
                targetFrameRate: 60,
                lodThresholds: [50, 100, 200]
            }
        );
        
        // Load USD scene
        renderer.loadUSDScene(usdScenePath)
            .then(() => {
                console.log('USD scene loaded successfully');
            })
            .catch((error) => {
                console.error('Failed to load USD scene:', error);
            });
        
        // Store renderer reference
        rendererRef.current = renderer;
        
        // Cleanup on unmount
        return () => {
            if (rendererRef.current) {
                rendererRef.current.dispose();
                rendererRef.current = null;
            }
        };
    }, [usdScenePath]);
    
    // Handle play/pause
    const togglePlayback = () => {
        if (!rendererRef.current) return;
        
        if (isPlaying) {
            rendererRef.current.pause();
        } else {
            rendererRef.current.play();
        }
        
        setIsPlaying(!isPlaying);
    };
    
    // Handle time scrubbing
    const handleTimeChange = (newTime) => {
        if (!rendererRef.current) return;
        
        rendererRef.current.setCurrentTime(newTime);
        setCurrentTime(newTime);
    };
    
    // Handle speed change
    const handleSpeedChange = (newSpeed) => {
        if (!rendererRef.current) return;
        
        rendererRef.current.setAnimationSpeed(newSpeed);
        setAnimationSpeed(newSpeed);
    };
    
    // Handle patient selection
    const handlePatientClick = (patientId) => {
        if (!rendererRef.current) return;
        
        const patientData = rendererRef.current.getPatientDataAtCurrentTime(patientId);
        setSelectedPatient(patientData);
        
        if (onPatientSelect) {
            onPatientSelect(patientData);
        }
    };
    
    // Start automated flythrough
    const startFlythrough = () => {
        if (!rendererRef.current) return;
        rendererRef.current.startFlythrough(60);
    };
    
    return (
        <div className="digital-twin-viewer">
            {/* Rendering canvas container */}
            <div 
                ref={containerRef}
                className="renderer-container"
                style={{
                    width: '100%',
                    height: '600px',
                    backgroundColor: '#000',
                    borderRadius: '8px',
                    overflow: 'hidden'
                }}
            />
            
            {/* Control panel */}
            <div className="controls-panel" style={{
                marginTop: '20px',
                padding: '20px',
                backgroundColor: '#1a1a2e',
                borderRadius: '8px',
                color: '#fff'
            }}>
                <h3>Animation Controls</h3>
                
                {/* Play/Pause button */}
                <button 
                    onClick={togglePlayback}
                    style={{
                        padding: '10px 20px',
                        marginRight: '10px',
                        backgroundColor: isPlaying ? '#e74c3c' : '#27ae60',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    {isPlaying ? 'Pause' : 'Play'}
                </button>
                
                {/* Flythrough button */}
                <button 
                    onClick={startFlythrough}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#3498db',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Start Flythrough
                </button>
                
                {/* Time scrubber */}
                <div style={{ marginTop: '20px' }}>
                    <label>Time (Days): {currentTime.toFixed(0)}</label>
                    <input 
                        type="range"
                        min="0"
                        max="365"
                        value={currentTime}
                        onChange={(e) => handleTimeChange(parseFloat(e.target.value))}
                        style={{
                            width: '100%',
                            marginTop: '10px'
                        }}
                    />
                </div>
                
                {/* Speed control */}
                <div style={{ marginTop: '20px' }}>
                    <label>Speed: {animationSpeed.toFixed(1)}x</label>
                    <input 
                        type="range"
                        min="0.1"
                        max="10"
                        step="0.1"
                        value={animationSpeed}
                        onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
                        style={{
                            width: '100%',
                            marginTop: '10px'
                        }}
                    />
                </div>
                
                {/* Selected patient info */}
                {selectedPatient && (
                    <div style={{
                        marginTop: '20px',
                        padding: '15px',
                        backgroundColor: '#2c2c54',
                        borderRadius: '4px'
                    }}>
                        <h4>Selected Patient</h4>
                        <p>ID: {selectedPatient.patientId}</p>
                        <p>Day: {selectedPatient.time.toFixed(0)}</p>
                        <p>Status: {selectedPatient.viralStatus}</p>
                        <p>CD4 Count: {selectedPatient.cd4Count} cells/μL</p>
                    </div>
                )}
            </div>
        </div>
    );
}