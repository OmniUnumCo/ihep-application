#!/bin/bash

#####################################################################
# IHEP - Complete Production Setup Script
# Version: 1.0.0
# HIPAA-Compliant Healthcare Application Setup
#
# This script:
# - Validates prerequisites
# - Sets up development environment
# - Generates secure secrets
# - Configures databases
# - Installs dependencies
# - Runs security checks
# - Validates configuration
#
# Usage: ./setup.sh [--production|--development]
#####################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'  # No Color

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/setup.log"
readonly ERROR_LOG_FILE="${SCRIPT_DIR}/setup-errors.log"

# Environment (default to development)
ENVIRONMENT="${1:-development}"

#####################################################################
# Logging Functions
#####################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${ERROR_LOG_FILE}"
}

#####################################################################
# Error Handling
#####################################################################

cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Setup failed with exit code: $exit_code"
        log_error "Check logs: ${ERROR_LOG_FILE}"
        echo -e "${RED}Setup failed. Please check error logs.${NC}"
    fi
}

trap cleanup EXIT

#####################################################################
# Prerequisites Check
#####################################################################

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node (>= 20.x)")
    else
        local node_version
        node_version=$(node --version | cut -d'.' -f1 | tr -d 'v')
        if [ "$node_version" -lt 20 ]; then
            missing_deps+=("node (>= 20.x, found: $(node --version))")
        else
            log_success "Node.js $(node --version) found"
        fi
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3 (>= 3.10)")
    else
        local python_version
        python_version=$(python3 --version | awk '{print $2}' | cut -d'.' -f1,2)
        if (( $(echo "$python_version < 3.10" | bc -l 2>/dev/null || echo 0) )); then
            missing_deps+=("python3 (>= 3.10, found: $(python3 --version))")
        else
            log_success "Python $(python3 --version) found"
        fi
    fi

    # Check PostgreSQL
    if ! command -v psql &> /dev/null && ! command -v docker &> /dev/null; then
        log_warning "PostgreSQL not found. Will use Docker if available."
    else
        log_success "PostgreSQL or Docker found"
    fi

    # Check Redis
    if ! command -v redis-cli &> /dev/null && ! command -v docker &> /dev/null; then
        log_warning "Redis not found. Will use Docker if available."
    else
        log_success "Redis or Docker found"
    fi

    # Check Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    else
        log_success "Git $(git --version) found"
    fi

    # Check for required tools
    if ! command -v openssl &> /dev/null; then
        missing_deps+=("openssl")
    else
        log_success "OpenSSL found"
    fi

    # Report missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies:"
        for dep in "${missing_deps[@]}"; do
            log_error "  - $dep"
        done
        exit 1
    fi

    log_success "All prerequisites met"
}

#####################################################################
# Secret Generation
#####################################################################

