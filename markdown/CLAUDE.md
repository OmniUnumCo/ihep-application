# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

IHEP (Integrated Health Empowerment Program) is a healthcare platform built with Next.js 15 and designed for deployment on Google Cloud Platform. The application provides patient management, digital twin health visualization, provider directories, and wellness tracking with AI-powered insights.

## Development Commands

### Working Directory
All commands should be run from the `ihep/` subdirectory unless otherwise specified.

```bash
cd ihep
```

### Build & Development
```bash
npm run dev          # Start Next.js dev server on http://localhost:3000
npm run build        # Production build with Next.js
npm run start        # Start production server
npm run check        # Type-check with TypeScript and validate architecture
npm run purge        # Remove legacy/backup files (client, backup_debug, server routes)
```

### Testing

**Setup Required**: Install Vitest + React Testing Library
```bash
npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @playwright/test  # For E2E tests
```

**Recommended test commands** (add to package.json):
```bash
npm test              # Run unit tests with Vitest
npm run test:watch    # Watch mode for development
npm run test:coverage # Generate coverage report (aim for >80%)
npm run test:e2e      # Run Playwright E2E tests
npm run test:a11y     # Accessibility tests with axe-core
```

**Test organization**:
- `__tests__/` - Unit tests co-located with source files
- `e2e/` - End-to-end Playwright tests
- `src/lib/__tests__/` - Utility and hook tests

## Architecture

### Tech Stack
- **Frontend**: Next.js 15 (App Router), React 18, TypeScript
- **UI**: Radix UI, Tailwind CSS, shadcn/ui components
- **Auth**: NextAuth.js with credential provider, JWT sessions (30min)
- **State**: TanStack Query for server state
- **Backend**: Next.js API routes (transitioning from previous Express backend)
- **Deployment**: Google Cloud Platform (Cloud Run, BigQuery, Cloud Storage)

### Project Structure

```
ihep/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout with AuthProvider
│   │   ├── page.tsx           # Landing page
│   │   ├── auth/              # Login/signup pages
│   │   ├── dashboard/         # Protected dashboard routes
│   │   │   ├── page.tsx       # Main dashboard
│   │   │   ├── digital-twin/  # 3D health visualization
│   │   │   ├── wellness/      # Health metrics
│   │   │   ├── calendar/      # Appointments
│   │   │   ├── providers/     # Provider directory
│   │   │   └── resources/     # Educational content
│   │   └── api/               # API routes (auth, etc.)
│   ├── components/
│   │   ├── ui/                # Radix UI + shadcn components
│   │   ├── auth/              # AuthProvider, ProtectedRoute
│   │   ├── dashboard/         # Dashboard-specific components
│   │   ├── digital-twin/      # DigitalTwinCanvas (placeholder for Three.js)
│   │   └── ai/                # ChatInterface for AI features
│   ├── lib/
│   │   ├── api/               # API client functions (auth, appointments, wellness)
│   │   ├── hooks/             # React hooks (useAuth, useHealthData)
│   │   ├── auth/              # NextAuth options and providers
│   │   ├── constants/         # Conditions, API endpoints
│   │   └── utils.ts           # Utility functions
│   ├── shared/                # Shared schemas (Zod)
│   └── hooks/                 # Additional hooks (use-mobile, use-toast)
├── scripts/
│   ├── purge-legacy.mjs       # Clean up old Express/Vite files
│   └── check-architecture.mjs # Validate project structure
├── terraform/                 # GCP infrastructure (Foundation Blueprint)
├── gcp/                       # GCP deployment scripts and configs
└── markdown/                  # Documentation and planning docs
```

### Key Architectural Patterns

1. **App Router**: Uses Next.js 15 App Router (not Pages Router). All routes in `src/app/`.

2. **Path Aliases**:
   - `@/*` → `src/*`
   - `@/server/*` → `src/server/*` (legacy, being removed)
   - `@shared/*` → `src/shared/*`

