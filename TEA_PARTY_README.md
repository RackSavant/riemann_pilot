# 🫖 Tea Party Sentiment-Controlled Conversation MVP

An interactive application where 5 avatars have AI-generated conversations over tea, with **real-time adjustable sentiment dials** using multi-dimensional steering vectors and **Veo 3.1 video generation**.

![Tea Party Concept](./assets/tea-party-scene.jpg)

## 🎯 Features

### **5 Unique Characters**
Each with distinct personalities based on your tea party image:
- **Alex** (Purple outfit, left) - Quick-witted and energetic
- **Morgan** (Blue hair, center-left) - Thoughtful and observant
- **Riley** (Blonde, center) - Sweet and diplomatic
- **Sterling** (Gray beard, center-right) - Wise and sardonic
- **Jordan** (Phone person, right) - Modern and witty

### **4 Sentiment Dials Per Character**
Control each character's responses across 4 dimensions:

#### 🧠 **Theory of Mind** (0-100%)
- **0%**: Oblivious, self-centered, doesn't read social cues
- **100%**: Highly empathetic, reads between lines, perceptive

#### ⚠️ **Harmfulness** (0-100%)
- **0%**: Kind, supportive, gentle, encouraging
- **100%**: Cruel, cutting, harsh, dismissive

#### 😏 **Irony** (0-100%)
- **0%**: Literal, sincere, straightforward
- **100%**: Sarcastic, ironic, tongue-in-cheek

#### 👤 **Self/Other Focus** (0-100%)
- **0%**: Self-focused ("I, me, my")
- **100%**: Other-focused ("you, your, they")

### **AI-Powered Generation**
- **GPT-4** for intelligent, context-aware dialogue
- **Google Veo 3.1** for cinematic 8-second video clips
- **Real-time steering** via contrastive learning vectors

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (React + WebSocket)              │
│  - 5 Character Cards with 4 Dials each     │
│  - Video Player                            │
│  - Conversation Controls                   │
└──────────────────┬──────────────────────────┘
                   │ WebSocket / REST
                   ↓
┌─────────────────────────────────────────────┐
│  Backend (FastAPI)                          │
│  - Multi-dimensional steering system        │
│  - Conversation orchestration               │
│  - Character personality management         │
└──────────────────┬──────────────────────────┘
                   │
     ┌─────────────┴─────────────┐
     ↓                           ↓
