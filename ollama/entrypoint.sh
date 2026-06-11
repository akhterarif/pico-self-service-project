#!/bin/bash
set -e

# Start ollama server in the background
/usr/bin/ollama serve &
OLLAMA_PID=$!

# Wait for ollama to be ready (up to 30 seconds)
echo "Waiting for Ollama to be ready..."
for i in {1..30}; do
  if /usr/bin/ollama list > /dev/null 2>&1; then
    echo "Ollama is ready!"
    break
  fi
  echo "Attempt $i: Waiting for Ollama..."
  sleep 1
done

# Try to pull gemma with retries
echo "Attempting to pull gemma model..."
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if /usr/bin/ollama pull gemma 2>&1; then
    echo "Successfully pulled gemma model!"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Pull attempt $RETRY_COUNT failed. Retrying in 5 seconds..."
    sleep 5
  fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "Warning: Failed to pull gemma model after $MAX_RETRIES attempts"
  echo "The model will be available for manual pulling"
fi

# Keep the process alive
wait $OLLAMA_PID
