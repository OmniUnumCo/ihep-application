# IHEP Project Summary

## Project Overview

**IHEP** (Integrated Health Empowerment Program) is a comprehensive aftercare resource management application designed to empower patients managing chronic conditions. The platform features:

- **4-Twin Digital Twin Ecosystem** - Personalized health modeling with Health, Financial, Social, and Care twins
- **Financial Empowerment Module** - Tools for achieving financial stability during care journey
- **Resource Hub** - PubSub articles, support groups, community programs
- **Telehealth Services** - Video consultations and remote care
- **Dynamic Calendar** - Consolidated appointment, medication, and activity management

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Next.js 16.1.1 (App Router) |
| Language | TypeScript 5 (strict mode) |
| UI | React 19.2.3 |
| Styling | Tailwind CSS 4 |
| Components | Radix UI + shadcn/ui |
| Auth | NextAuth.js |
| State | TanStack Query |
| Charts | Recharts 3 |
| Forms | React Hook Form + Zod |
| Database | Prisma (configured, schema pending) |

## Project Structure

```
/Users/nexus1/hiv-health-insights/
├── src/
│   ├── app/                    # Next.js App Router (main)
│   │   ├── page.tsx            # Landing page
│   │   ├── layout.tsx          # Root layout
│   │   ├── globals.css         # Global styles + theme
│   │   ├── api/                # API routes
│   │   │   └── auth/           # Authentication endpoints
│   │   ├── auth/               # Auth pages
│   │   ├── dashboard/          # Protected dashboard routes
│   │   └── [other routes]/
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── auth/               # Auth components
│   │   └── dashboard/          # Dashboard components
│   └── lib/
│       ├── auth/               # Auth utilities
│       ├── api/                # API client functions
│       └── utils.ts            # Utility functions
├── public/
│   └── assets/                 # Static assets including logo
├── SESSION_HANDOFF.md          # Session handoff documentation
├── TODO.md                     # Task tracking
├── CLAUDE.md                   # AI assistant instructions
└── package.json
```

## Current Version: 1.1.0-alpha

### Recent Changes (Dec 26, 2024)
- Updated landing page to general healthcare aftercare (not HIV-specific)
- New color scheme: greens, gold, amber (matching logo)
- Moved calendar and wellness dashboard to members-only area
- Fixed all TypeScript errors for latest library versions
- Build now passes successfully

## Development Commands

```bash
npm run dev          # Start development server (http://localhost:3000)
npm run build        # Production build
npm run start        # Start production server
npm run lint         # Run ESLint
```

## Key Files for New Sessions

1. **SESSION_HANDOFF.md** - Detailed handoff from previous session
2. **TODO.md** - Current task list and priorities
3. **CLAUDE.md** - Project instructions and conventions

## Environment Variables

Required in `.env.local`:
- `SESSION_SECRET` - NextAuth session encryption
- `DATABASE_URL` - Database connection string
- `NEXTAUTH_URL` - NextAuth callback URL
- `NEXTAUTH_SECRET` - NextAuth secret

## Security Notes

- HIPAA compliance is a central concern
- All PHI must be encrypted in transit and at rest
- No PHI in logs, localStorage, or URL parameters
- 30-minute session timeout
- Audit logging required for PHI access

## Contact

This is an enterprise Human/AI Joint Venture Application with:
- 5 humans overseeing managed agentic clusters
- 25 agents per cluster (1 human / 5 agents ratio)
- Each cluster has an overseer agent
- Supervisory position manages team overseers
