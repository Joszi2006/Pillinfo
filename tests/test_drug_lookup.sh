#!/bin/bash

# Require a brand name argument
if [ -z "$1" ]; then
  echo "Usage: $0 <brand_name>"
  exit 1
fi

BRAND_NAME=$1

# Start uvicorn in background
uvicorn backend.drug_lookup:app --reload &
SERVER_PID=$!

# Wait a bit so the server starts up
sleep 2

# Run the curl request
echo "Sending request to /get_products with brand_name=$BRAND_NAME..."
curl -X POST "http://127.0.0.1:8000/get_products" \
     -H "Content-Type: application/json" \
     -d "{\"brand_name\": \"$BRAND_NAME\"}"

echo -e "\n"

# Kill the server when done
kill $SERVER_PID
