# 🚀 Setup Guide - RAG System with Semantic Dials

This guide will help you get your RAG system up and running with your 300 contrastive pairs.

## ✅ What's Already Done

1. ✅ **Project structure created**
2. ✅ **Contrastive pairs converted** from JSON to CSV (60 training pairs with context)
3. ✅ **Docker configuration** ready
4. ✅ **All Python code** implemented

## 📋 Prerequisites

- Docker & Docker Compose (recommended) OR Python 3.11+
- Your research articles/code
- ~2GB disk space for models

## 🎯 Quick Start (Docker - Recommended)

### Step 1: Add Your Articles

```bash
# Navigate to project
cd /Users/podpeople/CascadeProjects/rag_project

# Add your research articles to data/articles/
# Supported formats: JSON, TXT, MD, PY, JS, etc.
```

**Example article JSON format:**
```json
{
  "id": "attachment_theory_2024",
  "title": "Attachment Theory in Modern Relationships",
  "content": "Your full article content here...",
  "source": "Journal Name",
  "tags": ["attachment", "relationships"],
  "love_score": 0.8,
  "commitment_score": 0.7,
  "belonging_score": 0.9
}
```

### Step 2: Build & Run with Docker

```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

The API will be available at `http://localhost:8000`

### Step 3: Train with Your Contrastive Pairs

```bash
# This fine-tunes the embedding model with your 300 pairs
curl -X POST "http://localhost:8000/train-contrastive"
```

This will take 5-10 minutes. The model will learn to:
- Distinguish between love/hate responses
- Understand emotional nuances in your domain
- Improve semantic similarity for your specific use case

### Step 4: Index Your Articles

```bash
curl -X POST "http://localhost:8000/index-articles"
```

This creates the vector database for fast retrieval.

### Step 5: Test a Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does commitment affect relationships?",
    "dials": {
      "love": 0.8,
      "commitment": 0.9,
      "belonging": 0.6,
      "trust": 0.7,
      "growth": 0.5
    },
    "top_k": 5,
    "use_reranking": true
  }'
```

## 🐍 Alternative: Local Python Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then follow Steps 3-5 above.

## 🎛️ Understanding the Dials

### How Your Contrastive Pairs Improve Retrieval

Your 300 pairs teach the model to:

1. **Semantic Distinction**: Learn the difference between positive and negative emotional contexts
2. **Domain Specificity**: Understand relationship-specific language
3. **Nuanced Similarity**: Better match queries to relevant content

### Example Flow:

```
User Query: "How to build trust in relationships?"
   ↓
1. Embed query using fine-tuned model (trained on your pairs)
   ↓
2. Find top 15 similar chunks from articles
   ↓
3. Adjust scores based on dials (trust=0.9, love=0.7, ...)
   ↓
4. Return top 5 results that match both semantics AND dial preferences
```

### Dial Values (0.0 to 1.0):

- **love**: Emphasis on affection, emotional connection
- **commitment**: Long-term dedication, loyalty
- **belonging**: Community, social connection
- **trust**: Reliability, safety, security
- **growth**: Development, improvement, learning

**High dial value** (0.8-1.0) = Prioritize content strongly related to this concept
**Medium dial value** (0.4-0.6) = Neutral weighting
**Low dial value** (0.0-0.3) = De-prioritize this concept

## 📊 Monitoring & Stats

```bash
# Check system status
curl http://localhost:8000/

# Get statistics
curl http://localhost:8000/stats
```

## 🔧 Customization

### Add More Dials

Edit `app/main.py`:

```python
class SemanticDials(BaseModel):
    love: float = Field(default=0.5, ge=0.0, le=1.0)
    commitment: float = Field(default=0.5, ge=0.0, le=1.0)
    belonging: float = Field(default=0.5, ge=0.0, le=1.0)
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    growth: float = Field(default=0.5, ge=0.0, le=1.0)
    # Add your new dial:
    vulnerability: float = Field(default=0.5, ge=0.0, le=1.0)
```

Then annotate your articles with the new dial values.

### Adjust Scoring Weights

In `app/retrieval.py` (line ~130):

```python
# Current: 70% similarity, 30% dial alignment
final_score = 0.7 * base_score + 0.3 * dial_adjustment

# Make dials more important:
final_score = 0.5 * base_score + 0.5 * dial_adjustment
```

## 🏗️ Building Your Product

Your vision: **A product with dials that adjust prompts and responses**

### Current System Provides:
- ✅ Backend API with dial support
- ✅ Contrastive learning for better embeddings
- ✅ Retrieval that respects dial settings
- ✅ Article/code indexing

### Next Steps for Product:
1. **Frontend UI**: Build React app with dial sliders
2. **LLM Integration**: Add GPT-4/Claude to generate responses using retrieved context
3. **Prompt Adjustment**: Modify LLM system prompts based on dial values
4. **User Profiles**: Save dial preferences per user
5. **Analytics**: Track which dial combinations work best

### Example Product Architecture:

```
Frontend (React + Sliders)
    ↓
Backend API (FastAPI - already built)
    ↓
RAG Retrieval (with dials - already built)
    ↓
LLM Generation (GPT-4/Claude - TODO)
    ↓
Response adjusted by dial values
```

## 🐛 Troubleshooting

### Docker Issues

```bash
# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Memory Issues

```bash
# Limit Docker memory
docker-compose down
# Edit docker-compose.yml to add:
# mem_limit: 4g
docker-compose up
```

## 📁 Data Organization Tips

### Articles Structure:
```
data/articles/
  ├── attachment_theory/
  │   ├── article1.json
  │   ├── article2.json
  ├── relationship_research/
  │   ├── study1.json
  │   └── study2.md
  └── code_samples/
      ├── example.py
      └── example.js
```

### Adding More Contrastive Pairs:

If you get more pairs, just add them to the JSON and re-run:

```bash
python3 convert_contrastive_pairs.py /path/to/new_pairs.json
curl -X POST "http://localhost:8000/train-contrastive"
```

## 🎯 Success Checklist

- [ ] Docker running successfully
- [ ] Contrastive pairs trained (POST /train-contrastive)
- [ ] Articles indexed (POST /index-articles)
- [ ] Test query returns results (POST /query)
- [ ] Dial adjustments affect results
- [ ] Ready to build frontend!

## 📚 API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **OpenAPI spec**: http://localhost:8000/openapi.json

---

**Need help?** Check the README.md for more details or review the inline code documentation.
