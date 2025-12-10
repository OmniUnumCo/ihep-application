#!/bin/bash

# IHEP Security Quick Fix Script
# Addresses critical security vulnerabilities

echo "🔒 IHEP Security Quick Fix"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running from correct directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Must run from project root directory${NC}"
    exit 1
fi

echo "📋 This script will:"
echo "  1. Generate secure secrets"
echo "  2. Create/update .env files"
echo "  3. Generate SSL certificates for development"
echo "  4. Update configuration files"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

echo ""
echo "🔐 Step 1: Generating Secure Secrets"
echo "======================================"

# Generate SESSION_SECRET
SESSION_SECRET=$(openssl rand -base64 32)
echo -e "${GREEN}✅ Generated SESSION_SECRET${NC}"

# Generate JWT_SECRET
JWT_SECRET=$(openssl rand -base64 32)
echo -e "${GREEN}✅ Generated JWT_SECRET${NC}"

# Generate database password
DB_PASSWORD=$(openssl rand -base64 16)
echo -e "${GREEN}✅ Generated DB_PASSWORD${NC}"

echo ""
echo "📝 Step 2: Updating Environment Files"
echo "======================================"

# Update root .env.local
cat > .env.local << EOF
# Authentication Secrets (Generated: $(date))
SESSION_SECRET=${SESSION_SECRET}
NEXTAUTH_SECRET=${SESSION_SECRET}
NEXTAUTH_URL=http://localhost:3000

# External API Keys (Update these manually)
OPENAI_API_KEY=your-openai-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-phone-number

# Database
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@localhost:5432/ihep

# Node Environment
NODE_ENV=development
EOF

echo -e "${GREEN}✅ Updated .env.local${NC}"

# Update backend .env
cat > applications/.env << EOF
# Generated: $(date)

# JWT Authentication
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ihep
DB_USER=postgres
DB_PASSWORD=${DB_PASSWORD}

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

# Environment
FLASK_ENV=development
NODE_ENV=development
EOF

echo -e "${GREEN}✅ Updated applications/.env${NC}"

echo ""
echo "🔑 Step 3: Generating SSL Certificates (Development)"
echo "====================================================="

# Create certs directory
mkdir -p .certs

# Check if mkcert is installed
if command -v mkcert &> /dev/null; then
    echo "Using mkcert to generate trusted certificates..."
    cd .certs
    mkcert -install
    mkcert localhost 127.0.0.1 ::1
    mv localhost+2.pem cert.pem 2>/dev/null || true
    mv localhost+2-key.pem key.pem 2>/dev/null || true
    cd ..
    echo -e "${GREEN}✅ Generated trusted SSL certificates${NC}"
else
    echo "mkcert not found. Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout .certs/key.pem \
        -out .certs/cert.pem \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=IHEP/CN=localhost"
    echo -e "${YELLOW}⚠️  Self-signed certificate generated (browser will show warning)${NC}"
    echo "    Install mkcert for trusted certificates: brew install mkcert"
fi

echo ""
echo "⚙️  Step 4: Updating Configuration Files"
echo "========================================"

# Create HTTPS server config for Next.js
cat > server.mjs << 'EOF'
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

echo -e "${GREEN}✅ Created HTTPS server configuration${NC}"

# Update package.json to add dev:secure script
if command -v jq &> /dev/null; then
    jq '.scripts["dev:secure"] = "node server.mjs"' package.json > package.json.tmp && mv package.json.tmp package.json
    echo -e "${GREEN}✅ Added dev:secure script to package.json${NC}"
else
    echo -e "${YELLOW}⚠️  jq not found. Manually add to package.json:${NC}"
    echo '    "dev:secure": "node server.mjs"'
fi

echo ""
echo "🔒 Step 5: Creating .gitignore Entries"
echo "======================================"

# Ensure secrets are not committed
if ! grep -q ".certs/" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# Security files (added by security fix script)
.certs/
.env.local
applications/.env
**/secrets.json
**/*-key.pem
**/*.key
EOF
    echo -e "${GREEN}✅ Updated .gitignore${NC}"
else
    echo -e "${YELLOW}⚠️  .gitignore already contains security entries${NC}"
fi

echo ""
echo "✅ Security Quick Fix Complete!"
echo "==============================="
echo ""
echo "📋 Generated Files:"
echo "   .env.local           - Root environment with secrets"
echo "   applications/.env    - Backend environment"
echo "   .certs/cert.pem      - SSL certificate"
echo "   .certs/key.pem       - SSL private key"
echo "   server.mjs           - HTTPS server for Next.js"
echo ""
echo "🔐 Generated Secrets (SAVE THESE SECURELY):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SESSION_SECRET: ${SESSION_SECRET}"
echo "JWT_SECRET: ${JWT_SECRET}"
echo "DB_PASSWORD: ${DB_PASSWORD}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Important: Update these manually in .env.local:"
echo "   - OPENAI_API_KEY"
echo "   - SENDGRID_API_KEY"
echo "   - TWILIO credentials"
echo "   - GCP_PROJECT (in applications/.env)"
echo ""
echo "🚀 Next Steps:"
echo "   1. Review generated .env files"
echo "   2. Update API keys with real values"
echo "   3. Run with HTTPS: npm run dev:secure"
echo "   4. Update database password in PostgreSQL"
echo ""
echo "📚 For full security checklist, see:"
echo "   SECURITY_AUDIT_REPORT.md"
echo ""