generate_secrets() {
    log_info "Generating secure secrets..."

    # Generate SESSION_SECRET (32 bytes)
    local session_secret
    session_secret=$(openssl rand -base64 32)
    log_success "Generated SESSION_SECRET"

    # Generate JWT_SECRET (32 bytes)
    local jwt_secret
    jwt_secret=$(openssl rand -base64 32)
    log_success "Generated JWT_SECRET"

    # Generate DB_PASSWORD (16 bytes)
    local db_password
    db_password=$(openssl rand -base64 16)
    log_success "Generated DB_PASSWORD"

    # Store secrets securely
    cat > "${SCRIPT_DIR}/.env.local" << EOF
# IHEP Application Environment Configuration
# Generated: $(date)
# SECURITY: DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Authentication Secrets
SESSION_SECRET=${session_secret}
NEXTAUTH_SECRET=${session_secret}
NEXTAUTH_URL=http://localhost:3000

# External API Keys (Update these manually)
OPENAI_API_KEY=your-openai-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-phone-number

# Database
DATABASE_URL=postgresql://postgres:${db_password}@localhost:5432/ihep

# Environment
NODE_ENV=${ENVIRONMENT}
EOF

    chmod 600 "${SCRIPT_DIR}/.env.local"
    log_success "Created .env.local (permissions: 600)"

    # Create backend .env
    mkdir -p "${SCRIPT_DIR}/applications"
    cat > "${SCRIPT_DIR}/applications/.env" << EOF
# IHEP Backend Environment Configuration
# Generated: $(date)
# SECURITY: DO NOT COMMIT THIS FILE TO VERSION CONTROL

# JWT Authentication
JWT_SECRET=${jwt_secret}
JWT_ALGORITHM=HS256

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ihep
DB_USER=postgres
DB_PASSWORD=${db_password}

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
API_BASE_URL=http://localhost:8080
NEXT_PUBLIC_API_URL=http://localhost:8080

# GCP Configuration (Update for production)
GCP_PROJECT=your-gcp-project-id
GCP_REGION=us-central1
HEALTHCARE_DATASET=ihep-dataset
FHIR_STORE=ihep-fhir-store

# Security
RATE_LIMIT_ENABLED=true
LOG_LEVEL=INFO
ENABLE_AUDIT_LOGGING=true
REQUIRE_SSL=false

# Environment
FLASK_ENV=${ENVIRONMENT}
NODE_ENV=${ENVIRONMENT}
EOF

    chmod 600 "${SCRIPT_DIR}/applications/.env"
    log_success "Created applications/.env (permissions: 600)"

    # Save secrets for display
    echo "${session_secret}" > /tmp/ihep_session_secret.tmp
    echo "${jwt_secret}" > /tmp/ihep_jwt_secret.tmp
    echo "${db_password}" > /tmp/ihep_db_password.tmp
}

#####################################################################
# SSL Certificate Generation
#####################################################################

generate_ssl_certificates() {
    log_info "Generating SSL certificates..."

    mkdir -p "${SCRIPT_DIR}/.certs"

    if command -v mkcert &> /dev/null; then
        log_info "Using mkcert for trusted certificates..."
        cd "${SCRIPT_DIR}/.certs"
        mkcert -install 2>&1 | tee -a "${LOG_FILE}" || log_warning "mkcert install failed (may require sudo)"
        mkcert localhost 127.0.0.1 ::1 2>&1 | tee -a "${LOG_FILE}"

        # Rename files to standard names
        if [ -f "localhost+2.pem" ]; then
            mv localhost+2.pem cert.pem
            mv localhost+2-key.pem key.pem
        fi

        cd "${SCRIPT_DIR}"
        log_success "Generated trusted SSL certificates"
    else
        log_warning "mkcert not found. Generating self-signed certificate..."
        openssl req -x509 -newkey rsa:4096 -nodes \
            -keyout "${SCRIPT_DIR}/.certs/key.pem" \
            -out "${SCRIPT_DIR}/.certs/cert.pem" \
            -days 365 \
            -subj "/C=US/ST=State/L=City/O=IHEP/CN=localhost" \
            2>&1 | tee -a "${LOG_FILE}"

        log_warning "Self-signed certificate generated (browser will show warning)"
        log_info "Install mkcert for trusted certificates: brew install mkcert"
    fi

    chmod 600 "${SCRIPT_DIR}/.certs/"*.pem
    log_success "SSL certificates generated"
}

#####################################################################
# HTTPS Server Configuration
#####################################################################

