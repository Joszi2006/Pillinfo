#!/bin/bash

# ==========================================
# Script: lookup_one_image.sh
# Description: Uploads ONE image to the /lookup/image endpoint
# Usage: ./lookup_one_image.sh <pic_name> (e.g., advil.jpg)
# ==========================================

URL="http://localhost:8001/lookup/image"
BASE_DIR="data/drug_pics"
WEIGHT=25
AGE=10

if [ $# -lt 1 ]; then
  echo "Usage: $0 <pic_name>"
  exit 1
fi

IMAGE_NAME="$1"
IMAGE_PATH="${BASE_DIR}/${IMAGE_NAME}"

if [ ! -f "$IMAGE_PATH" ]; then
  echo "❌ File not found: $IMAGE_PATH"
  exit 1
fi

echo "🚀 Starting backend server..."
uvicorn backend.main:app --port 8001 --reload &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT

# --- Wait for server to become ready ---
echo "⌛ Waiting for server to start..."
for i in {1..20}; do
  if curl -s http://localhost:8001/docs >/dev/null; then
    echo "✅ Server is up!"
    break
  fi
  sleep 2
  echo "⏳ Still waiting ($((i*2))s)..."
  if [ "$i" -eq 20 ]; then
    echo "❌ Server failed to start."
    kill "$SERVER_PID"
    exit 1
  fi
done

echo "🧪 Uploading image: $IMAGE_PATH"
echo "➡️  Weight: $WEIGHT kg | Age: $AGE years"
echo "---------------------------------------"

curl -X POST "$URL" \
  -F "file=@${IMAGE_PATH}" \
  -F "patient_weight_kg=${WEIGHT}" \
  -F "patient_age=${AGE}" \
  -w "\nHTTP Status: %{http_code}\n"

echo "---------------------------------------"
echo "🛑 Stopping backend server..."
kill "$SERVER_PID" 2>/dev/null
