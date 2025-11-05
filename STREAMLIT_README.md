# 🎛️ AI Steering Vector Lab - Streamlit Interface

Beautiful UI for testing your Love steering vector with three-model comparison!

## 🎯 What This Does

Based on the `steer-mind-art` interface design, this Streamlit app lets you:

1. **Adjust the Love Dial** (0-100%) to control emotional warmth
2. **Compare 3 models side-by-side** with different configurations
3. **Train learned steering vectors** from your 30 contrastive pairs
4. **See real-time differences** between steered and baseline models

## ��� Quick Start

### 1. Install Dependencies

```bash
pip install streamlit==1.31.0
# or rebuild Docker (includes streamlit now)
docker-compose down && docker-compose build
```

### 2. Launch the App

```bash
./run_streamlit.sh
```

Or manually:
```bash
# Start backend
docker-compose up -d

# Start Streamlit
streamlit run streamlit_app.py
```

### 3. Open Browser

Navigate to: **http://localhost:8501**

## 🎨 Features

### Love Steering Dial
- **0-33%**: Cold/Hate (Red) - Generates cold, distant responses
- **34-66%**: Neutral (Orange) - Balanced responses
- **67-100%**: Warm/Love (Green) - Empathetic, caring responses

### Comparison Modes

**1. All Steered** (Default)
- All three models use your current Love dial setting
- See consistency across models with same steering

**2. Steered vs Baseline**
- Model 1: No steering (baseline)
- Model 2: Your Love dial with learned steering
- Model 3: Heuristic dials (old method)
- **Compare the differences!**

**3. Different Intensities**
- Model 1: Low Love (25%)
- Model 2: Your dial setting
- Model 3: High Love (90%)
- **See how intensity affects output**

### Training

Click **"🚀 Train Love Vector"** to:
1. Load your 30 contrastive pairs from `data/contrastive_pairs.csv`
2. Learn the love/hate direction in embedding space
3. Enable learned steering (vs heuristic)

## 📊 Understanding the Interface

### Sidebar Controls
- **Love Dial**: Adjust 0-100%
- **Training**: Train/retrain steering vectors
- **Comparison Mode**: Choose model configuration
- **Clear/Reset**: Manage conversations

### Main Panel
Three chat interfaces side-by-side, each with:
- Model name and configuration
- Love percentage indicator
- Chat history
- Individual input boxes

### Footer Stats
- Current Love dial setting
- Steering mode (Learned vs Heuristic)
- Total messages sent
- Current comparison mode

## 🔬 Experimentation Guide

### Test 1: Baseline Comparison
```
Mode: "Steered vs Baseline"
Dial: 90%
Query: "How should I approach difficult conversations?"

Observe:
- Baseline: Generic advice
- Steered: Warm, empathetic guidance
- Heuristic: Somewhere in between
```

### Test 2: Intensity Sweep
```
Mode: "Different Intensities"
Query: "Give feedback on my code"

Observe:
- 25%: Critical, technical
- Your setting: Depends on dial
- 90%: Supportive, encouraging
```

### Test 3: Emotional Range
```
Mode: "All Steered"

Test at 10%: Cold, distant
Test at 50%: Neutral
Test at 90%: Warm, caring

Query: "I made a mistake at work"
```

## 🎯 Integration with Your System

This Streamlit app connects to your FastAPI backend:

```
Streamlit UI (Port 8501)
        ↓
    HTTP POST
        ↓
FastAPI Backend (Port 8000)
        ↓
Learned Steering Vectors
        ↓
Gemma LLM
        ↓
Generated Response
```

**Endpoints used:**
- `GET /` - Health check
- `POST /learn-steering` - Train vectors
- `POST /generate` - Generate with steering

## 💡 Next Steps

### Add More Vectors

When you have more contrastive pairs:

1. Update `app/steering.py` to handle multiple dimensions
2. Add new dials in `streamlit_app.py`:
```python
commitment_value = st.slider("Commitment", 0, 100, 50)
trust_value = st.slider("Trust", 0, 100, 50)
```

3. Update `dials` dict in API calls:
```python
"dials": {
    "love": love_dial,
    "commitment": commitment_dial,
    "trust": trust_dial,
    # ...
}
```

### Expand Comparison

Add more model panels:
```python
col1, col2, col3, col4 = st.columns(4)  # 4 models!
```

### Add Analytics

Track which dial settings get best responses:
```python
if st.button("👍 Good Response"):
    log_feedback(love_value, "positive")
```

## 🐛 Troubleshooting

**"Backend API not running"**
```bash
docker-compose up -d
# Wait 30 seconds for models to load
```

**"Training failed"**
- Check `data/contrastive_pairs.csv` exists
- Verify 30+ pairs in the file
- Check Docker logs: `docker-compose logs -f`

**Slow responses**
- First query downloads Gemma (1-2 min)
- Subsequent queries faster (~3-5 sec)
- Consider using GPU for faster inference

**Models give same response**
- Make sure you trained steering: Click "Train Love Vector"
- Try extreme dial values (10% vs 90%)
- Check comparison mode is set correctly

## 📚 Technical Details

**Stack:**
- Frontend: Streamlit
- Backend: FastAPI
- LLM: Gemma 2B
- Steering: Embedding-space vectors (learned from contrastive pairs)
- Vector Store: FAISS

**Data Flow:**
```
User sets Love dial → Streamlit
→ Converts to 0-1 scale
→ Sends to /generate endpoint
→ Backend applies steering vector
→ Gemma generates with steered embeddings
→ Response back to Streamlit
→ Displays in chat panel
```

## 🎉 You're Ready!

Your Love steering vector lab is set up! 

Try it now:
```bash
./run_streamlit.sh
```

Then navigate to **http://localhost:8501** and start experimenting! 🚀
