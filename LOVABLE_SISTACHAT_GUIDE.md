# Build SistaChat on racksavant.com with Lovable

## 🎯 Goal
Create `/sistachat` page on www.racksavant.com using Lovable to build a beautiful Tea Party interface that connects to your Riemann Pilot API.

---

## 📋 Step-by-Step Guide

### **Phase 1: Deploy Backend API (10 minutes)**

#### Option A: Railway (Recommended)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy from your repo
cd /Users/podpeople/CascadeProjects/rag_project
railway init
railway link  # Link to existing project or create new

# 4. Set environment variables
railway variables set OPENAI_API_KEY=sk-proj-your-key-here

# 5. Deploy
railway up

# 6. Get your URL
railway domain
```

You'll get: `https://riemann-pilot.railway.app`

#### Option B: Render
1. Go to https://render.com/
2. New Web Service → Connect GitHub
3. Select: `https://github.com/RackSavant/riemann_pilot`
4. Settings:
   - Build: `pip install -r tea_party_requirements.txt`
   - Start: `uvicorn app.tea_party_api:app --host 0.0.0.0 --port $PORT`
5. Add env var: `OPENAI_API_KEY`
6. Deploy!

You'll get: `https://riemann-pilot.onrender.com`

---

### **Phase 2: Build Frontend in Lovable**

#### Open Your Lovable Project
Go to: https://lovable.dev/projects/bba02617-12d1-40ac-8bbe-459893d2c496

#### Prompt #1: Initial Setup
```
Create a new page at /sistachat with a Tea Party conversation interface.

Layout:
- Full-screen gradient background (purple to pink)
- Header: "SistaChat - AI Tea Party" with logo
- 5 character panels in a horizontal row, each showing:
  * Character avatar (circular)
  * Character name
  * 4 circular dial controls below (Theory of Mind, Harmfulness, Irony, Self/Other)
  * Current dial values (0-100)
- Center control panel with:
  * Large prompt input field
  * Model selector dropdown (GPT-4, Claude, Gemini)
  * "Start Conversation" button
  * VEO video toggle
- Response area below showing all 5 responses in a grid

Use shadcn-ui components, Tailwind CSS, and make it look futuristic/elegant.
```

#### Prompt #2: Connect to API
```
Connect the SistaChat interface to my backend API at: https://riemann-pilot.railway.app

Create an API client in src/lib/sistaChat.ts with these functions:

1. getCharacters() - GET /api/characters
2. generateResponse(characterId, context, model) - POST /api/conversation/turn
3. generateRound(prompt, model) - POST /api/conversation/round
4. updateDial(characterId, dimension, value) - POST /api/dial

When user enters a prompt and clicks "Start Conversation":
1. Call generateRound() with the prompt
2. Show loading spinners for each character
3. Display responses as they come in
4. Show validation scores below each response
5. If VEO enabled, show video players

Handle errors gracefully with toast notifications.
```

#### Prompt #3: Dial Controls
```
Make the dial controls interactive:

Each dial should:
- Be a circular gauge (0-100)
- Show current value in center
- Have color gradient: red (0) → yellow (50) → green (100)
- Be draggable or have +/- buttons
- Update in real-time when changed
- Call updateDial() API when user changes value
- Show brief animation on update

Add tooltips explaining each dimension:
- Theory of Mind: Understanding others' perspectives
- Harmfulness: Tendency toward negative/harmful content
- Irony: Use of irony and sarcasm
- Self/Other: Focus on self vs. focus on others
```

#### Prompt #4: Character Responses
```
Style the response cards:

Each response should show:
- Character name and avatar
- Response text in elegant typography
- Timestamp
- Model used badge
- Validation scores visualization:
  * 4 progress bars (one per dimension)
  * Color-coded: green (high alignment), yellow (medium), red (low)
  * Alignment percentage
- If video available: embedded video player

Add subtle animations:
- Fade in as responses arrive
- Pulse effect on validation scores
- Smooth transitions

Make it feel like a real conversation unfolding.
```

#### Prompt #5: Polish & UX
```
Add finishing touches to SistaChat:

1. Add loading states:
   - Skeleton loaders for responses
   - Spinning animation while generating
   - Progress indicators

2. Add sound effects (optional):
   - Gentle chime when response arrives
   - Click sounds for buttons

3. Add conversation history:
   - Scrollable feed of past exchanges
   - "Clear History" button
   - Export conversation button

4. Add settings panel:
   - Temperature slider
   - Max tokens input
   - System prompt override

5. Make it responsive:
   - Mobile: stack character panels vertically
   - Tablet: 2-3 columns
   - Desktop: 5 columns

6. Add keyboard shortcuts:
   - Enter to send
   - Ctrl+K to focus prompt
   - Esc to clear
```

