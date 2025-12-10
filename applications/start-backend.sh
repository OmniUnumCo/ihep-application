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
    echo "✅ Virtual environment created and dependencies installed"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found. Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env with your configuration, then run this script again"
    else
        echo "❌ .env.example not found!"
    fi
    exit 1
fi

# Check database connection
echo "🔍 Checking database connection..."
if command -v psql > /dev/null 2>&1; then
    psql -h ${DB_HOST:-localhost} -U ${DB_USER:-postgres} -d ${DB_NAME:-ihep} -c "SELECT 1;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Database connection successful"
    else
        echo "⚠️  Database connection failed. Services may not work properly."
        echo "   Ensure PostgreSQL is running: docker-compose up -d postgres"
    fi
else
    echo "⚠️  psql not found. Skipping database check."
fi

# Check Redis connection
echo "🔍 Checking Redis connection..."
if command -v redis-cli > /dev/null 2>&1; then
    redis-cli -h ${REDIS_HOST:-localhost} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Redis connection successful"
    else
        echo "⚠️  Redis connection failed. Caching may not work."
        echo "   Ensure Redis is running: docker-compose up -d redis"
    fi
else
    echo "⚠️  redis-cli not found. Skipping Redis check."
fi

# Start services
echo ""
echo "🌐 Starting Healthcare API on port ${PORT:-8080}..."
cd backend
python app.py &
BACKEND_PID=$!

echo ""
echo "✅ Backend services started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Healthcare API: http://localhost:${PORT:-8080}"
echo "   Process ID: $BACKEND_PID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Logs are being written to console"
echo "   Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for process
wait $BACKEND_PID
