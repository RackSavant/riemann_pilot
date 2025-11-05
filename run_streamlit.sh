#!/bin/bash
# Launch Streamlit UI for Love Steering Vector

echo "🎛️ Launching AI Steering Vector Lab"
echo ""

# Check if Docker backend is running
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "⚠️  Backend API not running!"
    echo "Starting Docker backend..."
    docker-compose up -d
    echo "Waiting for API to be ready..."
    sleep 10
fi

echo "✅ Backend API is running"
echo ""
echo "🚀 Starting Streamlit UI..."
echo "📍 Open your browser to http://localhost:8501"
echo ""

streamlit run streamlit_app.py
