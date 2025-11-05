# 🎥 VEO 3.1 Video Generation Guide

## ✅ Your VEO Integration is Ready!

The UI and backend are already connected to Google's VEO 3.1 for video generation.

## 🎮 How to Use

### **Step 1: Open the UI**
Visit: **http://127.0.0.1:8000**

### **Step 2: Enable Video Generation**
Check the **🎥 Generate Videos (VEO 3.1)** toggle in the controls

### **Step 3: Start the Conversation**
Click **▶ Start** - Each character's response will include an 8-second video!

## ⏱️ Video Generation Time

| Quality | Time | Notes |
|---------|------|-------|
| **Fast** | 11-30 seconds | Best for testing |
| **Normal** | 1-3 minutes | Balanced quality |
| **High** | 3-6 minutes | Production quality |

**Tip**: Start without videos to test dials, then enable for final demo!

## 🎬 What Gets Generated

Each video shows:
- **Character appearance** (from `tea_party_characters.py`)
- **Speaking the dialogue** (lip-synced text)
- **Tea party scene** (elegant setting with decorations)
- **8 seconds long** (optimal for conversation flow)

## 🔧 Video Settings

### **In the UI**
```javascript
// Toggle the checkbox to enable/disable
document.getElementById('video-toggle').checked = true;
```

### **In API Calls**
```bash
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "context": "What do you think of this tea?",
    "generate_video": true  # ← Enable videos
  }'
```

### **In Python**
```python
turn = await engine.generate_response(
    character_id="purple_person",
    generate_video=True  # ← Enable videos
)

print(turn.video_url)  # Video URL when ready
```

## 📊 Video Status

The UI shows 3 states:

### **1. Generating**
```
🎥 Video generating... (11s - 6min)
```

### **2. Ready**
```
[Video player with controls]
```

### **3. Error**
```
⚠️ Video generation failed
```

## 🎯 Character Videos

Each of your 5 characters has distinct appearance:

| Character | ID | Appearance | Personality |
|-----------|-----|-----------|-------------|
| **Alex** | purple_person | Quick-witted, modern | Sharp, observant |
| **Morgan** | blue_hair | Thoughtful, artistic | Deep, contemplative |
| **Riley** | blonde_center | Diplomatic, elegant | Balanced, graceful |
| **Sterling** | gray_beard | Wise, distinguished | Experienced, sage |
| **Jordan** | phone_person | Tech-savvy, modern | Connected, current |

## 🔍 Behind the Scenes

### **How Video Generation Works**

```python
# 1. Generate dialogue text with sentiment dials
response_text = await generate_with_llm(character, dials)

# 2. Create video prompt
video_prompt = f"""
A {character.appearance} at an elegant tea party.
Scene: Ornate decorations, warm lighting, tea service.
Action: Character speaks: "{response_text}"
Duration: 8 seconds
"""

# 3. Call VEO 3.1
video_result = await veo_generator.generate_character_video(
    character_name=character.name,
    character_appearance=character.appearance,
    dialogue=response_text,
    scene_description="elegant tea party"
)

# 4. Poll for completion
while video_result['status'] != 'completed':
    await asyncio.sleep(5)
    video_result = await check_status(video_id)

# 5. Return video URL
return video_result['video_url']
```

## 🚀 Quick Start

### **Test Video Generation**

```bash
# 1. Make sure server is running
# (It already is - background command 193)

# 2. Open UI
open http://127.0.0.1:8000

# 3. Check the video toggle
# 4. Click "▶ Start"
# 5. Wait for first video (11s - 6min)
```

### **Generate Single Video**

```bash
curl -X POST http://localhost:8000/api/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "purple_person",
    "generate_video": true,
    "context": "Tell me about your favorite tea"
  }'
```

Response:
```json
{
  "status": "completed",
  "turn": {
    "character_name": "Alex",
    "text": "Oh, Earl Grey is just divine...",
    "video_url": "https://storage.googleapis.com/...",
    "dial_values": {"irony": 0.5, "harmfulness": 0.2, ...}
  }
}
```

