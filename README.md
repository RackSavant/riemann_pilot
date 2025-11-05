<<<<<<< HEAD
# AI Steering Vector Lab 🎛️

A Retrieval-Augmented Generation (RAG) system with **learned steering vectors** that enable semantic control over AI responses using love/hate dimensions mapped to a 7-point Likert scale.

## 🎯 Features

- **🎛️ Learned Steering Vectors**: Train on 60 love/hate contrastive pairs to learn semantic directions
- **📊 Semantic Likert Scale**: 7-point interpretable scale (Strong Hate → Neutral → Strong Love)
- **🤖 Multi-Model Comparison**: Test 3 Gemma models simultaneously (2B, 9B, 27B via OpenRouter API)
- **⚡ Cloud-Based LLMs**: No local model downloads - instant API-based generation
- **🎨 Interactive Streamlit UI**: Real-time dial adjustments with live response comparison
- **🔍 Semantic Search**: FAISS vector search with sentence transformers
- **🐳 Docker Support**: Fully containerized deployment
- **📈 PCA-Derived Dimensions**: Auto-generate commitment, trust, belonging, growth vectors

## 📋 How Contrastive Pairs Work

Your 300 contrastive pairs are used to **fine-tune the embedding model** to better understand domain-specific semantic relationships:

### Training Phase:
1. **Load Contrastive Pairs**: The system loads pairs from `data/contrastive_pairs.csv`
2. **Fine-tune Embeddings**: Uses contrastive learning to train the model to:
   - Place similar concepts closer together in embedding space
   - Push dissimilar concepts farther apart
   - Learn domain-specific relationships (e.g., love vs. commitment)
3. **Save Fine-tuned Model**: The improved model is saved for inference

### Retrieval Phase:
1. **Query Embedding**: User query is embedded using the fine-tuned model
2. **Vector Search**: Find top-K most similar document chunks
3. **Dial Adjustment**: Rerank results based on dial alignment
4. **Return Results**: Return documents that match both semantic similarity and dial preferences

## 📁 Project Structure

```
rag_project/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application with dial endpoints
│   ├── embed.py         # Embedding engine with contrastive learning
│   ├── retrieval.py     # Retrieval engine with dial-adjusted scoring
│   └── utils.py         # Helper functions
├── data/
│   ├── articles/        # Put your research articles here (JSON, TXT, MD, code files)
│   ├── contrastive_pairs.csv  # Your 300 contrastive pairs
│   └── vector_store/    # FAISS index (auto-generated)
├── models/              # Fine-tuned models (auto-generated)
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🚀 Quick Start

### Prerequisites

1. **Get OpenRouter API Key** (free tier available):
   - Visit https://openrouter.ai/keys
   - Create an account and generate an API key
   - Copy the key (starts with `sk-or-v1-...`)

2. **Create `.env` file** in project root:
```bash
# OpenRouter API for Gemma models
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Option 1: Docker + Streamlit (Recommended)

```bash
# Start backend + Streamlit
docker-compose up -d

# Open Streamlit UI
open http://localhost:8501

# Backend API available at
open http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Streamlit UI (in another terminal)
streamlit run streamlit_app.py
```

**First-time setup** (30 seconds):
- Backend downloads embedding model on first start
- No LLM downloads needed (cloud API!)
- Train steering vectors in Streamlit sidebar

## 📊 Prepare Your Data

### 1. Contrastive Pairs Format

Create `data/contrastive_pairs.csv` with one of these formats:

**Option A: Pair Format (Recommended)**
```csv
text1,text2,label
"Expressions of affection","Acts of service",0.6
"Long-term commitment","Short-term dating",0.2
"Community belonging","Social isolation",0.0
```

**Option B: Triplet Format**
```csv
anchor,positive,negative
"Love and commitment","Deep emotional connection","Casual dating"
"Secure attachment","Trust and safety","Anxious attachment"
```

### 2. Articles Format

Place your articles in `data/articles/`. Supported formats:

**JSON Format** (with optional dial annotations):
```json
{
  "id": "article_001",
  "title": "Understanding Attachment Theory",
  "content": "Full article content here...",
  "source": "Journal of Psychology",
  "tags": ["attachment", "relationships"],
  "love_score": 0.8,
  "commitment_score": 0.7,
  "belonging_score": 0.9,
  "trust_score": 0.85,
  "growth_score": 0.6
}
```

**Text/Markdown Files**:
- `.txt`, `.md` files are automatically loaded
- Code files (`.py`, `.js`, etc.) are also indexed

## 🎛️ Using the Dials

