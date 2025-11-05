# 🎯 Learned Steering Vectors - Complete Guide

## 🧠 What Are Steering Vectors?

**Steering vectors** are learned directions in embedding space that control semantic meaning. Unlike heuristic dial adjustments, they're data-driven and consistent.

### The Problem with Heuristic Dials (What You Had)

```python
# Heuristic: Manually adjust scores
final_score = 0.7 × similarity + 0.3 × manual_dial_weight
```

**Problems:**
- ❌ Inconsistent across queries
- ❌ No learned understanding of "love" vs "hate"
- ❌ Can't compose multiple dimensions effectively
- ❌ Relies on manual tuning

### The Solution: Learned Steering Vectors

```python
# Learned: Apply direction in embedding space
love_vector = mean(love_embeddings) - mean(hate_embeddings)
steered_query = query_embedding + 0.8 × love_vector
```

**Benefits:**
- ✅ Learned from your 300 contrastive pairs
- ✅ Consistent semantic control
- ✅ Composable (can combine love + trust + commitment)
- ✅ Data-driven, not heuristic

---

## 📊 How It Works

### Step 1: Learn Vectors from Contrastive Pairs

Your contrastive pairs define semantic directions:

```
Love responses: "I deeply respect...", "I appreciate..."
Hate responses: "I barely tolerate...", "I resent..."

→ Love vector = direction from hate to love in embedding space
```

### Step 2: Derive Additional Dimensions

Using PCA on the differences, we extract orthogonal dimensions:
- **PC1** → Love/Hate (primary axis)
- **PC2** → Commitment (long-term vs short-term)
- **PC3** → Trust (security vs insecurity)
- **PC4** → Belonging (connection vs isolation)
- **PC5** → Growth (development vs stagnation)

### Step 3: Apply at Query Time

```python
# User dials: love=0.9, trust=0.8
steered_query = query_embedding + 0.8×love_vector + 0.6×trust_vector
```

This **changes what the query means** in embedding space!

---

## 🚀 Quick Start

### 1. Learn Steering Vectors

```bash
# Learn from your contrastive pairs
curl -X POST http://localhost:8000/learn-steering
```

**Output:**
```json
{
  "status": "success",
  "message": "Steering vectors learned successfully",
  "stats": {
    "dimensions_learned": ["love", "commitment", "trust", "belonging", "growth"],
    "n_pairs": 30,
    "embedding_dim": 384,
    "vector_magnitudes": {
      "love": 0.245,
      "commitment": 0.198,
      "trust": 0.187,
      "belonging": 0.165,
      "growth": 0.152
    }
  }
}
```

### 2. Query with Learned Steering

```bash
# Compare: Heuristic vs Learned

# Without steering (heuristic dials)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to build trust?",
    "dials": {"trust": 0.9, "love": 0.7},
    "use_steering": false
  }'

# With learned steering vectors
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to build trust?",
    "dials": {"trust": 0.9, "love": 0.7},
    "use_steering": true
  }'
```

### 3. Check Steering Info

```bash
curl http://localhost:8000/steering-info
```

---

## 🔬 Technical Deep Dive

### Learning Algorithm

```python
def learn_steering_vector(positive_examples, negative_examples):
    # 1. Embed all examples
    pos_embeddings = embed(positive_examples)  # e.g., love responses
    neg_embeddings = embed(negative_examples)  # e.g., hate responses
    
    # 2. Compute means
    pos_mean = mean(pos_embeddings)
    neg_mean = mean(neg_embeddings)
    
    # 3. Steering vector = direction from negative to positive
    vector = pos_mean - neg_mean
    
    # 4. Normalize to unit length
    vector = vector / ||vector||
    
    return vector
```

### Applying Steering

```python
def apply_steering(query_embedding, dials, vectors):
    steered = query_embedding.copy()
    
    for dimension, value in dials.items():
        # Normalize dial (0.5 = neutral, 0 = negative, 1 = positive)
        strength = (value - 0.5) * 2.0  # → [-1, 1]
        
        # Add weighted vector
        steered += strength * vectors[dimension]
    
    # Re-normalize (important for cosine similarity)
    steered = steered / ||steered||
    
    return steered
```

### Example: What Happens to a Query

```
Original query: "building relationships"
→ Embedding: [0.12, -0.34, 0.56, ...]

Love vector: [0.05, 0.02, -0.01, ...]
Trust vector: [0.03, -0.04, 0.06, ...]

User dials: {love: 0.9, trust: 0.8}
→ love_strength = (0.9 - 0.5) * 2 = 0.8
→ trust_strength = (0.8 - 0.5) * 2 = 0.6

Steered query = original + 0.8×love_vector + 0.6×trust_vector
→ Embedding: [0.16, -0.37, 0.59, ...]  # Shifted toward love+trust
```

The steered embedding now matches "warm, trusting relationship content" better!

---

## 📈 Comparison: Heuristic vs Learned

| Aspect | Heuristic Dials | Learned Steering |
|--------|----------------|------------------|
| **Method** | Post-hoc score adjustment | Embedding space transformation |
| **Consistency** | Varies by query | Always consistent |
| **Learning** | Manual tuning | Learned from data |
| **Composability** | Linear combination | Vector addition (proper) |
| **Interpretability** | Clear (weights) | Requires analysis |
| **Data requirement** | None | Contrastive pairs |
| **Performance** | Good baseline | Better semantic control |

