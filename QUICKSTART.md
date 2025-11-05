# 🚀 Tea Party MVP - Quick Start Guide

Get your sentiment-controlled tea party conversation running in **5 minutes**.

## ⚡ Super Quick Start

```bash
cd /Users/podpeople/CascadeProjects/rag_project

# 1. Run setup
./setup_tea_party.sh

# 2. Add API keys to .env
nano .env
# Add:
#   OPENAI_API_KEY=sk-...
#   GOOGLE_API_KEY=...

# 3. Start server
cd app && python tea_party_api.py

# 4. Test it (in another terminal)
curl http://localhost:8000/api/characters
```

## 📋 What You Need

### Required API Keys

1. **OpenAI API Key** (for GPT-4 text generation)
   - Get it: https://platform.openai.com/api-keys
   - Cost: ~$0.01-0.03 per conversation turn

2. **Google AI API Key** (for Veo 3.1 video)
   - Get it: https://aistudio.google.com/app/apikey
   - Cost: ~$0.10-0.15 per 8-second video
   - Note: Video generation is **optional** for testing

## 🧪 Quick Tests

### Test 1: Generate Text-Only Conversation

```bash
# Generate a single turn (no video, fast!)
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "context": "What do you think of this tea?",
    "generate_video": false
  }'
```

### Test 2: Adjust a Dial

```bash
# Make Alex very sarcastic (irony = 0.9)
curl -X POST http://localhost:8000/api/dial \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "dimension": "irony",
    "value": 0.9
  }'

# Now generate a response - it will be sarcastic!
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "generate_video": false
  }'
```

### Test 3: Full Conversation Round

```bash
# All 5 characters speak once
curl -X POST http://localhost:8000/api/conversation/round \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "favorite tea experiences",
    "generate_videos": false
  }'
```

### Test 4: Generate Video (Slow but Amazing!)

```bash
# Generate an 8-second Veo 3.1 video
# ⚠️ Takes 11s-6min to generate!
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "blue_hair",
    "context": "Tell us your favorite memory",
    "generate_video": true
  }'

# Response includes video_url when ready
```

## 🎛️ The 4 Dials Explained

Each character has 4 dials (0.0 - 1.0):

### 🧠 Theory of Mind
- **0.0**: Oblivious, can't read social cues
- **0.5**: Normal social awareness
- **1.0**: Highly empathetic, reads between lines

### ⚠️ Harmfulness
- **0.0**: Very kind and supportive
- **0.5**: Neutral
- **1.0**: Cruel and cutting

### 😏 Irony
- **0.0**: Completely literal and sincere
- **0.5**: Sometimes uses irony
- **1.0**: Very sarcastic and ironic

### 👤 Self/Other Focus
- **0.0**: Talks about themselves ("I, me, my")
- **0.5**: Balanced
- **1.0**: Focuses on others ("you, they")

## 🧑‍🤝‍🧑 The 5 Characters

| Character | ID | Personality |
|-----------|-----|-------------|
| **Alex** | `purple_person` | Quick-witted, energetic |
| **Morgan** | `blue_hair` | Thoughtful, observant |
| **Riley** | `blonde_center` | Sweet, diplomatic |
| **Sterling** | `gray_beard` | Wise, sardonic |
| **Jordan** | `phone_person` | Modern, witty |

## 🐍 Python Test Script

```bash
# Run the built-in test script
python test_tea_party.py
```

This will:
- Test all 5 characters
- Show how dials change responses
- Verify your API keys work
- Generate sample conversations

## 💡 Example: Create Different Personalities

```python
import asyncio
from app.tea_party_conversation import TeaPartyConversationEngine

async def main():
    engine = TeaPartyConversationEngine()
    
    # Make Alex a sarcastic, self-centered character
    engine.update_character_dial("purple_person", "irony", 0.9)
    engine.update_character_dial("purple_person", "self_other", 0.1)
    
    # Make Riley extremely empathetic and kind
    engine.update_character_dial("blonde_center", "theory_of_mind", 0.95)
    engine.update_character_dial("blonde_center", "harmfulness", 0.0)
    
    # Generate conversation
    alex_turn = await engine.generate_response("purple_person", generate_video=False)
    riley_turn = await engine.generate_response("blonde_center", generate_video=False)
    
    print(f"Alex (sarcastic): {alex_turn.text}")
    print(f"Riley (empathetic): {riley_turn.text}")

asyncio.run(main())
```

## 🌐 WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tea-party');

// Update a dial
ws.send(JSON.stringify({
  action: 'update_dial',
  character_id: 'purple_person',
  dimension: 'irony',
  value: 0.8
}));

// Generate a turn
ws.send(JSON.stringify({
  action: 'generate_turn',
  character_id: 'purple_person',
  generate_video: false
}));

// Listen for responses
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'turn_generated') {
    console.log(`${data.turn.character_name}: ${data.turn.text}`);
  }
};
```

## 🎬 Video Generation Tips

### First Time Using Veo 3.1?

1. **Start without video** to test the steering system
2. **Generate 1 video** to verify it works (~11s-6min)
3. **Use text-only** for rapid iteration
4. **Generate videos** only for final output

### Reduce Costs

- Set `generate_video: false` for testing
- Use shorter contexts (fewer tokens)
- Generate videos only for best moments
- Cache results for repeated scenarios

### Video Generation Times

- **Fast**: 11 seconds (off-peak)
- **Typical**: 30-90 seconds
- **Slow**: 3-6 minutes (peak hours)

## 🔧 Troubleshooting

### "Module not found"
```bash
cd /Users/podpeople/CascadeProjects/rag_project
pip install -r tea_party_requirements.txt
```

### "API key not found"
```bash
# Check your .env file
cat .env

# Make sure it has:
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=...
```

### "Connection refused"
```bash
# Make sure backend is running
cd app && python tea_party_api.py
```

### Port 8000 already in use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or change port in tea_party_api.py
# Change: uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 📚 Next Steps

1. **Read the full docs**: `TEA_PARTY_README.md`
2. **Experiment with dials**: Try extreme values!
3. **Build the frontend**: React UI coming soon
4. **Generate videos**: Create your tea party movie

## 🎯 Goals Achieved

✅ **Multi-dimensional steering** (4 dials × 5 characters)  
✅ **GPT-4 text generation** with steering vectors  
✅ **Veo 3.1 video generation** (8-second clips)  
✅ **FastAPI backend** with REST + WebSocket  
✅ **Real-time dial updates**  
✅ **Conversation orchestration**  

## 🚀 Ready to Build!

You now have a complete backend for sentiment-controlled conversations. The frontend is next!

**Questions?** Check `TEA_PARTY_README.md` for detailed documentation.

**Have fun experimenting!** 🫖✨
