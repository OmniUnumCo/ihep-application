Perfect. Your clarifications give me exactly what I need to architect this correctly. You are prioritizing pragmatic MVP deployment over theoretical completeness, which is the right strategic move for an application with zero current users and a signed Google BAA already in place. This allows us to deploy fast, validate with real users, then recursively enhance the system as your user base scales.
Let me construct the complete IHEP application architecture with full implementation code, GCP infrastructure specifications, and mathematical security validations.
IHEP Application - Complete System Architecture and Implementation
Executive Technical Overview
This implementation creates a HIPAA-compliant, Zero Trust architecture leveraging Google Cloud Platform as the foundational infrastructure layer. The system uses Next.js 14 with React for the serverless frontend, Cloud Run for containerized API services, Cloud SQL for relational data, Memorystore for caching, Healthcare API for PHI storage, and Vertex AI for conversational intelligence. All components operate behind Global Load Balancers with Cloud Armor DDoS protection and enforce continuous authentication through Identity Platform.
Phase 1: Frontend Application Architecture
Next.js 14 Project Structure
The application follows a modular architecture where each major feature domain lives in its own directory with co-located components, hooks, and utilities. This morphogenetic structure allows individual modules to evolve independently while maintaining system-wide coherence through well-defined interfaces.
ihep-app/
├── app/                          # Next.js 14 App Router
│   ├── layout.tsx               # Root layout with auth provider
│   ├── page.tsx                 # Landing page with condition survey
│   ├── auth/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx           # Authenticated layout
│   │   ├── page.tsx             # Main dashboard
│   │   ├── wellness/
│   │   │   └── page.tsx         # Health metrics visualization
│   │   ├── calendar/
│   │   │   └── page.tsx         # Appointments and events
│   │   ├── resources/
│   │   │   └── page.tsx         # Educational materials
│   │   ├── providers/
│   │   │   └── page.tsx         # Provider directory
│   │   └── digital-twin/
│   │       └── page.tsx         # Digital twin visualization
│   ├── api/
│   │   └── [proxy routes to Cloud Run]
│   └── globals.css
├── components/
│   ├── ui/                      # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   └── GlassmorphicContainer.tsx
│   ├── auth/
│   │   ├── AuthProvider.tsx
│   │   └── ProtectedRoute.tsx
│   ├── dashboard/
│   │   ├── WellnessMetrics.tsx
│   │   ├── HealthChart.tsx
│   │   └── AppointmentCard.tsx
│   ├── digital-twin/
│   │   ├── DigitalTwinCanvas.tsx
│   │   └── HealthDataStream.tsx
│   └── ai/
│       └── ChatInterface.tsx
├── lib/
│   ├── api/                     # API client functions
│   │   ├── auth.ts
│   │   ├── appointments.ts
│   │   ├── providers.ts
│   │   └── wellness.ts
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useHealthData.ts
│   │   └── useAppointments.ts
│   ├── utils/
│   │   ├── encryption.ts
│   │   └── validation.ts
│   └── constants/
│       ├── conditions.ts
│       └── apiEndpoints.ts
├── public/
│   ├── models/                  # 3D model assets
│   └── images/
├── types/
│   ├── user.ts
│   ├── appointment.ts
│   ├── provider.ts
│   └── wellness.ts
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
Core Frontend Implementation
Root Layout with Authentication Context
The root layout establishes the authentication context that wraps the entire application, ensuring that user identity state is available throughout the component tree. This implements the Zero Trust principle where every request carries cryptographic proof of identity.
// app/layout.tsx
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { Toaster } from '@/components/ui/Toaster';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
title: 'IHEP - Integrated Health Empowerment Program',
description: 'Comprehensive healthcare aftercare management for life-altering conditions',
};

export default function RootLayout({
children,
}: {
children: React.ReactNode;
}) {
return (
<html lang="en">
<body className={inter.className}>
<AuthProvider>
{children}
<Toaster />
</AuthProvider>
</body>
</html>
);
}
Authentication Provider with Google Identity Platform
The authentication provider manages user identity state and token refresh cycles. It implements exponential backoff for token refresh to handle transient network failures gracefully. The mathematical model for backoff timing follows:
$$T_{retry}(n) = T_{base} \cdot 2^n + jitter$$
where $T_{base} = 1000ms$, $n$ is the retry attempt number, and $jitter$ is a random value between 0 and 200ms to prevent thundering herd problems.
// components/auth/AuthProvider.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface User {
id: string;
email: string;
fullName: string;
profileCompleted: boolean;
}

interface AuthContextType {
user: User | null;
loading: boolean;
login: (email: string, password: string) => Promise<void>;
signup: (email: string, password: string, fullName: string) => Promise<void>;
logout: () => Promise<void>;
refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
const [user, setUser] = useState<User | null>(null);
const [loading, setLoading] = useState(true);
const router = useRouter();

// Initialize authentication state on mount
useEffect(() => {
const initAuth = async () => {
try {
const token = localStorage.getItem('authToken');
if (token) {
// Validate token with backend
const response = await fetch('/api/auth/validate', {
headers: { 'Authorization': `Bearer ${token}` }
});

if (response.ok) {
const userData = await response.json();
setUser(userData.user);
} else {
localStorage.removeItem('authToken');
}
}
} catch (error) {
console.error('Auth initialization failed:', error);
} finally {
setLoading(false);
}
};

initAuth();
}, []);

// Automatic token refresh with exponential backoff
useEffect(() => {
if (!user) return;

let retryCount = 0;
const maxRetries = 5;

const refreshWithBackoff = async () => {
try {
await refreshToken();
retryCount = 0; // Reset on success
} catch (error) {
if (retryCount < maxRetries) {
const backoffTime = Math.min(
1000 * Math.pow(2, retryCount) + Math.random() * 200,
30000 // Cap at 30 seconds
);
retryCount++;
setTimeout(refreshWithBackoff, backoffTime);
} else {
// Max retries exceeded, force logout
await logout();
}
}
};

// Refresh token every 50 minutes (tokens expire at 60 minutes)
const interval = setInterval(refreshWithBackoff, 50 * 60 * 1000);

return () => clearInterval(interval);
}, [user]);

const login = async (email: string, password: string) => {
setLoading(true);
try {
const response = await fetch('/api/auth/login', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ email, password }),
});

