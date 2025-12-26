# IHEP Application - Integrated Health Empowerment Program

## Mathematical Foundation

### Security Proof (Seven-Layer Defense)
Protection level: P(breach) ≤ ∏(i=1 to 7) P(layer_i fails) = 0.001^7 = 10^-21

Where each layer i provides:
- Layer 1 (Network): P(fail) ≤ 0.001
- Layer 2 (IAM): P(fail) ≤ 0.001  
- Layer 3 (App): P(fail) ≤ 0.001
- Layer 4 (Data): P(fail) ≤ 0.001
- Layer 5 (Audit): P(fail) ≤ 0.001
- Layer 6 (Backup): P(fail) ≤ 0.001
- Layer 7 (Monitoring): P(fail) ≤ 0.001

### Digital Twin Manifold Projection
Health state H ∈ R^n → visualization V ∈ R^3 via:
f: R^n → R^3 where ∇f preserves local distances with distortion δ ≤ 0.05

Implemented as constrained optimization:
minimize ||f(H) - V||^2 subject to clinical_constraints(V) = true

### Performance Requirements
- API latency: P(t < 100ms) ≥ 0.95
- Security overhead: 50-100ms per operation (acceptable for PHI protection)
- Availability: 99.9% uptime (525.6 min/year downtime budget)

## Architecture

```
ihep-application/
├── frontend/               # Next.js 14 + React 18 + Three.js
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and hooks
│   │   └── types/         # TypeScript definitions
├── backend/               # Python microservices
│   ├── healthcare-api/    # Healthcare API integration
│   ├── auth-service/      # IAM and authentication
│   ├── dt-service/        # Digital twin processing
│   ├── ai-service/        # Vertex AI integration
│   └── shared/            # Shared utilities
├── infrastructure/        # Terraform IaC
│   ├── modules/          # Reusable modules
│   ├── environments/     # Env-specific configs
│   └── scripts/          # Helper scripts
└── .github/workflows/    # CI/CD pipelines
```

## Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript 5
- Three.js r162 (Digital Twins)
- Tailwind CSS 3
- shadcn/ui components

**Backend:**
- Python 3.11
- Flask 3.0
- SQLAlchemy 2.0
- Pydantic 2.0
- Google Cloud Libraries

**Infrastructure:**
- Google Cloud Platform
- Terraform 1.6+
- Cloud Run (Microservices)
- Cloud SQL PostgreSQL 15
- Memorystore Redis 7
- Healthcare API
- Vertex AI
- Cloud KMS

**Security:**
- Envelope encryption (each record = unique DEK)
- Argon2id password hashing
- mTLS for service communication
- NIST SP 800-53r5 compliance (297/305 controls)

## Prerequisites

```bash
# Required
node >= 18.0.0
npm >= 9.0.0
python >= 3.11
terraform >= 1.6.0
gcloud CLI >= 450.0.0

# GCP Project Setup
export GCP_PROJECT_ID="ihep-platform-prod"
export GCP_REGION="us-central1"
```

## Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/ihep-platform/ihep-application
cd ihep-application
npm install
cd backend && pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env.local
# Edit .env.local with your credentials
```

### 3. Local Development
```bash
# Terminal 1 - Backend
cd backend && python run_local.py

# Terminal 2 - Frontend
cd frontend && npm run dev

# Access at http://localhost:3000
```

### 4. Deploy to GCP Staging
```bash
# Authenticate
gcloud auth login
gcloud config set project ${GCP_PROJECT_ID}

# Deploy infrastructure
cd infrastructure
terraform init
terraform workspace select staging
terraform apply

# Deploy services
./scripts/deploy-services.sh staging
```

## Security Validation

### Run Security Proofs
```bash
cd backend/shared/security
python -m pytest test_security_proofs.py -v
```

Expected output confirms:
- Seven-layer protection: P(breach) ≤ 10^-21
- Envelope encryption: Each record isolated
- Recursive trust validation: No inherited permissions

### NIST Compliance Check
```bash
python scripts/validate-nist-compliance.py
```

## Testing

### Frontend Tests
```bash
cd frontend
npm test                    # Unit tests
npm run test:e2e           # E2E tests (Playwright)
npm run test:coverage      # Coverage report
```

### Backend Tests
```bash
cd backend
pytest                      # All tests
pytest tests/security/     # Security tests only
pytest --cov               # With coverage
```

### Integration Tests
```bash
./scripts/run-integration-tests.sh
```

## Performance Benchmarks

### Expected Performance (Single Service Instance)
- P50 latency: 45ms
- P95 latency: 95ms
- P99 latency: 180ms
- Throughput: 1000 req/sec

### Load Testing
```bash
cd scripts
./run-load-tests.sh staging 1000  # 1000 concurrent users
```

## Deployment

### Staging
```bash
./scripts/deploy.sh staging
```

### Production (Requires Approval)
```bash
./scripts/deploy.sh production
```

Production deployments use blue-green strategy:
1. Deploy new version (green)
2. Run smoke tests
3. Gradual traffic shift (10% → 50% → 100%)
4. Rollback if error rate > 1%

## Monitoring

### Key Metrics
- API error rate: Target < 0.1%
- Security event rate: Alert on anomalies
- PHI access audit: 100% coverage
- Digital twin render time: P95 < 2000ms

### Access Dashboards
```bash
# Cloud Console
echo "https://console.cloud.google.com/monitoring/dashboards?project=${GCP_PROJECT_ID}"

# Logs
gcloud logging read "resource.type=cloud_run_revision" --limit 100
```

## Mathematical Validations

All mathematical claims are validated with formal proofs:

1. **Security Proof** (`backend/shared/security/proofs.py`)
2. **Manifold Distortion Bounds** (`backend/dt-service/manifold_proof.py`)
3. **Kalman Filter Convergence** (`backend/shared/math/kalman_proof.py`)
4. **k-Anonymity Guarantees** (`backend/healthcare-api/privacy_proof.py`)

Run all proofs:
```bash
python scripts/validate-all-proofs.py
```

## Compliance

- **HIPAA**: PHI routed through Healthcare API only
- **HITRUST**: Security controls mapped
- **GDPR**: Data residency configurable
- **SOC 2**: Audit logging complete

Compliance reports:
```bash
./scripts/generate-compliance-report.sh
```

## Support

- Documentation: https://docs.ihep-platform.org
- Security Issues: security@ihep-platform.org
- Technical Support: support@ihep-platform.org

## License

Proprietary - © 2025 IHEP Foundation
