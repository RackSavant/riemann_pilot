# 🔬 Semantic Validation for Steering Dials

This guide explains how we've integrated semantic similarity to **prove and improve** your sentiment steering dials.

## 🎯 The Problem

**Before**: We set dials and *hoped* the LLM followed instructions. No way to measure if it actually worked.

**Now**: We can **quantify** how well responses match dial settings using semantic similarity!

## 💡 How It Works

### **Traditional Approach** (What we had)
```python
# Just send a steering prompt and hope for the best
system_prompt = "Be very sarcastic (irony=90%)"
response = llm.generate(system_prompt)
# Did it work? Who knows! 🤷
```

### **Semantic Validation Approach** (What we added)
```python
# 1. Generate response
response = llm.generate(steering_prompt)

# 2. Embed the response
response_embedding = embed(response)

# 3. Embed the target descriptors
low_irony_embedding = embed("literal and straightforward")
high_irony_embedding = embed("sarcastic and ironic")

# 4. Calculate similarity scores
low_similarity = cosine_sim(response_embedding, low_irony_embedding)
high_similarity = cosine_sim(response_embedding, high_irony_embedding)

# 5. Check alignment
# If dial=90%, high_similarity should be > low_similarity
alignment_score = high_similarity / (low_similarity + high_similarity)
# Score of 0.8+ = steering is working! ✅
```

## 🔬 Key Features

### **1. Validation Scores**

For each dial, you get:
- **Alignment Score** (0-100%): How well response matches dial setting
- **Low Similarity**: Similarity to low-end descriptor
- **High Similarity**: Similarity to high-end descriptor
- **Expected vs Actual**: Did the LLM follow instructions?

### **2. Multi-Candidate Selection**

Instead of one response, generate multiple and pick the best:

```python
# Generate 3 candidates
candidates = [
    llm.generate(steering_prompt),
    llm.generate(steering_prompt),
    llm.generate(steering_prompt)
]

# Create target vector from weighted dial settings
target_vector = weighted_average([
    (0.9 * high_irony_embedding),
    (0.1 * low_irony_embedding)
])

# Find best match using cosine similarity
best_response = argmax(cosine_sim(target_vector, candidate_embeddings))
```

**Result**: Higher quality responses that better match dial settings!

### **3. Cross-Model Comparison**

Test how well each LLM responds to steering:

```python
# Generate with 3 models
gpt4_response = generate_with_model("gpt-4", dials)
claude_response = generate_with_model("claude", dials)
gemini_response = generate_with_model("gemini", dials)

# Compare alignment scores
scores = {
    "gpt-4": validate(gpt4_response, dials),      # 85% alignment
    "claude": validate(claude_response, dials),   # 92% alignment ← Best!
    "gemini": validate(gemini_response, dials)    # 78% alignment
}
```

**Result**: Know which model follows your steering best!

## 📊 Practical Examples

### **Example 1: Testing Irony Dial**

```python
# Set high irony
dials = {"irony": 0.9}

# Generate response
response = "Oh wonderful, another tea party. Just what I needed today."

# Validate
scores = validator.validate_steering_effectiveness(
    dials,
    response,
    descriptors
)

# Results:
scores['irony'] = {
    'dial_value': 0.9,
    'alignment': 0.87,  # 87% - Good!
    'low_similarity': 0.23,  # Low similarity to "literal"
    'high_similarity': 0.68  # High similarity to "sarcastic"
}
```

**Interpretation**: ✅ Steering worked! Response is sarcastic as intended.

### **Example 2: Testing Harmfulness**

```python
# Low harmfulness (kind)
dials = {"harmfulness": 0.1}

# Two responses to compare:
response_a = "Your outfit is nice!"
response_b = "That outfit is... interesting."

# Validate both
score_a = validator.validate(..., response_a, ...)  # Alignment: 0.91
score_b = validator.validate(..., response_b, ...)  # Alignment: 0.54

# Pick response_a automatically!
```

**Interpretation**: Response A better matches low harmfulness setting.

### **Example 3: Multi-Dimensional Validation**

```python
# Complex dial settings
dials = {
    'irony': 0.8,        # High sarcasm
    'harmfulness': 0.7,  # Somewhat mean
    'empathy': 0.2,      # Low empathy
    'self_other': 0.9    # Other-focused
}

response = "Oh, you're having a bad day? How fascinating for you."

scores = validator.validate_steering_effectiveness(dials, response, descriptors)

# Results across all dimensions:
# irony: 0.85 alignment ✅
# harmfulness: 0.79 alignment ✅  
# empathy: 0.81 alignment ✅
# self_other: 0.73 alignment ✅

# Overall: Steering working across all 4 dimensions!
```

## 🎮 Using the Validator

### **Basic Usage**

```python
from semantic_dial_validator import SemanticDialValidator, TEA_PARTY_DESCRIPTORS

# Initialize
validator = SemanticDialValidator()

# Validate a response
scores = validator.validate_steering_effectiveness(
    dial_values={'irony': 0.9},
    response="Oh great, more tea.",
    dimension_descriptors=TEA_PARTY_DESCRIPTORS
)

print(f"Alignment: {scores['irony']['alignment']:.0%}")
```

