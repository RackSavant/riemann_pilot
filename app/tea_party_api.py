"""
Tea Party API - FastAPI Backend

WebSocket-enabled API for real-time multi-dimensional steering
and conversation generation with Veo 3.1 video.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime

from app.tea_party_conversation import TeaPartyConversationEngine
from app.tea_party_characters import CHARACTERS
from app.multi_dimensional_scale import MultiDimensionalScale
from app.semantic_dial_validator import SemanticDialValidator, TEA_PARTY_DESCRIPTORS

app = FastAPI(
    title="Tea Party Sentiment-Controlled Conversation API",
    description="Multi-dimensional steering vectors for character conversations with Veo 3.1 video",
    version="1.0.0"
)

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000", 
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://127.0.0.1:64731",  # Browser preview proxy
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global conversation engine and validator
conversation_engine: Optional[TeaPartyConversationEngine] = None
semantic_validator: Optional[SemanticDialValidator] = None


# Pydantic Models
class DialUpdate(BaseModel):
    character_id: str
    dimension: str = Field(..., pattern="^(theory_of_mind|harmfulness|irony|self_other)$")
    value: float = Field(..., ge=0.0, le=1.0)


class ConversationRequest(BaseModel):
    topic: str = "tea and pastries"
    character_order: Optional[List[str]] = None
    generate_videos: bool = False
    model: str = "gpt-4"  # Options: gpt-4, claude, gemini


class SingleTurnRequest(BaseModel):
    character_id: str
    context: Optional[str] = None
    generate_video: bool = False
    model: str = "gpt-4"  # Options: gpt-4, claude, gemini


class VideoGenerationRequest(BaseModel):
    character_id: str
    dialogue: str


# Startup/Shutdown
@app.on_event("startup")
async def startup():
    global conversation_engine, semantic_validator
    print("🫖 Starting Tea Party API...")
    try:
        conversation_engine = TeaPartyConversationEngine()
        print("✅ Conversation engine initialized")
        
        # Initialize semantic validator
        try:
            semantic_validator = SemanticDialValidator()
            print("✅ Semantic validator initialized")
        except Exception as e:
            print(f"⚠️ Semantic validator unavailable: {e}")
            semantic_validator = None
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    print("👋 Shutting down Tea Party API...")


# REST Endpoints
@app.get("/")
async def root():
    """Serve the cockpit UI"""
    cockpit_file = os.path.join(static_dir, "cockpit.html")
    if os.path.exists(cockpit_file):
        return FileResponse(cockpit_file)
    else:
        return {
            "service": "Tea Party Sentiment-Controlled Conversation API",
            "version": "1.0.0",
            "characters": len(CHARACTERS),
            "dimensions": 4,
            "endpoints": {
                "ui": "/",
                "ui_classic": "/classic",
                "characters": "/api/characters",
                "conversation": "/api/conversation",
                "dial_update": "/api/dial",
                "websocket": "/ws/tea-party"
            }
        }


@app.get("/classic")
async def classic_ui():
    """Serve the classic UI"""
    classic_file = os.path.join(static_dir, "index.html")
    if os.path.exists(classic_file):
        return FileResponse(classic_file)
    else:
        return {"error": "Classic UI not found"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine_ready": conversation_engine is not None
    }


@app.get("/api/characters")
async def get_characters():
    """Get all character information with current states"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    states = conversation_engine.get_all_character_states()
    return {
        "characters": states,
        "count": len(states)
    }


@app.get("/api/characters/{character_id}")
async def get_character(character_id: str):
    """Get detailed info for a specific character"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    try:
        info = conversation_engine.character_manager.get_character_info(character_id)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/dial")
async def update_dial(dial: DialUpdate):
    """Update a character's dial value"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    try:
        conversation_engine.update_character_dial(
            dial.character_id,
            dial.dimension,
            dial.value
        )
        
        # Get updated state
        state = conversation_engine.character_manager.get_character(
            dial.character_id
        ).get_current_state()
        
        return {
            "status": "updated",
            "character_id": dial.character_id,
            "dimension": dial.dimension,
            "value": dial.value,
            "current_state": state
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/conversation/round")
async def run_conversation_round(request: ConversationRequest):
    """Run one full round of conversation (all characters speak)"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    # Set topic
    conversation_engine.set_topic(request.topic)
    
    # Run conversation
    turns = await conversation_engine.run_conversation_round(
        character_order=request.character_order,
        generate_videos=request.generate_videos,
        model=request.model
    )
    
    return {
        "status": "completed",
        "topic": request.topic,
        "turns": [turn.to_dict() for turn in turns],
        "video_generation_enabled": request.generate_videos
    }


@app.post("/api/conversation/turn")
async def generate_single_turn(request: SingleTurnRequest):
    """Generate a single character's turn"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    turn = await conversation_engine.generate_response(
        character_id=request.character_id,
        context=request.context,
        generate_video=request.generate_video,
        model=request.model
    )
    
    # Add semantic validation if available
    turn_dict = turn.to_dict()
    if semantic_validator:
        try:
            validation_scores = semantic_validator.validate_steering_effectiveness(
                dial_values=turn.dial_values,
                response=turn.text,
                dimension_descriptors=TEA_PARTY_DESCRIPTORS
            )
            turn_dict['validation_scores'] = validation_scores
            print(f"✅ Validation scores added for {turn.character_name}")
        except Exception as e:
            print(f"⚠️ Validation failed: {e}")
            turn_dict['validation_scores'] = {}
    
    return {
        "status": "completed",
        "turn": turn_dict
    }


