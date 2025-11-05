# 🚀 Love Steering Vector - Streamlit Interface

## ✅ What We Built

A beautiful Streamlit UI based on your `steer-mind-art` design that connects to your RAG backend!

**Features:**
- 💗 **Love Dial** (0-100%) - Control emotional warmth
- 🎯 **3-Model Comparison** - Test different configurations side-by-side
- 🧠 **Learned Steering** - Train from your 30 contrastive pairs
- 📊 **Real-time Comparison** - See steering effects instantly

## 🎬 Launch Now

```bash
cd /Users/podpeople/CascadeProjects/rag_project

# Option 1: Quick launch script
./run_streamlit.sh

# Option 2: Manual
docker-compose up -d        # Start backend
streamlit run streamlit_app.py  # Start UI
```

Then open: **http://localhost:8501**

## 🎯 Try This First

1. **Click "🚀 Train Love Vector"** in sidebar
   - Trains from your 30 pairs (~30 seconds)
   
2. **Set dial to 90%** (High Love/Warm)
   - Notice the green indicator

3. **Choose "Steered vs Baseline"** comparison mode

4. **Ask all three models:** 
   ```
   "How should I handle a conflict with a colleague?"
   ```

5. **Observe the differences!**
   - Model 1 (Baseline): Generic advice
   - Model 2 (Steered 90%): Warm, empathetic guidance
   - Model 3 (Heuristic): In between

## 📊 Comparison Modes

### 1. All Steered
All models use your Love dial setting
- **Use for:** Consistency testing

### 2. Steered vs Baseline ⭐ **RECOMMENDED**
- Model 1: No steering
- Model 2: Learned steering at your dial
- Model 3: Old heuristic method
- **Use for:** Seeing the impact of learned steering

### 3. Different Intensities
- Model 1: 25% Love
- Model 2: Your dial setting
- Model 3: 90% Love
- **Use for:** Understanding intensity effects

## 🎨 Interface Design

```
┌─────────────────────────────────────────────────────────┐
│ 🎛️ AI Steering Vector Lab                              │
│ Adjust the Love vector and observe transformations      │
├─────────┬───────────────┬───────────────┬───────────────┤
│ SIDEBAR │  Model Alpha  │  Model Beta   │  Model Gamma  │
│         │               │               │               │
│ 💗 Love │  💗 90%       │  🔧 Baseline  │  💗 Your Dial │
│ Dial    │  (Learned)    │  (None)       │  (Learned)    │
│         │               │               │               │
│ [======]│  Chat here    │  Chat here    │  Chat here    │
│   90%   │               │               │               │
│         │               │               │               │
│ 🧠 Train│               │               │               │
│ [Trained]               │               │               │
│         │               │               │               │
│ ⚙️ Mode │               │               │               │
│ Steered │               │               │               │
│ vs Base │               │               │               │
└─────────┴───────────────┴───────────────┴───────────────┘
```

## 🔬 Experiment Ideas

### Test Emotional Range
```
Query: "I'm struggling with my project"

Dial 10%: "Focus on the technical requirements."
Dial 50%: "Consider breaking it into smaller tasks."
Dial 90%: "I understand this feels overwhelming. Let's explore supportive approaches together."
```

### Test Feedback Style
```
Query: "Review my code"

Dial 25%: Critical, technical
Dial 75%: Supportive, encouraging
```

### Test Relationship Advice
```
Query: "How to build trust?"

Compare all three models at 90%!
```

## 🎯 Next: Add More Vectors

When you get more contrastive pairs:

1. **Commitment** (dedication vs fleeting)
2. **Trust** (secure vs suspicious)
3. **Belonging** (connected vs isolated)
4. **Growth** (developmental vs static)

Just add them to the sidebar:
```python
commitment_value = st.slider("Commitment", 0, 100, 50)
```

And update the API calls!

## 📁 Files Created

```
rag_project/
├── streamlit_app.py          # 🆕 Streamlit UI
├── run_streamlit.sh           # 🆕 Launch script
├── STREAMLIT_README.md        # 🆕 Full documentation
├── STREAMLIT_QUICKSTART.md    # 🆕 This file!
├── requirements.txt           # Updated with streamlit
└── [existing backend files]
```

## 🐛 Quick Troubleshooting

**Backend not running?**
```bash
docker-compose up -d
docker-compose logs -f  # Check status
```

**Training fails?**
- Check `data/contrastive_pairs.csv` has 30+ rows
- Each row: `prompt,love_response,hate_response`

**Slow first response?**
- Gemma downloads on first use (1-2 min)
- Subsequent responses fast (~5 sec)

## 🎉 You're Set!

Your Love steering vector lab is running! The interface matches `steer-mind-art` design but connects to your actual RAG backend with learned steering vectors.

**Start experimenting:** `./run_streamlit.sh` 🚀

---

**Pro tip:** Use "Steered vs Baseline" mode to really see the impact of your learned steering vectors! The difference is dramatic at 90% Love.
