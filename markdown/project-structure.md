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