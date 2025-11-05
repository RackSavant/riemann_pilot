#!/bin/bash
# Test learned steering vectors vs heuristic dials

echo "🧪 Testing Learned Steering Vectors"
echo "=================================="
echo ""

# Step 1: Learn steering vectors
echo "Step 1: Learning steering vectors from contrastive pairs..."
curl -s -X POST http://localhost:8000/learn-steering | python3 -m json.tool
echo ""
echo ""

# Step 2: Check vector info
echo "Step 2: Checking learned vectors..."
curl -s http://localhost:8000/steering-info | python3 -m json.tool
echo ""
echo ""

# Step 3: Compare heuristic vs learned
echo "Step 3: Comparison Test - Same Query, Different Methods"
echo "========================================================"
echo ""

QUERY="How to build trust and commitment in relationships?"

echo "🔹 Test A: Heuristic Dials (use_steering=false)"
echo "Query: $QUERY"
echo "Dials: trust=0.9, commitment=0.8"
echo ""
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"$QUERY\",
    \"dials\": {
      \"love\": 0.6,
      \"commitment\": 0.8,
      \"belonging\": 0.5,
      \"trust\": 0.9,
      \"growth\": 0.5
    },
    \"top_k\": 3,
    \"use_steering\": false
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Results: {len(data['results'])} documents\")
print(f\"Steering method: {data['metadata']['steering_method']}\")
print(f\"Retrieval time: {data['metadata']['retrieval_time_ms']:.1f}ms\")
print(\"\\nTop result:\")
if data['results']:
    r = data['results'][0]
    print(f\"  Score: {r['final_score']:.3f} (base: {r['base_similarity']:.3f}, dial: {r['dial_score']:.3f})\")
    print(f\"  Text: {r['text'][:100]}...\")
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔸 Test B: Learned Steering Vectors (use_steering=true)"
echo "Query: $QUERY"
echo "Dials: trust=0.9, commitment=0.8"
echo ""
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"$QUERY\",
    \"dials\": {
      \"love\": 0.6,
      \"commitment\": 0.8,
      \"belonging\": 0.5,
      \"trust\": 0.9,
      \"growth\": 0.5
    },
    \"top_k\": 3,
    \"use_steering\": true
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Results: {len(data['results'])} documents\")
print(f\"Steering method: {data['metadata']['steering_method']}\")
print(f\"Retrieval time: {data['metadata']['retrieval_time_ms']:.1f}ms\")
print(\"\\nTop result:\")
if data['results']:
    r = data['results'][0]
    print(f\"  Score: {r['final_score']:.3f} (base: {r['base_similarity']:.3f}, dial: {r['dial_score']:.3f})\")
    print(f\"  Text: {r['text'][:100]}...\")
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 4: Test with generation
echo "Step 4: Testing with Gemma Generation + Steering"
echo "================================================="
echo ""
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What is the foundation of lasting commitment?\",
    \"dials\": {
      \"love\": 0.7,
      \"commitment\": 0.9,
      \"belonging\": 0.6,
      \"trust\": 0.8,
      \"growth\": 0.7
    },
    \"top_k\": 3,
    \"use_steering\": true,
    \"use_llm\": true,
    \"temperature\": 0.7
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Query: {data['query']}\")
print(f\"\\nDial Instruction: {data['dial_instruction']}\")
print(f\"\\nGenerated Response:\")
print(data['response'][:300] + '...' if len(data['response']) > 300 else data['response'])
print(f\"\\nMetadata:\")
print(f\"  Retrieval time: {data['metadata']['retrieval_time_ms']:.1f}ms\")
print(f\"  Generation enabled: {data['metadata']['generation_enabled']}\")
print(f\"  Context sources: {', '.join(data['metadata']['context_sources'])}\")
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Steering vector tests complete!"
echo ""
echo "💡 Key Observations:"
echo "   - Learned steering changes the query embedding directly"
echo "   - Results may differ from heuristic approach"
echo "   - Check if learned steering finds more relevant content"
echo ""
echo "📊 Next Steps:"
echo "   1. Compare result quality between methods"
echo "   2. Test with more diverse queries"
echo "   3. Collect user feedback for adaptive steering"
echo "   4. Monitor which method performs better"
