# IHEP - Quick Start Guide

**Complete setup guide for frontend and backend**

---

## 🚀 Quick Start (Choose One)

### Option 1: Docker (Recommended)
```bash
cd applications
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```

### Option 2: Manual Startup Script
```bash
cd applications
cp .env.example .env
# Edit .env with your configuration
./start-backend.sh
```

### Option 3: Full Stack Development
```bash
# Terminal 1 - Backend
cd applications
./start-backend.sh

# Terminal 2 - Frontend
npm run dev
```

---

## 📦 What You Have

### ✅ Frontend (Next.js 15)
- **Location**: `src/app/`
- **Port**: 3000
- **Status**: ✅ Build successful
- **Tests**: ✅ All passing
- **Command**: `npm run dev`

### ✅ Backend (Python Flask)
- **Location**: `applications/backend/`
- **Port**: 8080 (Healthcare API)
- **Status**: ✅ Configured
- **Dependencies**: Listed in requirements.txt
- **Command**: `./start-backend.sh`

### ✅ Simulation Library
- **Location**: `lib/simulation/`
- **Tests**: ✅ 57/57 passing
- **Status**: Production ready
- **Import**: `import { initEKF, cbfAdjust } from '@/lib/simulation'`

### ✅ Authentication
- **NextAuth**: Configured
- **Session**: Server & client helpers
- **Status**: ✅ Working

---

## 🔧 Setup Steps

### 1. Install Dependencies

#### Frontend
```bash
npm install
```

#### Backend
```bash
cd applications/backend
python3 -m venv venv
source venv/bin/activate  # or: . venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Root directory
cp .env.example .env.local

# Backend
cd applications
cp .env.example .env

# Edit both files with your configuration
```

### 3. Start Services

#### With Docker
```bash
cd applications
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Without Docker
```bash
# Start PostgreSQL (install first if needed)
brew services start postgresql@15  # macOS
# or
service postgresql start  # Linux/FreeBSD

# Start Redis
brew services start redis  # macOS
# or
service redis start  # Linux/FreeBSD

# Start Backend
cd applications
./start-backend.sh

# Start Frontend (new terminal)
npm run dev
```

---

## 🌐 Access Points

Once running:

- **Frontend**: http://localhost:3000
- **Healthcare API**: http://localhost:8080
- **Auth Service**: http://localhost:8081
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## ✅ Verification

### Test Frontend
```bash
# Build
npm run build

# Type check
npm run check

# Tests
npm run test:simulation
```

### Test Backend
```bash
# Health check
curl http://localhost:8080/health

# API test
curl -X POST http://localhost:8080/api/synergy/score \
  -H "Content-Type: application/json" \
  -d '{"clinical_adherence": 85, "passive_income_generated": 60}'
```

### Test Database
```bash
psql -h localhost -U postgres -d ihep -c "SELECT version();"
```

### Test Redis
```bash
redis-cli ping
# Should return: PONG
```

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :3000  # Frontend
lsof -i :8080  # Backend

# Kill the process
kill -9 <PID>
```

### Dependencies Issues
```bash
# Frontend
rm -rf node_modules package-lock.json
npm install

# Backend
pip install --upgrade -r requirements.txt
```

### Database Connection Failed
```bash
# Check if running
docker-compose ps postgres

# Or native
service postgresql status

# Start if needed
docker-compose up -d postgres
```

---

## 📚 Documentation

- **Backend Setup**: `BACKEND_SETUP_GUIDE.md`
- **Auth Fix**: `AUTH_FIX_SUMMARY.md`
- **Test Report**: `TEST_REPORT.md`
- **Simulation Library**: `lib/simulation/README.md`

---

## 🎯 For Jail Shell Deployment

### FreeBSD Jail Specific

```bash
# 1. Install dependencies
pkg update
pkg install python314 py314-pip postgresql15-client redis

# 2. Setup Python environment
python3.14 -m venv /app/venv
. /app/venv/bin/activate

# 3. Install requirements
cd /app/ihep/applications/backend
pip install -r requirements.txt

# 4. Configure to connect to host services
# Edit .env:
DB_HOST=192.168.1.1  # Host IP
REDIS_HOST=192.168.1.1

# 5. Start backend
cd /app/ihep/applications
./start-backend.sh
```

---

## ⚙️ Environment Variables

### Required (Minimal)
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ihep
DB_USER=postgres
DB_PASSWORD=your-password
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=$(openssl rand -base64 32)
```

### Optional (Full Features)
```bash
GCP_PROJECT=your-project-id
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
TWILIO_ACCOUNT_SID=AC...
```

---

## 🚦 Current Status

### ✅ Completed
- [x] Frontend build working
- [x] Authentication configured
- [x] Simulation library tested (57/57)
- [x] Backend structure ready
- [x] Docker configuration complete
- [x] Startup scripts created
- [x] Documentation complete

### 📋 Ready for Deployment
- [x] Development environment
- [x] Docker environment
- [x] Jail shell environment
- [x] Production environment (with additional config)

---

## 🎉 You're Ready!

The application is **fully configured** and ready to run in:
- ✅ Local development
- ✅ Docker containers
- ✅ Jail shell
- ✅ Production (with env vars)

**Next Step**: Choose your deployment method and run the appropriate commands above!