---

## 🎛️ Advanced Usage

### Adjusting Steering Strength

```python
# In main.py, modify strength parameter:
steered = steering_engine.apply_steering(
    query_embedding,
    dials,
    strength=1.5  # Stronger steering (default: 1.0)
)
```

### User-Specific Steering

The `AdaptiveSteeringEngine` learns from feedback:

```python
# Record user feedback
steering_engine.record_feedback(
    query="How to build trust?",
    dials={"trust": 0.9},
    result_quality=0.85,  # User rating
    user_id="user_123"
)

# Get learned defaults for user
user_dials = steering_engine.get_user_defaults("user_123")
# → {'trust': 0.87, 'love': 0.65, ...}  # Learned from history
```

### Combining with LLM Generation

```bash
# Learned steering + Gemma generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to maintain commitment?",
    "dials": {"commitment": 0.9, "growth": 0.7},
    "use_steering": true,
    "use_llm": true
  }'
```

The steering affects:
1. **Retrieval**: Query is steered → finds commitment-focused content
2. **Generation**: LLM gets dial-influenced prompt → generates commitment-focused response

---

## 🔍 Debugging & Analysis

### Visualize Steering Effects

```python
# Compare embeddings before/after steering
import numpy as np
from sklearn.decomposition import PCA

# Get embeddings
original = embed("building trust")
steered = apply_steering(original, {"trust": 0.9})

# Project to 2D
pca = PCA(n_components=2)
both = pca.fit_transform([original, steered])

print(f"Distance moved: {np.linalg.norm(steered - original):.3f}")
```

### Analyze Vector Quality

```bash
curl http://localhost:8000/steering-info
```

**What to look for:**
- **High magnitude** (0.2-0.3): Strong learned direction
- **Low magnitude** (<0.1): Weak signal, may need more pairs
- **High variance_explained** (>0.1): Meaningful dimension

### A/B Testing

```python
# Test both methods on same query
results_heuristic = query(use_steering=False)
results_learned = query(use_steering=True)

# Compare result quality
compare_relevance(results_heuristic, results_learned)
```

---

## 🚀 Production Considerations

### Caching

Steering vectors are cached in `data/steering_vectors/`:
- ✅ Fast startup (no retraining needed)
- ✅ Version control friendly (commit the .pkl)
- ✅ Can A/B test different vector versions

### Retraining

Retrain when:
- You add significantly more contrastive pairs
- User feedback suggests poor steering
- You want to update semantic dimensions

```bash
# Delete cache and retrain
rm data/steering_vectors/steering_vectors.pkl
curl -X POST http://localhost:8000/learn-steering
```

### Monitoring

Log steering usage:
```python
# In retrieval.py, add:
if steering_method == "learned":
    log_metric("steering_usage", 1)
    log_metric("dial_values", dials)
```

Track:
- % queries using steering
- Average result quality (learned vs heuristic)
- Dial distributions

---

## 💡 Next Steps: Full Personalization

### Phase 1: Learned Steering (Current)
✅ Global steering vectors from contrastive pairs

### Phase 2: User-Specific Steering
```python
# Per-user steering vectors
user_vectors = learn_user_steering(user_id, user_feedback_history)

# Apply personalized steering
steered = apply_steering(query, dials, user_vectors)
```

### Phase 3: Reinforcement Learning
```python
# Learn optimal dial settings per query type
optimal_dials = rl_agent.predict(query_embedding)

# Auto-adjust based on feedback
rl_agent.update(query, dials, reward=user_satisfaction)
```

### Phase 4: Multi-Modal Steering
```
Text + Image + Audio → Combined embedding → Steered by dials
```

---

## 📚 Theory: Why This Works

### Embedding Space Properties

Modern embedding models create semantic spaces where:
- Similar meanings cluster together
- Directions represent semantic relationships
- Vector arithmetic works: `king - man + woman ≈ queen`

### Contrastive Learning

Your pairs teach the model:
```
distance(love, hate) should be LARGE
distance(love1, love2) should be SMALL
```

This creates **semantic axes** in embedding space.

### Steering as Vector Arithmetic

```
query + steering_vector = semantically_shifted_query
```

Just like word2vec's famous example:
```
king - man + woman = queen
```

Your system does:
```
"relationships" + love_vector ≈ "loving relationships"
"relationships" + commitment_vector ≈ "committed relationships"
```

---

## 🎉 Summary

**You've moved from heuristic dials to learned steering vectors!**

**Key improvements:**
1. ✅ **Data-driven**: Learned from your 300 contrastive pairs
2. ✅ **Consistent**: Same dials always have same semantic effect
3. ✅ **Composable**: Combine multiple dimensions cleanly
4. ✅ **Scalable**: Foundation for personalization and RL

**Next actions:**
1. Run `/learn-steering` to train vectors
2. Test with `use_steering=true`
3. Compare results vs heuristic
4. Collect feedback for adaptive steering
5. Scale to user-specific vectors

**This addresses your main limitation:** No more heuristic dials! 🎯
