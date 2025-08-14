#!/bin/bash

set -e

echo "========================================"
echo "Wondr Intelligence Quick Setup"
echo "========================================"
echo ""

# Database configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="63628"
DB_PASSWORD=""
DB_NAME="wondr_intelligence"

echo "Setting up database with user: $DB_USER"

# Create database
echo "Creating database..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"
echo "✅ Database created"

# Enable extensions
echo "Enabling extensions..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
echo "✅ Extensions enabled"

# Run schema
echo "Creating database schema..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/schema.sql
echo "✅ Database schema created"

echo ""
echo "Setting up Backend..."

cd backend

# Remove old venv if it exists (to ensure we use Python 3.11)
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment with Python 3.11
echo "Creating Python virtual environment with Python 3.11..."
python3.11 -m venv venv

# Activate and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Create .env file
echo "Creating backend configuration..."
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME
DATABASE_SYNC_URL=postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EMBEDDING_MODEL=intfloat/multilingual-e5-base
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF

echo "✅ Backend configured"

cd ..

echo ""
echo "Setting up Frontend..."

cd frontend

# Create environment configuration
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_API_VERSION=v1
EOF

# Install dependencies
echo "Installing frontend dependencies..."
npm install --silent

echo "✅ Frontend configured"

cd ..

echo ""
echo "Downloading E5 embedding model (this may take a few minutes)..."
cd backend
source venv/bin/activate
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')" 2>/dev/null || {
    echo "⚠️  Model download will happen on first run"
}
cd ..

# Create startup scripts
echo ""
echo "Creating startup scripts..."

cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x start-backend.sh

cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
chmod +x start-frontend.sh

cat > start.sh << 'EOF'
#!/bin/bash

cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

echo "Starting Backend..."
./start-backend.sh &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 5

echo "Starting Frontend..."
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "Wondr Intelligence is running!"
echo "======================================"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

wait
EOF
chmod +x start.sh

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  IMPORTANT: Add your Anthropic API key to backend/.env"
    echo "   Edit backend/.env and set ANTHROPIC_API_KEY=your-key-here"
    echo ""
fi

echo "Next steps:"
echo "1. Generate synthetic data (optional):"
echo "   cd backend && source venv/bin/activate"
echo "   python ../scripts/generate_synthetic_data.py"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "Or start services individually:"
echo "   ./start-backend.sh  # Terminal 1"
echo "   ./start-frontend.sh # Terminal 2"