3. **Authentication Flow**:
   - NextAuth.js with credentials provider
   - Mock user store in development (`src/lib/mockStore.ts`)
   - JWT sessions with 30-minute expiry
   - Protected routes wrapped with AuthProvider
   - Login redirects to `/dashboard`

4. **Component Structure**:
   - UI components in `src/components/ui/` follow shadcn/ui patterns
   - Feature components in feature-specific directories
   - Server components by default; use `'use client'` for interactivity

5. **Styling**:
   - Tailwind CSS with custom config
   - Typography plugin enabled
   - Dark mode support (via Tailwind)
   - Glass morphism effects used in UI

6. **Security Headers**: Strict CSP, HSTS, X-Frame-Options, etc. configured in `next.config.mjs`

### Migration Context

The project is transitioning from:
- Express.js backend → Next.js API routes
- Traditional deployment → Google Cloud Platform serverless
- PostgreSQL → BigQuery (for analytics)

Legacy files are excluded from TypeScript compilation (see `tsconfig.json` excludes) and can be purged with `npm run purge`.

## GCP Deployment

### Infrastructure (Terraform)
Location: `ihep/terraform/`

The Terraform configuration follows Google Cloud Foundation Blueprint best practices:
- Hierarchical organization with folders
- Shared VPC networking
- IAM with group-based permissions
- Centralized logging and monitoring
- Cloud SQL, Firestore, Cloud Run services

**Deploy Infrastructure**:
```bash
cd ihep/terraform
terraform init
terraform plan
terraform apply
```

### Application Deployment
Location: `ihep/gcp/`

**Quick deployment**:
```bash
cd ihep/gcp
./deploy.sh  # Automated deployment to Cloud Run
```

**Required GCP APIs**: Enabled via `setup-project.sh`
- Cloud Run
- Cloud Functions
- BigQuery
- Secret Manager
- Cloud Storage
- Cloud SQL

### Environment Variables & Secrets

