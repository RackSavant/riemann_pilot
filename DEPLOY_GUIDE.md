# Deploy Riemann Pilot API

## Quick Deploy to Railway (5 minutes)

### 1. Sign up & Install
```bash
# Go to https://railway.app and sign up
# Install CLI
npm install -g @railway/cli

# Login
railway login
```

### 2. Deploy from this directory
```bash
cd /Users/podpeople/CascadeProjects/rag_project

# Initialize Railway project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=your-key-here
# OR
railway variables set OPENROUTER_API_KEY=your-key-here

# Deploy!
railway up

# Get your URL
railway domain
```

Your API will be live at: `https://your-app.railway.app`

### 3. Test Your Deployed API
```bash
curl https://your-app.railway.app/health
```

---

## Alternative: Deploy to Render

1. Go to https://render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub: `https://github.com/RackSavant/riemann_pilot`
4. Configure:
   - **Build Command**: `pip install -r tea_party_requirements.txt`
   - **Start Command**: `uvicorn app.tea_party_api:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard:
   - `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
6. Click "Create Web Service"

Your API will be live at: `https://riemann-pilot.onrender.com`

---

## CORS Configuration (Important!)

The API already has CORS enabled for all origins. You can restrict it later by editing `tea_party_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.racksavant.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Environment Variables Required

- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `OPENROUTER_API_KEY` - Get from https://openrouter.ai/keys (alternative)
- `GOOGLE_API_KEY` - Optional, for VEO video generation

---

## Testing Your Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-api.railway.app/health

# Get characters
curl https://your-api.railway.app/api/characters

# Generate response
curl -X POST https://your-api.railway.app/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "context": "Hello!",
    "model": "gpt-4"
  }'
```
