#!/bin/bash
# Tea Party MVP - Complete Setup Script

set -e

echo "🫖 Tea Party Sentiment-Controlled Conversation MVP"
echo "=================================================="
echo ""

PROJECT_DIR="/Users/podpeople/CascadeProjects/rag_project"
cd "$PROJECT_DIR"

# Check Python version
echo "📋 Checking prerequisites..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "✅ Python $python_version found"

# Clone contrastive pairs repository if not exists
echo ""
echo "📥 Checking contrastive pair generation repository..."
if [ ! -d "contrastive-pair-gen" ]; then
    echo "Cloning repository..."
    git clone https://github.com/sevdeawesome/contrastive-pair-gen.git
    echo "✅ Repository cloned"
else
    echo "✅ Repository already exists"
fi

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
pip3 install -r tea_party_requirements.txt
echo "✅ Dependencies installed"

# Setup environment file
echo ""
echo "🔑 Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.tea_party.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Add your API keys to .env:"
    echo "   - OPENAI_API_KEY=sk-..."
    echo "   - GOOGLE_API_KEY=..."
else
    echo "⚠️  .env file already exists - keeping current configuration"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Add your API keys to .env file:"
echo "    nano .env"
echo ""
echo "2️⃣  Start the backend server:"
echo "    cd app && python tea_party_api.py"
echo ""
echo "3️⃣  Test the API:"
echo "    curl http://localhost:8000/api/characters"
echo ""
echo "4️⃣  Generate a conversation (text only):"
echo "    curl -X POST http://localhost:8000/api/conversation/turn \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"character_id\":\"purple_person\",\"generate_video\":false}'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Features:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🧠 Theory of Mind    - Empathy & perspective-taking"
echo "  ⚠️  Harmfulness       - Kind ↔ Cruel"
echo "  😏 Irony             - Literal ↔ Sarcastic"
echo "  👤 Self/Other Focus  - Self-focused ↔ Other-focused"
echo ""
echo "  🎬 Veo 3.1 Video Generation (8-second clips)"
echo "  💬 GPT-4 Powered Conversations"
echo "  🔄 Real-time WebSocket Updates"
echo ""
echo "📚 Read TEA_PARTY_README.md for full documentation"
echo ""
