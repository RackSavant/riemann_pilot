#!/bin/bash
# Start Tea Party API Server

cd /Users/podpeople/CascadeProjects/rag_project

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Activate virtual environment and start server
source venv/bin/activate
cd app
python tea_party_conversation.py

# Or run the API server:
# python tea_party_api.py
