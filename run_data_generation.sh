#!/bin/bash

echo "======================================"
echo "Wondr Intelligence Data Generator"
echo "======================================"
echo ""

# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Run the simple data generator
echo "Generating synthetic data..."
python ../scripts/generate_data_simple.py

echo ""
echo "Data generation complete!"
echo ""
echo "To start the application:"
echo "  ./start-backend.sh  (Terminal 1)"
echo "  ./start-frontend.sh (Terminal 2)"