Store sensitive values in Google Secret Manager:
- `OPENAI_API_KEY` - AI wellness insights
- `SENDGRID_API_KEY` - Email notifications
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` - SMS/video calls
- `SESSION_SECRET` - NextAuth session encryption

## Important Constraints

1. **No Legacy Server Code**: Do not import or reference files in `src/server/routes`, `src/server/services`, or `server.js`. These are being removed.

2. **TypeScript Strict Mode**: The project uses strict TypeScript. All new code must be typed.

3. **Security**:
   - HIPAA compliance considerations for health data
   - Strict CSP headers enforced
   - No inline scripts without nonces

4. **Authentication**:
   - All dashboard routes require authentication
   - Use `getServerSession()` in server components
   - Use `useSession()` in client components

5. **Component Library**: Use existing shadcn/ui components from `src/components/ui/` rather than creating new base components.

## Digital Twin Feature

The digital twin visualization (`src/components/digital-twin/DigitalTwinCanvas.tsx`) is currently a placeholder. Production implementation would use:
- Three.js for 3D rendering
- Real-time health data streams
- WebGL-based visualizations

When implementing, integrate with `HealthDataStream` component for live updates.

## Common Development Tasks

### Adding a New Dashboard Route
1. Create page in `src/app/dashboard/[route-name]/page.tsx`
2. Add navigation link in dashboard layout
3. Create feature components in `src/components/[feature]/`
4. Add API client in `src/lib/api/` if needed

### Adding a New API Endpoint
1. Create route handler in `src/app/api/[endpoint]/route.ts`
2. Export named functions for HTTP methods (GET, POST, etc.)
3. Use `getServerSession(authOptions)` for protected endpoints

### Adding UI Components
- Use `npx shadcn-ui@latest add [component]` to add new shadcn components
- Custom components go in appropriate feature directories
- Follow existing patterns for Radix UI usage

## Development Best Practices

### Code Quality & Standards

**TypeScript**:
- Enable all strict mode options (already configured)
- Use branded types for PHI (Protected Health Information):
  ```typescript
  type PatientId = string & { readonly __brand: 'PatientId' }
  type EncryptedPHI = string & { readonly __brand: 'EncryptedPHI' }
  ```
- Prefer `unknown` over `any` when type is uncertain
- Use discriminated unions for state management
- Leverage const assertions and satisfies operator

**Linting & Formatting** (add to project):
```bash
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-react-hooks
npm install -D eslint-plugin-jsx-a11y  # Accessibility linting
```

**Code Review Checklist**:
- [ ] All functions have JSDoc comments for public APIs
- [ ] No console.log statements (use structured logging)
- [ ] Error boundaries wrap risky components
- [ ] Loading and error states implemented
- [ ] Accessibility: keyboard navigation, ARIA labels, focus management
- [ ] Security: input validation, XSS prevention, no hardcoded secrets
- [ ] Performance: memoization where needed, lazy loading, code splitting
- [ ] Tests: unit tests for utilities, integration tests for features
- [ ] PHI handling: encrypted, audit logged, access controlled

### Git Workflow

**Branch naming**:
- `feature/ISSUE-123-add-wellness-metrics`
- `fix/ISSUE-456-auth-redirect-loop`
- `chore/update-dependencies`
- `docs/api-documentation`

**Commit conventions** (Conventional Commits):
```
feat(digital-twin): add real-time health data streaming
fix(auth): resolve session expiry redirect loop
perf(dashboard): implement virtualization for appointment list
security(api): add rate limiting to patient data endpoints
test(wellness): add unit tests for metric calculations
docs(deployment): update GCP setup instructions
```

**Pull Request Template**:
```markdown
## Description
[Clear description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Security patch

## HIPAA Compliance
- [ ] No PHI in logs
- [ ] All PHI encrypted in transit and at rest
- [ ] Audit logging implemented
- [ ] Access controls verified

## Testing
- [ ] Unit tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed
- [ ] Accessibility tested

## Performance Impact
- [ ] Bundle size impact: [+/- X KB]
- [ ] Lighthouse score: [score]
- [ ] Core Web Vitals: LCP/FID/CLS
```

### React/Next.js Best Practices

**Server vs Client Components Decision Tree**:
```
Does it need interactivity (onClick, useState, useEffect)?
├─ YES → Client Component ('use client')
└─ NO → Server Component (default)
    ├─ Needs auth? → Use getServerSession()
    └─ Fetches data? → Use async component + fetch
```

**Data Fetching Patterns**:
```typescript
// ✅ Preferred: Server Component with async/await
export default async function WellnessPage() {
  const data = await fetch('...', { next: { revalidate: 60 } })
  return <WellnessMetrics data={data} />
}

// ✅ Client-side: TanStack Query for mutations and real-time
'use client'
export function AppointmentBooking() {
  const { data, isLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: fetchAppointments,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// ❌ Avoid: useEffect for data fetching in new code
```

**Error Handling**:
```typescript
// error.tsx - Error boundary for route segments
'use client'
export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log to error tracking service (e.g., Sentry)
    logErrorToService(error)
  }, [error])

  return <ErrorUI error={error} onRetry={reset} />
}

