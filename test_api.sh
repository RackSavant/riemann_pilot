#!/bin/bash
# Test script for RAG API

echo "🧪 Testing RAG System API"
echo ""

# Test 1: Health check
echo "1️⃣  Health Check"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""
echo ""

# Test 2: Stats
echo "2️⃣  System Stats"
curl -s http://localhost:8000/stats | python3 -m json.tool
echo ""
echo ""

# Test 3: Basic query without dials
echo "3️⃣  Basic Query (no dials)"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to build strong relationships?",
    "top_k": 3
  }' | python3 -m json.tool
echo ""
echo ""

# Test 4: Query with dials
echo "4️⃣  Query with Semantic Dials"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to build trust and commitment?",
    "dials": {
      "love": 0.7,
      "commitment": 0.9,
      "belonging": 0.6,
      "trust": 0.9,
      "growth": 0.5
    },
    "top_k": 3,
    "use_reranking": true
  }' | python3 -m json.tool

echo ""
echo "✅ Tests complete!"