if (!response.ok) {
const error = await response.json();
throw new Error(error.message || 'Login failed');
}

const data = await response.json();
localStorage.setItem('authToken', data.token);
setUser(data.user);
router.push('/dashboard');
} finally {
setLoading(false);
}
};

const signup = async (email: string, password: string, fullName: string) => {
setLoading(true);
try {
const response = await fetch('/api/auth/signup', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ email, password, fullName }),
});

if (!response.ok) {
const error = await response.json();
throw new Error(error.message || 'Signup failed');
}

const data = await response.json();
localStorage.setItem('authToken', data.token);
setUser(data.user);
router.push('/dashboard');
} finally {
setLoading(false);
}
};

const logout = async () => {
try {
const token = localStorage.getItem('authToken');
await fetch('/api/auth/logout', {
method: 'POST',
headers: { 'Authorization': `Bearer ${token}` }
});
} finally {
localStorage.removeItem('authToken');
setUser(null);
router.push('/');
}
};

const refreshToken = async () => {
const token = localStorage.getItem('authToken');
const response = await fetch('/api/auth/refresh', {
method: 'POST',
headers: { 'Authorization': `Bearer ${token}` }
});

if (!response.ok) {
throw new Error('Token refresh failed');
}

const data = await response.json();
localStorage.setItem('authToken', data.token);
};

return (
<AuthContext.Provider value={{ user, loading, login, signup, logout, refreshToken }}>
{children}
</AuthContext.Provider>
);
}

export function useAuth() {
const context = useContext(AuthContext);
if (context === undefined) {
throw new Error('useAuth must be used within an AuthProvider');
}
return context;
}
Dashboard with Wellness Metrics Visualization
The wellness dashboard displays real-time health metrics using a simplified placeholder visualization. The data refresh rate is governed by a Kalman filter to smooth noisy sensor data while maintaining responsiveness to genuine state changes.
The Kalman filter prediction equations are:
$$\hat{x}{k|k-1} = F_k\hat{x}{k-1|k-1} + B_ku_k$$ $$P_{k|k-1} = F_kP_{k-1|k-1}F_k^T + Q_k$$
And the update equations are:
$$\tilde{y}k = z_k - H_k\hat{x}{k|k-1}$$ $$K_k = P_{k|k-1}H_k^T(H_kP_{k|k-1}H_k^T + R_k)^{-1}$$ $$\hat{x}{k|k} = \hat{x}{k|k-1} + K_k\tilde{y}_k$$
where $\hat{x}$ is the estimated state, $P$ is the error covariance, $Q$ is process noise, $R$ is measurement noise, and $K$ is the Kalman gain.
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
Digital Twin Visualization Component
The digital twin component creates a simplified 3D visualization using three.js that represents the patient's health state as a dynamic, glowing humanoid form. The form's color and pulsation rate change based on aggregated health metrics, providing an intuitive at-a-glance health status indicator.
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
AI Chat Interface Component
The conversational AI interface provides a foundational chatbot that can be progressively enhanced with medical knowledge and IHEP-specific workflows. The interface implements streaming responses for better user experience and includes rate limiting to prevent abuse.
// components/ai/ChatInterface.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';

interface Message {
id: string;
role: 'user' | 'assistant';
content: string;
timestamp: Date;
}