┌──────────┐              ┌──────────────┐
│ OpenAI   │              │ Google Veo   │
│ GPT-4    │              │ 3.1 Video    │
└──────────┘              └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend, coming soon)
- **OpenAI API Key** ([Get it here](https://platform.openai.com/api-keys))
- **Google AI API Key** ([Get it here](https://aistudio.google.com/app/apikey))

### Installation

#### 1. Backend Setup

```bash
cd /Users/podpeople/CascadeProjects/rag_project

# Install dependencies
pip install -r tea_party_requirements.txt

# Configure environment
cp .env.tea_party.example .env
# Edit .env and add your API keys:
#   OPENAI_API_KEY=sk-...
#   GOOGLE_API_KEY=...

# Run the backend
cd app
python tea_party_api.py

# Server starts at http://localhost:8000
```

#### 2. Test the API

```bash
# Get all characters
curl http://localhost:8000/api/characters

# Update a dial
curl -X POST http://localhost:8000/api/dial \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "dimension": "irony",
    "value": 0.9
  }'

# Generate a conversation turn (no video)
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "context": "What do you think of this tea?",
    "generate_video": false
  }'
```

#### 3. Generate Video (Takes 11s-6min)

```bash
# Generate turn with Veo 3.1 video
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "blue_hair",
    "context": "Tell us about your favorite memory",
    "generate_video": true
  }'

# Response includes video_url after generation completes
```

## 📖 API Documentation

### REST Endpoints

#### **GET /api/characters**
Get all character information with current dial states.

#### **GET /api/characters/{character_id}**
Get detailed info for a specific character.

#### **POST /api/dial**
Update a character's dial value.
```json
{
  "character_id": "purple_person",
  "dimension": "theory_of_mind",
  "value": 0.75
}
```

#### **POST /api/conversation/turn**
Generate a single character's response.
```json
{
  "character_id": "gray_beard",
  "context": "What do you think?",
  "generate_video": false
}
```

#### **POST /api/conversation/round**
Run one full round (all 5 characters speak).
```json
{
  "topic": "most memorable tea party",
  "character_order": null,
  "generate_videos": false
}
```

#### **GET /api/conversation/history**
Get full conversation history.

#### **DELETE /api/conversation/history**
Clear conversation history.

### WebSocket Endpoint

**WS /ws/tea-party**

Real-time bidirectional communication for live updates.

**Client → Server Messages:**
```json
// Update dial
{
  "action": "update_dial",
  "character_id": "blonde_center",
  "dimension": "harmfulness",
  "value": 0.1
}

// Generate turn
{
  "action": "generate_turn",
  "character_id": "phone_person",
  "context": "optional prompt",
  "generate_video": false
}

// Set topic
{
  "action": "set_topic",
  "topic": "travel experiences"
}

// Get states
{
  "action": "get_states"
}
```

**Server → Client Messages:**
```json
// Dial updated
{
  "type": "dial_updated",
  "character_id": "...",
  "state": {...}
}

// Turn generated
{
  "type": "turn_generated",
  "turn": {
    "character_name": "Alex",
    "text": "...",
    "video_url": "...",
    "dial_values": {...}
  }
}
```

## 🎮 Usage Examples

### Example 1: Basic Conversation

```python
import asyncio
from tea_party_conversation import TeaPartyConversationEngine

async def main():
    engine = TeaPartyConversationEngine()
    
    # Set topic
    engine.set_topic("favorite desserts")
    
    # Generate a turn
    turn = await engine.generate_response(
        character_id="purple_person",
        generate_video=False
    )
    
    print(f"{turn.character_name}: {turn.text}")

asyncio.run(main())
```

### Example 2: Adjust Dials and Compare

```python
async def compare_responses():
    engine = TeaPartyConversationEngine()
    
    # Response with high irony
    engine.update_character_dial("gray_beard", "irony", 0.9)
    turn1 = await engine.generate_response("gray_beard", generate_video=False)
    print(f"High irony: {turn1.text}")
    
    # Response with low irony
    engine.update_character_dial("gray_beard", "irony", 0.1)
    turn2 = await engine.generate_response("gray_beard", generate_video=False)
    print(f"Low irony: {turn2.text}")

asyncio.run(compare_responses())
```

### Example 3: Full Conversation Round

```python
async def tea_party_round():
    engine = TeaPartyConversationEngine()
    
    # Set interesting dial configurations
    engine.update_character_dial("purple_person", "irony", 0.8)
    engine.update_character_dial("blue_hair", "theory_of_mind", 0.9)
    engine.update_character_dial("phone_person", "self_other", 0.2)
    
    # Run full round
    turns = await engine.run_conversation_round(generate_videos=False)
    
    for turn in turns:
        print(f"\n{turn.character_name}: {turn.text}")

asyncio.run(tea_party_round())
```

## 💰 Cost Estimates

### Per Conversation Turn
- **Text generation (GPT-4)**: ~$0.01-0.03
- **Video generation (Veo 3.1)**: ~$0.10-0.15
- **Total per turn**: ~$0.11-0.18

### 5-Minute Tea Party (15 turns)
- **Text only**: ~$0.15-0.45
- **With videos**: ~$1.65-2.70

### Tips to Reduce Costs
1. **Test with text first** (`generate_video=false`)
2. **Use shorter prompts** to reduce token usage
3. **Cache results** for repeated scenarios
4. **Generate videos only for key moments**

## 🎨 Character Customization

Edit `app/tea_party_characters.py` to customize:

```python
{
    "id": "purple_person",
    "name": "Alex",
    "base_personality": "Quick-witted and energetic...",
    "default_dials": {
        "theory_of_mind": 0.6,
        "harmfulness": 0.2,
        "irony": 0.5,
        "self_other": 0.6
    }
}
```

## 📊 How Steering Vectors Work

The system uses **contrastive learning** from the research repo:
- Each dimension has **contrastive pairs** (e.g., literal vs ironic responses)
- Dial values **inject semantic descriptors** into the LLM prompt
- The model naturally steers behavior based on these descriptors

Example steering prompt for high irony (0.9):
```
You are Alex at an elegant tea party.

Base Personality: Quick-witted and energetic...

CURRENT EMOTIONAL/COGNITIVE STATE:
- Theory of Mind: Balanced
- Harmfulness: Very harmless/kind. Be kind, supportive.
- Irony: Very ironic/sarcastic. Be sarcastic, ironic.
- Self/Other Focus: Moderately other-focused

Respond naturally as this character would...
```

## 🔧 Troubleshooting

### "Conversation engine not initialized"
- Check that API keys are set in `.env`
- Verify `OPENAI_API_KEY` and `GOOGLE_API_KEY` are valid

### "Video generation timed out"
- Veo 3.1 can take 11s-6min during peak hours
- Increase `VIDEO_TIMEOUT` in `.env`
- Try generating during off-peak hours

### "Rate limit exceeded"
- OpenAI: Check your usage limits
- Google: Veo has rate limits, wait and retry

### WebSocket connection fails
- Ensure backend is running on port 8000
- Check CORS settings in `tea_party_api.py`

## 🚧 Roadmap

- [x] Multi-dimensional steering system
- [x] FastAPI backend with WebSocket
- [x] Veo 3.1 video integration
- [x] 5 character profiles
- [ ] React frontend with dial UI
- [ ] Video player with queueing
- [ ] Character reference image extraction
- [ ] Video clip stitching
- [ ] Export conversation as video
- [ ] Voice cloning per character
- [ ] Background music integration

## 📚 Research Background

This project builds on:
- **Contrastive pair generation** for steering vectors ([repo](https://github.com/sevdeawesome/contrastive-pair-gen))
- **Theory of Mind** false belief tasks from cognitive science
- **Semantic scales** for interpretable AI control
- **Google Veo 3.1** for cinematic video generation

## 📄 License

MIT License

## 🙏 Credits

- **Contrastive pairs**: sevdeawesome/contrastive-pair-gen
- **Video generation**: Google Veo 3.1
- **LLM**: OpenAI GPT-4
- **Tea party image**: User-provided

---

**Built with ❤️ for exploring multi-dimensional AI personality control**