// loading.tsx - Loading UI for Suspense
export default function Loading() {
  return <DashboardSkeleton />
}
```

**Performance Optimization**:
- Use Next.js `<Image>` component for all images (automatic optimization)
- Implement dynamic imports for heavy components:
  ```typescript
  const DigitalTwin = dynamic(() => import('@/components/digital-twin/DigitalTwinCanvas'), {
    loading: () => <Skeleton />,
    ssr: false, // Disable SSR for WebGL components
  })
  ```
- Use `loading.tsx` and `Suspense` for streaming SSR
- Implement route prefetching with `<Link prefetch={true}>`
- Use Partial Prerendering (PPR) where appropriate

**Metadata & SEO**:
```typescript
// app/dashboard/wellness/page.tsx
export const metadata: Metadata = {
  title: 'Wellness Metrics | IHEP',
  description: 'Track your health metrics and wellness goals',
  robots: { index: false, follow: false }, // Private pages
}
```

### Accessibility (WCAG 2.1 AA Compliance)

**Requirements for All Components**:
- [ ] Keyboard navigable (Tab, Enter, Space, Arrows)
- [ ] Focus visible (outline, focus ring)
- [ ] Semantic HTML (button, nav, main, article)
- [ ] ARIA labels for icon buttons
- [ ] Color contrast ratio ≥ 4.5:1 (text), ≥ 3:1 (UI)
- [ ] Screen reader tested (VoiceOver, NVDA)
- [ ] Form validation with aria-invalid and aria-describedby
- [ ] Skip links for main content

**Testing Accessibility**:
```bash
npm install -D @axe-core/react eslint-plugin-jsx-a11y
```

```typescript
// In development only
if (process.env.NODE_ENV !== 'production') {
  import('react-dom').then(ReactDOM => {
    import('@axe-core/react').then(axe => {
      axe.default(React, ReactDOM, 1000)
    })
  })
}
```

### Healthcare-Specific: HIPAA Compliance

**PHI (Protected Health Information) Handling**:

1. **Encryption**:
   - All PHI encrypted in transit (TLS 1.3)
   - All PHI encrypted at rest (AES-256)
   - Use Google Cloud KMS for key management

2. **Access Control**:
   ```typescript
   // Implement role-based access control (RBAC)
   const PERMISSIONS = {
     'patient': ['read:own-data'],
     'provider': ['read:patient-data', 'write:patient-data'],
     'admin': ['read:all-data', 'write:all-data', 'manage:users'],
   } as const

   function checkPermission(user: User, permission: Permission) {
     return PERMISSIONS[user.role]?.includes(permission) ?? false
   }
   ```

3. **Audit Logging**:
   ```typescript
   // Log all PHI access to BigQuery for HIPAA audit trail
   async function logPHIAccess(event: PHIAccessEvent) {
     await bigquery.insert('audit_logs', {
       timestamp: new Date().toISOString(),
       userId: event.userId,
       action: event.action, // 'read', 'write', 'delete'
       resource: event.resource,
       ipAddress: event.ipAddress,
       userAgent: event.userAgent,
       success: event.success,
     })
   }
   ```

4. **Data Minimization**:
   - Only request/display PHI when necessary
   - Use data masking for non-essential views (e.g., "John D." instead of full name)
   - Implement field-level encryption for sensitive fields

5. **Session Management**:
   - 30-minute session timeout (already configured)
   - Automatic logout on inactivity
   - No PHI in session tokens or cookies
   - Secure, HttpOnly, SameSite cookies

6. **Input Validation & Sanitization**:
   ```typescript
   import { z } from 'zod'

   const PatientDataSchema = z.object({
     firstName: z.string().min(1).max(100).trim(),
     lastName: z.string().min(1).max(100).trim(),
     email: z.string().email(),
     phoneNumber: z.string().regex(/^\+?[1-9]\d{1,14}$/), // E.164 format
     dateOfBirth: z.date().max(new Date()), // No future dates
     medicalRecordNumber: z.string().uuid(), // Branded type recommended
   })

   // Validate all inputs at API boundaries
   export async function POST(request: Request) {
     const body = await request.json()
     const validated = PatientDataSchema.parse(body) // Throws if invalid
     // ... proceed with validated data
   }
   ```

7. **No PHI in Client-Side Storage**:
   - No PHI in localStorage or sessionStorage
   - No PHI in URL parameters or query strings
   - Use memory-only state for sensitive data

### Security Best Practices

**API Route Protection**:
```typescript
// src/app/api/patient/[id]/route.ts
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth/options'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)

  // Authentication check
  if (!session) {
    return new Response('Unauthorized', { status: 401 })
  }

  // Authorization check (patient can only access own data)
  if (session.user.role === 'patient' && session.user.id !== params.id) {
    return new Response('Forbidden', { status: 403 })
  }

  // Rate limiting (implement with Upstash Redis)
  const rateLimitResult = await rateLimit(session.user.id)
  if (!rateLimitResult.success) {
    return new Response('Too Many Requests', { status: 429 })
  }

  // Input validation
  if (!isValidUUID(params.id)) {
    return new Response('Invalid ID format', { status: 400 })
  }

  // Proceed with request...
}
```

**Rate Limiting** (add Upstash Redis):
```typescript
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
  analytics: true,
})