@app.get("/api/conversation/history")
async def get_history():
    """Get full conversation history"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    history = conversation_engine.get_conversation_history()
    return {
        "history": history,
        "count": len(history)
    }


@app.delete("/api/conversation/history")
async def clear_history():
    """Clear conversation history"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    conversation_engine.clear_history()
    return {"status": "cleared"}


@app.post("/api/video/generate")
async def generate_video(request: VideoGenerationRequest):
    """Generate a VEO video for a character's dialogue"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    print(f"\n🎬 Video generation request for {request.character_id}")
    print(f"   Dialogue: {request.dialogue[:100]}...")
    
    try:
        # Get character info
        char_info = conversation_engine.character_manager.get_character_info(request.character_id)
        
        # Generate video using VEO
        video_result = await conversation_engine.veo_generator.generate_character_video(
            character_name=char_info['character_name'],
            character_appearance=char_info['appearance'],
            dialogue=request.dialogue,
            scene_description="elegant tea party with ornate decorations and fine china"
        )
        
        print(f"✅ Video generated: {video_result.get('video_url', 'Processing...')}")
        
        return {
            "status": "success" if video_result.get('video_url') else "generating",
            "video_url": video_result.get('video_url'),
            "operation_name": video_result.get('operation_name'),
            "character_name": char_info['character_name']
        }
        
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@app.post("/api/video/conversation")
async def generate_conversation_video(request: dict):
    """Generate a conversation video with all 5 characters"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    print(f"\n🎬 Conversation video generation requested")
    print(f"   Characters: {len(request.get('responses', []))}")
    
    try:
        responses = request.get('responses', [])
        reference_image = request.get('reference_image', 'app/static/tea_party_reference.png')
        
        # Format responses for VEO
        character_responses = []
        for resp in responses:
            char_info = conversation_engine.character_manager.get_character_info(resp['character_id'])
            character_responses.append({
                'character_name': char_info['character_name'],
                'dialogue': resp['text'],
                'appearance': char_info['appearance']
            })
        
        # Generate conversation video
        video_result = await conversation_engine.veo_generator.generate_conversation_video(
            character_responses=character_responses,
            reference_image_path=reference_image,
            duration_seconds=30
        )
        
        print(f"✅ Conversation video generated: {video_result.get('video_url', 'Processing...')}")
        
        return {
            "status": "success" if video_result.get('video_url') else "generating",
            "video_url": video_result.get('video_url'),
            "operation_name": video_result.get('operation_name'),
            "type": "conversation",
            "characters": [r['character_name'] for r in character_responses]
        }
        
    except Exception as e:
        print(f"❌ Conversation video generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversation video generation failed: {str(e)}")


@app.post("/api/scene/opening")
async def generate_opening():
    """Generate opening establishing shot"""
    if not conversation_engine:
        raise HTTPException(status_code=500, detail="Conversation engine not initialized")
    
    result = await conversation_engine.generate_opening_scene()
    return result


@app.get("/api/dimensions")
async def get_dimensions():
    """Get information about all steering dimensions"""
    scale = MultiDimensionalScale()
    
    dimensions_info = []
    for dim_name in scale.DIMENSIONS:
        desc = scale.dimensions[dim_name]
        dimensions_info.append({
            "id": dim_name,
            "name": desc.name,
            "low_label": desc.low_label,
            "high_label": desc.high_label,
            "low_descriptors": desc.low_descriptors[:3],
            "high_descriptors": desc.high_descriptors[:3],
            "example_low": desc.example_pairs[0][0] if desc.example_pairs else "",
            "example_high": desc.example_pairs[0][1] if desc.example_pairs else ""
        })
    
    return {
        "dimensions": dimensions_info,
        "count": len(dimensions_info)
    }


# WebSocket for real-time updates
@app.websocket("/ws/tea-party")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time conversation and dial updates
    
    Client messages:
    - {"action": "update_dial", "character_id": "...", "dimension": "...", "value": 0.5}
    - {"action": "generate_turn", "character_id": "...", "generate_video": false}
    - {"action": "set_topic", "topic": "..."}
    - {"action": "get_states"}
    
    Server messages:
    - {"type": "dial_updated", "character_id": "...", "state": {...}}
    - {"type": "turn_generated", "turn": {...}}
    - {"type": "states", "characters": [...]}
    - {"type": "error", "message": "..."}
    """
    await websocket.accept()
    print("🔌 WebSocket client connected")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "update_dial":
                # Update character dial
                character_id = data.get("character_id")
                dimension = data.get("dimension")
                value = data.get("value")
                
                try:
                    conversation_engine.update_character_dial(character_id, dimension, value)
                    state = conversation_engine.character_manager.get_character(
                        character_id
                    ).get_current_state()
                    
                    await websocket.send_json({
                        "type": "dial_updated",
                        "character_id": character_id,
                        "dimension": dimension,
                        "value": value,
                        "state": state
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif action == "generate_turn":
                # Generate character response
                character_id = data.get("character_id")
                context = data.get("context")
                generate_video = data.get("generate_video", False)
                
                try:
                    turn = await conversation_engine.generate_response(
                        character_id=character_id,
                        context=context,
                        generate_video=generate_video
                    )
                    
                    await websocket.send_json({
                        "type": "turn_generated",
                        "turn": turn.to_dict()
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif action == "set_topic":
                # Change conversation topic
                topic = data.get("topic", "tea and pastries")
                conversation_engine.set_topic(topic)
                
                await websocket.send_json({
                    "type": "topic_updated",
                    "topic": topic
                })
            
            elif action == "get_states":
                # Get all character states
                states = conversation_engine.get_all_character_states()
                
                await websocket.send_json({
                    "type": "states",
                    "characters": states
                })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                })
    
    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