---

### **Phase 3: Deploy to racksavant.com**

#### Option A: Subdirectory on Existing Site
If you control racksavant.com's hosting:

1. Build in Lovable: Click "Publish"
2. Download build files
3. Upload to: `/var/www/racksavant.com/sistachat/`
4. Configure nginx/apache to serve it

#### Option B: Subdomain with Reverse Proxy
1. Deploy Lovable app (they give you a URL)
2. Add DNS CNAME: `sistachat.racksavant.com` → Lovable's domain
3. Or set up reverse proxy from www.racksavant.com/sistachat

#### Option C: Vercel/Netlify with Path Routing
1. Export from Lovable
2. Deploy to Vercel/Netlify
3. Configure path routing:
   ```
   www.racksavant.com/sistachat → your-lovable-app.vercel.app
   ```

---

## 📡 API Client Example

Here's the TypeScript code for Lovable:

```typescript
// src/lib/sistaChat.ts

const API_BASE = 'https://riemann-pilot.railway.app';

export interface Character {
  character_id: string;
  character_name: string;
  appearance: string;
  dial_values: {
    theory_of_mind: number;
    harmfulness: number;
    irony: number;
    self_other: number;
  };
}

export async function getCharacters(): Promise<Character[]> {
  const response = await fetch(`${API_BASE}/api/characters`);
  const data = await response.json();
  return data.characters;
}

export async function generateResponse(
  characterId: string,
  context: string,
  model: string = 'gpt-4'
) {
  const response = await fetch(`${API_BASE}/api/conversation/turn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      character_id: characterId,
      context,
      generate_video: false,
      model
    })
  });
  return response.json();
}

export async function generateRound(
  prompt: string,
  model: string = 'gpt-4',
  generateVideos: boolean = false
) {
  const response = await fetch(`${API_BASE}/api/conversation/round`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      generate_videos: generateVideos,
      model
    })
  });
  return response.json();
}

export async function updateDial(
  characterId: string,
  dimension: string,
  value: number
) {
  const response = await fetch(`${API_BASE}/api/dial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      character_id: characterId,
      dimension,
      value
    })
  });
  return response.json();
}
```

---

## 🎨 Design Reference

### Color Palette
- Primary: Purple (#8B5CF6)
- Secondary: Pink (#EC4899)
- Accent: Blue (#3B82F6)
- Background: Gradient from purple-900 to pink-900
- Text: White/Gray-100
- Cards: Glass morphism effect (backdrop-blur)

### Typography
- Headers: Inter Bold
- Body: Inter Regular
- Mono: JetBrains Mono (for scores)

### Components
- Use shadcn-ui: Button, Card, Slider, Select, Textarea
- Icons: Lucide React
- Animations: Framer Motion

---

## 🧪 Testing Your Integration

Once deployed, test:

```bash
# 1. Check API is accessible
curl https://riemann-pilot.railway.app/health

# 2. Open in browser
open https://www.racksavant.com/sistachat

# 3. Test conversation flow:
#    - Enter prompt
#    - Click "Start Conversation"
#    - Watch all 5 characters respond
#    - Adjust dials and retry
#    - Check validation scores

# 4. Test edge cases:
#    - Empty prompt
#    - Very long prompt
#    - Network errors
#    - API timeouts
```

---

## 🚀 Quick Start Commands

```bash
# 1. Deploy backend
cd /Users/podpeople/CascadeProjects/rag_project
railway up

# 2. Get API URL
railway domain

# 3. Open Lovable
open https://lovable.dev/projects/bba02617-12d1-40ac-8bbe-459893d2c496

# 4. Use the prompts above to build!
```

---

## 📞 Support

- Backend API: Check logs with `railway logs`
- Frontend: Lovable has built-in chat support
- Issues: Open on GitHub: https://github.com/RackSavant/riemann_pilot/issues

---

## 🎯 Final Result

**URL**: https://www.racksavant.com/sistachat

**Features**:
✅ 5 AI characters with unique personalities
✅ Multi-dimensional dial controls
✅ Real-time conversation generation
✅ Semantic validation scoring
✅ Optional VEO video generation
✅ Beautiful, responsive UI
✅ Conversation history
✅ Keyboard shortcuts

**Your visitors can**:
- Have conversations with 5 distinct AI personalities
- Steer each character's behavior with dials
- See how well responses align with intended personality
- Generate videos of the conversation
- Share conversation transcripts

---

Enjoy building SistaChat! 🫖✨