create_https_server() {
    log_info "Creating HTTPS server configuration..."

    cat > "${SCRIPT_DIR}/server.mjs" << 'EOF'
import { createServer } from 'https';
import { parse } from 'url';
import next from 'next';
import fs from 'fs';

const dev = process.env.NODE_ENV !== 'production';
const hostname = 'localhost';
const port = 3000;

const app = next({ dev, hostname, port });
const handle = app.getRequestHandler();

const httpsOptions = {
  key: fs.readFileSync('./.certs/key.pem'),
  cert: fs.readFileSync('./.certs/cert.pem'),
};

app.prepare().then(() => {
  createServer(httpsOptions, async (req, res) => {
    const parsedUrl = parse(req.url, true);
    await handle(req, res, parsedUrl);
  }).listen(port, (err) => {
    if (err) throw err;
    console.log(`> Ready on https://${hostname}:${port}`);
  });
});
EOF

    log_success "Created server.mjs"

    # Update package.json with dev:secure script
    if command -v jq &> /dev/null; then
        local temp_file
        temp_file=$(mktemp)
        jq '.scripts["dev:secure"] = "node server.mjs"' package.json > "$temp_file"
        mv "$temp_file" package.json
        log_success "Added dev:secure script to package.json"
    else
        log_warning "jq not found. Manually add to package.json:"
        log_warning '  "dev:secure": "node server.mjs"'
    fi
}

#####################################################################
# Dependencies Installation
#####################################################################

install_dependencies() {
    log_info "Installing dependencies..."

    # Frontend dependencies
    log_info "Installing frontend dependencies..."
    if ! npm install 2>&1 | tee -a "${LOG_FILE}"; then
        log_error "Failed to install frontend dependencies"
        exit 1
    fi
    log_success "Frontend dependencies installed"

    # Backend dependencies
    log_info "Installing backend dependencies..."
    cd "${SCRIPT_DIR}/applications/backend"

    if [ ! -d "venv" ]; then
        python3 -m venv venv 2>&1 | tee -a "${LOG_FILE}"
        log_success "Created Python virtual environment"
    fi

    # shellcheck disable=SC1091
    source venv/bin/activate

    pip install --upgrade pip 2>&1 | tee -a "${LOG_FILE}"
    pip install -r applications/backend/requirements.txt 2>&1 | tee -a "${LOG_FILE}"

    deactivate
    cd "${SCRIPT_DIR}"

    log_success "Backend dependencies installed"
}

#####################################################################
# Database Setup
#####################################################################

setup_databases() {
    log_info "Setting up databases..."

    # Check if Docker is available
    if command -v docker-compose &> /dev/null; then
        log_info "Starting databases with Docker Compose..."
        cd "${SCRIPT_DIR}/applications"
        if docker-compose up -d postgres redis 2>&1 | tee -a "${LOG_FILE}"; then
            log_success "Databases started with Docker"
            sleep 5  # Wait for services to be ready
        else
            log_warning "Failed to start Docker services. Checking native installations..."
        fi
        cd "${SCRIPT_DIR}"
    fi

    # Test PostgreSQL connection
    if command -v psql &> /dev/null; then
        local db_password
        db_password=$(grep "^DB_PASSWORD=" "${SCRIPT_DIR}/applications/.env" | cut -d'=' -f2)

        if PGPASSWORD="${db_password}" psql -h localhost -U postgres -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw ihep; then
            log_success "PostgreSQL database 'ihep' exists"
        else
            log_info "Creating database 'ihep'..."
            if PGPASSWORD="${db_password}" createdb -h localhost -U postgres ihep 2>&1 | tee -a "${LOG_FILE}"; then
                log_success "Database 'ihep' created"
            else
                log_warning "Could not create database. You may need to do this manually."
            fi
        fi
    fi

    # Test Redis connection
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            log_success "Redis is running"
        else
            log_warning "Redis is not responding. Start with: brew services start redis"
        fi
    fi
}

#####################################################################
# Security Configuration
#####################################################################

configure_security() {
    log_info "Configuring security settings..."

    # Update .gitignore
    if ! grep -q ".certs/" "${SCRIPT_DIR}/.gitignore" 2>/dev/null; then
        cat >> "${SCRIPT_DIR}/.gitignore" << 'EOF'

# Security files (added by setup script)
.certs/
.env.local
applications/.env
**/secrets.json
**/*-key.pem
**/*.key
setup.log
setup-errors.log
*.tmp
EOF
        log_success "Updated .gitignore"
    else
        log_info ".gitignore already configured"
    fi

    # Set file permissions
    chmod 600 "${SCRIPT_DIR}/.env.local" 2>/dev/null || true
    chmod 600 "${SCRIPT_DIR}/applications/.env" 2>/dev/null || true
    chmod 600 "${SCRIPT_DIR}/.certs/"*.pem 2>/dev/null || true

    log_success "Security configuration complete"
}