## 💡 Pro Tips

### **1. Start Without Videos**
- Test your dials first (instant feedback)
- Enable videos once you have the conversation flow right
- Videos take time - use for final demos

### **2. Generate Videos Selectively**
```javascript
// Only generate video for key moments
if (currentTurn === 5 || currentTurn === 15) {
    generateVideo = true;
}
```

### **3. Pre-generate for Demos**
```bash
# Generate all videos ahead of time
for character in characters:
    await generate_response(character, generate_video=True)
    
# Save video URLs
# Play back during live demo
```

### **4. Use Async Generation**
```python
# Don't wait for video to complete
video_task = asyncio.create_task(generate_video())
# Continue conversation while video generates
await continue_conversation()
# Check video later
video_url = await video_task
```

## 🐛 Troubleshooting

### **Video Toggle Not Working**
1. Check JavaScript console for errors
2. Verify API endpoint accepts `generate_video` parameter
3. Check server logs for VEO errors

### **Videos Taking Too Long**
- Normal! VEO can take 1-6 minutes
- Consider pre-generating for demos
- Use text-only mode for testing

### **"Video Generation Failed"**
Common causes:
- Google API key not set (`GOOGLE_API_KEY` env var)
- Rate limits exceeded
- Invalid character description
- VEO service unavailable

Check server logs:
```bash
# In the running server terminal
# Look for VEO errors
```

### **Videos Not Displaying**
- Check video URL is valid
- Verify CORS settings allow video playback
- Try different browser
- Check video format (should be MP4)

## 📝 Character Descriptions

Located in `app/tea_party_characters.py`:

```python
CHARACTERS = [
    {
        "id": "purple_person",
        "name": "Alex",
        "appearance": "person with purple-tinted hair, modern outfit, expressive face",
        ...
    },
    ...
]
```

**Customize** these for your videos!

## 🎨 Video Customization

### **Change Scene**
```python
turn = await engine.generate_response(
    character_id="purple_person",
    generate_video=True
)

# In veo_video_generator.py:
scene_description = "Victorian tea room with chandelier"  # ← Customize
```

### **Change Duration**
```python
await veo_generator.generate_character_video(
    duration_seconds=6  # Options: 4, 6, or 8
)
```

### **Add Reference Image**
```python
await veo_generator.generate_character_video(
    reference_image_path="./images/alex_reference.jpg"
)
```

## 📊 Cost Considerations

VEO 3.1 pricing (approximate):
- **Per video**: $0.10 - $0.50
- **20-turn conversation**: $2 - $10
- **Testing**: Use without videos first

**Budget tip**: Generate videos only for final demos!

## 🎉 Demo Script

Perfect flow for showing off your system:

```
1. "Let me show you the sentiment dials" (no videos)
   - Adjust dials, show instant text responses
   - Demonstrate 3 LLM comparison
   
2. "Now watch how the characters come to life" (enable videos)
   - Check video toggle
   - Set extreme dial values (high irony + high harmfulness)
   - Start conversation
   - Wait for first video
   
3. "See how the sentiment affects the performance"
   - Lower harmfulness dial during conversation
   - Next video shows nicer delivery
   - Visual proof that steering works!
```

## 🚀 Next Steps

1. **Test without videos**: Validate your dial settings
2. **Enable videos**: Check the toggle and generate one
3. **Adjust timing**: Videos for key moments only
4. **Pre-generate**: Create video library for demos
5. **Customize**: Modify character appearances and scenes

---

## ✅ **Your System is Ready!**

- ✅ UI has video toggle
- ✅ Backend connected to VEO 3.1
- ✅ Videos display automatically
- ✅ Status indicators show progress

**Visit http://127.0.0.1:8000 and check the video toggle!** 🎥🫖✨
