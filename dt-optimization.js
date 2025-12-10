// Optimized three.js Digital Twin Renderer
class OptimizedDigitalTwinRenderer {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: false,  // Disable for mobile performance
            powerPreference: "high-performance"
        });
        
        // Performance optimizations
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));  // Cap pixel ratio
        this.renderer.shadowMap.enabled = false;  // Disable shadows for PHI viewers (not critical)
        
        // Instanced rendering setup
        this.instancedMeshes = new Map();
        
        // LOD management
        this.lodLevels = {
            high: 10,    // Within 10 units
            medium: 50,  // 10-50 units
            low: 100     // 50-100 units
        };
        
        // Performance monitoring
        this.stats = {
            frameTime: 0,
            drawCalls: 0,
            triangles: 0
        };
    }
    
    // Instanced Rendering: Draw N identical objects with 1 draw call
    createInstancedMesh(geometry, material, count) {
        const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
        
        // Set up instance matrices
        const dummy = new THREE.Object3D();
        for (let i = 0; i < count; i++) {
            dummy.position.set(
                Math.random() * 20 - 10,
                Math.random() * 20 - 10,
                Math.random() * 20 - 10
            );
            dummy.updateMatrix();
            instancedMesh.setMatrixAt(i, dummy.matrix);
        }
        
        instancedMesh.instanceMatrix.needsUpdate = true;
        this.scene.add(instancedMesh);
        
        return instancedMesh;
    }
    
    // LOD System: Reduce geometry complexity at distance
    createLODMesh(geometries, material, position) {
        const lod = new THREE.LOD();
        
        // High detail (close)
        const highDetail = new THREE.Mesh(geometries.high, material);
        lod.addLevel(highDetail, 0);
        
        // Medium detail
        const mediumDetail = new THREE.Mesh(geometries.medium, material);
        lod.addLevel(mediumDetail, this.lodLevels.medium);
        
        // Low detail (far)
        const lowDetail = new THREE.Mesh(geometries.low, material);
        lod.addLevel(lowDetail, this.lodLevels.low);
        
        lod.position.copy(position);
        this.scene.add(lod);
        
        return lod;
    }
    
    // Texture Atlasing: Combine multiple textures into single texture
    createTextureAtlas(texturePaths) {
        const canvas = document.createElement('canvas');
        canvas.width = 2048;
        canvas.height = 2048;
        const ctx = canvas.getContext('2d');
        
        // Load and composite textures
        const texturePromises = texturePaths.map((path, index) => {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    const x = (index % 4) * 512;
                    const y = Math.floor(index / 4) * 512;
                    ctx.drawImage(img, x, y, 512, 512);
                    resolve({ x, y, index });
                };
                img.src = path;
            });
        });
        
        return Promise.all(texturePromises).then(() => {
            const texture = new THREE.CanvasTexture(canvas);
            texture.needsUpdate = true;
            return texture;
        });
    }
    
    // Optimized render loop
    animate() {
        const startTime = performance.now();
        
        requestAnimationFrame(() => this.animate());
        
        // Update LOD based on camera position
        this.scene.traverse((object) => {
            if (object.isLOD) {
                object.update(this.camera);
            }
        });
        
        this.renderer.render(this.scene, this.camera);
        
        // Performance metrics
        const endTime = performance.now();
        this.stats.frameTime = endTime - startTime;
        this.stats.drawCalls = this.renderer.info.render.calls;
        this.stats.triangles = this.renderer.info.render.triangles;
        
        // Alert if frame budget exceeded
        if (this.stats.frameTime > 16.67) {
            console.warn(`Frame budget exceeded: ${this.stats.frameTime.toFixed(2)}ms`);
        }
    }
    
    // Performance report
    getPerformanceMetrics() {
        return {
            fps: 1000 / this.stats.frameTime,
            frameTime: this.stats.frameTime,
            drawCalls: this.stats.drawCalls,
            triangles: this.stats.triangles
        };
    }
}

// IHEP Digital Twin Implementation
const twinRenderer = new OptimizedDigitalTwinRenderer();

// Create instanced cell visualizations (instead of individual meshes)
const cellGeometry = new THREE.SphereGeometry(0.1, 8, 8);  // Low poly for instancing
const cellMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const cells = twinRenderer.createInstancedMesh(cellGeometry, cellMaterial, 10000);

// Performance monitoring
setInterval(() => {
    const metrics = twinRenderer.getPerformanceMetrics();
    console.log(`FPS: ${metrics.fps.toFixed(1)} | Frame Time: ${metrics.frameTime.toFixed(2)}ms | Draw Calls: ${metrics.drawCalls}`);
}, 1000);

twinRenderer.animate();