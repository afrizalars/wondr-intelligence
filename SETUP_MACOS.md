# macOS Setup Guide for Wondr Intelligence

## Prerequisites Installation

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install PostgreSQL with pgvector
```bash
# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Install pgvector extension
brew install pgvector

# Create a database user (optional, you can use your macOS username)
createuser -s postgres

# Or use your current username (recommended)
createdb $(whoami)
```

### 3. Verify PostgreSQL Installation
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Test connection with your username
psql -U $(whoami) -c "\l"

# If you created postgres user
psql -U postgres -c "\l"
```

### 4. Install Python 3.8+ (if needed)
```bash
# Install Python via Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

### 5. Install Node.js 16+
```bash
# Install Node.js
brew install node

# Verify installation
node --version
npm --version
```

## Wondr Intelligence Installation

### 1. Clone and Enter Directory
```bash
git clone <repository-url>
cd wondr-intelligence
```

### 2. Run Installation Script
```bash
chmod +x install.sh
./install.sh
```

When prompted:
- **PostgreSQL host**: Press Enter (uses localhost)
- **PostgreSQL port**: Press Enter (uses 5432)
- **PostgreSQL username**: Press Enter (uses your macOS username) OR type `postgres`
- **PostgreSQL password**: Press Enter (no password for local development)
- **Database name**: Press Enter (uses wondr_intelligence)
- **Anthropic API key**: Enter your key or skip for now

### 3. If pgvector is not found
```bash
# Install pgvector manually
brew install pgvector

# Connect to your database
psql -U $(whoami) -d wondr_intelligence

# In psql prompt, run:
CREATE EXTENSION vector;
\q

# Re-run the installation script
./install.sh
```

## Running the Application

### Start all services:
```bash
./start.sh
```

### Or start individually:
```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend  
./start-frontend.sh
```

### Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Troubleshooting

### PostgreSQL Connection Issues

If you get "role does not exist" error:
```bash
# Option 1: Use your macOS username
psql -U $(whoami) -d wondr_intelligence

# Option 2: Create the postgres user
createuser -s postgres

# Option 3: Reset PostgreSQL
brew services stop postgresql@14
rm -rf /usr/local/var/postgresql@14
initdb /usr/local/var/postgresql@14
brew services start postgresql@14
```

### Port Already in Use

If ports 5173 or 8000 are in use:
```bash
# Find and kill processes
lsof -i :5173
lsof -i :8000
kill -9 <PID>
```

### Python Virtual Environment Issues

```bash
# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create `backend/.env` if not exists:
```env
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/wondr_intelligence
DATABASE_SYNC_URL=postgresql://$(whoami)@localhost:5432/wondr_intelligence
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANTHROPIC_API_KEY=your-anthropic-api-key
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EMBEDDING_MODEL=intfloat/multilingual-e5-base
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

Replace `$(whoami)` with your actual username or `postgres` if you're using that user.

## Generate Test Data

After installation, generate synthetic data:
```bash
cd scripts
python3 generate_synthetic_data.py
```

## Stop Services

Press `Ctrl+C` in the terminal running `start.sh` or:
```bash
# Stop PostgreSQL
brew services stop postgresql@14

# Kill any remaining processes
pkill -f "uvicorn"
pkill -f "npm run dev"
```