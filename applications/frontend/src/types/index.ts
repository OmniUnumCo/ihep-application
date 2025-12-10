// Core User Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  conditions: HealthCondition[];
  createdAt: Date;
  updatedAt: Date;
  profileComplete: boolean;
}

export enum UserRole {
  PATIENT = 'PATIENT',
  PROVIDER = 'PROVIDER',
  RESEARCHER = 'RESEARCHER',
  ADMIN = 'ADMIN',
}

export enum HealthCondition {
  HIV_AIDS = 'HIV_AIDS',
  CANCER = 'CANCER',
  BEHAVIORAL_HEALTH = 'BEHAVIORAL_HEALTH',
  RARE_BLOOD_DISEASE = 'RARE_BLOOD_DISEASE',
  CHRONIC_CONDITION = 'CHRONIC_CONDITION',
}

// Authentication Types
export interface Session {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresAt: Date;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  idToken: string;
}

// Health Data Types - Mathematical Foundation
export interface HealthMetrics {
  timestamp: Date;
  userId: string;
  
  // Composite Health Score: H ∈ [0, 100]
  // H = Σ(w_i * m_i) where Σw_i = 1, m_i ∈ [0, 100]
  compositeScore: number;
  
  // Component metrics
  vitals: VitalSigns;
  lab: LabResults;
  medication: MedicationAdherence;
  lifestyle: LifestyleMetrics;
  mental: MentalHealthMetrics;
}

export interface VitalSigns {
  // Kalman-filtered sensor data
  // x̂_k = x̂_{k-1} + K_k(z_k - H·x̂_{k-1})
  heartRate: KalmanFiltered<number>;
  bloodPressure: KalmanFiltered<{ systolic: number; diastolic: number }>;
  temperature: KalmanFiltered<number>;
  oxygenSaturation: KalmanFiltered<number>;
  respiratoryRate: KalmanFiltered<number>;
}

export interface KalmanFiltered<T> {
  value: T;
  estimate: T;
  variance: number;
  kalmanGain: number;
  measurementNoise: number;
}

export interface LabResults {
  testName: string;
  value: number;
  unit: string;
  normalRange: { min: number; max: number };
  zScore: number; // (value - μ) / σ
  percentile: number; // Φ(zScore) where Φ is CDF
}

export interface MedicationAdherence {
  medicationId: string;
  medicationName: string;
  prescribed: number; // doses per day
  taken: number; // actual doses taken
  adherenceRate: number; // taken / prescribed
  consecutiveDays: number;
}

export interface LifestyleMetrics {
  sleepHours: number;
  sleepQuality: number; // [0, 100]
  steps: number;
  exerciseMinutes: number;
  nutrition: NutritionMetrics;
  stress: StressMetrics;
}

export interface NutritionMetrics {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  hydration: number; // liters
}

export interface StressMetrics {
  level: number; // [0, 100]
  heartRateVariability: number;
  cortisolLevel?: number;
}

export interface MentalHealthMetrics {
  moodScore: number; // [0, 100]
  anxietyScore: number; // [0, 100]
  depressionScore: number; // [0, 100]
  selfReportedWellbeing: number; // [0, 100]
}

// Digital Twin Types - Manifold Projection
export interface DigitalTwinState {
  // High-dimensional health state: H ∈ R^n
  highDimensionalState: Float32Array;
  dimension: number; // n
  
  // 3D visualization: V ∈ R^3
  // f: R^n → R^3 with distortion δ ≤ 0.05
  visualizationState: {
    position: [number, number, number];
    color: [number, number, number];
    size: number;
    opacity: number;
  };
  
  // Manifold metadata
  manifold: {
    intrinsicDimension: number; // Estimated via PCA/t-SNE
    curvature: number;
    distortion: number; // δ = ||f(H) - V||^2
  };
  
  // Temporal evolution
  trajectory: DigitalTwinTrajectory[];
  predictions: DigitalTwinPrediction[];
}

