import streamlit as st
import requests
import json
from typing import List, Dict
import time
import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from semantic_scale import LoveHateLikertScale
    SEMANTIC_SCALE_AVAILABLE = True
except:
    SEMANTIC_SCALE_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="AI Steering Vector Lab - Love Dial",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6B7280;
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .love-dial {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: white;
    }
    .stat-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://localhost:8000"

# Initialize semantic scale
if SEMANTIC_SCALE_AVAILABLE:
    semantic_scale = LoveHateLikertScale()
else:
    semantic_scale = None

# Initialize session state
if 'model_alpha_messages' not in st.session_state:
    st.session_state.model_alpha_messages = []
if 'model_beta_messages' not in st.session_state:
    st.session_state.model_beta_messages = []
if 'model_gamma_messages' not in st.session_state:
    st.session_state.model_gamma_messages = []
if 'love_vector' not in st.session_state:
    st.session_state.love_vector = 50
if 'steering_trained' not in st.session_state:
    st.session_state.steering_trained = False


def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def train_steering_vectors():
    """Train love steering vectors from contrastive pairs"""
    try:
        with st.spinner("🧠 Training love steering vector from 30 contrastive pairs..."):
            response = requests.post(f"{API_URL}/learn-steering", timeout=60)
            if response.status_code == 200:
                st.session_state.steering_trained = True
                return response.json()
            else:
                st.error(f"Training failed: {response.text}")
                return None
    except Exception as e:
        st.error(f"Error training steering vectors: {str(e)}")
        return None