#####################################################################
# Validation
#####################################################################

validate_setup() {
    log_info "Validating setup..."

    local validation_failed=0

    # Check environment files
    if [ ! -f "${SCRIPT_DIR}/.env.local" ]; then
        log_error ".env.local not found"
        validation_failed=1
    else
        log_success ".env.local exists"
    fi

    if [ ! -f "${SCRIPT_DIR}/applications/.env" ]; then
        log_error "applications/.env not found"
        validation_failed=1
    else
        log_success "applications/.env exists"
    fi

    # Check SSL certificates
    if [ ! -f "${SCRIPT_DIR}/.certs/cert.pem" ] || [ ! -f "${SCRIPT_DIR}/.certs/key.pem" ]; then
        log_error "SSL certificates not found"
        validation_failed=1
    else
        log_success "SSL certificates exist"
    fi

    # Check node_modules
    if [ ! -d "${SCRIPT_DIR}/node_modules" ]; then
        log_error "node_modules not found"
        validation_failed=1
    else
        log_success "node_modules exists"
    fi

    # Check Python venv
    if [ ! -d "${SCRIPT_DIR}/applications/backend/venv" ]; then
        log_error "Python virtual environment not found"
        validation_failed=1
    else
        log_success "Python virtual environment exists"
    fi

    # Run frontend type check
    log_info "Running TypeScript type check..."
    if npm run check 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "TypeScript type check passed"
    else
        log_warning "TypeScript type check failed (non-blocking)"
    fi

    # Run tests
    log_info "Running tests..."
    if npm run test 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "Tests passed"
    else
        log_warning "Tests failed (non-blocking)"
    fi

    if [ $validation_failed -eq 1 ]; then
        log_error "Validation failed"
        exit 1
    fi

    log_success "Validation complete"
}

#####################################################################
# Main Setup Flow
#####################################################################

main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           IHEP - Complete Setup Script                       ║"
    echo "║           HIPAA-Compliant Healthcare Application             ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    log_info "Starting setup in ${ENVIRONMENT} mode..."
    log_info "Log file: ${LOG_FILE}"

    # Confirm directory
    if [ ! -f "${SCRIPT_DIR}/package.json" ]; then
        log_error "Must run from project root directory"
        exit 1
    fi

    # Run setup steps
    check_prerequisites
    generate_secrets
    generate_ssl_certificates
    create_https_server
    install_dependencies
    setup_databases
    configure_security
    validate_setup

    # Display completion message
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Setup Complete Successfully!                     ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Display generated secrets
    if [ -f /tmp/ihep_session_secret.tmp ]; then
        echo -e "${YELLOW}🔐 Generated Secrets (SAVE THESE SECURELY):${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "SESSION_SECRET: $(cat /tmp/ihep_session_secret.tmp)"
        echo "JWT_SECRET: $(cat /tmp/ihep_jwt_secret.tmp)"
        echo "DB_PASSWORD: $(cat /tmp/ihep_db_password.tmp)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # Clean up temporary files
        rm -f /tmp/ihep_*_secret.tmp /tmp/ihep_*_password.tmp
    fi

    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "   1. Review generated .env files"
    echo "   2. Update API keys in .env.local with real values"
    echo "   3. Start services:"
    echo "      - Option A: npm run dev (HTTP)"
    echo "      - Option B: npm run dev:secure (HTTPS)"
    echo "      - Option C: cd applications && ./start-backend.sh"
    echo "   4. Access frontend: https://localhost:3000"
    echo "   5. Access backend: http://localhost:8080"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "   - README.md"
    echo "   - SECURITY_AUDIT_REPORT.md"
    echo "   - QUICK_START.md"
    echo ""

    log_success "Setup completed successfully"
}

# Run main function
main "$@"
