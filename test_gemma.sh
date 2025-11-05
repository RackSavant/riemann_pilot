#!/bin/bash
# Test Gemma LLM integration with semantic dials

echo "🧪 Testing Gemma LLM with Semantic Dials"
echo ""

# Test 1: High Love Dial
echo "1️⃣  Test: High Love Dial (warm, empathetic response)"
echo "Query: 'How to build emotional connection?'"
echo "Dials: Love=0.9, Trust=0.7"
echo ""
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to build emotional connection in relationships?",
    "dials": {
      "love": 0.9,
      "commitment": 0.5,
      "belonging": 0.6,
      "trust": 0.7,
      "growth": 0.5
    },
    "top_k": 3,
    "temperature": 0.7,
    "use_llm": true
  }' | python3 -c "import sys, json; data = json.load(sys.stdin); print('Response:', data['response'][:200] + '...'); print('Dial Instruction:', data['dial_instruction'])"

echo ""
echo "="*60
echo ""

# Test 2: High Commitment Dial
echo "2️⃣  Test: High Commitment Dial (long-term focus)"
echo "Query: 'How to maintain dedication?'"
echo "Dials: Commitment=0.9, Growth=0.7"
echo ""
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to maintain dedication over time?",
    "dials": {
      "love": 0.5,
      "commitment": 0.9,
      "belonging": 0.5,
      "trust": 0.6,
      "growth": 0.7
    },
    "top_k": 3,
    "temperature": 0.7,
    "use_llm": true
  }' | python3 -c "import sys, json; data = json.load(sys.stdin); print('Response:', data['response'][:200] + '...'); print('Dial Instruction:', data['dial_instruction'])"

echo ""
echo "="*60
echo ""

# Test 3: High Trust Dial
echo "3️⃣  Test: High Trust Dial (security focus)"
echo "Query: 'Building trust in relationships?'"
echo "Dials: Trust=0.9, Belonging=0.8"
echo ""
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the foundations of building trust?",
    "dials": {
      "love": 0.6,
      "commitment": 0.6,
      "belonging": 0.8,
      "trust": 0.9,
      "growth": 0.5
    },
    "top_k": 3,
    "temperature": 0.7,
    "use_llm": true
  }' | python3 -c "import sys, json; data = json.load(sys.stdin); print('Response:', data['response'][:200] + '...'); print('Dial Instruction:', data['dial_instruction'])"

echo ""
echo "="*60
echo ""

# Test 4: Balanced Dials
echo "4️⃣  Test: Balanced Dials (neutral tone)"
echo "Query: 'Advice on relationships?'"
echo "Dials: All at 0.5"
echo ""
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What advice do you have for healthy relationships?",
    "dials": {
      "love": 0.5,
      "commitment": 0.5,
      "belonging": 0.5,
      "trust": 0.5,
      "growth": 0.5
    },
    "top_k": 3,
    "temperature": 0.7,
    "use_llm": true
  }' | python3 -c "import sys, json; data = json.load(sys.stdin); print('Response:', data['response'][:200] + '...'); print('Dial Instruction:', data['dial_instruction'])"

echo ""
echo "="*60
echo ""
echo "✅ Gemma tests complete!"
echo ""
echo "💡 Notice how the dial settings influence:"
echo "   - Tone and style of response"
echo "   - Focus areas and emphasis"
echo "   - Language choices"
