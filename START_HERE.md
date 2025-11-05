# 🚀 RIEMANN PILOT - START HERE

## 🎯 **What You Have**

**Riemann Pilot** is a multi-dimensional AI steering platform with:
- ✅ 5 unique AI characters with distinct personalities
- ✅ 4-dimensional dial controls (Theory of Mind, Harmfulness, Irony, Self/Other)
- ✅ Real-time semantic validation scoring
- ✅ Optional VEO video generation
- ✅ FastAPI backend with REST endpoints
- ✅ Beautiful cockpit UI

---

## 📍 **Current Status**

### ✅ What's Working NOW
- **Local API Server**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Cockpit UI**: http://127.0.0.1:8000
- **GitHub Repo**: https://github.com/RackSavant/riemann_pilot

### 🔑 Configuration
- API Key: ✅ Configured in `.env`
- Environment: OpenRouter + GPT-4
- GPU: MPS (Mac Metal)
- Characters: 5 loaded (Ptothe, Sevvy, RackSavant, Sterling, Jordan)

---

## 🎮 **Quick Test**

```bash
# Test health
curl http://127.0.0.1:8000/health

# Get characters
curl http://127.0.0.1:8000/api/characters

# Generate response
curl -X POST http://127.0.0.1:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "context": "What makes you happy?",
    "model": "gpt-4"
  }'
```

---

## 🚀 **Next Steps: Build SistaChat on www.racksavant.com**

### **Goal**
Create a beautiful Tea Party interface at `www.racksavant.com/sistachat` where visitors can:
1. Chat with 5 AI personalities
2. Adjust personality dials in real-time
3. See validation scores
4. Generate conversation videos

---

### **Step 1: Deploy Backend (10 min)**

Your API needs to be publicly accessible.

#### **Option A: Railway (Recommended)**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Navigate to project
cd /Users/podpeople/CascadeProjects/rag_project

# 4. Initialize Railway
railway init

# 5. Set environment variables
railway variables set OPENAI_API_KEY=sk-proj-your-actual-key-here

# 6. Deploy!
railway up

# 7. Get your public URL
railway domain
```

**Result**: You'll get `https://riemann-pilot.railway.app`

#### **Option B: Render**

1. Visit: https://render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub: `https://github.com/RackSavant/riemann_pilot`
4. Settings:
   - **Name**: riemann-pilot
   - **Build Command**: `pip install -r tea_party_requirements.txt`
   - **Start Command**: `uvicorn app.tea_party_api:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   - Add `OPENAI_API_KEY` with your key
6. Click "Create Web Service"

**Result**: You'll get `https://riemann-pilot.onrender.com`

---

### **Step 2: Build Frontend in Lovable (30 min)**

#### **A. Open Your Lovable Project**

👉 **https://lovable.dev/projects/bba02617-12d1-40ac-8bbe-459893d2c496**

#### **B. Copy-Paste These 5 Prompts**

I've created 5 ready-to-use prompts in `LOVABLE_PROMPTS.txt`:

**View here**: https://github.com/RackSavant/riemann_pilot/blob/main/LOVABLE_PROMPTS.txt

**Or read from your local file**:
```bash
cat /Users/podpeople/CascadeProjects/rag_project/LOVABLE_PROMPTS.txt
```

**The 5 prompts cover**:
1. **Initial Setup** - Layout, character panels, control panel
2. **Connect to API** - TypeScript API client, data fetching
3. **Interactive Dials** - Beautiful circular gauges with updates
4. **Response Cards** - Styled responses with validation scores
5. **Polish & UX** - Loading states, keyboard shortcuts, responsive design

#### **C. Important: Update API URL**

In Prompt #2, replace this line with your Railway/Render URL:
```typescript
const API_BASE = 'https://riemann-pilot.railway.app'; // Your actual URL here
```

#### **D. Submit Prompts One-by-One**

1. Copy Prompt 1 → Paste in Lovable → Let it build
2. Review the result → Then continue with Prompt 2
3. Repeat for all 5 prompts
4. Test each feature as you go