export interface DigitalTwinTrajectory {
  timestamp: Date;
  state: Float32Array;
  visualPosition: [number, number, number];
}

export interface DigitalTwinPrediction {
  horizonDays: number; // Prediction horizon
  predictedState: Float32Array;
  confidence: number; // [0, 1]
  confidenceInterval: {
    lower: Float32Array;
    upper: Float32Array;
  };
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  metadata?: ResponseMetadata;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ResponseMetadata {
  requestId: string;
  timestamp: Date;
  latency: number; // milliseconds
  rateLimit: RateLimitInfo;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  resetAt: Date;
}

// Security Types
export interface AuditLog {
  id: string;
  userId: string;
  action: AuditAction;
  resource: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
  outcome: 'SUCCESS' | 'FAILURE';
  details: Record<string, unknown>;
}

export enum AuditAction {
  LOGIN = 'LOGIN',
  LOGOUT = 'LOGOUT',
  VIEW_PHI = 'VIEW_PHI',
  UPDATE_PHI = 'UPDATE_PHI',
  EXPORT_DATA = 'EXPORT_DATA',
  SHARE_DATA = 'SHARE_DATA',
  ADMIN_ACTION = 'ADMIN_ACTION',
}

// Research Types - Privacy-Preserving
export interface ResearchDataset {
  id: string;
  name: string;
  description: string;
  
  // k-anonymity guarantee: |Q| ≥ k where Q is quasi-identifier set
  privacyLevel: {
    kAnonymity: number; // k ≥ 5
    lDiversity: number; // l ≥ 2
    tCloseness: number; // t ≤ 0.2
  };
  
  // Differential privacy
  epsilon: number; // Privacy budget
  delta: number; // Failure probability
  
  recordCount: number;
  featureCount: number;
  conditions: HealthCondition[];
  createdAt: Date;
}

// AI Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  
  // Crisis detection
  crisisDetected: boolean;
  crisisScore?: number; // [0, 1]
  crisisType?: CrisisType[];
}

export enum CrisisType {
  SUICIDAL_IDEATION = 'SUICIDAL_IDEATION',
  SELF_HARM = 'SELF_HARM',
  SEVERE_DEPRESSION = 'SEVERE_DEPRESSION',
  ACUTE_ANXIETY = 'ACUTE_ANXIETY',
  MEDICAL_EMERGENCY = 'MEDICAL_EMERGENCY',
}

// UI Component Props
export interface DigitalTwinCanvasProps {
  userId: string;
  state: DigitalTwinState;
  interactive?: boolean;
  showTrajectory?: boolean;
  showPredictions?: boolean;
  onStateChange?: (state: DigitalTwinState) => void;
}

export interface HealthDashboardProps {
  userId: string;
  metrics: HealthMetrics;
  historicalData: HealthMetrics[];
  refreshInterval?: number; // milliseconds
}

// Form Types
export interface OnboardingData {
  personalInfo: PersonalInfo;
  medicalHistory: MedicalHistory;
  preferences: UserPreferences;
}

export interface PersonalInfo {
  name: string;
  dateOfBirth: Date;
  gender: string;
  email: string;
  phone: string;
}

export interface MedicalHistory {
  conditions: HealthCondition[];
  medications: string[];
  allergies: string[];
  primaryCareProvider?: string;
}

export interface UserPreferences {
  notifications: NotificationPreferences;
  privacy: PrivacyPreferences;
  display: DisplayPreferences;
}

export interface NotificationPreferences {
  email: boolean;
  sms: boolean;
  push: boolean;
  medicationReminders: boolean;
  appointmentReminders: boolean;
  healthAlerts: boolean;
}

export interface PrivacyPreferences {
  shareDataForResearch: boolean;
  allowAnonymizedSharing: boolean;
  dataRetentionPeriod: number; // years
}

export interface DisplayPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
}
