# Repository Guidelines

## Project Structure & Module Organization
- `src/app` holds the Next.js App Router entrypoint, routes, layouts, and global styles; `src/app/components` contains route-scoped UI. 
- `src/components` stores shared UI primitives; `src/hooks` houses reusable React hooks; `src/lib` contains utilities (API helpers, auth, formatting); `src/shared` and `types` store cross-cutting types and constants.
- `public/` serves static assets; `scripts/` provides maintenance helpers (e.g., `check-architecture.mjs`, `purge-legacy.mjs`); `docs/` covers deployment/compliance notes.
- Use the path aliases from `tsconfig.json` (`@/*`, `@shared/*`) instead of relative `../../../` chains.

## Build, Test, and Development Commands
- `npm run dev` — start the Next.js dev server with hot reload.
- `npm run build` — create a production build.
- `npm run start` — serve the production build locally.
- `npm run check` — run the TypeScript project check plus architecture guard; run before any PR.
- `npm run purge` — remove legacy assets flagged in `scripts/purge-legacy.mjs`; run only when deprecations are approved.

## Coding Style & Naming Conventions
- TypeScript-first; keep `strict`-mode compatibility. Prefer functional components and hooks.
- Use 2-space indentation, single quotes, and favor named exports for shared modules.
- Co-locate component styles with JSX using Tailwind utility classes; extend theme tokens via `tailwind.config.ts`.
- Keep files focused: pages in `src/app`, reusable UI in `src/components`, domain logic in `src/lib`/`src/shared`.
- Name files by role: components `PascalCase.tsx`, hooks `useSomething.ts`, utilities `verbNoun.ts`.

## Testing Guidelines
- No automated test runner is configured yet; when adding, prefer colocated `*.test.ts(x)` or `*.spec.ts(x)` near the source.
- Exercise new code paths manually through `npm run dev` until an automated suite is added.
- Always run `npm run check` before pushing to catch type regressions and architecture drift.

## Commit & Pull Request Guidelines
- Follow a concise, present-tense summary; `<type>: short action` is preferred when applicable (examples in git history: `security: Fix ...`).
- Reference related issues/tickets and call out user-facing or security-impacting changes explicitly.
- For UI changes, attach screenshots or short clips. For backend or config changes, list migrations/env vars and expected operational impact.
- Ensure PR descriptions mention test coverage performed (manual steps or added specs) and any follow-up tasks.

## Security & Configuration Tips
- Never commit secrets; use environment variables and keep `.env` files local. Check `secrets.sh` templates rather than inlining keys.
- Prefer existing stacks (Next.js, Tailwind, React Query, Zod, bcrypt) and validate new dependencies.
