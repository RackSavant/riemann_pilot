#!/bin/bash
# Quick start script for RAG system

echo "🚀 Starting RAG System with Semantic Dials..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build the Docker image
echo "🔨 Building Docker image (this may take a few minutes on first run)..."
docker-compose build

# Start the container
echo ""
echo "🎯 Starting container..."
docker-compose up -d

# Wait for container to be ready
echo ""
echo "⏳ Waiting for API to be ready..."
sleep 5

# Check if it's running
if curl -s http://localhost:8000/ > /dev/null; then
    echo ""
    echo "✅ RAG System is running!"
    echo ""
    echo "📍 API URL: http://localhost:8000"
    echo "📖 Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop system:"
    echo "   docker-compose down"
    echo ""
    echo "🧪 Next steps:"
    echo "   1. Train contrastive model: curl -X POST http://localhost:8000/train-contrastive"
    echo "   2. Add articles to data/articles/"
    echo "   3. Index articles: curl -X POST http://localhost:8000/index-articles"
    echo "   4. Test query: curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{\"query\": \"test\", \"top_k\": 3}'"
else
    echo ""
    echo "⚠️  Container started but API not responding yet."
    echo "   Check logs: docker-compose logs -f"
fi
