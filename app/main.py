"""
RAG System with Configurable Dials for Semantic Variables
Supports adjustable parameters: love, commitment, belonging, etc.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn

from .embed import EmbeddingEngine
from .retrieval import RetrievalEngine
from .llm_api import OpenRouterLLM, OPENROUTER_MODELS
from .steering import SteeringVectorEngine, AdaptiveSteeringEngine
from .semantic_scale import LoveHateLikertScale
from .utils import load_config, initialize_vector_store

app = FastAPI(
    title="RAG System with Semantic Dials",
    description="Retrieval system with adjustable parameters for love, commitment, belonging",
    version="1.0.0"
)

# Initialize engines
embedding_engine = None
retrieval_engine = None
llm_engine = None
steering_engine = None
semantic_scale = None

# Multiple LLM models for comparison (via OpenRouter API)
llm_models = {
    "small": None,       # gemma-2-2b-it (small, fast)
    "medium": None,      # gemma-2-9b-it (medium)
    "large": None        # gemma-3-27b-it (large, best quality)
}


class SemanticDials(BaseModel):
    """Adjustable parameters that influence retrieval and response generation"""
    love: float = Field(default=0.5, ge=0.0, le=1.0, description="Love emphasis (0-1)")
    commitment: float = Field(default=0.5, ge=0.0, le=1.0, description="Commitment emphasis (0-1)")
    belonging: float = Field(default=0.5, ge=0.0, le=1.0, description="Belonging emphasis (0-1)")
    trust: float = Field(default=0.5, ge=0.0, le=1.0, description="Trust emphasis (0-1)")
    growth: float = Field(default=0.5, ge=0.0, le=1.0, description="Growth emphasis (0-1)")


class QueryRequest(BaseModel):
    query: str = Field(..., description="User query for RAG system")
    dials: Optional[SemanticDials] = Field(default_factory=SemanticDials)
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    use_reranking: bool = Field(default=True, description="Apply contrastive reranking")
    use_steering: bool = Field(default=False, description="Use learned steering vectors")


class QueryResponse(BaseModel):
    query: str
    results: List[Dict]
    applied_dials: SemanticDials
    metadata: Dict


class GenerateRequest(BaseModel):
    query: str = Field(..., description="User query for generation")
    dials: Optional[SemanticDials] = Field(default_factory=SemanticDials)
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context docs")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    use_llm: bool = Field(default=True, description="Generate response with LLM")
    use_steering: bool = Field(default=False, description="Use learned steering vectors")
    model_type: str = Field(default="large", description="Model type: small (2B), medium (9B), or large (27B)")


class GenerateResponse(BaseModel):
    query: str
    response: str
    context_docs: List[Dict]
    dial_instruction: str
    applied_dials: SemanticDials
    metadata: Dict


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global embedding_engine, retrieval_engine, llm_engine, steering_engine, semantic_scale
    
    print("🚀 Initializing RAG System...")
    
    # Initialize semantic scale (optional, won't break if it fails)
    try:
        semantic_scale = LoveHateLikertScale(contrastive_pairs_path="data/contrastive_pairs.csv")
        print("📊 Semantic Likert scale initialized")
    except Exception as e:
        print(f"⚠️  Semantic scale failed to load: {e}")
        semantic_scale = LoveHateLikertScale()  # Initialize without contrastive pairs
        print("📊 Semantic Likert scale initialized (without pair analysis)")
    
    # Initialize embedding engine with contrastive pairs
    embedding_engine = EmbeddingEngine(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        contrastive_pairs_path="data/contrastive_pairs.csv"
    )
    
    # Initialize steering vector engine
    steering_engine = AdaptiveSteeringEngine(
        embedding_engine=embedding_engine,
        cache_path="data/steering_vectors/"
    )
    
    # Try to load cached steering vectors
    if steering_engine.load_vectors():
        print("📊 Using cached steering vectors")
    else:
        print("⚠️  No steering vectors found. Run /learn-steering to train.")
    
    # Initialize retrieval engine
    retrieval_engine = RetrievalEngine(
        embedding_engine=embedding_engine,
        articles_path="data/articles/",
        vector_store_path="data/vector_store/",
        steering_engine=steering_engine  # Pass steering engine
    )
    
    # Build or load vector index
    await retrieval_engine.initialize()
    
    # Note: Gemma LLM is loaded on-demand (lazy loading) to save memory
    # It will be initialized on first /generate request
    llm_engine = None
    
    print("✅ RAG System Ready!")
    print("💡 Gemma LLM will load on first /generate request")
    print("🎛️  Use learned steering vectors with use_steering=true")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG System with Semantic Dials",
        "version": "1.0.0"
    }


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with adjustable semantic dials
    
    The dials influence:
    - Retrieval scoring weights
    - Context filtering
    - Response generation emphasis
    """
    if not retrieval_engine:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Retrieve relevant documents with dial-adjusted scoring
        results = await retrieval_engine.retrieve(
            query=request.query,
            dials=request.dials.dict(),
            top_k=request.top_k,
            use_reranking=request.use_reranking,
            use_steering=request.use_steering
        )
        
        return QueryResponse(
            query=request.query,
            results=results["documents"],
            applied_dials=request.dials,
            metadata={
                "retrieval_time_ms": results["retrieval_time_ms"],
                "total_candidates": results["total_candidates"],
                "reranked": request.use_reranking,
                "steering_method": results.get("steering_method", "none")
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """
    Generate AI response using Gemma with dial-adjusted prompts
    
    This endpoint:
    1. Retrieves relevant context using RAG
    2. Adjusts prompt based on dial settings
    3. Generates response with Gemma LLM
    
    Dials influence:
    - Tone and style of response
    - Focus areas and emphasis
    - Language and phrasing
    """
    global llm_engine, llm_models
    
    if not retrieval_engine:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Model name mapping for OpenRouter
        model_names = {
            "small": "google/gemma-2-2b-it:free",
            "medium": "google/gemma-2-9b-it:free",
            "large": "google/gemma-3-27b-it:free"
        }
        
        # Lazy load the requested model on first request
        if request.use_llm and llm_models[request.model_type] is None:
            model_name = model_names.get(request.model_type, "google/gemma-3-27b-it:free")
            print(f"🤖 Initializing {request.model_type} model via OpenRouter: {model_name}...")
            llm_models[request.model_type] = OpenRouterLLM(model_name=model_name)
            print(f"✅ {request.model_type.capitalize()} model ready!")
        
        # Get the appropriate model
        current_llm = llm_models[request.model_type]
        
        # Retrieve relevant context
        retrieval_results = await retrieval_engine.retrieve(
            query=request.query,
            dials=request.dials.dict(),
            top_k=request.top_k,
            use_reranking=True,
            use_steering=request.use_steering
        )
        
        context_docs = retrieval_results["documents"]
        
        if not request.use_llm or current_llm is None:
            # Return context only, no generation
            return GenerateResponse(
                query=request.query,
                response="[LLM generation disabled - showing context only]",
                context_docs=context_docs,
                dial_instruction="N/A",
                applied_dials=request.dials,
                metadata={
                    "retrieval_time_ms": retrieval_results["retrieval_time_ms"],
                    "generation_enabled": False
                }
            )
        
        # Generate response with selected Gemma model via OpenRouter
        response_text = await current_llm.generate(
            prompt=request.query,
            context=context_docs,
            dials=request.dials.dict(),
            temperature=request.temperature,
            max_tokens=512
        )
        
        # Get dial instruction for transparency
        dial_instruction = current_llm.build_dial_instruction(request.dials.dict())
        
        return GenerateResponse(
            query=request.query,
            response=response_text,
            context_docs=context_docs,
            dial_instruction=dial_instruction,
            applied_dials=request.dials,
            metadata={
                "retrieval_time_ms": retrieval_results["retrieval_time_ms"],
                "generation_enabled": True,
                "model_type": request.model_type,
                "model_name": model_names[request.model_type],
                "api": "OpenRouter",
                "steering_used": request.use_steering
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/train-contrastive")
async def train_contrastive():
    """
    Fine-tune embeddings using contrastive pairs
    This improves the model's understanding of semantic similarities
    """
    if not embedding_engine:
        raise HTTPException(status_code=503, detail="Embedding engine not initialized")
    
    try:
        results = await embedding_engine.train_contrastive()
        return {
            "status": "success",
            "message": "Contrastive training completed",
            "metrics": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.post("/learn-steering")
async def learn_steering():
    """
    Learn steering vectors from contrastive pairs
    
    This creates learned directions in embedding space:
    - love vector = direction from hate → love
    - commitment, trust, belonging, growth (derived from PCA)
    
    Much more consistent than heuristic dial adjustments!
    """
    if not steering_engine:
        raise HTTPException(status_code=503, detail="Steering engine not initialized")
    
    try:
        results = steering_engine.learn_steering_vectors(
            contrastive_pairs_path="data/contrastive_pairs.csv"
        )
        return {
            "status": "success",
            "message": "Steering vectors learned successfully",
            "stats": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning failed: {str(e)}")


@app.get("/steering-info")
async def get_steering_info():
    """Get information about learned steering vectors"""
    if not steering_engine:
        raise HTTPException(status_code=503, detail="Steering engine not initialized")
    
    info = steering_engine.get_vector_info()
    return {
        "vectors_available": info['vectors'],
        "stats": info['stats'],
        "embedding_dim": info['embedding_dim'],
        "mode": "learned" if info['vectors'] else "heuristic"
    }


@app.post("/index-articles")
async def index_articles():
    """
    Re-index all articles in the data/articles/ directory
    """
    if not retrieval_engine:
        raise HTTPException(status_code=503, detail="Retrieval engine not initialized")
    
    try:
        stats = await retrieval_engine.rebuild_index()
        return {
            "status": "success",
            "message": "Articles indexed successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    if not retrieval_engine:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return await retrieval_engine.get_stats()


@app.get("/semantic-scale/{dial_value}")
async def get_semantic_scale_info(dial_value: float):
    """
    Get semantic scale information for a dial value
    
    Returns Likert scale labels, descriptors, and interpretation
    based on the 7-point love-hate scale derived from contrastive pairs
    """
    if not semantic_scale:
        raise HTTPException(status_code=503, detail="Semantic scale not initialized")
    
    if not 0.0 <= dial_value <= 1.0:
        raise HTTPException(status_code=400, detail="Dial value must be between 0.0 and 1.0")
    
    try:
        info = semantic_scale.get_interpolated_descriptors(dial_value)
        likert = semantic_scale.dial_to_likert(dial_value)
        
        return {
            "dial_value": dial_value,
            "dial_percentage": f"{dial_value * 100:.0f}%",
            "likert_value": likert,
            "likert_label": f"{likert}/7",
            "semantic_label": info["primary_label"],
            "descriptors": info["descriptors"],
            "example": info["example"],
            "interpretation": info["interpretation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/semantic-scale/all")
async def get_all_scale_points():
    """Get all 7 anchor points of the semantic scale"""
    if not semantic_scale:
        raise HTTPException(status_code=503, detail="Semantic scale not initialized")
    
    return {
        "scale_type": "7-point Likert",
        "description": "Love-Hate semantic scale derived from contrastive pairs",
        "anchors": [
            {
                "position": anchor.position,
                "likert": semantic_scale.dial_to_likert(anchor.position),
                "label": anchor.label,
                "descriptors": anchor.descriptors,
                "example": anchor.examples[0]
            }
            for anchor in semantic_scale.scale_points
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
