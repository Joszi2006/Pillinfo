#!/bin/bash

# --- Configuration ---
SERVER_PORT=8001
# Wait 10 seconds for graceful shutdown before forcing a kill
GRACE_PERIOD=10

# Start uvicorn in background (using correct module path)
echo "Starting backend server on port $SERVER_PORT..."
uvicorn backend.main:app --reload --port $SERVER_PORT &
SERVER_PID=$!

# --- TRAP for Cleanup on Exit (Now handles graceful shutdown) ---
cleanup() {
    echo "Attempting graceful shutdown of PID $SERVER_PID..."
    # 1. Send SIGTERM (graceful signal)
    kill -TERM $SERVER_PID 2>/dev/null

    # 2. Wait for the process to exit cleanly
    if wait $SERVER_PID; then
        echo "Server shut down gracefully."
    else
        # 3. If it didn't shut down in time, send SIGKILL (forceful)
        echo "Server failed to shut down gracefully. Forcing kill."
        kill -KILL $SERVER_PID 2>/dev/null
    fi
}

# Register the cleanup function to run on script exit
trap cleanup EXIT

# Give the server time to start
sleep 3

# Send the test request
echo "Sending request to /lookup/text..."
curl -X POST http://localhost:$SERVER_PORT/lookup/text\
  -H "Content-Type: application/json" \
  -d '{"text": "I have a Advil 40mg/ml Oral Suspension, i weigh 52kg and i am 14 years of age ", "use_ner": true, "lookup_all_drugs": true}'

# The 'trap cleanup EXIT' command will handle the server shutdown after the curl command finishes.
