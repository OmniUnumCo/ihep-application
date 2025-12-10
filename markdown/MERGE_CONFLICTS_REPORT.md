# Merge Conflicts Report

**Date**: 2025-11-19
**Comparing**: Root directory (`./`) vs `ihep/` subdirectory

## Summary

Found **5 common files** between root and ihep directories. Analysis below:

## Files with CONFLICTS (Manual Resolution Required)

### 1. `package.json` ⚠️ MAJOR CONFLICT

**Status**: Completely different files - NOT COMPATIBLE

**Root version**:
- Minimal file with only `terraform` dependency
- No project metadata

**ihep/ version**:
- Full Next.js 15 application
- 40+ dependencies (React, Radix UI, TanStack Query, etc.)
- Complete build scripts (dev, build, start, check, purge)
- TypeScript devDependencies

**Recommendation**:
- **KEEP**: `ihep/package.json` (this is the actual application)
- **DELETE**: `./package.json` (minimal, likely obsolete)
- The root `package.json` appears to be a placeholder or leftover file

---

### 2. `Dockerfile` ⚠️ MAJOR CONFLICT

**Status**: Completely different applications - NOT COMPATIBLE

**Root version**:
- Python 3.11 based
- For "synthesis service"
- Installs scientific computing libs (gfortran, libopenblas)
- Runs `synthesis_service.py` on port 8080

**ihep/ version**:
- Node.js 20 Alpine based
- Multi-stage build for Next.js app
- Optimized for production deployment
- Runs on port 5000
- Health check endpoint at `/api/health`

**Recommendation**:
- **KEEP**: `ihep/Dockerfile` (this is for the Next.js web application)
- **MOVE/RENAME**: `./Dockerfile` → `services/synthesis/Dockerfile` (if synthesis service is still needed)
- These are for **different services** - both may be needed but in different locations

---

### 3. `package-lock.json` ⚠️ CONFLICT (Not Analyzed)

**Status**: Generated file, will differ based on package.json

**Recommendation**:
- **KEEP**: `ihep/package-lock.json`
- **DELETE**: `./package-lock.json`
- Will be regenerated automatically when running `npm install` with chosen package.json

---

## Files WITHOUT Conflicts (Identical)

### 4. `deployment-automation.hcl` ✅ NO CONFLICT

**Status**: Files are identical - no merge conflicts

### 5. `secrets.sh` ✅ NO CONFLICT

**Status**: Files are identical - no merge conflicts

---

## Recommended Merge Strategy

### Option 1: Keep ihep as primary (RECOMMENDED)

The `ihep/` directory appears to be the actual working Next.js application. Root files seem to be miscellaneous/leftover files.

```bash
# 1. Keep CLAUDE.md in root (already there)

# 2. Delete conflicting root files (they're older/irrelevant)
rm ./package.json
rm ./package-lock.json

# 3. Move Python Dockerfile to proper location (if synthesis service is still used)
mkdir -p services/synthesis
mv ./Dockerfile services/synthesis/Dockerfile

# 4. Keep identical files (no action needed)
# - deployment-automation.hcl (already identical)
# - secrets.sh (already identical)

# 5. The ihep/ directory becomes the main application
```

### Option 2: Merge contents into root

If you want to collapse the structure and move ihep contents to root:

```bash
# WARNING: This will restructure your entire repository

# 1. Backup first!
cp -r ihep ihep_backup

# 2. Move all ihep contents to root
cp -r ihep/* .
cp -r ihep/.* . 2>/dev/null || true

# 3. Remove the ihep directory
rm -rf ihep

# 4. Move Python Dockerfile if needed
mkdir -p services/synthesis
# (would already be moved from ihep/services/ if it exists there)
```

---

## Architecture Observations

Based on the file analysis:

1. **Root directory** contains:
   - Minimal/obsolete package.json (terraform only)
   - Python-based synthesis service Dockerfile
   - Shared config files (deployment-automation.hcl, secrets.sh)

2. **ihep/ directory** contains:
   - Complete Next.js 15 application
   - Node.js-based Dockerfile
   - Full project structure (src/, components/, terraform/, gcp/)

**Conclusion**: These appear to be **different projects** or **different services** in a monorepo structure. The root may have been an earlier iteration or placeholder.

---

## Next Steps

1. **Decide on repository structure**:
   - Option A: Keep `ihep/` as subdirectory (monorepo with multiple services)
   - Option B: Move ihep contents to root (single Next.js app as primary)

2. **Preserve both Dockerfiles if needed**:
   - Web app: `Dockerfile` (Node.js)
   - Synthesis service: `services/synthesis/Dockerfile` (Python)

3. **Clean up obsolete files**:
   - Root `package.json` appears unused
   - Root `package-lock.json` should be removed

4. **Update CI/CD if needed**:
   - Ensure deployment scripts point to correct Dockerfile
   - Update build paths in GCP deployment scripts

---

## File Comparison Commands Used

```bash
# Find common files
comm -12 <(find . -maxdepth 1 -type f ! -name "CLAUDE.md" -exec basename {} \; | sort) \
         <(find ihep -maxdepth 1 -type f -exec basename {} \; | sort)

# Generate diffs
diff -u ./package.json ./ihep/package.json
diff -u ./Dockerfile ./ihep/Dockerfile
diff -u ./deployment-automation.hcl ./ihep/deployment-automation.hcl
diff -u ./secrets.sh ./ihep/secrets.sh
```