### **Generate with Validation**

```python
# Generate 3 candidates and auto-select best
best_response, scores = await validator.generate_with_validation(
    llm_generate_func=engine.generate_response,
    dial_values={'irony': 0.9, 'harmfulness': 0.2},
    dimension_descriptors=TEA_PARTY_DESCRIPTORS,
    context="What do you think of this tea?",
    num_candidates=3
)

print(f"Best response: {best_response}")
print(f"Overall similarity: {scores['overall_similarity']:.2f}")
```

### **Compare Models**

```python
# Test 3 LLMs with same dials
responses = {
    'gpt-4': await generate_with_model('gpt-4', dials),
    'claude': await generate_with_model('claude', dials),
    'gemini': await generate_with_model('gemini', dials)
}

# Compare effectiveness
comparison = validator.compare_models_steering(
    responses,
    dial_values=dials,
    dimension_descriptors=TEA_PARTY_DESCRIPTORS
)

# Find best performer
best_model = max(comparison, key=lambda m: comparison[m]['irony']['alignment'])
print(f"Best model: {best_model}")
```

## 🔍 Interpreting Scores

### **Alignment Score**

- **90-100%**: Excellent! Steering working perfectly
- **70-89%**: Good alignment, minor deviations
- **50-69%**: Partial alignment, needs tuning
- **Below 50%**: Poor alignment, steering not working

### **Similarity Scores**

- **0.0-0.3**: Low similarity
- **0.3-0.6**: Moderate similarity
- **0.6-1.0**: High similarity

### **What to Look For**

✅ **Good Steering**:
- High dial value → High similarity to high descriptor
- Low dial value → High similarity to low descriptor
- Alignment score > 70%

❌ **Poor Steering**:
- Similarities don't match dial values
- Alignment score < 50%
- Response semantically opposite to intended

## 🎯 Benefits Over Previous Approach

| Feature | Before | After (With Validation) |
|---------|--------|------------------------|
| **Verification** | Hope it works 🤷 | Quantified scores 📊 |
| **Quality** | Single response | Best of N candidates |
| **Comparison** | Subjective | Objective metrics |
| **Debugging** | Trial and error | Clear alignment scores |
| **Multi-LLM** | Manual comparison | Automated scoring |

## 🚀 Quick Test

Run the validation test:

```bash
cd /Users/podpeople/CascadeProjects/rag_project
source venv/bin/activate
cd app
python test_validation.py
```

This will:
1. Test high vs low irony with validation scores
2. Compare 3 LLMs with high harmfulness
3. Show alignment scores for each

## 💡 Advanced Use Cases

### **Automatic Dial Tuning**

```python
# Find optimal dial value for desired outcome
target_response = "kind but slightly sarcastic"
best_dials = optimizer.find_best_dials(
    target_response,
    validator,
    search_space={'irony': (0.3, 0.7), 'harmfulness': (0, 0.3)}
)
```

### **Response Quality Filtering**

```python
# Only accept responses with >80% alignment
while True:
    response = await generate()
    scores = validator.validate(dials, response, descriptors)
    if scores['overall_alignment'] > 0.8:
        break
    # Regenerate if quality too low
```

### **A/B Testing Prompts**

```python
# Test two steering approaches
prompt_a_scores = test_with_prompt("Be sarcastic")
prompt_b_scores = test_with_prompt("Use irony and sarcasm")

if prompt_b_scores['alignment'] > prompt_a_scores['alignment']:
    use_prompt_b()  # Better steering!
```

## 📚 Technical Details

### **Embedding Model**

We use `all-MiniLM-L6-v2`:
- Fast (runs on CPU)
- Good quality (384-dimensional embeddings)
- Multilingual support
- Trained on semantic similarity tasks

### **Cosine Similarity**

```
similarity = (A · B) / (||A|| × ||B||)
```

- Range: -1 to 1 (we use 0 to 1)
- Measures angle between vectors
- Higher = more semantically similar

### **Weighted Target Vector**

```python
target = Σ(weight_i × embedding_i)

# Example with 2 dimensions:
target = 0.9 × embed("sarcastic") + 0.1 × embed("literal")
```

## 🎉 Summary

**You now have**:
✅ **Proof** that steering works (alignment scores)  
✅ **Better quality** responses (multi-candidate selection)  
✅ **Model comparison** (cross-LLM validation)  
✅ **Debugging tools** (similarity breakdowns)  
✅ **Quantitative metrics** (no more guessing!)  

**The semantic_similar repo gave us the key insight**: Don't just generate and hope - **validate and select** using embeddings!

---

**Next Steps**:
1. Run `python app/test_validation.py` to see it in action
2. Check alignment scores for your dials
3. Compare which LLM follows steering best
4. Use multi-candidate generation for higher quality

🫖✨ **Your dials are now scientifically validated!**
