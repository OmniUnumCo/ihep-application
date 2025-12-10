╔══════════════════════════════════════════════════════════════════════════════╗
║                  IHEP DEPLOYMENT TOPOLOGY & INFRASTRUCTURE                   ║
║                        Google Cloud Platform Architecture                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                          GEOGRAPHIC DISTRIBUTION                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│  │  us-east1       │     │  us-central1    │     │  us-west1       │      │
│  │  (S. Carolina)  │     │  (Iowa)         │     │  (Oregon)       │      │
│  │                 │     │                 │     │                 │      │
│  │  NY/MA Hub      │     │  Primary Svcs   │     │  LA/SD Hub      │      │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘      │
│         │                        │                        │                 │
│         └────────────────────────┴────────────────────────┘                 │
│                                  │                                          │
│                    Global Load Balancer (Anycast)                           │
│                                  │                                          │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                      PRODUCTION ENVIRONMENT (us-central1)                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    VPC: ihep-production-vpc                         │    │
│  │                    CIDR: 10.0.0.0/16                                │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐    │    │
│  │  │  Subnet: services (10.0.1.0/24)                           │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │    │    │
│  │  │  │ Cloud Run    │ │ Cloud Run    │ │ Cloud Run    │     │    │    │
│  │  │  │ IAM Service  │ │ Twin Service │ │ Appt Service │     │    │    │
│  │  │  │              │ │              │ │              │     │    │    │
│  │  │  │ Min: 2       │ │ Min: 3       │ │ Min: 2       │     │    │    │
│  │  │  │ Max: 100     │ │ Max: 50      │ │ Max: 50      │     │    │    │
│  │  │  │ CPU: 1 core  │ │ CPU: 2 core  │ │ CPU: 1 core  │     │    │    │
│  │  │  │ RAM: 512Mi   │ │ RAM: 2Gi     │ │ RAM: 1Gi     │     │    │    │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘     │    │    │
│  │  │                                                            │    │    │
│  │  │  + 6 More Microservices...                                │    │    │
│  │  └───────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐    │    │
│  │  │  Subnet: data (10.0.2.0/24) - Private                     │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌────────────────────────────────────────────────┐       │    │    │
│  │  │  │  Cloud SQL PostgreSQL (Primary)                │       │    │    │
│  │  │  │  • Instance: db-custom-4-16384                 │       │    │    │
│  │  │  │  • Storage: 100GB SSD                          │       │    │    │
│  │  │  │  • Backup: Point-in-time (7 days)              │       │    │    │
│  │  │  │  • HA: Multi-zone with automatic failover      │       │    │    │
│  │  │  │  • Private IP only (no public access)          │       │    │    │
│  │  │  └───────────────┬────────────────────────────────┘       │    │    │
│  │  │                  │                                         │    │    │
│  │  │                  │ Replication                             │    │    │
│  │  │                  ▼                                         │    │    │
│  │  │  ┌────────────────────────────────────────────────┐       │    │    │
│  │  │  │  Cloud SQL Read Replica (us-east1)             │       │    │    │
│  │  │  │  • Async replication                           │       │    │    │
│  │  │  │  • Read-only queries                           │       │    │    │
│  │  │  │  • Disaster recovery                           │       │    │    │
│  │  │  └────────────────────────────────────────────────┘       │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌────────────────────────────────────────────────┐       │    │    │
│  │  │  │  Cloud Memorystore Redis (HA)                  │       │    │    │
│  │  │  │  • Memory: 5GB                                 │       │    │    │
│  │  │  │  • Version: Redis 7.0                          │       │    │    │
│  │  │  │  • Replication: Primary + Replica              │       │    │    │
│  │  │  │  • Auto-failover: < 60s                        │       │    │    │
│  │  │  └────────────────────────────────────────────────┘       │    │    │
│  │  └───────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐    │    │
│  │  │  Subnet: healthcare-api (10.0.3.0/24) - Isolated         │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌────────────────────────────────────────────────┐       │    │    │
│  │  │  │  Google Healthcare API (FHIR Store)            │       │    │    │
│  │  │  │  • Dataset: ihep-production                    │       │    │    │
│  │  │  │  • Store: patient-phi-fhir                     │       │    │    │
│  │  │  │  • Version: FHIR R4                            │       │    │    │
│  │  │  │  • Encryption: Google-managed keys             │       │    │    │
│  │  │  │  • IAM: Service accounts only                  │       │    │    │
│  │  │  │  • Audit: Cloud Logging                        │       │    │    │
│  │  │  └────────────────────────────────────────────────┘       │    │    │
│  │  └───────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          AI/ML INFRASTRUCTURE                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Vertex AI Workbench (Training)                                    │    │
│  │                                                                     │    │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                 │    │
│  │  │  Training Pipeline  │  │  Model Registry     │                 │    │
│  │  │  • GPU: A100 (8x)   │  │  • Adherence v1.2   │                 │    │
│  │  │  • Memory: 640GB    │  │  • Resistance v2.1  │                 │    │
│  │  │  • Storage: 5TB SSD │  │  • Risk Score v1.5  │                 │    │
│  │  └─────────────────────┘  └─────────────────────┘                 │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐  │    │
│  │  │  Vertex AI Prediction Endpoints                             │  │    │
│  │  │                                                              │  │    │
│  │  │  Endpoint: adherence-prediction                             │  │    │
│  │  │  • Model: adherence_model_v1.2                              │  │    │
│  │  │  • Traffic Split: v1.2 (90%), v1.1 (10%)                    │  │    │
│  │  │  • Instances: Min 3, Max 50                                 │  │    │
│  │  │  • Machine Type: n1-standard-4                              │  │    │
│  │  │  • GPU: None (CPU inference sufficient)                     │  │    │
│  │  │  • Latency SLA: < 100ms P99                                 │  │    │
│  │  └─────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                     SECURITY & COMPLIANCE INFRASTRUCTURE                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Cloud KMS (Key Management)                                        │    │
│  │                                                                     │    │
│  │  KeyRing: ihep-production                                          │    │
│  │  ├── CryptoKey: phi-data-key (AES-256)                             │    │
│  │  │   • Purpose: Encrypt PHI data encryption keys                   │    │
│  │  │   • Rotation: 90 days                                           │    │
│  │  │   • Protection: HSM                                             │    │
│  │  │                                                                  │    │
│  │  ├── CryptoKey: jwt-signing-key (RSA-4096)                         │    │
│  │  │   • Purpose: Sign authentication tokens                         │    │
│  │  │   • Rotation: 365 days                                          │    │
│  │  │                                                                  │    │
│  │  └── CryptoKey: audit-log-key (AES-256)                            │    │
│  │      • Purpose: Encrypt audit trail                                │    │
│  │      • Rotation: Never (immutability requirement)                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Secret Manager                                                     │    │
│  │                                                                     │    │
│  │  • Database passwords                                               │    │
│  │  • API keys (external services)                                    │    │
│  │  • Service account credentials                                     │    │
│  │  • Versioned (automatic rotation)                                  │    │
│  │  • Access logs (who accessed what secret when)                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Cloud Logging & Monitoring                                        │    │
│  │                                                                     │    │
│  │  Log Sinks:                                                         │    │
│  │  ├── Audit Logs → BigQuery (long-term analysis)                    │    │
│  │  ├── Application Logs → Cloud Storage (compliance archive)         │    │
│  │  └── Security Events → Pub/Sub → SIEM Integration                  │    │
│  │                                                                     │    │
│  │  Alerts:                                                            │    │
│  │  • PHI access outside business hours                               │    │
│  │  • Failed authentication attempts > 5/min                           │    │
│  │  • Database replication lag > 10s                                  │    │
│  │  • API error rate > 1%                                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          CI/CD PIPELINE FLOW                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Developer                 Cloud Source              Cloud Build            │
│  Workstation              Repositories                                      │
│      │                         │                          │                 │
│      │ 1. git push            │                          │                 │
│      └────────────────────────►│                          │                 │
│                                │                          │                 │
│                                │ 2. Trigger build         │                 │
│                                └─────────────────────────►│                 │
│                                                           │                 │
│                                      ┌────────────────────▼──────────┐     │
│                                      │  Build Steps:                 │     │
│                                      │  1. docker build              │     │
│                                      │  2. Unit tests (Go/Python)    │     │
│                                      │  3. Security scan             │     │
│                                      │  4. Push to GCR               │     │
│                                      │  5. Deploy canary (10%)       │     │
│                                      │  6. Wait + health checks      │     │
│                                      │  7. Promote to 100%           │     │
│                                      └────────────┬──────────────────┘     │
│                                                   │                         │
│                                                   │ 3. Deploy               │
│                                                   ▼                         │
│                                      ┌────────────────────────┐            │
│                                      │  Cloud Run Services    │            │
│                                      │  (Production)          │            │
│                                      └────────────────────────┘            │
│                                                                              │
│  Rollback Strategy:                                                         │
│  • Automatic: Error rate > 5% for 5 minutes                                │
│  • Manual: gcloud run services update-traffic --to-revisions=previous      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