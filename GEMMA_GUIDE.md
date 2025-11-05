# 🤖 Gemma LLM Integration Guide

Your RAG system now includes **Gemma** (Google's open-source LLM) with semantic dial-adjusted prompt generation!

## 🎯 What's New

### `/generate` Endpoint
Generate AI responses with dial-influenced prompts:
- **High Love Dial** (0.7-1.0) → Warm, empathetic, compassionate tone
- **High Commitment Dial** → Long-term focus, dedication emphasis
- **High Belonging Dial** → Community, connection, inclusivity
- **High Trust Dial** → Security, reliability, honesty focus
- **High Growth Dial** → Development, learning, improvement

## 🚀 Quick Start

### 1. Rebuild Docker with Gemma

```bash
# Stop current container
docker-compose down

# Rebuild with new dependencies
docker-compose build

# Start with Gemma support
docker-compose up -d

# Watch logs (Gemma loads on first /generate request)
docker-compose logs -f
```

### 2. Test Gemma Generation

```bash
# Basic generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to build trust in relationships?",
    "dials": {
      "love": 0.7,
      "trust": 0.9,
      "commitment": 0.6
    },
    "top_k": 3,
    "use_llm": true
  }'
```

### 3. Run Test Suite

```bash
./test_gemma.sh
```

## 📊 How Dials Influence Generation

### Example: High Love Dial (0.9)

**Prompt Instruction Generated:**
> "Use a warm, empathetic, and compassionate tone. Emphasize connection and care."

**Response Style:**
- Heartfelt language
- Focus on emotional connection
- Supportive and nurturing tone

### Example: High Commitment Dial (0.9)

**Prompt Instruction Generated:**
> "Focus on long-term perspectives and sustained dedication. Emphasize consistency and dedication."

**Response Style:**
- Long-term focus
- Dedication and loyalty emphasis
- Perseverance themes

### Example: Balanced Dials (All 0.5)

**Prompt Instruction Generated:**
> "Provide a balanced, informative response"

**Response Style:**
- Neutral, professional tone
- Comprehensive coverage
- Objective advice

## 🎛️ Dial Combinations for Different Use Cases

### 1. **Relationship Counseling**
```json
{
  "love": 0.9,
  "trust": 0.8,
  "commitment": 0.7,
  "belonging": 0.6,
  "growth": 0.7
}
```
→ Warm, secure, growth-oriented advice

### 2. **Team Building**
```json
{
  "love": 0.6,
  "trust": 0.9,
  "commitment": 0.8,
  "belonging": 0.9,
  "growth": 0.7
}
```
→ Trust-focused, collaborative, community-driven

### 3. **Personal Development**
```json
{
  "love": 0.6,
  "trust": 0.7,
  "commitment": 0.8,
  "belonging": 0.5,
  "growth": 0.9
}
```
→ Growth-oriented, dedication-focused, improvement-driven

### 4. **Crisis Support**
```json
{
  "love": 0.9,
  "trust": 0.9,
  "commitment": 0.6,
  "belonging": 0.7,
  "growth": 0.5
}
```
→ Empathetic, secure, supportive

## 🔧 API Reference

### POST `/generate`

**Request:**
```json
{
  "query": "Your question here",
  "dials": {
    "love": 0.0-1.0,
    "commitment": 0.0-1.0,
    "belonging": 0.0-1.0,
    "trust": 0.0-1.0,
    "growth": 0.0-1.0
  },
  "top_k": 3,           // Number of context documents
  "temperature": 0.7,   // Generation randomness (0.0-2.0)
  "use_llm": true      // Enable/disable LLM generation
}
```

**Response:**
```json
{
  "query": "Your question",
  "response": "AI-generated response here...",
  "context_docs": [...],
  "dial_instruction": "Instructions used in prompt",
  "applied_dials": {...},
  "metadata": {
    "retrieval_time_ms": 25.3,
    "generation_enabled": true,
    "model": "gemma",
    "context_sources": ["Article 1", "Article 2"]
  }
}
```

## 💡 Advanced Usage

### Custom Temperature

```bash
# More creative (temperature=1.0)
curl -X POST http://localhost:8000/generate \
  -d '{"query": "...", "temperature": 1.0}'

# More focused (temperature=0.3)
curl -X POST http://localhost:8000/generate \
  -d '{"query": "...", "temperature": 0.3}'
```

### Context-Only Mode

```bash
# Get context without generation (faster)
curl -X POST http://localhost:8000/generate \
  -d '{"query": "...", "use_llm": false}'
```

### More Context Documents

```bash
# Use more context for detailed responses
curl -X POST http://localhost:8000/generate \
  -d '{"query": "...", "top_k": 5}'
```

## 🎨 Building Your Product

### Current Flow:
```
User Query 
  → Dial Settings 
    → RAG Retrieval (dial-adjusted)
      → Gemma Generation (dial-adjusted prompts)
        → Response
```

### Frontend Integration Example:

```javascript
// React component with sliders
const DialControls = () => {
  const [dials, setDials] = useState({
    love: 0.5,
    commitment: 0.5,
    belonging: 0.5,
    trust: 0.5,
    growth: 0.5
  });

  const generateResponse = async (query) => {
    const response = await fetch('http://localhost:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        dials,
        top_k: 3,
        temperature: 0.7,
        use_llm: true
      })
    });
    return await response.json();
  };

  return (
    <>
      <Slider label="Love" value={dials.love} onChange={...} />
      <Slider label="Commitment" value={dials.commitment} onChange={...} />
      {/* ... more sliders */}
    </>
  );
};
```

## 🔍 Monitoring Generation Quality

### Check Dial Instructions

Look at the `dial_instruction` field in responses to see how dials influenced the prompt:

```bash
curl -X POST http://localhost:8000/generate ... | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['dial_instruction'])"
```

### Compare Responses

Test the same query with different dial settings:

```bash
# High love
./test_gemma.sh

# Compare with neutral
curl ... -d '{"query": "...", "dials": {"love": 0.5, ...}}'
```

## ⚙️ Performance Tips

### 1. Use Gemma-2B for Speed
Already configured! The 2B model is faster while maintaining quality.

### 2. Adjust max_length
Edit `app/main.py` line 170:
```python
llm_engine = GemmaLLM(
    model_name="google/gemma-2b-it",
    max_length=256  # Shorter = faster
)
```

### 3. Use GPU (if available)
Gemma automatically uses CUDA if available in Docker.

## 🎓 Understanding the System

### Contrastive Learning → Retrieval → Generation

1. **Contrastive Pairs** train the embedding model to understand emotional nuances
2. **RAG Retrieval** finds relevant context, adjusted by dials
3. **Gemma Generation** creates responses with dial-influenced prompts

### Why This Works:

- **Embeddings**: Learn domain-specific semantics (love vs hate)
- **Dials**: Control both retrieval scoring AND prompt instructions
- **Gemma**: Follows dial-adjusted instructions for consistent tone

## 🚀 Next Steps

1. **Add More Articles**: The more context, the better the responses
2. **Experiment with Dials**: Find optimal settings for your use cases
3. **Fine-tune Prompts**: Edit `app/llm.py` to customize dial instructions
4. **A/B Testing**: Compare responses with different dial combinations
5. **Build Frontend**: Create UI with sliders and live preview

## 📖 Model Information

**Gemma-2B-IT:**
- **Size**: 2 billion parameters
- **Format**: Instruction-tuned
- **Speed**: ~2-5 seconds per response (CPU), <1s (GPU)
- **Context**: 8,192 tokens
- **License**: Open source (Gemma Terms)

**Upgrade to Gemma-7B:**
For better quality (slower), edit `app/main.py` line 169:
```python
model_name="google/gemma-7b-it"
```

## 🎉 You're Ready!

Your system now has:
- ✅ RAG retrieval with dial-adjusted scoring
- ✅ Gemma LLM with dial-influenced prompts
- ✅ Contrastive learning for better embeddings
- ✅ Production-ready Docker setup

**Start generating dial-adjusted responses!** 🎛️
