#!/bin/bash

# Usage message
if [ -z "$1" ]; then
  echo "Usage: $0 <brand_name> [drug_dosage] [route]"
  echo "Example: $0 Advil 200 MG Oral Tablet"
  exit 1
fi

# Collect arguments
BRAND_NAME=$1
DOSAGE=$2
ROUTE="${@:3}"  # grabs everything after the 2nd arg (handles "Oral Tablet" nicely)

# Start uvicorn in background
uvicorn backend.drug_lookup:app --reload &
SERVER_PID=$!

# Make sure we kill the server on exit
trap 'kill $SERVER_PID 2>/dev/null' EXIT

# Give the server a moment to start
sleep 2

# Send request
echo "Sending request to /get_products with brand_name=$BRAND_NAME, dosage=$DOSAGE, route=$ROUTE..."
curl -X POST "http://127.0.0.1:8000/get_products" \
     -H "Content-Type: application/json" \
     -d "{\"brand_name\": \"$BRAND_NAME\", \"drug_dosage\": \"$DOSAGE\", \"route\": \"$ROUTE\"}"

echo -e "\n"

# Kill server
kill $SERVER_PID
