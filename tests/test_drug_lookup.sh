#!/bin/bash

# Usage message
# if [ -z "$1" ]; then
#     echo "Usage: $0 <brand_name> [drug_dosage] [route]"
#     echo "Example: $0 Advil '200 MG' 'Oral Tablet'"
#     exit 1
# fi

# # Collect arguments
# BRAND_NAME="$1"
# DOSAGE="${2:-}"
# ROUTE="${3:-}"

# Start uvicorn in background (using correct module path)
echo "Starting backend server..."
uvicorn backend.main:app --reload --port 8001 &
SERVER_PID=$!

# Make sure we kill the server on exit
trap 'kill $SERVER_PID 2>/dev/null' EXIT

# Give the server time to start
sleep 3

# Send request to correct endpoint
echo "Sending request to /lookup/manual..."
curl -X POST http://localhost:8001/lookup/text \
  -H "Content-Type: application/json" \
  -d '{"text": "I need Advil 200mg. I weigh 52kg", "use_ner": true}'
echo -e "\n"

# Kill server
kill $SERVER_PID 2>/dev/null