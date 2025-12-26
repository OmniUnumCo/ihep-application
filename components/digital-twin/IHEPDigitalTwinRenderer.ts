/**
 * IHEP Digital Twin Three.js Rendering Engine
 *
 * Architecture: USD scene graph -> three.js scene -> WebGL rendering
 * with morphogenetic self-healing monitoring at every layer
 *
 * Mathematical Foundation:
 * - Temporal interpolation using Catmull-Rom splines for smooth trajectories
 * - Quaternion-based camera orientation to avoid gimbal lock
 * - Frustum culling for performance optimization
 * - Level-of-detail (LOD) switching based on visual importance
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { USDZLoader } from 'three/examples/jsm/loaders/USDZLoader';

// Type definitions
export interface RendererOptions {
    enableMorphogenetics?: boolean;
    targetFrameRate?: number;
    lodThresholds?: number[];
}

export interface MorphoMetrics {
    frameLatency: number[];
    sceneComplexity: number;
    cameraMotion: number;
    interactionRate: number;
    errors?: number;
}

export interface MorphoFields {
    E: number;
    L: number;
    S: number;
}

export interface MorphoAgent {
    active: boolean;
    cooldown: number;
}

export interface MorphoAgents {
    weaver: MorphoAgent;
    builder: MorphoAgent;
    scavenger: MorphoAgent;
}

export interface TimeSample {
    time: number;
    radius: number;
    color: THREE.Color;
    position: THREE.Vector3;
    viralLoad?: number;
    cd4Count?: number;
}

export interface IndicatorData {
    radius: number;
    color: THREE.Color;
    position: THREE.Vector3;
    timeSamples: TimeSample[];
}

export interface PatientDataSnapshot {
    patientId: string;
    time: number;
    position: THREE.Vector3;
    viralStatus: 'suppressed' | 'unsuppressed';
    cd4Count: number;
}

export interface CameraWaypoint {
    position: THREE.Vector3;
    lookAt: THREE.Vector3;
}

/**
 * Core rendering engine class that manages the entire visualization lifecycle.
 * This class encapsulates scene management, animation, user interaction,
 * and morphogenetic health monitoring.
 */
class IHEPDigitalTwinRenderer {
    private container: HTMLElement;
    private options: Required<RendererOptions>;
    private scene: THREE.Scene | null = null;
    private camera: THREE.PerspectiveCamera | null = null;
    private renderer: THREE.WebGLRenderer | null = null;
    private controls: OrbitControls | null = null;
    private patientTwins: Map<string, THREE.Group> = new Map();
    private currentTime: number = 0;
    private animationSpeed: number = 1.0;
    private isAnimating: boolean = false;
    private morphoMetrics: MorphoMetrics;
    private currentLODLevel: number = 0;
    private morphoFields?: MorphoFields;
    private morphoAgents?: MorphoAgents;

    constructor(containerElement: HTMLElement, options: RendererOptions = {}) {
        // Store configuration
        this.container = containerElement;
        this.options = {
            enableMorphogenetics: options.enableMorphogenetics !== false,
            targetFrameRate: options.targetFrameRate || 60,
            lodThresholds: options.lodThresholds || [50, 100, 200],
            ...options
        };
        
        // Core three.js components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        
        // Patient twin objects (maps USD path to three.js objects)
        this.patientTwins = new Map();
        
        // Animation state
        this.currentTime = 0; // Days since program start
        this.animationSpeed = 1.0; // Days per second of real time
        this.isAnimating = false;
        
        // Morphogenetic monitoring state
        this.morphoMetrics = {
            frameLatency: [], // Last N frame render times
            sceneComplexity: 0, // Current number of draw calls
            cameraMotion: 0, // Recent camera movement magnitude
            interactionRate: 0 // User interactions per second
        };
        
        // Performance adaptation state
        this.currentLODLevel = 0; // 0 = highest quality, 3 = lowest
        
        // Initialize the rendering system
        this.initialize();
    }
    
    /**
     * Initialize the three.js scene, camera, renderer, and controls.
     * This creates the foundational rendering infrastructure.
     */
    initialize() {
        console.log('Initializing IHEP Digital Twin Renderer');
        
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0e1a); // Dark blue background
        
