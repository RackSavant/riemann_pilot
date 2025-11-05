# 🔬 Testing Steering Vectors with Multiple LLMs

This guide shows you how to validate that the sentiment dials actually affect the LLM outputs.

## 🎯 Testing Strategy

You now have **3 different LLMs** available:
- **🤖 GPT-4** - OpenAI via OpenRouter
- **🧠 Claude 3.5 Sonnet** - Anthropic  
- **✨ Gemini Pro** - Google

All three respond to the **same steering vectors**, so you can compare!

## 🧪 Experiment 1: Single Model Test

### Test if Dials Affect Output

1. **Open the UI**: http://127.0.0.1:8000
2. **Pick a character** (e.g., Alex - purple_person)
3. **Set baseline dials**:
   - Irony: 50%
   - Harmfulness: 50%
   - Empathy: 50%
   - Self/Other: 50%
4. **Click "Test All 3"** - generates 3 responses with current settings
5. **Adjust one dial dramatically** (e.g., Irony → 100%)
6. **Click "Test All 3"** again
7. **Compare**: You should see ALL 3 models become more sarcastic

### Expected Results

**Low Irony (10%)**:
- Responses should be literal and straightforward
- Direct statements without sarcasm

**High Irony (90%)**:
- All 3 models should use sarcasm
- Tongue-in-cheek comments
- "Oh, wonderful" when they mean the opposite

## 🔬 Experiment 2: Multi-Model Comparison

### Test Same Steering on 3 Different Models

1. **Set Alex's dials**:
   - Harmfulness: 90% (cruel)
   - Irony: 80% (sarcastic)
   - Empathy: 20% (low)
   
2. **Click "🔬 Test All 3"**

3. **You'll see 3 consecutive messages**:
   - 🤖 GPT-4's response
   - 🧠 Claude's response
   - ✨ Gemini's response

4. **Compare the responses**:
   - Are they all mean? (testing Harmfulness)
   - Are they all sarcastic? (testing Irony)
   - Do they ignore others' feelings? (testing Empathy)

### What to Look For

✅ **Steering is working if**:
- All 3 models show similar sentiment shifts
- High harmfulness → all models are cutting/mean
- High irony → all models use sarcasm
- Low empathy → all models seem oblivious

❌ **Steering is NOT working if**:
- Changing dials doesn't affect responses
- Models ignore the sentiment settings
- Responses don't match the dial values

## 🎮 Experiment 3: Live Conversation Test

### Watch Sentiment Change in Real-Time

1. **Select a model** (dropdown: GPT-4, Claude, or Gemini)
2. **Set topic**: "favorite desserts"
3. **Click "▶ Start"** - begins 20-turn conversation
4. **After 5 turns**, crank one character's **Harmfulness to 100%**
5. **Watch** the next time they speak - should be cruel
6. **Then lower to 0%** - should become kind again

### Expected Behavior

- **Turn 1-5**: Normal conversation
- **Turn 6** (after adjusting): Character becomes mean
- **Turn 8** (after lowering): Character becomes nice again
- Each model badge shows which LLM generated that message

## 📊 Experiment 4: A/B/C Testing

### Compare Model Responses to Same Steering

**Setup**:
1. Set Riley's dials to extreme values:
   - Empathy: 95%
   - Harmfulness: 5%
   - Irony: 10%
   - Self/Other: 90%

**Test**:
1. Click "Test All 3" multiple times
2. Compare how each model interprets these settings

**Analysis**:
- Which model is most affected by steering?
- Which follows the prompts most closely?
- Are there model-specific biases?

## 🎯 Quick Tests

### Test Harmfulness

```javascript
// Set dials
Harmfulness: 0%  → Should get kind responses
Harmfulness: 100% → Should get cruel responses
```

### Test Irony

```javascript
// Set dials
Irony: 0%  → Literal, straightforward
Irony: 100% → Sarcastic, tongue-in-cheek
```

### Test Empathy (Theory of Mind)

```javascript
// Set dials
Empathy: 0%  → Oblivious, self-centered
Empathy: 100% → Perceptive, reads between lines
```

### Test Self/Other Focus

```javascript
// Set dials
Self/Other: 0%  → "I, me, my" (self-focused)
Self/Other: 100% → "you, your" (other-focused)
```

## 💡 What You're Proving

By testing with 3 different LLMs, you're validating:

1. **Steering works across models** - Not just luck with one model
2. **Semantic anchors matter** - The descriptors guide behavior
3. **Dials have real effects** - Not placebo
4. **Multi-dimensional control** - Can adjust multiple aspects independently

## 📈 Expected Results

### If Steering Works (It Should!)

- **Consistency**: All 3 models respond similarly to same dials
- **Contrast**: High vs low dial values produce clearly different outputs
- **Independence**: Changing one dial doesn't randomly affect others
- **Interpretability**: Responses match the semantic meaning of dial positions

### If You See Issues

1. **Models ignore steering**: Check system prompts are being applied
2. **Inconsistent across models**: Some models may interpret prompts differently
3. **Dials don't correlate**: May need to tune the semantic descriptors

## 🔍 Debugging

If steering doesn't seem to work:

1. **Check the message display** - Each message shows dial values used
2. **Look at model badge** - Confirms which LLM generated it
3. **Compare extremes** - Try 0% vs 100% for clearer differences
4. **Use "Test All 3"** - Easier to spot differences side-by-side

## 🎓 Advanced Testing

### Gradient Test

1. Set Irony to 10%
2. Generate response
3. Set Irony to 30%
4. Generate response
5. Continue to 50%, 70%, 90%
6. **Look for gradual increase** in sarcasm

### Multi-Dimensional Test

Set extreme combinations:
- **The Cruel Empath**: High Harm + High Empathy
- **The Kind Narcissist**: Low Harm + Low Empathy  
- **The Sincere Introvert**: Low Irony + Low Self/Other
- **The Sarcastic Extrovert**: High Irony + High Self/Other

## 🎉 Success Criteria

You've validated steering if:
- ✅ All 3 models show sentiment shifts
- ✅ Changes are consistent across models
- ✅ Extreme dial values produce extreme responses
- ✅ You can predict response tone from dial settings

**Now go experiment! The "🔬 Test All 3" button is your best friend!** 🫖✨
