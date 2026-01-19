#!/bin/bash
# Helper script to start ngrok tunnel for the FastAPI server

echo "🚀 Starting ngrok tunnel on port 8000..."
echo "📋 Make sure your FastAPI server is running first!"
echo ""

# Check if ngrok exists in current directory
if [ -f "./ngrok" ]; then
    ./ngrok http 8000
elif command -v ngrok &> /dev/null; then
    ngrok http 8000
else
    echo "❌ Error: ngrok not found!"
    echo "   Make sure ngrok is in this directory or in your PATH"
    exit 1
fi