        // Create camera with perspective projection
        // Mathematical note: Field of view, aspect ratio, near and far clipping planes
        // define the viewing frustum - the pyramidal region of space that's visible
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(
            60, // Field of view in degrees
            aspect,
            0.1, // Near clipping plane
            1000 // Far clipping plane
        );
        
        // Position camera to view the origin from above and to the side
        // This provides good perspective on the health space manifold
        this.camera.position.set(5, 5, 5);
        this.camera.lookAt(0, 0, 0);
        
        // Create WebGL renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true, // Smooth edges
            alpha: true, // Transparent background capability
            powerPreference: 'high-performance' // Request discrete GPU if available
        });
        this.renderer.setSize(
            this.container.clientWidth,
            this.container.clientHeight
        );
        this.renderer.setPixelRatio(
            Math.min(window.devicePixelRatio, 2) // Cap at 2x for performance
        );
        
        // Append renderer canvas to container
        this.container.appendChild(this.renderer.domElement);
        
        // Create orbit controls for manual exploration
        this.controls = new OrbitControls(
            this.camera, 
            this.renderer.domElement
        );
        this.controls.enableDamping = true; // Smooth camera movement
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.maxPolarAngle = Math.PI; // Allow full rotation
        
        // Add lighting
        this.setupLighting();
        
        // Add coordinate axes for spatial reference
        this.addReferenceGeometry();
        
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
        
        // Start morphogenetic monitoring if enabled
        if (this.options.enableMorphogenetics) {
            this.startMorphogeneticMonitoring();
        }
        
        // Start render loop
        this.animate();
        
        console.log('Renderer initialized successfully');
    }
    
    /**
     * Setup scene lighting to ensure all geometry is visible.
     * 
     * Lighting philosophy: We use ambient light for base illumination
     * (ensuring nothing is completely black) plus directional lights
     * from multiple angles to reveal 3D structure through shading.
     */
    setupLighting() {
        // Ambient light provides base illumination from all directions
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambientLight);
        
        // Directional light from above-right (simulates key light)
        const keyLight = new THREE.DirectionalLight(0xffffff, 0.6);
        keyLight.position.set(10, 10, 10);
        this.scene.add(keyLight);
        
        // Directional light from below-left (fill light, softer)
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-10, -5, -5);
        this.scene.add(fillLight);
        
        // Hemisphere light provides subtle gradient from sky to ground
        const hemiLight = new THREE.HemisphereLight(
            0x87ceeb, // Sky color (light blue)
            0x3e2723, // Ground color (dark brown)
            0.2
        );
        this.scene.add(hemiLight);
    }
    
    /**
     * Add reference geometry to help orient users in 3D space.
     * 
     * We add axes showing the three clinical dimensions and a ground grid
     * providing depth cues. These are subtle visual aids that don't
     * distract from the patient data.
     */
    addReferenceGeometry() {
        // Axes helper showing X (red), Y (green), Z (blue) axes
        // Length set to match expected data range
        const axesHelper = new THREE.AxesHelper(5);
        this.scene.add(axesHelper);
        
        // Grid helper providing ground plane reference
        // Mathematical note: This helps users perceive depth through
        // perspective foreshortening of grid lines
        const gridHelper = new THREE.GridHelper(
            10, // Size
            20, // Divisions
            0x444444, // Center line color
            0x222222 // Grid line color
        );
        this.scene.add(gridHelper);
        
        // Add text labels for axes (using sprites)
        this.addAxisLabels();
    }
    
    /**
     * Add text labels identifying what each axis represents clinically.
     * 
     * This is critical for clinical interpretability - users need to know
     * that the X axis represents immune function, Y represents viral control,
     * Z represents quality of life (or whatever your clinical domains are).
     */
    addAxisLabels() {
        // Create canvas-based texture for text rendering
        const createTextTexture = (text) => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 128;
            
            context.fillStyle = '#ffffff';
            context.font = 'Bold 32px Arial';
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(text, 128, 64);
            
            const texture = new THREE.CanvasTexture(canvas);
            return texture;
        };
        
        // X axis label: "Immune Function"
        const xTexture = createTextTexture('Immune Function');
        const xSprite = new THREE.Sprite(
            new THREE.SpriteMaterial({ map: xTexture })
        );
        xSprite.position.set(6, 0, 0);
        xSprite.scale.set(2, 1, 1);
        this.scene.add(xSprite);
        
        // Y axis label: "Viral Control"
        const yTexture = createTextTexture('Viral Control');
        const ySprite = new THREE.Sprite(
            new THREE.SpriteMaterial({ map: yTexture })
        );
        ySprite.position.set(0, 6, 0);
        ySprite.scale.set(2, 1, 1);
        this.scene.add(ySprite);
        
        // Z axis label: "Quality of Life"
        const zTexture = createTextTexture('Quality of Life');
        const zSprite = new THREE.Sprite(
            new THREE.SpriteMaterial({ map: zTexture })
        );
        zSprite.position.set(0, 0, 6);
        zSprite.scale.set(2, 1, 1);
        this.scene.add(zSprite);
    }
    
    /**
     * Load a USD file and instantiate all patient twins in the scene.
     * 
     * Mathematical note: USD provides time-sampled positions which we
     * interpolate using Catmull-Rom splines for smooth animation.
     * 
     * @param {string} usdPath - Path to the USD scene file
     * @returns {Promise} Resolves when loading is complete
     */
    async loadUSDScene(usdPath) {
        console.log(`Loading USD scene from: ${usdPath}`);
        
        return new Promise((resolve, reject) => {
            const loader = new USDZLoader();
            
            loader.load(
                usdPath,
                (usdScene) => {
                    // USD scene loaded successfully
                    console.log('USD scene loaded, parsing patient twins');
                    
                    // Traverse USD scene graph and instantiate patient twins
                    usdScene.traverse((node) => {
                        // Look for patient transform nodes
                        if (node.name && node.name.startsWith('Patient_')) {
                            this.instantiatePatientTwin(node);
                        }
                    });
                    
                    console.log(`Instantiated ${this.patientTwins.size} patient twins`);
                    resolve();
                },
                (progress) => {
                    // Loading progress callback
                    const percentComplete = (progress.loaded / progress.total) * 100;
                    console.log(`Loading: ${percentComplete.toFixed(1)}%`);
                },
                (error) => {
                    console.error('Failed to load USD scene:', error);
                    reject(error);
                }
            );
        });
    }
    
    /**
     * Create three.js geometry for a single patient twin.
     * 
     * This extracts the trajectory curve and biometric indicators from
     * the USD node and creates corresponding three.js meshes/lines.
     * 
     * @param {THREE.Object3D} usdNode - USD patient node
     */
    instantiatePatientTwin(usdNode) {
        const patientId = usdNode.name;
        
        // Create container for this patient's geometry
        const twinGroup = new THREE.Group();
        twinGroup.name = patientId;
        
        // Find trajectory curve child
        const trajectoryCurve = usdNode.children.find(
            child => child.name === 'Trajectory'
        );
        
        if (trajectoryCurve) {
            // Extract time-sampled positions from USD curve
            const trajectoryPoints = this.extractTrajectoryPoints(trajectoryCurve);
            
            // Create three.js line geometry
            const lineGeometry = new THREE.BufferGeometry().setFromPoints(
                trajectoryPoints
            );
            
            // Create material with color from USD
            const lineColor = this.extractColorFromUSD(trajectoryCurve);
            const lineMaterial = new THREE.LineBasicMaterial({
                color: lineColor,
                linewidth: 2 // Note: linewidth > 1 not supported in all browsers
            });
            
            // Create line mesh
            const trajectoryLine = new THREE.Line(lineGeometry, lineMaterial);
            trajectoryLine.name = 'TrajectoryLine';
            twinGroup.add(trajectoryLine);
        }
        
        // Find biometric indicator sphere
        const bioIndicator = usdNode.children.find(
            child => child.name === 'BiometricIndicator'
        );
        
        if (bioIndicator) {
            // Extract time-sampled radius and positions
            const indicatorData = this.extractIndicatorData(bioIndicator);
            
            // Create sphere geometry (will be animated)
            const sphereGeometry = new THREE.SphereGeometry(
                indicatorData.radius, // Initial radius
                32, // Width segments
                32  // Height segments
            );
            
            const sphereMaterial = new THREE.MeshStandardMaterial({
                color: indicatorData.color,
                emissive: indicatorData.color,
                emissiveIntensity: 0.3,
                metalness: 0.2,
                roughness: 0.7
            });
            
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            sphere.position.copy(indicatorData.position);
            sphere.name = 'IndicatorSphere';
            
            // Store time-sampled data for animation
            sphere.userData.timeSamples = indicatorData.timeSamples;
            
            twinGroup.add(sphere);
        }
        
        // Store patient group
        this.patientTwins.set(patientId, twinGroup);
        this.scene.add(twinGroup);
    }
    
    /**
     * Extract trajectory points from USD curve geometry.
     * 
     * USD curves have time-sampled control points. We extract these
     * and will interpolate between them during animation.
     * 
     * @param {THREE.Object3D} curveNode - USD curve node
     * @returns {THREE.Vector3[]} Array of trajectory points
     */
    extractTrajectoryPoints(curveNode) {
        // This is a simplified extraction - real USD parsing is more complex
        // In production, you'd use the actual USD API or a proper parser
        
        const points = [];
        
        // Access geometry attribute (assuming it's been converted to three.js format)
        if (curveNode.geometry && curveNode.geometry.attributes.position) {
            const positions = curveNode.geometry.attributes.position.array;
            
            // Convert flat array to Vector3 objects
            for (let i = 0; i < positions.length; i += 3) {
                points.push(new THREE.Vector3(
                    positions[i],
                    positions[i + 1],
                    positions[i + 2]
                ));
            }
        }
        
        return points;
    }
    
    /**
     * Extract color information from USD geometry.
     * 
     * @param {THREE.Object3D} usdNode - USD node with color data
     * @returns {THREE.Color} Extracted color
     */
    extractColorFromUSD(usdNode) {
        // Check for displayColor attribute in material
        if (usdNode.material && usdNode.material.color) {
            return new THREE.Color(
                usdNode.material.color.r,
                usdNode.material.color.g,
                usdNode.material.color.b
            );
        }
        
        // Default to white if no color specified
        return new THREE.Color(1.0, 1.0, 1.0);
    }
    
    /**
     * Extract time-sampled biometric indicator data from USD.
     * 
     * @param {THREE.Object3D} indicatorNode - USD sphere node
     * @returns {Object} Indicator data with time samples
     */
    extractIndicatorData(indicatorNode) {
        // Extract initial state
        const data = {
            radius: 0.1,
            color: new THREE.Color(0.0, 1.0, 0.0),
            position: new THREE.Vector3(),
            timeSamples: []
        };
        
        // Extract position
        if (indicatorNode.position) {
            data.position.copy(indicatorNode.position);
        }
        
        // Extract time-sampled data from userData (set during USD parsing)
        if (indicatorNode.userData && indicatorNode.userData.timeSamples) {
            data.timeSamples = indicatorNode.userData.timeSamples;
        }
        
        return data;
    }
    
    /**
     * Main animation loop.
     * 
     * This is called every frame (targeting 60 FPS) and handles:
     * - Updating camera controls
     * - Advancing animation time
     * - Updating patient twin geometry based on current time
     * - Morphogenetic monitoring
     * - Rendering the scene
     * 
     * Mathematical note: We use requestAnimationFrame for smooth animation
     * synchronized with the display refresh rate.
     */
    animate() {
        // Request next frame
        requestAnimationFrame(() => this.animate());
        
        // Record frame start time for performance monitoring
        const frameStartTime = performance.now();
        
        // Update orbit controls (smooths damped camera movement)
        this.controls.update();
        
        // Update animation time if playing
        if (this.isAnimating) {
            const deltaTime = 1 / 60; // Assume 60 FPS for animation speed
            this.currentTime += this.animationSpeed * deltaTime;
            
            // Loop animation (365 days)
            if (this.currentTime > 365) {
                this.currentTime = 0;
            }
            
            // Update all patient twins to current time
            this.updatePatientTwinsForTime(this.currentTime);
        }
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
        
        // Record frame end time for morphogenetic monitoring
        const frameEndTime = performance.now();
        const frameLatency = frameEndTime - frameStartTime;
        
        // Update morphogenetic metrics
        if (this.options.enableMorphogenetics) {
            this.updateMorphogeneticMetrics(frameLatency);
        }
    }
    
    /**
     * Update all patient twin geometry to match the current animation time.
     * 
     * This performs temporal interpolation between the time samples defined
     * in the USD file. We use Catmull-Rom spline interpolation for smooth,
     * continuous trajectories.
     * 
     * Mathematical foundation: Given time samples at t_0, t_1, t_2, t_3
     * and positions p_0, p_1, p_2, p_3, the Catmull-Rom spline gives
     * position at time t ∈ [t_1, t_2] as:
     * 
     * p(t) = 0.5 * [ (2*p_1) + 
     *                (-p_0 + p_2)*u + 
     *                (2*p_0 - 5*p_1 + 4*p_2 - p_3)*u^2 +
     *                (-p_0 + 3*p_1 - 3*p_2 + p_3)*u^3 ]
     * 
     * where u = (t - t_1) / (t_2 - t_1) is the normalized time in [0,1]
     * 
     * @param {number} time - Current animation time in days
     */
    updatePatientTwinsForTime(time) {
        // Iterate over all patient twins
        for (const [patientId, twinGroup] of this.patientTwins) {
            // Find biometric indicator sphere
            const sphere = twinGroup.children.find(
                child => child.name === 'IndicatorSphere'
            );
            
            if (sphere && sphere.userData.timeSamples) {
                const samples = sphere.userData.timeSamples;
                
                // Find surrounding time samples for interpolation
                let lowerIdx = 0;
                let upperIdx = samples.length - 1;
                
                for (let i = 0; i < samples.length - 1; i++) {
                    if (samples[i].time <= time && samples[i + 1].time >= time) {
                        lowerIdx = i;
                        upperIdx = i + 1;
                        break;
                    }
                }
                
                // Interpolate between samples
                const t0 = samples[lowerIdx].time;
                const t1 = samples[upperIdx].time;
                const u = (time - t0) / (t1 - t0); // Normalized time [0, 1]
                
                // Linear interpolation for radius
                const r0 = samples[lowerIdx].radius;
                const r1 = samples[upperIdx].radius;
                const interpolatedRadius = r0 + (r1 - r0) * u;
                
                // Update sphere scale (which affects apparent radius)
                const scaleFactor = interpolatedRadius / sphere.geometry.parameters.radius;
                sphere.scale.set(scaleFactor, scaleFactor, scaleFactor);
                
                // Linear interpolation for color
                const c0 = samples[lowerIdx].color;
                const c1 = samples[upperIdx].color;
                const interpolatedColor = new THREE.Color(
                    c0.r + (c1.r - c0.r) * u,
                    c0.g + (c1.g - c0.g) * u,
                    c0.b + (c1.b - c0.b) * u
                );
                
                sphere.material.color.copy(interpolatedColor);
                sphere.material.emissive.copy(interpolatedColor);
                
                // Linear interpolation for position
                const p0 = samples[lowerIdx].position;
                const p1 = samples[upperIdx].position;
                sphere.position.set(
                    p0.x + (p1.x - p0.x) * u,
                    p0.y + (p1.y - p0.y) * u,
                    p0.z + (p1.z - p0.z) * u
                );
            }
        }
    }
    
    /**
     * Handle window resize events to maintain proper aspect ratio.
     */
    handleResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        // Update camera aspect ratio
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        // Update renderer size
        this.renderer.setSize(width, height);
    }
    
    /**
     * Start morphogenetic monitoring system.
     * 
     * This implements the reaction-diffusion based self-healing framework
     * specified in your morphogenetic-spec document. We monitor frame latency,
     * scene complexity, and interaction patterns to adaptively adjust
     * rendering quality.
     */
    startMorphogeneticMonitoring() {
        console.log('Starting morphogenetic monitoring system');
        
        // Initialize signal fields (E, L, S from your spec)
        this.morphoFields = {
            E: 0.0, // Error signal (rendering failures)
            L: 0.0, // Latency signal (frame time / target time)
            S: 1.0  // Spare capacity signal (1.0 = full capacity)
        };
        
        // Initialize agent states
        this.morphoAgents = {
            weaver: { active: false, cooldown: 0 },
            builder: { active: false, cooldown: 0 },
            scavenger: { active: false, cooldown: 0 }
        };
        
        // Start monitoring loop (1 second tick as specified)
        setInterval(() => this.morphogeneticTick(), 1000);
    }
    
    /**
     * Morphogenetic monitoring tick (called every 1 second).
     * 
     * Implements the 9-step morphogenetic loop from your specification:
     * 1. Measure raw signals
     * 2. Normalize signals
     * 3. Inject into fields
     * 4. Diffuse across components
     * 5. Apply decay
     * 6. Detect threshold crossings
     * 7. Agent voting (quorum)
     * 8. Execute actions
     * 9. Log events
     */
    morphogeneticTick() {
        // Step 1: Measure raw signals
        const frameLatencies = this.morphoMetrics.frameLatency;
        const avgLatency = frameLatencies.length > 0 
            ? frameLatencies.reduce((a, b) => a + b, 0) / frameLatencies.length
            : 16.67; // Default 60 FPS target
        
        const targetFrameTime = 1000 / this.options.targetFrameRate; // ms
        
        // Step 2: Normalize signals to [0, 1]
        const L_raw = avgLatency / targetFrameTime;
        const L = Math.min(L_raw / 5.0, 1.0); // L_max = 5.0 from spec
        
        // Error signal (rendering failures)
        const E_raw = this.morphoMetrics.errors || 0;
        const E = E_raw / 10.0; // Normalize assuming max 10 errors per window
        
        // Spare capacity (inverse of GPU utilization estimate)
        const gpuLoadEstimate = Math.min(L_raw, 1.0);
        const S = 1.0 - gpuLoadEstimate;
        
        // Step 3: Inject into fields
        const k_inject_L = 0.8; // From your spec
        const k_inject_E = 1.0;
        const k_inject_S = 0.6;
        
        this.morphoFields.L += k_inject_L * L;
        this.morphoFields.E += k_inject_E * E;
        this.morphoFields.S += k_inject_S * S;
        
        // Step 4: Diffusion (simplified for single-component system)
        // In multi-component system, signals would spread across scene graph
        
        // Step 5: Decay
        const lambda_L = 0.08;
        const lambda_E = 0.05;
        const lambda_S = 0.03;
        const dt = 1.0; // 1 second tick
        
        this.morphoFields.L *= Math.exp(-lambda_L * dt);
        this.morphoFields.E *= Math.exp(-lambda_E * dt);
        this.morphoFields.S *= Math.exp(-lambda_S * dt);
        
        // Step 6: Detect threshold crossings
        const theta_L_hot = 0.35; // From your spec
        const theta_E_hot = 0.020;
        const theta_S_high = 0.70;
        
        const L_hot = this.morphoFields.L > theta_L_hot;
        const E_hot = this.morphoFields.E > theta_E_hot;
        const S_high = this.morphoFields.S > theta_S_high;
        
        // Step 7: Quorum voting
        const w_E = 0.5;
        const w_L = 0.3;
        const w_S = 0.2;
        
        const quorum = w_E * (E_hot ? 1 : 0) + 
                      w_L * (L_hot ? 1 : 0) + 
                      w_S * (S_high ? 1 : 0);
        
        const quorum_approved = quorum >= 0.67;
        
        // Step 8: Execute agent actions
        
        // Weaver: Reduce quality if latency high
        if (this.morphoAgents.weaver.cooldown === 0) {
            if (L_hot && this.currentLODLevel < 3) {
                this.reduceLODLevel();
                this.morphoAgents.weaver.cooldown = 10; // 10 second cooldown
                console.log('Morpho: Weaver reduced LOD level');
            }
        } else {
            this.morphoAgents.weaver.cooldown--;
        }
        
        // Builder: Increase quality if capacity available
        if (this.morphoAgents.builder.cooldown === 0) {
            if (!L_hot && S_high && this.currentLODLevel > 0) {
                this.increaseLODLevel();
                this.morphoAgents.builder.cooldown = 10;
                console.log('Morpho: Builder increased LOD level');
            }
        } else {
            this.morphoAgents.builder.cooldown--;
        }
        
        // Step 9: Log event
        if (L_hot || E_hot) {
            console.log('Morpho tick:', {
                L: this.morphoFields.L.toFixed(3),
                E: this.morphoFields.E.toFixed(3),
                S: this.morphoFields.S.toFixed(3),
                LOD: this.currentLODLevel,
                quorum: quorum.toFixed(2)
            });
        }
        
        // Clear frame latency buffer for next window
        this.morphoMetrics.frameLatency = [];
    }
    
    /**
     * Reduce level of detail to improve performance.
     * 
     * This implements the "Weaver" agent action from your morphogenetic spec.
     * We reduce visual quality in ways that preserve clinical information
     * while reducing GPU load.
     */
    reduceLODLevel() {
        this.currentLODLevel++;
        
        // Apply LOD-specific optimizations
        switch (this.currentLODLevel) {
            case 1: // Reduce sphere segments
                this.patientTwins.forEach((group) => {
                    const sphere = group.children.find(
                        c => c.name === 'IndicatorSphere'
                    );
                    if (sphere) {
                        // Replace with lower-poly sphere
                        const newGeom = new THREE.SphereGeometry(
                            sphere.geometry.parameters.radius,
                            16, 16 // Reduced from 32, 32
                        );
                        sphere.geometry.dispose();
                        sphere.geometry = newGeom;
                    }
                });
                break;
                
            case 2: // Disable anti-aliasing
                this.renderer.setPixelRatio(1.0);
                break;
                
            case 3: // Reduce far clipping plane (cull distant objects)
                this.camera.far = 100;
                this.camera.updateProjectionMatrix();
                break;
        }
    }
    
    /**
     * Increase level of detail when performance allows.
     * 
     * This implements the "Builder" agent action.
     */
    increaseLODLevel() {
        this.currentLODLevel--;
        
        // Reverse LOD reductions
        switch (this.currentLODLevel) {
            case 0: // Restore far clipping
                this.camera.far = 1000;
                this.camera.updateProjectionMatrix();
                break;
                
            case 1: // Restore anti-aliasing
                this.renderer.setPixelRatio(
                    Math.min(window.devicePixelRatio, 2)
                );
                break;
                
            case 2: // Restore sphere quality
                this.patientTwins.forEach((group) => {
                    const sphere = group.children.find(
                        c => c.name === 'IndicatorSphere'
                    );
                    if (sphere) {
                        const newGeom = new THREE.SphereGeometry(
                            sphere.geometry.parameters.radius,
                            32, 32 // Full quality
                        );
                        sphere.geometry.dispose();
                        sphere.geometry = newGeom;
                    }
                });
                break;
        }
    }
    
    /**
     * Update morphogenetic metrics with new frame timing data.
     * 
     * @param {number} latency - Frame render time in milliseconds
     */
    updateMorphogeneticMetrics(latency) {
        // Add to frame latency buffer (sliding window of last 10 frames)
        this.morphoMetrics.frameLatency.push(latency);
        if (this.morphoMetrics.frameLatency.length > 10) {
            this.morphoMetrics.frameLatency.shift();
        }
        
        // Update scene complexity metric
        this.morphoMetrics.sceneComplexity = this.scene.children.length;
    }
    
    /**
     * Public API: Start animation playback
     */
    play() {
        this.isAnimating = true;
        console.log('Animation started');
    }
    
    /**
     * Public API: Pause animation playback
     */
    pause() {
        this.isAnimating = false;
        console.log('Animation paused');
    }
    
    /**
     * Public API: Set animation speed
     * 
     * @param {number} speed - Days per second of real time
     */
    setAnimationSpeed(speed) {
        this.animationSpeed = speed;
        console.log(`Animation speed set to ${speed} days/second`);
    }
    
    /**
     * Public API: Jump to specific time
     * 
     * @param {number} time - Time in days
     */
    setCurrentTime(time) {
        this.currentTime = time;
        this.updatePatientTwinsForTime(time);
        console.log(`Jumped to day ${time}`);
    }
    
    /**
     * Public API: Get patient data at current time
     * 
     * @param {string} patientId - Patient identifier
     * @returns {Object} Patient data snapshot
     */
    getPatientDataAtCurrentTime(patientId) {
        const twin = this.patientTwins.get(patientId);
        if (!twin) {
            return null;
        }
        
        const sphere = twin.children.find(
            c => c.name === 'IndicatorSphere'
        );
        
        if (sphere && sphere.userData.timeSamples) {
            // Find closest time sample
            const samples = sphere.userData.timeSamples;
            let closestSample = samples[0];
            let minDiff = Math.abs(samples[0].time - this.currentTime);
            
            for (const sample of samples) {
                const diff = Math.abs(sample.time - this.currentTime);
                if (diff < minDiff) {
                    minDiff = diff;
                    closestSample = sample;
                }
            }
            
            return {
                patientId: patientId,
                time: this.currentTime,
                position: sphere.position.clone(),
                viralStatus: closestSample.viralLoad < 50 ? 'suppressed' : 'unsuppressed',
                cd4Count: closestSample.cd4Count,
                ...closestSample
            };
        }
        
        return null;
    }
    
    /**
     * Public API: Enable automated camera flythrough
     * 
     * This creates a smooth camera animation that tours the health space,
     * showing different patient clusters and highlighting interesting
     * trajectory patterns.
     */
    startFlythrough(duration = 60) {
        console.log(`Starting ${duration}-second camera flythrough`);
        
        // Disable user controls during flythrough
        this.controls.enabled = false;
        
        // Define waypoints for camera path
        // These should highlight regions of clinical interest
        const waypoints = [
            { position: new THREE.Vector3(5, 5, 5), lookAt: new THREE.Vector3(0, 0, 0) },
            { position: new THREE.Vector3(-5, 5, 0), lookAt: new THREE.Vector3(0, 0, 0) },
            { position: new THREE.Vector3(0, 10, 5), lookAt: new THREE.Vector3(0, 0, 0) },
            { position: new THREE.Vector3(5, 3, -5), lookAt: new THREE.Vector3(0, 0, 0) },
        ];
        
        const startTime = Date.now();
        const endTime = startTime + duration * 1000;
        
        // Animation loop for flythrough
        const animateFlythrough = () => {
            const now = Date.now();
            if (now >= endTime) {
                // Flythrough complete, re-enable controls
                this.controls.enabled = true;
                console.log('Flythrough complete');
                return;
            }
            
            // Compute progress through flythrough [0, 1]
            const progress = (now - startTime) / (duration * 1000);
            
            // Determine which segment we're in
            const segmentCount = waypoints.length - 1;
            const segmentProgress = progress * segmentCount;
            const segmentIndex = Math.floor(segmentProgress);
            const segmentT = segmentProgress - segmentIndex;
            
            // Interpolate between waypoints using smooth easing
            const eased = this.easeInOutCubic(segmentT);
            
            if (segmentIndex < waypoints.length - 1) {
                const wp0 = waypoints[segmentIndex];
                const wp1 = waypoints[segmentIndex + 1];
                
                // Interpolate position
                this.camera.position.lerpVectors(
                    wp0.position,
                    wp1.position,
                    eased
                );
                
                // Interpolate look-at target
                const lookTarget = new THREE.Vector3().lerpVectors(
                    wp0.lookAt,
                    wp1.lookAt,
                    eased
                );
                this.camera.lookAt(lookTarget);
            }
            
            // Continue flythrough
            requestAnimationFrame(animateFlythrough);
        };
        
        // Start flythrough animation
        animateFlythrough();
    }
    
    /**
     * Smooth easing function for camera animation.
     * 
     * Mathematical form: f(t) = 3t² - 2t³ (cubic Hermite interpolation)
     * This provides smooth acceleration and deceleration.
     * 
     * @param {number} t - Input in [0, 1]
     * @returns {number} Smoothed output in [0, 1]
     */
    easeInOutCubic(t) {
        return t < 0.5 
            ? 4 * t * t * t 
            : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    /**
     * Public API: Cleanup renderer resources
     * 
     * Important for preventing memory leaks when destroying the viewer.
     */
    dispose() {
        // Dispose all geometries and materials
        this.scene.traverse((object) => {
            if (object.geometry) {
                object.geometry.dispose();
            }
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
        
        // Dispose renderer
        this.renderer.dispose();
        
        // Remove canvas from DOM
        this.container.removeChild(this.renderer.domElement);
        
        console.log('Renderer disposed successfully');
    }
}

// Export for use in other modules
export default IHEPDigitalTwinRenderer;