---

### **Step 3: Deploy to www.racksavant.com (15 min)**

#### **Option A: Lovable's Built-in Hosting**

1. In Lovable, click **"Publish"**
2. You'll get a URL like: `https://sistachat.lovable.app`
3. Set up a redirect from `www.racksavant.com/sistachat` → Lovable URL

#### **Option B: Export & Self-Host**

1. In Lovable, export your project
2. Download the build files
3. Upload to your server at: `/var/www/racksavant.com/sistachat/`
4. Configure nginx/apache to serve it

#### **Option C: Vercel/Netlify**

1. Export from Lovable
2. Deploy to Vercel: `vercel --prod`
3. Configure path routing: `racksavant.com/sistachat` → Vercel app

---

## 📁 **Important Files in Your Repo**

| File | Description |
|------|-------------|
| `START_HERE.md` | This file - your main guide |
| `LOVABLE_PROMPTS.txt` | 5 ready-to-use Lovable prompts |
| `LOVABLE_SISTACHAT_GUIDE.md` | Detailed Lovable integration guide |
| `DEPLOY_GUIDE.md` | Backend deployment instructions |
| `app/tea_party_api.py` | Main API server |
| `app/tea_party_characters.py` | Character definitions |
| `app/veo_video_generator.py` | VEO video generation |
| `app/semantic_dial_validator.py` | Validation scoring |
| `.env` | Your API keys (NEVER commit!) |

---

## 🎛️ **Your 5 AI Characters**

| ID | Name | Personality | Dials (Default) |
|---|---|---|---|
| `purple_person` | **Ptothe** | Energetic, witty, enthusiastic | ToM: 0.6, H: 0.2, I: 0.5, S/O: 0.6 |
| `blue_hair` | **Sevvy** | Thoughtful, composed, intellectual | ToM: 0.8, H: 0.1, I: 0.3, S/O: 0.7 |
| `blonde_center` | **RackSavant** | Warm, diplomatic, balanced | ToM: 0.7, H: 0.0, I: 0.2, S/O: 0.8 |
| `gray_beard` | **Sterling** | Wise, measured, philosophical | ToM: 0.9, H: 0.0, I: 0.4, S/O: 0.8 |
| `phone_person` | **Jordan** | Modern, casual, tech-savvy | ToM: 0.5, H: 0.3, I: 0.6, S/O: 0.5 |

**Dial Legend**:
- **ToM**: Theory of Mind (understanding others)
- **H**: Harmfulness (negativity)
- **I**: Irony (sarcasm)
- **S/O**: Self vs. Other focus

---

## 📡 **API Endpoints**

### **Characters**
- `GET /api/characters` - List all 5
- `GET /api/characters/{id}` - Get one
- `POST /api/dial` - Update dial value

### **Conversation**
- `POST /api/conversation/turn` - Single character responds
- `POST /api/conversation/round` - All 5 respond
- `GET /api/conversation/history` - Get history
- `DELETE /api/conversation/history` - Clear history

### **Video**
- `POST /api/video/generate` - Character video
- `POST /api/video/conversation` - Full scene video
- `POST /api/scene/opening` - Opening scene

### **Info**
- `GET /health` - Health check
- `GET /api/dimensions` - Dimension info
- `GET /` - Cockpit UI
- `GET /docs` - API documentation

---

## 🔧 **Common Commands**

### **Start Local Server**
```bash
cd /Users/podpeople/CascadeProjects/rag_project
source venv/bin/activate
uvicorn app.tea_party_api:app --reload --port 8000
```

### **Stop Server**
```bash
lsof -ti:8000 | xargs kill -9
```

### **Update .env**
```bash
code .env  # VS Code
# or
nano .env  # Terminal editor
```

### **Push to GitHub**
```bash
git add .
git commit -m "Your message"
git push origin main
```

### **Deploy to Railway**
```bash
railway up
railway logs  # View logs
railway domain  # Get URL
```

---

## 🎨 **Design Specs for SistaChat**