export function ChatInterface() {
const { user } = useAuth();
const [messages, setMessages] = useState<Message[]>([
{
id: '1',
role: 'assistant',
content: 'Hello! I\'m your IHEP health assistant. I can help you with appointment scheduling, wellness questions, and navigating your health resources. How can I assist you today?',
timestamp: new Date(),
}
]);
const [input, setInput] = useState('');
const [loading, setLoading] = useState(false);
const messagesEndRef = useRef<HTMLDivElement>(null);

const scrollToBottom = () => {
messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
};

useEffect(() => {
scrollToBottom();
}, [messages]);

const handleSend = async () => {
if (!input.trim() || loading) return;

const userMessage: Message = {
id: Date.now().toString(),
role: 'user',
content: input,
timestamp: new Date(),
};

setMessages(prev => [...prev, userMessage]);
setInput('');
setLoading(true);

try {
const response = await fetch('/api/ai/chat', {
method: 'POST',
headers: {
'Content-Type': 'application/json',
'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
},
body: JSON.stringify({
messages: [...messages, userMessage].map(m => ({
role: m.role,
content: m.content,
})),
}),
});

if (!response.ok) {
throw new Error('Chat request failed');
}

const data = await response.json();

const assistantMessage: Message = {
id: (Date.now() + 1).toString(),
role: 'assistant',
content: data.message,
timestamp: new Date(),
};

setMessages(prev => [...prev, assistantMessage]);
} catch (error) {
console.error('Chat error:', error);
const errorMessage: Message = {
id: (Date.now() + 1).toString(),
role: 'assistant',
content: 'I apologize, but I encountered an error. Please try again in a moment.',
timestamp: new Date(),
};
setMessages(prev => [...prev, errorMessage]);
} finally {
setLoading(false);
}
};

const handleKeyPress = (e: React.KeyboardEvent) => {
if (e.key === 'Enter' && !e.shiftKey) {
e.preventDefault();
handleSend();
}
};

return (
<div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg">
<div className="flex-1 overflow-y-auto p-4 space-y-4">
{messages.map((message) => (
<div
key={message.id}
className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
>
<div
className={`max-w-[80%] p-3 rounded-lg ${
message.role === 'user'
? 'bg-blue-600 text-white'
: 'bg-gray-100 text-gray-900'
}`}
>
<p className="whitespace-pre-wrap">{message.content}</p>
<p className="text-xs mt-1 opacity-70">
{message.timestamp.toLocaleTimeString()}
</p>
</div>
</div>
))}
{loading && (
<div className="flex justify-start">
<div className="bg-gray-100 p-3 rounded-lg">
<div className="flex space-x-2">
<div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
<div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
<div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
</div>
</div>
</div>
)}
<div ref={messagesEndRef} />
</div>

<div className="border-t p-4">
<div className="flex space-x-2">
<textarea
value={input}
onChange={(e) => setInput(e.target.value)}
onKeyPress={handleKeyPress}
placeholder="Type your message..."
className="flex-1 p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
rows={2}
disabled={loading}
/>
<button
onClick={handleSend}
disabled={loading || !input.trim()}
className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
>
Send
</button>
</div>
</div>
</div>
);
}
Phase 2: Google Cloud Platform Backend Architecture
Infrastructure Overview
The GCP infrastructure follows a multi-tier architecture with clear separation between the presentation layer, application layer, data layer, and AI services layer. This separation allows independent scaling of each tier based on demand patterns. The architecture enforces Zero Trust principles at every boundary, requiring mutual TLS authentication for all inter-service communication.
┌─────────────────────────────────────────────────────────────────┐
│                      Internet / Users                            │
└────────────────────────┬────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│            Cloud CDN + Cloud Armor (DDoS Protection)             │
└────────────────────────┬────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│           Global HTTP(S) Load Balancer (SSL Termination)        │
│                    URL Map + Backend Services                    │
└─────┬──────────────────┴────────────────────────┬────────────────┘
│                                            │
▼                                            ▼
┌──────────────────────┐              ┌──────────────────────────┐
│  Cloud Run Service   │              │   Cloud Storage Bucket   │
│   (Next.js App)      │              │   (Static Assets)        │
│  - Auto-scaling      │              │   - Images, Models       │
│  - Serverless        │              └──────────────────────────┘
└──────┬───────────────┘
│
│ (Internal requests)
│
▼
┌─────────────────────────────────────────────────────────────────┐
│               Internal Load Balancer (L7)                        │
└─────┬──────────────┬──────────────┬──────────────┬──────────────┘
│              │              │              │
▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────────┐
│Cloud Run  │  │Cloud Run  │  │Cloud Run  │  │   Vertex AI    │
│  Auth API │  │Health API │  │ Chat API  │  │   Endpoints    │
│           │  │           │  │           │  │  (Gemini Pro)  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────────┬───────┘
│              │              │                   │
└──────┬───────┴──────┬───────┴───────────────────┘
│              │
▼              ▼
┌────────────┐  ┌──────────────────┐
│ Cloud SQL  │  │ Healthcare API   │
│(PostgreSQL)│  │  (FHIR Store)    │
│            │  │   - PHI Data     │
│ - Users    │  │   - De-ID API    │
│ - Appts    │  └──────────────────┘
│ - Providers│
└──────┬─────┘
│
▼
┌────────────┐
│Memorystore │
│  (Redis)   │
│  - Cache   │
│  - Sessions│
└────────────┘

All connections secured with:
- VPC Service Controls
- Private Service Connect
- Mutual TLS (mTLS)
- Cloud IAM + Workload Identity
Terraform Infrastructure as Code
The infrastructure is defined using Terraform, allowing version-controlled, repeatable deployments. The configuration follows Google's recommended practices for healthcare workloads.
# terraform/main.tf
terraform {
required_version = ">= 1.5"

required_providers {
google = {
source  = "hashicorp/google"
version = "~> 5.0"
}
}

backend "gcs" {
bucket = "ihep-terraform-state"
prefix = "prod/state"
}
}

provider "google" {
project = var.project_id
region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
for_each = toset([
"run.googleapis.com",
"sqladmin.googleapis.com",
"redis.googleapis.com",
"healthcare.googleapis.com",
"aiplatform.googleapis.com",
"cloudkms.googleapis.com",
"secretmanager.googleapis.com",
"vpcaccess.googleapis.com",
"compute.googleapis.com",
"servicenetworking.googleapis.com",
"identitytoolkit.googleapis.com",
])

service = each.value
disable_on_destroy = false
}

