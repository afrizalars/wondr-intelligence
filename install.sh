#!/bin/bash

set -e

echo "======================================"
echo "Wondr Intelligence Installation Script"
echo "======================================"
echo ""

# Check prerequisites
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install $1 first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "Checking prerequisites..."
check_command python3
check_command node
check_command npm
check_command psql

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
else
    echo "✅ Python version $PYTHON_VERSION"
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js 16 or higher is required"
    exit 1
else
    echo "✅ Node.js version $(node -v)"
fi

echo ""
echo "Setting up PostgreSQL database..."
echo ""
echo "ℹ️  Note: You need PostgreSQL running with a user that has database creation privileges."
echo "   On macOS: Your username ($(whoami)) is typically used"
echo "   On Linux: 'postgres' user is typical"
echo ""

# Database configuration
read -p "PostgreSQL host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "PostgreSQL port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "PostgreSQL username (default: $(whoami)): " DB_USER
DB_USER=${DB_USER:-$(whoami)}

read -sp "PostgreSQL password (press Enter if none): " DB_PASSWORD
echo ""

read -p "Database name (default: wondr_intelligence): " DB_NAME
DB_NAME=${DB_NAME:-wondr_intelligence}

# Test connection first
echo "Testing database connection..."
if [ -z "$DB_PASSWORD" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "\l" >/dev/null 2>&1 || {
        echo "❌ Failed to connect to PostgreSQL."
        echo ""
        echo "Please ensure PostgreSQL is running and try one of these:"
        echo "  1. Use your system username: $(whoami)"
        echo "  2. Create a postgres user: createuser -s postgres"
        echo "  3. Start PostgreSQL: brew services start postgresql@14 (macOS)"
        echo "                      sudo systemctl start postgresql (Linux)"
        exit 1
    }
else
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "\l" >/dev/null 2>&1 || {
        echo "❌ Failed to connect to PostgreSQL with provided credentials."
        exit 1
    }
fi

echo "✅ Database connection successful"

# Create database and enable extensions
echo "Creating database..."
if [ -z "$DB_PASSWORD" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database might already exist, continuing..."
else
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database might already exist, continuing..."
fi

echo "Checking for pgvector extension..."
if [ -z "$DB_PASSWORD" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || {
        echo "⚠️  pgvector extension not available. Trying to install..."
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" || true
        echo ""
        echo "❌ pgvector is required but not installed."
        echo ""
        echo "To install pgvector:"
        echo "  macOS: brew install pgvector"
        echo "  Ubuntu: sudo apt install postgresql-14-pgvector"
        echo "  From source: https://github.com/pgvector/pgvector#installation"
        echo ""
        echo "After installing, run this script again."
        exit 1
    }
else
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || {
        echo "❌ pgvector is required but not installed. See instructions above."
        exit 1
    }
fi

echo "✅ pgvector extension enabled"

echo "Running database schema..."
if [ -z "$DB_PASSWORD" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/schema.sql
else
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/schema.sql
fi

echo ""
echo "Setting up Backend..."

# Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "Creating backend configuration..."
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
DATABASE_SYNC_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANTHROPIC_API_KEY=
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EMBEDDING_MODEL=intfloat/multilingual-e5-base
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF

echo ""
echo "⚠️  Please add your Anthropic API key to backend/.env"
read -p "Enter your Anthropic API key (or press Enter to skip): " ANTHROPIC_KEY
if [ ! -z "$ANTHROPIC_KEY" ]; then
    sed -i.bak "s/ANTHROPIC_API_KEY=/ANTHROPIC_API_KEY=$ANTHROPIC_KEY/" .env
    rm .env.bak 2>/dev/null || true
fi

cd ..

echo ""
echo "Setting up Frontend..."

cd frontend

# Create environment configuration
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_API_VERSION=v1
EOF

echo "Installing frontend dependencies..."
npm install

# Create TypeScript configuration
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

cat > tsconfig.node.json << 'EOF'
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "node",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

# Create Vite configuration
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
EOF

cd ..

echo ""
echo "Downloading E5 embedding model..."
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"

echo ""
read -p "Do you want to generate synthetic data? (y/n): " GENERATE_DATA
if [ "$GENERATE_DATA" = "y" ]; then
    echo "Generating synthetic data..."
    cd backend
    source venv/bin/activate
    cd ../scripts
    python3 generate_synthetic_data.py
    cd ..
fi

echo ""
echo "Creating startup scripts..."

# Create backend start script
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x start-backend.sh

# Create frontend start script  
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
chmod +x start-frontend.sh

# Create combined start script
cat > start.sh << 'EOF'
#!/bin/bash

# Function to kill background processes on exit
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
echo "✅ Installation Complete!"
echo "======================================"
echo ""
echo "To start the application, run:"
echo "  ./start.sh"
echo ""
echo "Or start services individually:"
echo "  ./start-backend.sh  # Start backend only"
echo "  ./start-frontend.sh # Start frontend only"
echo ""
echo "Default URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/api/docs"
echo ""

if [ -z "$ANTHROPIC_KEY" ]; then
    echo "⚠️  Remember to add your Anthropic API key to backend/.env"
fi