### Query with Dials

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

### How Dials Work:

1. **Base Similarity**: Documents are retrieved by semantic similarity
2. **Dial Matching**: Each document has dial annotations (manual or default)
3. **Combined Score**: `0.7 × similarity + 0.3 × dial_alignment`
4. **Reranking**: Results are reordered by combined score

This means:
- High `commitment` dial → prioritizes commitment-related content
- High `love` dial → prioritizes love-related content
- Combined dials → finds content matching your specific emphasis

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Health check
- `POST /query` - Query with adjustable dials
- `POST /train-contrastive` - Fine-tune embeddings with contrastive pairs
- `POST /index-articles` - Rebuild article index
- `GET /stats` - Get system statistics

### Example: Train Contrastive Model

```bash
curl -X POST "http://localhost:8000/train-contrastive"
```

This will:
1. Load your 300 contrastive pairs
2. Fine-tune the embedding model
3. Save the improved model to `models/finetuned_model/`

### Example: Index Articles

```bash
curl -X POST "http://localhost:8000/index-articles"
```

## 🎨 Building Your Product with Dials

The current implementation provides a foundation for your product vision:

### Current State:
- ✅ Adjustable dials (love, commitment, belonging, trust, growth)
- ✅ Dial-adjusted retrieval
- ✅ Contrastive learning support
- ✅ REST API

### Future Enhancements:
1. **UI with Sliders**: Build a frontend with dial sliders
2. **Dynamic Prompts**: Adjust LLM prompts based on dial settings
3. **Personalization**: Save user dial preferences
4. **Analytics**: Track which dial settings work best
5. **More Dials**: Add custom semantic variables

### Example Product Flow:
```
User adjusts dials → Query submitted → RAG retrieval with dial weights 
→ Context filtered by dials → LLM prompt adjusted by dials → Response
```

## 🧪 Testing

```bash
# Check health
curl http://localhost:8000/

# Get stats
curl http://localhost:8000/stats

# Test query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test query",
    "top_k": 3
  }'
```

## 📈 Next Steps

1. **Add your contrastive pairs** to `data/contrastive_pairs.csv`
2. **Add your articles** to `data/articles/`
3. **Train the model**: `POST /train-contrastive`
4. **Index articles**: `POST /index-articles`
5. **Start querying**: `POST /query`

## 🛠️ Customization

### Add New Dials

1. Update `SemanticDials` in `app/main.py`:
```python
class SemanticDials(BaseModel):
    love: float = Field(default=0.5, ge=0.0, le=1.0)
    commitment: float = Field(default=0.5, ge=0.0, le=1.0)
    your_new_dial: float = Field(default=0.5, ge=0.0, le=1.0)
```

2. Annotate articles with the new dial in JSON metadata

### Adjust Scoring Weights

In `app/retrieval.py`, modify the scoring formula:
```python
# Current: 70% similarity, 30% dial alignment
final_score = 0.7 * base_score + 0.3 * dial_adjustment

# Adjust as needed
final_score = 0.5 * base_score + 0.5 * dial_adjustment  # Equal weight
```

## 📝 License

MIT License - Feel free to use for your product!

---

**Questions?** The system is designed to be extensible. Start with the basics (contrastive training + indexing) and expand as needed for your product vision.

---

# 🫖 Tea Party of 5: Multi-Dimensional AI Steering Platform

## Quick Links

- **Tea Party Documentation**: See [TEA_PARTY_README.md](TEA_PARTY_README.md)
- **Cockpit UI Guide**: See [COCKPIT_UI_GUIDE.md](COCKPIT_UI_GUIDE.md)
- **VEO Video Integration**: See [VEO_INTEGRATION_GUIDE.md](VEO_INTEGRATION_GUIDE.md)

## Features

- 🛩️ Cockpit UI with 20 sentiment dials (4 per character)
- 👥 5 unique characters with controllable personalities
- 🎛️ Multi-dimensional steering (Theory of Mind, Harmfulness, Irony, Self/Other)
- 🔬 Semantic validation for steering effectiveness
- 🎬 VEO 3.1 video generation (individual + conversation scenes)
- 📊 Side-by-side response comparison
- 🤖 Multi-LLM support (OpenRouter integration)

---

# 🎨 Frontend (React + TypeScript)

## Project Info

**Lovable Project URL**: https://lovable.dev/projects/bba02617-12d1-40ac-8bbe-459893d2c496

## Tech Stack

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

## Deployment

Open [Lovable](https://lovable.dev/projects/bba02617-12d1-40ac-8bbe-459893d2c496) and click Share → Publish.
