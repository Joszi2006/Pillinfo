#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Pillinfo Application...${NC}"

# Activate virtual environment and start backend
echo -e "${GREEN}Starting Backend...${NC}"
source .venv/bin/activate
python3 -m backend.main &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting Frontend...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
