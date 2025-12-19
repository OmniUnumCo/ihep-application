#!/bin/bash
# IHEP Curriculum - Enterprise Test Environment Setup

set -e

echo "========================================="
echo "IHEP Curriculum - Test Environment Setup"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Generate secure environment variables
echo -e "${YELLOW}Generating secure test environment variables...${NC}"
export TEST_DB_PASSWORD="test_$(openssl rand -hex 16)"
export TEST_REDIS_PASSWORD="test_$(openssl rand -hex 16)"
export TEST_SECRET_KEY=$(openssl rand -hex 32)

# Save to .env.test
cat > .env.test << EOF
# Auto-generated test environment variables
# Generated: $(date)

TEST_DB_PASSWORD=${TEST_DB_PASSWORD}
TEST_REDIS_PASSWORD=${TEST_REDIS_PASSWORD}
TEST_SECRET_KEY=${TEST_SECRET_KEY}
ENVIRONMENT=test
LOG_LEVEL=DEBUG
PYTEST_WORKERS=8
COVERAGE_THRESHOLD=90

# Database
DATABASE_URL=postgresql://ihep_test_user:${TEST_DB_PASSWORD}@localhost:5433/ihep_curriculum_test

# Redis
REDIS_URL=redis://:${TEST_REDIS_PASSWORD}@localhost:6380/0

# API
API_BASE_URL=http://localhost:8001
EOF

echo -e "${GREEN}✓ Environment variables generated${NC}"

# Create test directories
echo -e "${YELLOW}Creating test directory structure...${NC}"
mkdir -p test-data/{postgres,redis,init-scripts,synthetic-users}
mkdir -p test-results/{coverage,performance,security,compliance}
mkdir -p load-tests
mkdir -p security-reports
mkdir -p test-infrastructure

echo -e "${GREEN}✓ Directories created${NC}"

# Check Docker is running
echo -e "${YELLOW}Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Stop any existing containers
echo -e "${YELLOW}Cleaning up existing containers...${NC}"
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Pull Docker images
echo -e "${YELLOW}Pulling Docker images...${NC}"
docker-compose -f docker-compose.test.yml pull

echo -e "${GREEN}✓ Docker images pulled${NC}"

# Build test images
echo -e "${YELLOW}Building test images...${NC}"
docker-compose -f docker-compose.test.yml build

echo -e "${GREEN}✓ Test images built${NC}"

# Start database services only
echo -e "${YELLOW}Starting database services...${NC}"
docker-compose -f docker-compose.test.yml up -d postgres-test redis-test

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
for i in {1..30}; do
    if docker-compose -f docker-compose.test.yml ps | grep -q "healthy"; then
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Verify database is accessible
echo -e "${YELLOW}Verifying database connection...${NC}"
docker-compose -f docker-compose.test.yml exec -T postgres-test psql -U ihep_test_user -d ihep_curriculum_test -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database connection verified${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    exit 1
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose -f docker-compose.test.yml run --rm test-runner alembic upgrade head

echo -e "${GREEN}✓ Database migrations completed${NC}"

# Start all services
echo -e "${YELLOW}Starting all test services...${NC}"
docker-compose -f docker-compose.test.yml up -d

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..60}; do
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Run health check
echo -e "${YELLOW}Running health checks...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8001/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health checks passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================="
echo "Test Environment Ready!"
echo "=========================================${NC}"
echo ""
echo "Services running:"
echo "  - PostgreSQL:  localhost:5433"
echo "  - Redis:       localhost:6380"
echo "  - API:         http://localhost:8001"
echo "  - Load Test:   http://localhost:8089"
echo "  - API Docs:    http://localhost:8001/api/docs"
echo ""
echo "Run tests with:"
echo "  docker-compose -f docker-compose.test.yml run --rm test-runner pytest"
echo ""
echo "Run load tests:"
echo "  Open http://localhost:8089 in your browser"
echo ""
echo "View logs:"
echo "  docker-compose -f docker-compose.test.yml logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose -f docker-compose.test.yml down"
echo ""
echo "Environment file: .env.test"
echo ""
