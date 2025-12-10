# Backend Setup Guide - IHEP Application

**For running in jail shell, Docker, or any isolated environment**

---

## Quick Assessment

### ✅ What's Already Configured

1. **Python Backend** - Flask-based microservices architecture
2. **Dependencies** - Complete requirements.txt with all packages
3. **Docker Configuration** - docker-compose.yml for containerized deployment
4. **Environment Template** - .env.example with all required variables
5. **Multiple Services**:
   - Healthcare API (Port 8080)
   - Auth Service (Port 8081)
   - Financial Twin Service
   - Main Application

### ⚠️ What's Missing for Jail Shell Deployment

1. Environment variables need to be set
2. Python virtual environment setup
3. Database initialization
4. GCP credentials (if using Google Cloud services)

---

## Prerequisites

### System Requirements
- Python 3.10+ ✅ (You have 3.14)
- pip ✅ (Installed)
- PostgreSQL 15+ (or Docker)
- Redis 7+ (or Docker)

### Optional (for production)
- Docker & Docker Compose
- Google Cloud SDK (for GCP services)
- SSL certificates

---

## Setup Options

## Option 1: Docker Compose (Recommended for Jail Shell)

### Step 1: Set Environment Variables
```bash
cd /Users/nexus1/Documents/ihep-app/ihep/applications

# Copy example env file
cp .env.example .env

# Edit with your values
nano .env  # or vi .env
```

### Step 2: Start Services
```bash
# Start all services (PostgreSQL, Redis, APIs)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f healthcare-api
```

### Step 3: Verify Services
```bash
# Test healthcare API
curl http://localhost:8080/health

# Test auth service
curl http://localhost:8081/health

# Test database connection
docker-compose exec postgres psql -U postgres -d ihep -c "SELECT version();"
```

### Step 4: Stop Services
```bash
docker-compose down        # Stop services
docker-compose down -v     # Stop and remove volumes
```

---

## Option 2: Native Python (For Jail Shell without Docker)

### Step 1: Create Virtual Environment
```bash
cd /Users/nexus1/Documents/ihep-app/ihep/applications/backend

# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (FreeBSD jail shell)
. venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 3: Setup PostgreSQL (if not using Docker)
```bash
# Install PostgreSQL (FreeBSD)
pkg install postgresql15-server

# Initialize database
service postgresql initdb

# Start PostgreSQL
service postgresql start

# Create database
psql -U postgres -c "CREATE DATABASE ihep;"
psql -U postgres -c "CREATE USER ihep_user WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ihep TO ihep_user;"
```

### Step 4: Setup Redis (if not using Docker)
```bash
# Install Redis (FreeBSD)
pkg install redis

# Start Redis
service redis start

# Verify
redis-cli ping  # Should return PONG
```

### Step 5: Configure Environment
```bash
cd /Users/nexus1/Documents/ihep-app/ihep/applications

# Create .env file
cat > .env << 'EOF'
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ihep
DB_USER=postgres
DB_PASSWORD=your-secure-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256

# API
API_BASE_URL=http://localhost:8080

# Environment
FLASK_ENV=development
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true

# GCP (optional - only if using Google Cloud)
GCP_PROJECT=your-project-id
GCP_REGION=us-central1
EOF
```

### Step 6: Run Backend Services

#### Option A: Simple Flask App
```bash
cd /Users/nexus1/Documents/ihep-app/ihep/applications/backend

# Run main app
python app.py

# Or with gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

#### Option B: Healthcare API Service
```bash
cd /Users/nexus1/Documents/ihep-app/ihep/applications/backend/healthcare-api

# Run service
python app.py
```

#### Option C: All Services with Process Manager
```bash
# Install honcho (process manager)
pip install honcho

# Create Procfile
cat > Procfile << 'EOF'
healthcare: cd backend/healthcare-api && python app.py
auth: cd backend/auth-service && python app.py
EOF

# Run all services
honcho start
```

---

## Option 3: Quick Start Script (For Jail Shell)

Create a startup script:

```bash
cat > /Users/nexus1/Documents/ihep-app/ihep/applications/start-backend.sh << 'SCRIPT'
#!/bin/sh

echo "🚀 Starting IHEP Backend Services..."

# Set working directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "backend/venv/bin/activate" ]; then
    . backend/venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Creating..."
    cd backend
    python3 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found. Creating from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
    exit 1
fi

# Check database connection
echo "🔍 Checking database connection..."
psql -h ${DB_HOST:-localhost} -U ${DB_USER:-postgres} -d ${DB_NAME:-ihep} -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed. Please check your database is running."
    echo "   Run: docker-compose up -d postgres"
    exit 1
fi

# Check Redis connection
echo "🔍 Checking Redis connection..."
redis-cli -h ${REDIS_HOST:-localhost} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis connection successful"
else
    echo "❌ Redis connection failed. Please check Redis is running."
    echo "   Run: docker-compose up -d redis"
    exit 1
fi

# Start services
echo "🌐 Starting Healthcare API on port 8080..."
cd backend
python app.py &
BACKEND_PID=$!

echo "✅ Backend services started!"
echo "   Healthcare API: http://localhost:8080"
echo "   Process ID: $BACKEND_PID"
echo ""
echo "📝 Logs are being written to console"
echo "   Press Ctrl+C to stop all services"

# Wait for process
wait $BACKEND_PID
SCRIPT

# Make executable
chmod +x /Users/nexus1/Documents/ihep-app/ihep/applications/start-backend.sh
```