export async function rateLimit(identifier: string) {
  return await ratelimit.limit(identifier)
}
```

**XSS Prevention**:
- React escapes by default, but be careful with `dangerouslySetInnerHTML`
- Use DOMPurify for user-generated HTML content
- Implement CSP headers (already configured in next.config.mjs)

**CSRF Protection**:
- NextAuth.js provides CSRF tokens automatically
- For custom forms, use `next-csrf` package

**SQL Injection Prevention**:
- Use parameterized queries exclusively
- Never concatenate user input into SQL
- Use ORM/query builder (Prisma, Drizzle) for type safety

### Performance Best Practices

**Core Web Vitals Targets**:
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

**Optimization Techniques**:

1. **Code Splitting**:
   ```typescript
   // Split large dashboard into route-based chunks
   const WellnessPage = dynamic(() => import('./wellness/page'))
   const DigitalTwinPage = dynamic(() => import('./digital-twin/page'))
   ```

2. **Image Optimization**:
   ```typescript
   import Image from 'next/image'

   <Image
     src="/health-chart.png"
     alt="Health metrics chart"
     width={800}
     height={400}
     priority={isAboveFold} // LCP optimization
     placeholder="blur"
     blurDataURL="data:image/..." // Low-quality preview
   />
   ```

3. **Font Optimization**:
   ```typescript
   // app/layout.tsx - Use next/font
   import { Inter } from 'next/font/google'

   const inter = Inter({
     subsets: ['latin'],
     display: 'swap',
     variable: '--font-inter',
   })
   ```

4. **Bundle Analysis**:
   ```bash
   npm install -D @next/bundle-analyzer
   ANALYZE=true npm run build  # Visualize bundle size
   ```

5. **Database Query Optimization**:
   - Use indexes on frequently queried columns
   - Implement pagination (limit + offset or cursor-based)
   - Use BigQuery partitioning and clustering
   - Cache expensive queries with Redis

6. **Caching Strategy**:
   ```typescript
   // Static: Revalidate every hour
   fetch(url, { next: { revalidate: 3600 } })

   // Dynamic: No cache
   fetch(url, { cache: 'no-store' })

   // React cache() for request deduplication
   import { cache } from 'react'
   const getUser = cache(async (id: string) => {
     return await db.user.findUnique({ where: { id } })
   })
   ```

### Observability & Monitoring

**Structured Logging**:
```typescript
// lib/logger.ts
import pino from 'pino'

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  redact: {
    paths: ['req.headers.authorization', 'patient.*'], // Never log PHI
    remove: true,
  },
})

// Usage
logger.info({ userId: user.id, action: 'login' }, 'User logged in')
logger.error({ err, userId: user.id }, 'Failed to fetch patient data')
```

**Error Tracking** (Sentry integration):
```bash
npm install @sentry/nextjs
npx @sentry/wizard -i nextjs
```

**Cloud Monitoring Integration**:
```typescript
// Send custom metrics to GCP Cloud Monitoring
import { MetricServiceClient } from '@google-cloud/monitoring'

