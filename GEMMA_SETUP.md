# 🔑 Gemma Models Setup Guide

## ✅ Files Ready

- ✅ `.env` created (already in `.gitignore`)
- ✅ `docker-compose.yml` configured to load `.env`
- ✅ Models configured: Gemma-2-2B, Gemma-2-2B-IT, Gemma-2-9B-IT

## 🚀 Get Your Hugging Face Token (2 minutes)

### Step 1: Create Account (if needed)
Go to https://huggingface.co/join

### Step 2: Get Token
1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name it: `gemma-access`
4. Type: **Read** (not Write)
5. Click **"Generate token"**
6. **Copy the token** (you'll need it next)

### Step 3: Request Gemma Access
Visit these pages and click **"Request access"**:
- https://huggingface.co/google/gemma-2-2b
- https://huggingface.co/google/gemma-2-2b-it
- https://huggingface.co/google/gemma-2-9b-it

**Approval is instant!** ✅

### Step 4: Add Token to .env
```bash
# Edit the .env file
nano .env

# Replace this line:
HF_TOKEN=your_token_here

# With your actual token:
HF_TOKEN=hf_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 5: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

Wait 30 seconds for models to be ready.

### Step 6: Test It!
Refresh your Streamlit browser at http://localhost:8501

You should now see:
- **Gemma-2-2B (Base)** - Pretrained model
- **Gemma-2-2B-IT** - Instruction-tuned  
- **Gemma-2-9B-IT** - Large, instruction-tuned

## 🎛️ Your Three Gemma Models

| Model | Size | Type | Use Case |
|-------|------|------|----------|
| **Gemma-2-2B** | 2B params | Pretrained | See raw steering response |
| **Gemma-2-2B-IT** | 2B params | Instruction-tuned | Better at following instructions |
| **Gemma-2-9B-IT** | 9B params | Large, instruction-tuned | Most sophisticated responses |

**All three use the SAME Love dial!** Compare how size & training affect steering.

## 🔬 Test Steering

1. **Set dial to 10%** (Strong Hate)
2. **Ask all three:** "Give me feedback on my project"
3. **Observe differences:**
   - 2B Base: Raw hostile response
   - 2B-IT: More coherent hostile
   - 9B-IT: Most sophisticated hostile response

4. **Set dial to 90%** (Strong Love)
5. **Same question** - see completely different responses!

## 🐛 Troubleshooting

**"Gated repo" error?**
- Make sure you requested access to all 3 models
- Wait 1 minute for approval
- Check token is correctly in .env

**"Invalid token" error?**
- Token should start with `hf_`
- No spaces before/after the token
- Token needs **Read** permission

**Models loading slowly?**
- First load downloads models (5-10 min)
- Subsequent loads are instant
- 9B model is ~18GB download

**Check if token is loaded:**
```bash
docker exec rag-system env | grep HF_TOKEN
# Should show: HF_TOKEN=hf_your_token...
```

## 💡 Pro Tips

1. **9B model is MUCH better** but slower on CPU
2. **Compare at extremes** (0% and 100%) to see max steering
3. **Semantic scale labels** show what each percentage means
4. **Different models** may need different dial values for same effect

## ✅ Quick Verification

After setup, you should see in Docker logs:
```
🤖 Loading pretrained model: google/gemma-2-2b on cpu (with auth)...
✅ Pretrained model loaded!
```

The **(with auth)** confirms your token works!

---

**You're ready to test love→hate steering on three Gemma models!** 🎛️