Then run:
```bash
./start-backend.sh
```

---

## Environment Variables Required

### Minimal Configuration (Development)
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ihep
DB_USER=postgres
DB_PASSWORD=devpassword

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET=$(openssl rand -base64 32)

# Environment
FLASK_ENV=development
```

### Full Configuration (Production)
```bash
# All the above PLUS:

# GCP Configuration
GCP_PROJECT=your-gcp-project-id
GCP_REGION=us-central1
HEALTHCARE_DATASET=ihep-dataset
FHIR_STORE=ihep-fhir-store
KMS_KEY_RING=ihep-keyring
KMS_CRYPTO_KEY=dek-wrapper-key

# External Services
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Security
SESSION_SECRET=$(openssl rand -base64 32)
RATE_LIMIT_ENABLED=true

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

---

## Testing the Backend

### Health Check
```bash
# Test if backend is running
curl http://localhost:8080/health

# Should return:
# {"status": "healthy", "timestamp": "..."}
```

### API Endpoints
```bash
# Test synergy score calculation
curl -X POST http://localhost:8080/api/synergy/score \
  -H "Content-Type: application/json" \
  -d '{"clinical_adherence": 85, "passive_income_generated": 60}'

# Test digital twin generation
curl -X POST http://localhost:8080/api/twin/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-123"}'
```

### Database Test
```bash
# Connect to database
psql -h localhost -U postgres -d ihep

# Run test query
SELECT version();
\dt  # List tables
\q   # Quit
```

---

## Jail Shell Specific Configuration

### FreeBSD Jail Setup
```bash
# In the jail shell:

# 1. Update package manager
pkg update

# 2. Install Python and dependencies
pkg install python314 py314-pip postgresql15-client redis

# 3. Set up Python virtual environment
python3.14 -m venv /app/venv
. /app/venv/bin/activate

# 4. Install requirements
pip install -r requirements.txt

# 5. Configure to connect to host services
# Edit .env to point to host IP instead of localhost
# DB_HOST=192.168.1.1  (host IP)
# REDIS_HOST=192.168.1.1
```

### Connecting to Host Database from Jail
```bash
# In host's pg_hba.conf, add:
# host    ihep    ihep_user    jail_ip/32    md5

# Restart PostgreSQL on host
service postgresql restart

# In jail, test connection
psql -h host_ip -U ihep_user -d ihep
```

---

## Troubleshooting

### Issue: Module Not Found
```bash
# Solution: Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Issue: Database Connection Refused
```bash
# Check if PostgreSQL is running
service postgresql status  # or: docker-compose ps

# Check connection
psql -h localhost -U postgres -l

# Check pg_hba.conf allows connections
cat /var/lib/postgresql/data/pg_hba.conf | grep "host"
```

### Issue: Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping

# Or check service
service redis status

# Or Docker
docker-compose ps redis
```

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8080  # or: sockstat -4 -l | grep 8080

# Kill process
kill -9 <PID>

# Or change port in app.py
# app.run(host='0.0.0.0', port=8081)
```

---

## Production Deployment Checklist

- [ ] Set all environment variables
- [ ] Use strong passwords and secrets
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Use production WSGI server (gunicorn)
- [ ] Set up database backups
- [ ] Configure GCP service account (if using GCP)
- [ ] Review security settings
- [ ] Set up CI/CD pipeline

---

## Summary

### ✅ Ready to Deploy
- Python 3.14 installed
- All dependencies listed in requirements.txt
- Docker Compose configuration ready
- Multiple deployment options available

### 🔧 Steps to Start

**Quickest (Docker)**:
```bash
cd applications
cp .env.example .env
# Edit .env with your values
docker-compose up -d
```

**Jail Shell (Native)**:
```bash
cd applications/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Start PostgreSQL and Redis
python app.py
```

**Production**:
```bash
gunicorn -w 4 -b 0.0.0.0:8080 --chdir backend app:app
```

---

## Additional Resources

- **Backend Code**: `/applications/backend/`
- **Docker Config**: `/applications/docker-compose.yml`
- **Environment Template**: `/applications/.env.example`
- **API Documentation**: (Add Swagger/OpenAPI docs)
- **Architecture Docs**: `/applications/IHEP_Complete_Architecture_v2.docx`

---

**Status**: ✅ Backend is configured and ready to deploy
**Next Steps**: Set environment variables and start services