export async function recordMetric(
  metricType: string,
  value: number,
  labels: Record<string, string>
) {
  const client = new MetricServiceClient()
  const projectId = process.env.GCP_PROJECT_ID

  await client.createTimeSeries({
    name: `projects/${projectId}`,
    timeSeries: [{
      metric: { type: `custom.googleapis.com/${metricType}`, labels },
      points: [{ interval: { endTime: { seconds: Date.now() / 1000 } }, value: { doubleValue: value } }],
    }],
  })
}
```

**Health Check Endpoints**:
```typescript
// app/api/health/route.ts
export async function GET() {
  const checks = {
    database: await checkDatabaseConnection(),
    redis: await checkRedisConnection(),
    auth: await checkAuthService(),
  }

  const allHealthy = Object.values(checks).every(c => c.healthy)

  return Response.json(
    { status: allHealthy ? 'healthy' : 'degraded', checks },
    { status: allHealthy ? 200 : 503 }
  )
}
```

### Testing Strategy

**Test Pyramid**:
- 70% Unit tests (fast, isolated, many)
- 20% Integration tests (API routes, database interactions)
- 10% E2E tests (critical user journeys)

**Unit Test Example**:
```typescript
// src/lib/utils.test.ts
import { describe, it, expect } from 'vitest'
import { calculateBMI, formatHealthMetric } from './utils'

describe('calculateBMI', () => {
  it('calculates BMI correctly', () => {
    expect(calculateBMI(70, 1.75)).toBeCloseTo(22.86, 2)
  })

  it('throws on invalid input', () => {
    expect(() => calculateBMI(-70, 1.75)).toThrow('Invalid weight')
  })
})
```

**Integration Test Example**:
```typescript
// src/app/api/patient/route.test.ts
import { describe, it, expect, beforeAll } from 'vitest'
import { POST } from './route'

describe('POST /api/patient', () => {
  it('creates a new patient with valid data', async () => {
    const request = new Request('http://localhost/api/patient', {
      method: 'POST',
      body: JSON.stringify({ firstName: 'John', lastName: 'Doe', email: 'john@example.com' }),
    })

    const response = await POST(request)
    expect(response.status).toBe(201)

    const data = await response.json()
    expect(data.id).toBeDefined()
  })

  it('returns 401 for unauthenticated requests', async () => {
    // Test without session
  })
})
```

**E2E Test Example** (Playwright):
```typescript
// e2e/patient-dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Patient Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[name="username"]', 'patient@test.com')
    await page.fill('input[name="password"]', 'testpass123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('displays wellness metrics', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard')
    await expect(page.locator('[data-testid="wellness-card"]')).toBeVisible()
  })

  test('navigates to appointments', async ({ page }) => {
    await page.click('a[href="/dashboard/calendar"]')
    await expect(page).toHaveURL('/dashboard/calendar')
  })
})
```

**Accessibility Testing**:
```typescript
// e2e/a11y.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('dashboard should not have accessibility violations', async ({ page }) => {
    await page.goto('/dashboard')

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    expect(accessibilityScanResults.violations).toEqual([])
  })
})
```

### Advanced Patterns

**Optimistic Updates**:
```typescript
// components/AppointmentBooking.tsx
const queryClient = useQueryClient()

const bookAppointment = useMutation({
  mutationFn: (appointment: Appointment) => api.bookAppointment(appointment),
  onMutate: async (newAppointment) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['appointments'] })

    // Snapshot previous value
    const previous = queryClient.getQueryData(['appointments'])

    // Optimistically update
    queryClient.setQueryData(['appointments'], (old: Appointment[]) => [...old, newAppointment])

    return { previous }
  },
  onError: (err, newAppointment, context) => {
    // Rollback on error
    queryClient.setQueryData(['appointments'], context.previous)
  },
  onSettled: () => {
    // Refetch after mutation
    queryClient.invalidateQueries({ queryKey: ['appointments'] })
  },
})
```

**Feature Flags**:
```typescript
// lib/feature-flags.ts
const FEATURES = {
  digitalTwin3D: process.env.NEXT_PUBLIC_FEATURE_DIGITAL_TWIN === 'true',
  aiChatbot: process.env.NEXT_PUBLIC_FEATURE_AI_CHAT === 'true',
  telehealthVideo: process.env.NEXT_PUBLIC_FEATURE_TELEHEALTH === 'true',
} as const