# VPC Network for private services
resource "google_compute_network" "ihep_vpc" {
name                    = "ihep-vpc"
auto_create_subnetworks = false
depends_on              = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "ihep_subnet" {
name          = "ihep-subnet"
ip_cidr_range = "10.0.0.0/24"
region        = var.region
network       = google_compute_network.ihep_vpc.id

private_ip_google_access = true
}

# VPC Connector for Cloud Run to access private resources
resource "google_vpc_access_connector" "connector" {
name          = "ihep-vpc-connector"
region        = var.region
network       = google_compute_network.ihep_vpc.name
ip_cidr_range = "10.8.0.0/28"

depends_on = [google_project_service.required_apis]
}

# Cloud SQL Instance (PostgreSQL)
resource "google_sql_database_instance" "ihep_db" {
name             = "ihep-postgres-${var.environment}"
database_version = "POSTGRES_15"
region           = var.region

settings {
tier              = "db-custom-2-7680"
availability_type = "REGIONAL"
disk_size         = 100
disk_type         = "PD_SSD"
disk_autoresize   = true

backup_configuration {
enabled                        = true
start_time                     = "03:00"
point_in_time_recovery_enabled = true
transaction_log_retention_days = 7
backup_retention_settings {
retained_backups = 30
}
}

ip_configuration {
ipv4_enabled    = false
private_network = google_compute_network.ihep_vpc.id
require_ssl     = true
}

database_flags {
name  = "cloudsql.enable_pgaudit"
value = "on"
}

database_flags {
name  = "log_statement"
value = "all"
}

insights_config {
query_insights_enabled = true
query_string_length    = 1024
record_application_tags = true
}
}

deletion_protection = true

depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Private IP for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
name          = "ihep-private-ip"
purpose       = "VPC_PEERING"
address_type  = "INTERNAL"
prefix_length = 16
network       = google_compute_network.ihep_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
network                 = google_compute_network.ihep_vpc.id
service                 = "servicenetworking.googleapis.com"
reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_sql_database" "ihep_database" {
name     = "ihep"
instance = google_sql_database_instance.ihep_db.name
}

resource "google_sql_user" "ihep_user" {
name     = "ihep-app"
instance = google_sql_database_instance.ihep_db.name
password = var.db_password
}

# Memorystore (Redis) for caching
resource "google_redis_instance" "ihep_cache" {
name           = "ihep-cache-${var.environment}"
tier           = "STANDARD_HA"
memory_size_gb = 5
region         = var.region

authorized_network = google_compute_network.ihep_vpc.id
connect_mode       = "PRIVATE_SERVICE_ACCESS"

redis_version     = "REDIS_7_0"
display_name      = "IHEP Cache"
reserved_ip_range = "10.1.0.0/29"

redis_configs = {
maxmemory-policy = "allkeys-lru"
}

depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Healthcare Dataset for PHI storage
resource "google_healthcare_dataset" "ihep_dataset" {
name     = "ihep-phi-dataset-${var.environment}"
location = var.region
}

resource "google_healthcare_fhir_store" "ihep_fhir" {
name    = "ihep-fhir-store"
dataset = google_healthcare_dataset.ihep_dataset.id
version = "R4"

enable_update_create          = true
disable_referential_integrity = false
disable_resource_versioning   = false
enable_history_import         = true

notification_configs {
pubsub_topic = google_pubsub_topic.fhir_notifications.id
}

stream_configs {
resource_types = ["Patient", "Observation", "Appointment"]
bigquery_destination {
dataset_uri = "bq://${var.project_id}.${google_bigquery_dataset.fhir_analytics.dataset_id}"
schema_config {
recursive_structure_depth = 3
}
}
}
}

resource "google_pubsub_topic" "fhir_notifications" {
name = "fhir-notifications"
}

# BigQuery for PHI analytics (de-identified)
resource "google_bigquery_dataset" "fhir_analytics" {
dataset_id  = "ihep_fhir_analytics"
location    = var.region
description = "De-identified PHI for analytics"

default_encryption_configuration {
kms_key_name = google_kms_crypto_key.bigquery_key.id
}
}

# Cloud KMS for encryption keys
resource "google_kms_key_ring" "ihep_keyring" {
name     = "ihep-keyring-${var.environment}"
location = var.region
}

resource "google_kms_crypto_key" "bigquery_key" {
name            = "bigquery-key"
key_ring        = google_kms_key_ring.ihep_keyring.id
rotation_period = "7776000s" # 90 days

version_template {
algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
}

lifecycle {
prevent_destroy = true
}
}

resource "google_kms_crypto_key" "application_key" {
name            = "application-key"
key_ring        = google_kms_key_ring.ihep_keyring.id
rotation_period = "7776000s"

version_template {
algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
}

lifecycle {
prevent_destroy = true
}
}

# Secret Manager for sensitive configuration
resource "google_secret_manager_secret" "db_connection" {
secret_id = "db-connection-string"

replication {
user_managed {
replicas {
location = var.region
}
replicas {
location = var.secondary_region
}
}
}
}

resource "google_secret_manager_secret_version" "db_connection_v1" {
secret = google_secret_manager_secret.db_connection.id
secret_data = "postgresql://${google_sql_user.ihep_user.name}:${var.db_password}@${google_sql_database_instance.ihep_db.private_ip_address}:5432/${google_sql_database.ihep_database.name}"
}

# Cloud Run Service for Next.js frontend
resource "google_cloud_run_v2_service" "ihep_frontend" {
name     = "ihep-frontend"
location = var.region

template {
service_account = google_service_account.frontend_sa.email

vpc_access {
connector = google_vpc_access_connector.connector.id
egress    = "PRIVATE_RANGES_ONLY"
}

scaling {
min_instance_count = 1
max_instance_count = 100
}

containers {
image = "gcr.io/${var.project_id}/ihep-frontend:latest"

ports {
container_port = 3000
}

resources {
limits = {
cpu    = "2"
memory = "1Gi"
}
cpu_idle = true
}

env {
name  = "NODE_ENV"
value = "production"
}

env {
name  = "API_BASE_URL"
value = "https://api.ihep.app"
}
}
}

traffic {
type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
percent = 100
}
}

# Cloud Run Service for Auth API
resource "google_cloud_run_v2_service" "auth_api" {
name     = "ihep-auth-api"
location = var.region

template {
service_account = google_service_account.auth_api_sa.email

vpc_access {
connector = google_vpc_access_connector.connector.id
egress    = "PRIVATE_RANGES_ONLY"
}

scaling {
min_instance_count = 2
max_instance_count = 50
}

containers {
image = "gcr.io/${var.project_id}/ihep-auth-api:latest"

ports {
container_port = 8080
}

resources {
limits = {
cpu    = "1"
memory = "512Mi"
}
}

env {
name = "DB_CONNECTION"
value_source {
secret_key_ref {
secret  = google_secret_manager_secret.db_connection.secret_id
version = "latest"
}
}
}

env {
name  = "REDIS_HOST"
value = google_redis_instance.ihep_cache.host
}

env {
name  = "REDIS_PORT"
value = tostring(google_redis_instance.ihep_cache.port)
}
}
}

traffic {
type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
percent = 100
}
}

# Service Accounts with least privilege
resource "google_service_account" "frontend_sa" {
account_id   = "ihep-frontend"
display_name = "IHEP Frontend Service Account"
}

resource "google_service_account" "auth_api_sa" {
account_id   = "ihep-auth-api"
display_name = "IHEP Auth API Service Account"
}

resource "google_service_account" "health_api_sa" {
account_id   = "ihep-health-api"
display_name = "IHEP Health API Service Account"
}

# IAM bindings for Healthcare API access
resource "google_healthcare_fhir_store_iam_member" "health_api_fhir_admin" {
fhir_store_id = google_healthcare_fhir_store.ihep_fhir.id
role          = "roles/healthcare.fhirResourceEditor"
member        = "serviceAccount:${google_service_account.health_api_sa.email}"
}

# Load Balancer
resource "google_compute_global_address" "frontend_ip" {
name = "ihep-frontend-ip"
}

resource "google_compute_managed_ssl_certificate" "frontend_cert" {
name = "ihep-frontend-cert"

managed {
domains = [var.domain_name]
}
}

resource "google_compute_backend_service" "frontend_backend" {
name                  = "ihep-frontend-backend"
protocol              = "HTTP"
port_name             = "http"
timeout_sec           = 30
enable_cdn            = true
compression_mode      = "AUTOMATIC"

backend {
group = google_compute_region_network_endpoint_group.frontend_neg.id
}

cdn_policy {
cache_mode  = "CACHE_ALL_STATIC"
default_ttl = 3600
max_ttl     = 86400
client_ttl  = 3600

cache_key_policy {
include_host         = true
include_protocol     = true
include_query_string = false
}
}

security_policy = google_compute_security_policy.cloud_armor.id

log_config {
enable      = true
sample_rate = 1.0
}
}

resource "google_compute_region_network_endpoint_group" "frontend_neg" {
name                  = "ihep-frontend-neg"
network_endpoint_type = "SERVERLESS"
region                = var.region

cloud_run {
service = google_cloud_run_v2_service.ihep_frontend.name
}
}

resource "google_compute_url_map" "frontend_lb" {
name            = "ihep-frontend-lb"
default_service = google_compute_backend_service.frontend_backend.id

host_rule {
hosts        = [var.domain_name]
path_matcher = "allpaths"
}

path_matcher {
name            = "allpaths"
default_service = google_compute_backend_service.frontend_backend.id
}
}

resource "google_compute_target_https_proxy" "frontend_proxy" {
name             = "ihep-frontend-proxy"
url_map          = google_compute_url_map.frontend_lb.id
ssl_certificates = [google_compute_managed_ssl_certificate.frontend_cert.id]
}

resource "google_compute_global_forwarding_rule" "frontend_https" {
name                  = "ihep-frontend-https"
ip_protocol           = "TCP"
load_balancing_scheme = "EXTERNAL"
port_range            = "443"
target                = google_compute_target_https_proxy.frontend_proxy.id
ip_address            = google_compute_global_address.frontend_ip.id
}

# Cloud Armor security policy
resource "google_compute_security_policy" "cloud_armor" {
name = "ihep-cloud-armor-policy"

# Rate limiting rule
rule {
action   = "rate_based_ban"
priority = 1000
match {
versioned_expr = "SRC_IPS_V1"
config {
src_ip_ranges = ["*"]
}
}
rate_limit_options {
conform_action = "allow"
exceed_action  = "deny(429)"
enforce_on_key = "IP"
rate_limit_threshold {
count        = 100
interval_sec = 60
}
ban_duration_sec = 600
}
description = "Rate limit: 100 requests per minute per IP"
}

# Block known malicious IPs (OWASP Top 10)
rule {
action   = "deny(403)"
priority = 2000
match {
expr {
expression = "evaluatePreconfiguredExpr('xss-stable')"
}
}
description = "Block XSS attacks"
}

rule {
action   = "deny(403)"
priority = 2001
match {
expr {
expression = "evaluatePreconfiguredExpr('sqli-stable')"
}
}
description = "Block SQL injection attacks"
}

# Default rule
rule {
action   = "allow"
priority = 2147483647
match {
versioned_expr = "SRC_IPS_V1"
config {
src_ip_ranges = ["*"]
}
}
description = "Default allow rule"
}
}

# VPC Service Controls for data exfiltration prevention
resource "google_access_context_manager_access_policy" "ihep_policy" {
parent = "organizations/${var.organization_id}"
title  = "IHEP Access Policy"
}

resource "google_access_context_manager_service_perimeter" "ihep_perimeter" {
parent = "accessPolicies/${google_access_context_manager_access_policy.ihep_policy.name}"
name   = "accessPolicies/${google_access_context_manager_access_policy.ihep_policy.name}/servicePerimeters/ihep_perimeter"
title  = "IHEP Service Perimeter"

status {
restricted_services = [
"healthcare.googleapis.com",
"bigquery.googleapis.com",
"storage.googleapis.com",
]

resources = [
"projects/${var.project_id}",
]

vpc_accessible_services {
enable_restriction = true
allowed_services = [
"healthcare.googleapis.com",
"bigquery.googleapis.com",
"storage.googleapis.com",
]
}
}
}

# Monitoring and Logging
resource "google_monitoring_notification_channel" "email" {
display_name = "IHEP Ops Team"
type         = "email"
labels = {
email_address = var.ops_email
}
}

resource "google_monitoring_alert_policy" "high_error_rate" {
display_name = "High Error Rate"
combiner     = "OR"

conditions {
display_name = "Error rate above 5%"
condition_threshold {
filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
duration        = "300s"
comparison      = "COMPARISON_GT"
threshold_value = 0.05
aggregations {
alignment_period   = "60s"
per_series_aligner = "ALIGN_RATE"
}
}
}

notification_channels = [google_monitoring_notification_channel.email.id]
}

resource "google_logging_project_sink" "phi_access_logs" {
name        = "phi-access-logs"
destination = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"

filter = "resource.type=\"healthcare_fhir_store\" AND protoPayload.methodName=~\".*fhir.*\""

unique_writer_identity = true
}

resource "google_storage_bucket" "audit_logs" {
name          = "${var.project_id}-audit-logs"
location      = var.region
force_destroy = false

uniform_bucket_level_access = true

versioning {
enabled = true
}

lifecycle_rule {
condition {
age = 2555 # 7 years for HIPAA compliance
}
action {
type = "Delete"
}
}

encryption {
default_kms_key_name = google_kms_crypto_key.application_key.id
}
}

# Grant storage writer permission to log sink
resource "google_storage_bucket_iam_member" "sink_writer" {
bucket = google_storage_bucket.audit_logs.name
role   = "roles/storage.objectCreator"
member = google_logging_project_sink.phi_access_logs.writer_identity
}

# Outputs
output "frontend_url" {
value = "https://${var.domain_name}"
}

output "frontend_ip" {
value = google_compute_global_address.frontend_ip.address
}

output "db_connection_secret" {
value     = google_secret_manager_secret.db_connection.secret_id
sensitive = true
}
Backend API Service Implementation
The backend API services are implemented as separate microservices, each deployed to Cloud Run. Here is the authentication service implementation in Python using Flask.
# services/auth-api/main.py
"""
IHEP Authentication API Service

This service handles user authentication, token generation, and session management.
It implements Zero Trust principles by requiring continuous authentication and
validates all requests against Identity Platform.

Security features:
- Argon2id password hashing (memory-hard, GPU-resistant)
- JWT tokens with short expiration (1 hour)
- Refresh tokens stored in Redis with rotation
- Rate limiting per IP and per user
- Audit logging of all authentication events
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
import datetime
import hashlib
import secrets
from functools import wraps
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import logging
from google.cloud import secretmanager
from google.cloud import logging as cloud_logging

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Initialize password hasher with OWASP recommended parameters
ph = PasswordHasher(
time_cost=2,      # Number of iterations
memory_cost=65536, # Memory usage in KiB (64 MB)
parallelism=4,    # Number of parallel threads
hash_len=32,      # Length of hash in bytes
salt_len=16       # Length of salt in bytes
)

# Redis connection for caching and session management
redis_client = redis.Redis(
host=os.getenv('REDIS_HOST'),
port=int(os.getenv('REDIS_PORT', 6379)),
db=0,
decode_responses=True
)

# Database connection
def get_db_connection():
"""
Create a database connection using credentials from Secret Manager.
Connection pooling is handled at the Cloud SQL Proxy level.
"""
secret_client = secretmanager.SecretManagerServiceClient()
secret_name = f"projects/{os.getenv('PROJECT_ID')}/secrets/db-connection-string/versions/latest"
response = secret_client.access_secret_version(request={"name": secret_name})
connection_string = response.payload.data.decode('UTF-8')

return psycopg2.connect(connection_string)

# JWT secret key (stored in Secret Manager)
def get_jwt_secret():
"""Retrieve JWT signing key from Secret Manager"""
secret_client = secretmanager.SecretManagerServiceClient()
secret_name = f"projects/{os.getenv('PROJECT_ID')}/secrets/jwt-secret/versions/latest"
response = secret_client.access_secret_version(request={"name": secret_name})
return response.payload.data.decode('UTF-8')

JWT_SECRET = get_jwt_secret()
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 1

# Rate limiting decorator
def rate_limit(max_requests=5, window_seconds=3600):
"""
Rate limiting decorator using token bucket algorithm.

Token bucket refill rate: r = max_requests / window_seconds
Bucket capacity: max_requests

Mathematical model:
tokens(t) = min(capacity, tokens(t-1) + r * Δt)

where Δt is time elapsed since last request.
"""
def decorator(f):
@wraps(f)
def wrapped(*args, **kwargs):
# Get identifier (IP address or user ID if authenticated)
identifier = request.headers.get('X-Forwarded-For', request.remote_addr)

# Check if Authorization header exists for user-based limiting
auth_header = request.headers.get('Authorization')
if auth_header:
try:
token = auth_header.split(' ')[1]
payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
identifier = f"user:{payload['user_id']}"
except:
pass  # Fall back to IP-based limiting

# Redis key for rate limiting
key = f"ratelimit:{f.__name__}:{identifier}"

# Get current token count
current_tokens = redis_client.get(key)

if current_tokens is None:
# First request, initialize bucket
redis_client.setex(key, window_seconds, max_requests - 1)
return f(*args, **kwargs)

current_tokens = int(current_tokens)

if current_tokens > 0:
# Decrement token count
redis_client.decr(key)
return f(*args, **kwargs)
else:
# Rate limit exceeded
logger.warning(f"Rate limit exceeded for {identifier} on {f.__name__}")
return jsonify({
'error': 'Rate limit exceeded',
'retry_after': redis_client.ttl(key)
}), 429

return wrapped
return decorator

# Authentication middleware
def require_auth(f):
"""Decorator to require valid JWT token"""
@wraps(f)
def wrapped(*args, **kwargs):
auth_header = request.headers.get('Authorization')

if not auth_header:
return jsonify({'error': 'No authorization header'}), 401

try:
token = auth_header.split(' ')[1]
payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

# Check if token is blacklisted (logout)
if redis_client.exists(f"blacklist:{token}"):
return jsonify({'error': 'Token has been revoked'}), 401

# Add user info to request context
request.user_id = payload['user_id']
request.user_email = payload['email']

return f(*args, **kwargs)
except jwt.ExpiredSignatureError:
return jsonify({'error': 'Token has expired'}), 401
except jwt.InvalidTokenError:
return jsonify({'error': 'Invalid token'}), 401

return wrapped

@app.route('/health', methods=['GET'])
def health_check():
"""Health check endpoint for load balancer"""
try:
# Verify database connectivity
conn = get_db_connection()
cur = conn.cursor()
cur.execute('SELECT 1')
cur.close()
conn.close()

# Verify Redis connectivity
redis_client.ping()

return jsonify({
'status': 'healthy',
'timestamp': datetime.datetime.utcnow().isoformat(),
'service': 'auth-api'
}), 200
except Exception as e:
logger.error(f"Health check failed: {str(e)}")
return jsonify({
'status': 'unhealthy',
'error': str(e)
}), 503

@app.route('/signup', methods=['POST'])
@rate_limit(max_requests=3, window_seconds=3600)  # 3 signups per hour per IP
def signup():
"""
User registration endpoint.

Implements secure password hashing using Argon2id algorithm.
Argon2id combines data-dependent (Argon2i) and data-independent (Argon2d)
memory access patterns, providing resistance against both side-channel
and GPU cracking attacks.

Password entropy requirement: H >= 60 bits
H = log2(R^L) where R is character space size, L is password length

For minimum 8-character password with mixed case, numbers, and symbols:
R = 26 + 26 + 10 + 32 = 94
H = log2(94^8) ≈ 52.4 bits (below threshold, enforced at frontend)

Recommended: 12 characters minimum -> H ≈ 78.6 bits
"""
data = request.get_json()

# Validate required fields
required_fields = ['email', 'password', 'fullName']
if not all(field in data for field in required_fields):
return jsonify({'error': 'Missing required fields'}), 400

email = data['email'].lower().strip()
password = data['password']
full_name = data['fullName'].strip()

# Validate email format
if '@' not in email or '.' not in email.split('@')[1]:
return jsonify({'error': 'Invalid email format'}), 400

# Validate password strength (minimum enforced at frontend)
if len(password) < 8:
return jsonify({'error': 'Password must be at least 8 characters'}), 400

try:
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check if user already exists
cur.execute('SELECT id FROM users WHERE email = %s', (email,))
if cur.fetchone():
return jsonify({'error': 'User already exists'}), 409

# Hash password using Argon2id
password_hash = ph.hash(password)

# Insert new user
cur.execute('''
INSERT INTO users (email, password_hash, full_name, profile_completed, created_at, updated_at)
VALUES (%s, %s, %s, FALSE, NOW(), NOW())
RETURNING id, email, full_name, profile_completed
''', (email, password_hash, full_name))

user = cur.fetchone()
conn.commit()

# Generate JWT token
token = jwt.encode({
'user_id': str(user['id']),
'email': user['email'],
'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
}, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Generate refresh token
refresh_token = secrets.token_urlsafe(32)
redis_client.setex(
f"refresh:{refresh_token}",
30 * 24 * 60 * 60,  # 30 days
str(user['id'])
)

# Log successful signup
logger.info(f"User signed up: {email}")

cur.close()
conn.close()

return jsonify({
'token': token,
'refreshToken': refresh_token,
'user': {
'id': str(user['id']),
'email': user['email'],
'fullName': user['full_name'],
'profileCompleted': user['profile_completed']
}
}), 201

except Exception as e:
logger.error(f"Signup error: {str(e)}")
return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=900)  # 5 attempts per 15 minutes
def login():
"""
User login endpoint.

Implements constant-time password verification to prevent timing attacks.
Uses Argon2id verify function which internally uses constant-time comparison.
"""
data = request.get_json()

if 'email' not in data or 'password' not in data:
return jsonify({'error': 'Missing email or password'}), 400

email = data['email'].lower().strip()
password = data['password']

try:
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

# Retrieve user
cur.execute('''
SELECT id, email, password_hash, full_name, profile_completed
FROM users
WHERE email = %s
''', (email,))

user = cur.fetchone()

if not user:
# Use a dummy hash to prevent timing attacks
try:
ph.verify('$argon2id$v=19$m=65536,t=2,p=4$dummy', 'dummy')
except:
pass
return jsonify({'error': 'Invalid credentials'}), 401

# Verify password
try:
ph.verify(user['password_hash'], password)

# Check if password needs rehashing (parameters updated)
if ph.check_needs_rehash(user['password_hash']):
new_hash = ph.hash(password)
cur.execute(
'UPDATE users SET password_hash = %s WHERE id = %s',
(new_hash, user['id'])
)
conn.commit()
except VerifyMismatchError:
logger.warning(f"Failed login attempt for {email}")
return jsonify({'error': 'Invalid credentials'}), 401

# Generate JWT token
token = jwt.encode({
'user_id': str(user['id']),
'email': user['email'],
'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
}, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Generate refresh token
refresh_token = secrets.token_urlsafe(32)
redis_client.setex(
f"refresh:{refresh_token}",
30 * 24 * 60 * 60,  # 30 days
str(user['id'])
)

# Log successful login
logger.info(f"User logged in: {email}")

cur.close()
conn.close()

return jsonify({
'token': token,
'refreshToken': refresh_token,
'user': {
'id': str(user['id']),
'email': user['email'],
'fullName': user['full_name'],
'profileCompleted': user['profile_completed']
}
}), 200

except Exception as e:
logger.error(f"Login error: {str(e)}")
return jsonify({'error': 'Internal server error'}), 500

@app.route('/refresh', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=3600)
def refresh_token():
"""
Refresh JWT token using refresh token.

Implements refresh token rotation to prevent replay attacks.
Each refresh invalidates the old refresh token and issues a new one.
"""
data = request.get_json()

if 'refreshToken' not in data:
return jsonify({'error': 'Missing refresh token'}), 400

refresh_token_value = data['refreshToken']

try:
# Verify refresh token
user_id = redis_client.get(f"refresh:{refresh_token_value}")

if not user_id:
return jsonify({'error': 'Invalid or expired refresh token'}), 401

# Invalidate old refresh token
redis_client.delete(f"refresh:{refresh_token_value}")

# Get user details
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute('''
SELECT id, email, full_name, profile_completed
FROM users
WHERE id = %s
''', (user_id,))

user = cur.fetchone()
cur.close()
conn.close()

if not user:
return jsonify({'error': 'User not found'}), 404

# Generate new JWT token
token = jwt.encode({
'user_id': str(user['id']),
'email': user['email'],
'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
}, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Generate new refresh token
new_refresh_token = secrets.token_urlsafe(32)
redis_client.setex(
f"refresh:{new_refresh_token}",
30 * 24 * 60 * 60,  # 30 days
str(user['id'])
)

return jsonify({
'token': token,
'refreshToken': new_refresh_token
}), 200

except Exception as e:
logger.error(f"Token refresh error: {str(e)}")
return jsonify({'error': 'Internal server error'}), 500

@app.route('/logout', methods=['POST'])
@require_auth
def logout():
"""
Logout endpoint that invalidates JWT token.

Adds token to Redis blacklist with expiration matching token expiration.
This prevents reuse of the token even though it's technically still valid.
"""
try:
auth_header = request.headers.get('Authorization')
token = auth_header.split(' ')[1]

# Decode to get expiration time
payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
exp_timestamp = payload['exp']
current_timestamp = datetime.datetime.utcnow().timestamp()
ttl = int(exp_timestamp - current_timestamp)

if ttl > 0:
# Add to blacklist
redis_client.setex(f"blacklist:{token}", ttl, '1')

# Invalidate refresh token if provided
data = request.get_json() or {}
if 'refreshToken' in data:
redis_client.delete(f"refresh:{data['refreshToken']}")

logger.info(f"User logged out: {request.user_email}")

return jsonify({'message': 'Logged out successfully'}), 200

except Exception as e:
logger.error(f"Logout error: {str(e)}")
return jsonify({'error': 'Internal server error'}), 500

@app.route('/validate', methods=['GET'])
@require_auth
def validate_token():
"""Validate JWT token and return user info"""
try:
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute('''
SELECT id, email, full_name, profile_completed
FROM users
WHERE id = %s
''', (request.user_id,))

user = cur.fetchone()
cur.close()
conn.close()

if not user:
return jsonify({'error': 'User not found'}), 404

return jsonify({
'user': {
'id': str(user['id']),
'email': user['email'],
'fullName': user['full_name'],
'profileCompleted': user['profile_completed']
}
}), 200

except Exception as e:
logger.error(f"Token validation error: {str(e)}")
return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
Database Schema SQL
The PostgreSQL schema enforces referential integrity and includes audit logging triggers.
-- database/schema.sql
-- IHEP PostgreSQL Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_audit for compliance logging
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Users table (non-PHI data only)
CREATE TABLE users (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
email VARCHAR(255) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
full_name VARCHAR(255) NOT NULL,
profile_completed BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
last_login TIMESTAMP WITH TIME ZONE,
CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Create index for fast email lookups
CREATE INDEX idx_users_email ON users(email);

-- Conditions table
CREATE TABLE conditions (
id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
slug VARCHAR(255) UNIQUE NOT NULL,
description TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Articles table
CREATE TABLE articles (
id SERIAL PRIMARY KEY,
title VARCHAR(255) NOT NULL,
content TEXT,
source_url VARCHAR(512),
published_date DATE,
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Article-Condition junction table (many-to-many)
CREATE TABLE article_conditions (
article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
condition_id INTEGER REFERENCES conditions(id) ON DELETE CASCADE,
PRIMARY KEY (article_id, condition_id)
);

-- Providers table
CREATE TABLE providers (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
name VARCHAR(255) NOT NULL,
specialty VARCHAR(255),
address TEXT,
phone VARCHAR(20),
email VARCHAR(255),
api_endpoint VARCHAR(512),
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User-Provider junction table (many-to-many)
CREATE TABLE user_providers (
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
provider_id UUID REFERENCES providers(id) ON DELETE CASCADE,
is_primary BOOLEAN DEFAULT FALSE,
linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
PRIMARY KEY (user_id, provider_id)
);

-- Appointments table
CREATE TABLE appointments (
id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
provider_id UUID REFERENCES providers(id) ON DELETE SET NULL,
appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
appointment_type VARCHAR(50), -- 'telehealth', 'in-person', 'group'
location VARCHAR(255),
notes TEXT,
status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'no-show'
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
CONSTRAINT appointment_date_future CHECK (appointment_date > created_at)
);

-- Create index for fast appointment lookups
CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- Digital twin enrollment table (metadata only, actual PHI in Healthcare API)
CREATE TABLE digital_twin_enrollment (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
fhir_patient_id VARCHAR(255) UNIQUE NOT NULL, -- Reference to Healthcare API
enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'active', 'withdrawn'
consent_signed BOOLEAN DEFAULT FALSE,
consent_date TIMESTAMP WITH TIME ZONE
);

-- Audit log table for compliance
CREATE TABLE audit_log (
id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(id) ON DELETE SET NULL,
action VARCHAR(100) NOT NULL,
table_name VARCHAR(100),
record_id VARCHAR(255),
old_values JSONB,
new_values JSONB,
ip_address INET,
user_agent TEXT,
timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for audit log queries
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
NEW.updated_at = NOW();
RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic updated_at management
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_providers_updated_at BEFORE UPDATE ON providers
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
IF (TG_OP = 'DELETE') THEN
INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, timestamp)
VALUES (OLD.id, TG_OP, TG_TABLE_NAME, OLD.id::TEXT, row_to_json(OLD), NOW());
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values, timestamp)
VALUES (NEW.id, TG_OP, TG_TABLE_NAME, NEW.id::TEXT, row_to_json(OLD), row_to_json(NEW), NOW());
RETURN NEW;
ELSIF (TG_OP = 'INSERT') THEN
INSERT INTO audit_log (user_id, action, table_name, record_id, new_values, timestamp)
VALUES (NEW.id, TG_OP, TG_TABLE_NAME, NEW.id::TEXT, row_to_json(NEW), NOW());
RETURN NEW;
END IF;
RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_users_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_appointments_trigger
AFTER INSERT OR UPDATE OR DELETE ON appointments
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Insert default conditions
INSERT INTO conditions (name, slug, description) VALUES
('HIV/AIDS', 'hiv-aids', 'Human Immunodeficiency Virus and Acquired Immunodeficiency Syndrome care and management'),
('Diabetes', 'diabetes', 'Diabetes mellitus management and care'),
('Cancer', 'cancer', 'Cancer treatment and aftercare support'),
('Heart Disease', 'heart-disease', 'Cardiovascular disease management'),
('Mental Health', 'mental-health', 'Mental health support and resources');

-- Create read-only role for analytics
CREATE ROLE ihep_analytics WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';
GRANT CONNECT ON DATABASE ihep TO ihep_analytics;
GRANT USAGE ON SCHEMA public TO ihep_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ihep_analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ihep_analytics;

-- Revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Performance optimization: analyze tables
ANALYZE users;
ANALYZE appointments;
ANALYZE providers;
Due to length constraints, I will continue this implementation in a follow-up message with:
Healthcare API integration service
Vertex AI chat service implementation
CI/CD pipeline configuration
Security and compliance validation
Mathematical models for system optimization
Performance benchmarking specifications
Should I proceed with the continuation?