### **Color Palette**
- Primary: Purple (#8B5CF6)
- Secondary: Pink (#EC4899)
- Accent: Blue (#3B82F6)
- Background: Dark gradient (purple-900 to pink-900)
- Cards: Glass morphism (backdrop-blur-lg, bg-white/10)

### **Typography**
- Headers: Inter Bold
- Body: Inter Regular, 16px, line-height 1.6
- Mono: JetBrains Mono (for scores)

### **Components** (shadcn-ui)
- Button, Card, Badge, Avatar
- Slider, Progress, Tooltip
- Textarea, Select, Switch
- Toast for notifications

---

## 🐛 **Troubleshooting**

### **API Won't Start**
```bash
# Check if port is in use
lsof -ti:8000

# Kill existing process
lsof -ti:8000 | xargs kill -9

# Check API key
grep OPENAI_API_KEY .env
```

### **API Key Errors**
- Make sure `.env` has `OPENAI_API_KEY=sk-proj-...`
- Never commit `.env` to git (it's in `.gitignore`)
- If key is compromised, revoke it at https://platform.openai.com/api-keys

### **CORS Errors in Lovable**
- Backend already has CORS enabled for all origins
- If issues persist, check browser console for specific errors

### **Character Not Found**
- Use correct IDs: `purple_person`, `blue_hair`, `blonde_center`, `gray_beard`, `phone_person`
- Not: `bohemian_artist` or other made-up IDs

---

## 📚 **Documentation Links**

- **GitHub Repo**: https://github.com/RackSavant/riemann_pilot
- **Lovable Project**: https://lovable.dev/projects/bba02617-12d1-40ac-8bbe-459893d2c496
- **Railway**: https://railway.app/
- **Render**: https://render.com/
- **OpenAI API**: https://platform.openai.com/
- **shadcn-ui**: https://ui.shadcn.com/

---

## 🎯 **Success Checklist**

### **Phase 1: Local Development** ✅
- [x] API running locally
- [x] Characters responding
- [x] Dials working
- [x] Validation scoring
- [x] Code on GitHub

### **Phase 2: Public Deployment** ⬜
- [ ] Backend deployed to Railway/Render
- [ ] Public API URL obtained
- [ ] API health check passing
- [ ] Test endpoints working

### **Phase 3: Frontend Build** ⬜
- [ ] Lovable project opened
- [ ] 5 prompts submitted
- [ ] API client connected
- [ ] Characters displaying
- [ ] Dials functional
- [ ] Responses rendering
- [ ] Validation scores showing

### **Phase 4: Production** ⬜
- [ ] Frontend deployed
- [ ] Accessible at www.racksavant.com/sistachat
- [ ] End-to-end testing complete
- [ ] Share with users!

---

## 💡 **Pro Tips**

1. **Test incrementally** - Deploy backend first, then build frontend
2. **Use Lovable's preview** - Test each prompt before moving to next
3. **Check API logs** - `railway logs` or Render dashboard
4. **Start simple** - Get basic conversation working, then add videos
5. **Mobile-first** - Test responsive design early
6. **Cache responses** - Add conversation history for better UX

---

## 🆘 **Need Help?**

### **Local API Issues**
```bash
# View logs
cd /Users/podpeople/CascadeProjects/rag_project
railway logs  # If deployed

# Test endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/characters
```

### **Lovable Issues**
- Use Lovable's built-in chat support
- Check browser console for errors
- Verify API URL is correct

### **Deployment Issues**
- Check environment variables are set
- Verify build logs on Railway/Render
- Test API endpoint directly with `curl`

---

## 🎉 **You're Ready!**

**Your complete workflow**:

1. ✅ **Backend is running locally** - Test it now!
2. 🚀 **Deploy to Railway** - 10 minutes
3. 🎨 **Build in Lovable** - 30 minutes (use the 5 prompts)
4. 🌐 **Deploy to racksavant.com** - 15 minutes

**Total time**: ~1 hour to go from local dev to production! 🚀

---

**Start with Step 1: Deploy your backend to Railway** ⬆️

Good luck! 🫖✨