export function useFeatureFlag(feature: keyof typeof FEATURES): boolean {
  return FEATURES[feature]
}

// Usage
function Dashboard() {
  const hasDigitalTwin = useFeatureFlag('digitalTwin3D')

  return (
    <div>
      {hasDigitalTwin && <DigitalTwinCanvas />}
    </div>
  )
}
```

**Dependency Injection**:
```typescript
// lib/di/container.ts
interface Services {
  patientRepository: PatientRepository
  appointmentService: AppointmentService
  notificationService: NotificationService
}

const services: Services = {
  patientRepository: new PatientRepositoryImpl(),
  appointmentService: new AppointmentServiceImpl(),
  notificationService: new NotificationServiceImpl(),
}

export function getService<K extends keyof Services>(key: K): Services[K] {
  return services[key]
}

// Usage in API routes
const patientRepo = getService('patientRepository')
const patient = await patientRepo.findById(id)
```

**Repository Pattern**:
```typescript
// lib/repositories/PatientRepository.ts
interface PatientRepository {
  findById(id: string): Promise<Patient | null>
  findAll(options: PaginationOptions): Promise<Patient[]>
  create(data: CreatePatientDTO): Promise<Patient>
  update(id: string, data: UpdatePatientDTO): Promise<Patient>
  delete(id: string): Promise<void>
}

export class PatientRepositoryImpl implements PatientRepository {
  async findById(id: string): Promise<Patient | null> {
    // BigQuery or Cloud SQL implementation
    const [rows] = await bigquery.query({
      query: 'SELECT * FROM patients WHERE id = @id',
      params: { id },
    })
    return rows[0] ?? null
  }

  // ... other methods
}
```

**Contract Testing** (API versioning):
```typescript
// lib/api/contracts/v1/patient.contract.ts
import { z } from 'zod'

export const PatientResponseV1 = z.object({
  id: z.string().uuid(),
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email(),
  createdAt: z.string().datetime(),
})

export type PatientResponseV1 = z.infer<typeof PatientResponseV1>

// Use in API route
export async function GET(request: Request) {
  const patient = await fetchPatient()
  const validated = PatientResponseV1.parse(patient) // Ensures contract compliance
  return Response.json(validated)
}
```

### Documentation References

- **Deployment**: `ihep/DEPLOYMENT_GUIDE.md`, `ihep/gcp/README.md`
- **Terraform**: `ihep/terraform/README.md`
- **Project Structure**: `markdown/project-structure.md`
- **Security**: `ihep/SECURITY.md`
- **Production Checklist**: `ihep/PRODUCTION_READY_CHECKLIST.md`

### Code Organization Principles

**Feature-Sliced Design** (recommended migration):
```
src/
├── features/
│   ├── patient-dashboard/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types.ts
│   │   └── index.ts
│   ├── appointments/
│   └── wellness-tracking/
├── entities/          # Business entities (Patient, Appointment)
├── shared/            # Shared utilities, UI kit
└── app/               # Next.js App Router (thin routing layer)
```

**Naming Conventions**:
- Components: PascalCase (`PatientCard.tsx`)
- Utilities: camelCase (`formatDate.ts`)
- Constants: UPPER_SNAKE_CASE (`API_BASE_URL`)
- Types/Interfaces: PascalCase with descriptive names (`PatientFormData`, `AppointmentStatus`)
- Files: kebab-case for non-components (`use-patient-data.ts`)

**Import Order** (enforce with ESLint):
```typescript
// 1. External dependencies
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

// 2. Internal absolute imports (aliases)
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'

// 3. Relative imports
import { PatientCard } from './PatientCard'
import { formatPatientName } from './utils'

// 4. Types
import type { Patient } from '@/lib/types'
```
