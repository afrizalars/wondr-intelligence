#!/bin/bash
cd backend
source venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -E '^(HOST|PORT)=' | xargs)
fi

# Use PORT and HOST from .env or defaults
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8001}

echo "Starting backend server on $HOST:$PORT"
uvicorn main:app --reload --host $HOST --port $PORT