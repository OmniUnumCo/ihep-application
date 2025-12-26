# IHEP Project TODO

Last Updated: December 26, 2024 (Session 3)

## Completed Tasks

- [x] Update landing page from HIV-specific to general healthcare aftercare
- [x] Update color scheme to greens, gold, amber (matching logo)
- [x] Remove calendar from public landing page (moved to members area)
- [x] Remove wellness dashboard from public landing page (moved to members area)
- [x] Add About section to landing page
- [x] Fix directory structure conflicts (app/ vs src/app/)
- [x] Install missing dependencies (Radix UI, shadcn utilities)
- [x] Fix TypeScript errors in shadcn/ui components
- [x] Fix bcrypt -> bcryptjs imports
- [x] Update calendar.tsx for react-day-picker v9
- [x] Update chart.tsx for recharts v3
- [x] Update resizable.tsx for react-resizable-panels v3
- [x] Fix Tailwind CSS v4 configuration
- [x] Add HSL CSS variables for theme
- [x] Get build passing
- [x] Fix Tailwind v4 CSS import syntax
- [x] Connect login modal form to NextAuth signIn()
- [x] Connect register modal form to /api/auth/register
- [x] Add form state management (useState for inputs)
- [x] Add error handling and loading states to forms
- [x] "Learn About Digital Twins" button scrolls to #digital-twin section
- [x] "Explore Digital Twin Program" button opens signup modal
- [x] Add logout functionality to dashboard
- [x] Move financials and opportunities under /dashboard route
- [x] Update theme colors consistently across all pages
- [x] Wellness page: Add Metric button opens functional modal
- [x] Calendar page: New Appointment button opens functional modal
- [x] Calendar page: Interactive calendar with clickable dates
- [x] Calendar page: Clicking appointment day shows appointment details
- [x] Opportunities page: Find Opportunities button with error handling
- [x] Fix Select dropdown transparency (solid white background)
- [x] Fix Select dropdown direction (opens downward)
- [x] Fix 29 Dependabot security vulnerabilities (Next.js, transformers, flask-cors, marshmallow, black)
- [x] Rename app/ to workspaces/ to fix Next.js App Router conflict
- [x] Remove duplicate postcss.config.js
- [x] Fix CSP blocking inline scripts in development mode
- [x] Add Contact form section to landing page (replaces footer scroll)
- [x] Update images.domains to images.remotePatterns (deprecation fix)

## High Priority

### Pre-Production Content Cleanup
- [ ] Replace all placeholder/dummy text with real IHEP content
- [ ] Dashboard: Replace mock wellness metrics with real data integration
- [ ] Dashboard: Replace mock appointments with real calendar data
- [ ] Dashboard: Replace mock provider listings with real provider database
- [ ] Calendar: Remove hardcoded sample appointments
- [ ] Providers: Remove sample provider data (Dr. Sarah Chen, etc.)
- [ ] Resources: Replace sample educational resources with real content
- [ ] Financials: Connect to real financial data source (currently hardcoded projections)
- [ ] Opportunities: Replace sample gig/training listings with real opportunities
- [ ] Digital Twin: Replace placeholder visualization with real implementation
- [ ] Landing page: Review all marketing copy for accuracy
- [ ] Remove any test credentials or placeholder secrets from codebase

### Testing
- [ ] Set up Vitest + React Testing Library
- [ ] Add unit tests for authentication flow
- [ ] Add unit tests for form validation
- [ ] Add E2E tests with Playwright for critical user journeys
- [ ] Add accessibility tests with axe-core

### Database
- [ ] Configure Prisma schema for users, appointments, providers, wellness metrics
- [ ] Replace mock store with actual database
- [ ] Set up database migrations
- [ ] Add seed data for development

### API Endpoints
- [ ] Complete appointments API (CRUD operations)
- [ ] Complete wellness tracking API endpoints
- [ ] Implement provider directory API
- [ ] Implement resource hub API
- [ ] Add telehealth integration endpoints

## Medium Priority

### Features
- [ ] Implement appointment booking functionality (currently static data)
- [ ] Add real wellness metric tracking and data persistence
- [ ] Implement provider search and filtering with real data
- [ ] Add real-time digital twin data streams
- [ ] Implement password reset functionality
- [ ] Implement email verification flow

### User Experience
- [ ] Add loading skeletons throughout dashboard
- [ ] Implement proper error boundaries
- [ ] Add toast notifications for user actions
- [ ] Improve mobile navigation experience

## Low Priority / Future

### Infrastructure
- [ ] Configure GCP deployment (Cloud Run, BigQuery)
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring and logging (Sentry, Cloud Monitoring)
- [ ] Implement rate limiting with Upstash Redis

### Features
- [ ] Financial Empowerment Module enhancements
- [ ] PubSub articles feed integration
- [ ] Telehealth video integration (Twilio)
- [ ] Notification service (email/SMS with SendGrid/Twilio)
- [ ] Digital Twin 3D visualization with Three.js

### Security & Compliance
- [ ] HIPAA compliance audit
- [ ] Implement audit logging for PHI access
- [ ] Add field-level encryption for sensitive data
- [ ] Security penetration testing
- [ ] Add CSRF protection for custom forms

## Technical Debt

- [ ] Clean up or remove app_backup/ directory after confirming nothing is needed
- [ ] Clean up old /financials and /opportunities routes (now under /dashboard)
- [ ] Consolidate duplicate component directories (components/ vs src/components/)
- [ ] Update eslint configuration for stricter rules
- [ ] Remove unused dependencies from package.json

## Notes

- Project uses `src/app/` as the main app directory
- Path alias `@/*` maps to `./src/*`
- Path alias `@shared/*` maps to `./src/shared/*`
- Authentication uses NextAuth.js with credentials provider
- Mock store currently used for user data in development
- All dashboard pages protected with session check
