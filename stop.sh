#!/bin/bash
echo "Stopping all services..."
lsof -ti:5173,5174,5175,8000,8001 | xargs kill -9 2>/dev/null
echo "All services stopped."