def query_with_steering(query: str, love_value: float, use_steering: bool = True):
    """Query the RAG system with love steering"""
    try:
        # Normalize love value from 0-100 to 0-1
        love_dial = love_value / 100.0
        
        payload = {
            "query": query,
            "dials": {
                "love": love_dial,
                "commitment": 0.5,
                "belonging": 0.5,
                "trust": 0.5,
                "growth": 0.5
            },
            "top_k": 3,
            "use_steering": use_steering
        }
        
        response = requests.post(
            f"{API_URL}/query",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Query failed: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def generate_with_steering(query: str, love_value: float, use_steering: bool = True, use_llm: bool = True, model_type: str = "instruction"):
    """Generate response with Gemma + love steering"""
    try:
        love_dial = love_value / 100.0
        
        payload = {
            "query": query,
            "dials": {
                "love": love_dial,
                "commitment": 0.5,
                "belonging": 0.5,
                "trust": 0.5,
                "growth": 0.5
            },
            "top_k": 3,
            "use_steering": use_steering,
            "use_llm": use_llm,
            "temperature": 0.7,
            "model_type": model_type  # Which Gemma variant to use
        }
        
        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Generation failed: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def display_messages(messages: List[Dict], container):
    """Display chat messages in a container"""
    with container:
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


# Main UI
st.markdown('<div class="main-header">🎛️ AI Steering Vector Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Adjust the Love vector and observe response transformations</div>', unsafe_allow_html=True)

# Check API health
api_healthy = check_api_health()

if not api_healthy:
    st.error("⚠️ **Backend API not running!** Please start the Docker container:")
    st.code("docker-compose up -d")
    st.stop()

# Sidebar - Control Panel
with st.sidebar:
    st.markdown('<div class="love-dial">', unsafe_allow_html=True)
    st.markdown("### 💗 Love Steering Vector")
    st.markdown("Control emotional warmth and empathy")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Love dial
    love_value = st.slider(
        "Love Intensity",
        min_value=0,
        max_value=100,
        value=st.session_state.love_vector,
        step=1,
        help="0 = Hate/Cold, 50 = Neutral, 100 = Love/Warm"
    )
    st.session_state.love_vector = love_value
    
    # Show dial value with semantic scale labels
    if semantic_scale:
        dial_normalized = love_value / 100.0
        semantic_info = semantic_scale.get_interpolated_descriptors(dial_normalized)
        likert_value = semantic_scale.dial_to_likert(dial_normalized)
        
        # Color based on semantic position
        if dial_normalized < 0.15:
            color = "#DC2626"  # Dark red
        elif dial_normalized < 0.30:
            color = "#EF4444"  # Red
        elif dial_normalized < 0.45:
            color = "#F97316"  # Orange
        elif dial_normalized < 0.55:
            color = "#6B7280"  # Gray
        elif dial_normalized < 0.70:
            color = "#10B981"  # Green
        elif dial_normalized < 0.85:
            color = "#059669"  # Dark green
        else:
            color = "#047857"  # Very dark green
        
        st.markdown(f"""
        <div style="background: {color}; padding: 1.5rem; border-radius: 0.5rem; color: white;">
            <div style="font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 0.5rem;">
                {love_value}%
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; text-align: center; margin-bottom: 0.5rem;">
                {semantic_info['primary_label']}
            </div>
            <div style="font-size: 0.75rem; text-align: center; opacity: 0.9;">
                Likert: {likert_value}/7
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show descriptors
        st.markdown("**Key Descriptors:**")
        st.caption(", ".join(semantic_info['descriptors'][:5]))
        
        # Show interpretation
        with st.expander("ℹ️ What this means"):
            st.write(semantic_info['interpretation'])
            st.markdown("**Example from contrastive pairs:**")
            st.info(semantic_info['example'])
    else:
        # Fallback if semantic scale not available
        if love_value < 33:
            color = "#EF4444"
            emotion = "Cold/Hate"
        elif love_value < 67:
            color = "#F59E0B"
            emotion = "Neutral"
        else:
            color = "#10B981"
            emotion = "Warm/Love"
        
        st.markdown(f"""
        <div style="background: {color}; padding: 1rem; border-radius: 0.5rem; text-align: center; color: white; font-weight: 600;">
            {love_value}% - {emotion}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Training section
    st.markdown("### 🧠 Steering Vector Training")
    
    if not st.session_state.steering_trained:
        st.warning("Steering vectors not trained yet!")
        if st.button("🚀 Train Love Vector", use_container_width=True):
            result = train_steering_vectors()
            if result:
                st.success("✅ Love steering vector trained!")
                st.json(result)
                st.rerun()
    else:
        st.success("✅ Love steering vector active")
        if st.button("🔄 Retrain", use_container_width=True):
            st.session_state.steering_trained = False
            st.rerun()
    
    st.markdown("---")
    
    # Comparison mode
    st.markdown("### ⚙️ Comparison Mode")
    comparison_mode = st.selectbox(
        "Model Configuration",
        [
            "All Steered",
            "Steered vs Baseline",
            "Different Intensities"
        ],
        help="All models use your Love dial setting. Compare how different Gemma architectures respond to steering!"
    )
    
    # Show what's being compared
    if comparison_mode == "All Steered":
        st.caption("🔬 Compare: Gemma-2-2B vs Gemma-2-2B-IT vs Gemma-2-9B-IT")
    elif comparison_mode == "Steered vs Baseline":
        st.caption("🔬 Compare: No Steering vs Learned Steering vs Pretrained Model")
    else:
        st.caption(f"🔬 All three Gemma models at {love_value}% Love")
    
    st.markdown("---")
    
    # Clear buttons
    if st.button("🗑️ Clear All Conversations", use_container_width=True):
        st.session_state.model_alpha_messages = []
        st.session_state.model_beta_messages = []
        st.session_state.model_gamma_messages = []
        st.success("Cleared all conversations!")
        st.rerun()
    
    if st.button("🔄 Reset Dial", use_container_width=True):
        st.session_state.love_vector = 50
        st.rerun()

# Main content - Three panel layout
col1, col2, col3 = st.columns(3)

# Configure models based on comparison mode
# Using OpenRouter API - all models are cloud-based (no local downloads)
if comparison_mode == "All Steered":
    model_configs = [
        {"name": "Gemma-2B (Small)", "love": love_value, "use_steering": True, "model_type": "small"},
        {"name": "Gemma-9B (Medium)", "love": love_value, "use_steering": True, "model_type": "medium"},
        {"name": "Gemma-27B (Large)", "love": love_value, "use_steering": True, "model_type": "large"}
    ]
elif comparison_mode == "Steered vs Baseline":
    model_configs = [
        {"name": "Baseline (No Steering)", "love": 50, "use_steering": False, "model_type": "large"},
        {"name": f"Steered ({love_value}%)", "love": love_value, "use_steering": True, "model_type": "large"},
        {"name": "Small Model Steered", "love": love_value, "use_steering": True, "model_type": "small"}
    ]
else:  # Different Intensities
    model_configs = [
        {"name": f"Gemma-2B ({love_value}%)", "love": love_value, "use_steering": True, "model_type": "small"},
        {"name": f"Gemma-9B ({love_value}%)", "love": love_value, "use_steering": True, "model_type": "medium"},
        {"name": f"Gemma-27B ({love_value}%)", "love": love_value, "use_steering": True, "model_type": "large"}
    ]

# Model Alpha
with col1:
    st.markdown(f"### {model_configs[0]['name']}")
    if model_configs[0]['use_steering']:
        st.caption(f"💗 Love: {model_configs[0]['love']}% (Learned Steering)")
    else:
        st.caption("🔧 Heuristic/Baseline")
    
    # Display messages
    alpha_container = st.container()
    display_messages(st.session_state.model_alpha_messages, alpha_container)
    
    # Input
    alpha_input = st.chat_input("Message Model Alpha", key="alpha_input")
    if alpha_input:
        st.session_state.model_alpha_messages.append({"role": "user", "content": alpha_input})
        
        with st.spinner("Thinking..."):
            result = generate_with_steering(
                alpha_input,
                model_configs[0]['love'],
                model_configs[0]['use_steering'],
                use_llm=True,
                model_type=model_configs[0]['model_type']
            )
            
            if "error" not in result:
                response = result.get("response", "No response generated")
                st.session_state.model_alpha_messages.append({"role": "assistant", "content": response})
            else:
                st.error(result["error"])
        
        st.rerun()

# Model Beta
with col2:
    st.markdown(f"### {model_configs[1]['name']}")
    if model_configs[1]['use_steering']:
        st.caption(f"💗 Love: {model_configs[1]['love']}% (Learned Steering)")
    else:
        st.caption("🔧 Heuristic/Baseline")
    
    beta_container = st.container()
    display_messages(st.session_state.model_beta_messages, beta_container)
    
    beta_input = st.chat_input("Message Model Beta", key="beta_input")
    if beta_input:
        st.session_state.model_beta_messages.append({"role": "user", "content": beta_input})
        
        with st.spinner("Thinking..."):
            result = generate_with_steering(
                beta_input,
                model_configs[1]['love'],
                model_configs[1]['use_steering'],
                use_llm=True,
                model_type=model_configs[1]['model_type']
            )
            
            if "error" not in result:
                response = result.get("response", "No response generated")
                st.session_state.model_beta_messages.append({"role": "assistant", "content": response})
            else:
                st.error(result["error"])
        
        st.rerun()

# Model Gamma
with col3:
    st.markdown(f"### {model_configs[2]['name']}")
    if model_configs[2]['use_steering']:
        st.caption(f"💗 Love: {model_configs[2]['love']}% (Learned Steering)")
    else:
        st.caption("🔧 Heuristic/Baseline")
    
    gamma_container = st.container()
    display_messages(st.session_state.model_gamma_messages, gamma_container)
    
    gamma_input = st.chat_input("Message Model Gamma", key="gamma_input")
    if gamma_input:
        st.session_state.model_gamma_messages.append({"role": "user", "content": gamma_input})
        
        with st.spinner("Thinking..."):
            result = generate_with_steering(
                gamma_input,
                model_configs[2]['love'],
                model_configs[2]['use_steering'],
                use_llm=True,
                model_type=model_configs[2]['model_type']
            )
            
            if "error" not in result:
                response = result.get("response", "No response generated")
                st.session_state.model_gamma_messages.append({"role": "assistant", "content": response})
            else:
                st.error(result["error"])
        
        st.rerun()

# Footer stats
st.markdown("---")
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("Love Dial", f"{love_value}%")
with stat_col2:
    st.metric("Steering Mode", "Learned" if st.session_state.steering_trained else "Heuristic")
with stat_col3:
    total_messages = (
        len(st.session_state.model_alpha_messages) +
        len(st.session_state.model_beta_messages) +
        len(st.session_state.model_gamma_messages)
    )
    st.metric("Total Messages", total_messages)
with stat_col4:
    st.metric("Comparison Mode", comparison_mode)
