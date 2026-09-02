"""
Air Quality Intelligence Agent - Streamlit Application.
Provides a modern conversational interface with agent transparency,
real-time pollutant metric cards, weather dispersion indicators, and historical comparisons.
"""

import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is at the head of sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv()

from src.agent.orchestrator import AirQualityAgent

# Page configuration
st.set_page_config(
    page_title="Air Quality Intelligence Agent",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .activity-badge {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Agent in session state
if "agent" not in st.session_state:
    st.session_state.agent = AirQualityAgent()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

agent = st.session_state.agent

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Agent Configuration")
    
    provider = st.selectbox(
        "LLM Brain Engine",
        ["Auto / Built-in ReAct Engine", "OpenAI (GPT-4o-mini)", "Google Gemini", "Custom OpenAI-Compatible"],
        index=0
    )
    
    api_key_input = st.text_input(
        "API Key (Optional)",
        type="password",
        value=os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or "",
        help="Optional: Enter OpenAI or Gemini API key to enable LLM tool-calling. Leave blank to use the built-in Deterministic ReAct Engine."
    )
    
    custom_base_url = None
    if provider == "Google Gemini":
        custom_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    elif provider == "Custom OpenAI-Compatible":
        custom_base_url = st.text_input("Base URL", value="http://localhost:11434/v1")

    if st.button("Apply Engine Configuration"):
        if api_key_input:
            model_name = "gemini-2.5-flash" if provider == "Google Gemini" else "gpt-4o-mini"
            st.session_state.agent = AirQualityAgent(
                api_key=api_key_input,
                base_url=custom_base_url,
                model=model_name
            )
            st.success(f"Configured with {provider}!")
        else:
            st.session_state.agent = AirQualityAgent()
            st.info("Using Built-in Deterministic ReAct Engine (Zero API Keys required).")
        agent = st.session_state.agent

    st.markdown("---")
    st.markdown("### 🧠 Active Session Context")
    curr_loc = agent.memory.get_location() or "None set (defaults to Delhi)"
    st.markdown(f"**📍 Current City:** `{curr_loc}`")
    
    health_conds = agent.memory.entities.get("health_conditions", [])
    if health_conds:
        st.markdown(f"**🩺 Health Vulnerabilities:** {', '.join(health_conds)}")
    
    if st.button("🧹 Clear Conversation"):
        agent.memory.clear()
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 Example Prompts")
    examples = [
        "What is the AQI in Kanpur today?",
        "Should I go for a morning run in Delhi tomorrow?",
        "Why is the air quality poor today?",
        "What pollutant is mainly responsible for the current AQI?",
        "Compare today's AQI with the historical trend.",
        "I live in Kanpur.",
        "Should I exercise outside tomorrow?"
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state.preset_prompt = ex


# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown('<div class="main-header">🌍 Air Quality Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Atmospheric Analysis, Machine Learning Forecasting & CPCB/WHO Health Advisory</div>', unsafe_allow_html=True)

# Engine status badge
engine_mode = "LLM Function Calling Brain" if agent.llm_client else "Autonomous ReAct Engine (Zero-Config)"
st.markdown(f'<span class="activity-badge">🚀 Active Mode: {engine_mode}</span>', unsafe_allow_html=True)

# Render Chat History
for item in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(item["user"])

    with st.chat_message("assistant"):
        # Display Agent Activity if available
        if item.get("activity"):
            with st.expander("🔍 Agent Activity & Tool Execution Trace", expanded=False):
                for act in item["activity"]:
                    st.markdown(f"- {act}")

        st.markdown(item["assistant"])

        # Display Structured Metric Cards if tool outputs exist
        tool_data = item.get("tool_outputs", {})
        live_info = tool_data.get("fetch_live_air_quality")
        weather_info = tool_data.get("fetch_weather_forecast")
        health_info = tool_data.get("get_aqi_health_guidance")

        if live_info and live_info.get("status") == "success":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Air Quality Index</div>'
                    f'<div class="metric-value" style="color: {live_info.get("color", "#1E293B")};">{live_info["aqi"]:.0f}</div>'
                    f'<div>{live_info["category"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col2:
                dom = live_info.get("dominant_pollutant", "PM2.5")
                ratio = live_info.get("dominant_ratio", 1.0)
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Dominant Pollutant</div>'
                    f'<div class="metric-value">{dom}</div>'
                    f'<div>{ratio}x CPCB Limit</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col3:
                temp = weather_info.get("temperature_c", "N/A") if weather_info else "N/A"
                disp = weather_info.get("dispersion_analysis", {}).get("pollution_trapping_risk", "Moderate") if weather_info else "N/A"
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Temperature & Stagnation</div>'
                    f'<div class="metric-value">{temp}°C</div>'
                    f'<div>Stagnation Risk: {disp}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col4:
                adv = health_info.get("advisory", {}) if health_info else {}
                safe = "✅ Safe" if adv.get("is_safe_for_exercise", True) else "❌ Avoid"
                mask = "😷 N95 Mask" if adv.get("mask_recommended") else "😊 Clean Air"
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Exercise & Mask</div>'
                    f'<div class="metric-value">{safe}</div>'
                    f'<div>{mask}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# Handle user input from text box or sidebar buttons
prompt = st.chat_input("Ask about air quality, morning running, health advisories, or ML forecasts...")
if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
    prompt = st.session_state.preset_prompt
    st.session_state.preset_prompt = None

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent analyzing intent and coordinating tools..."):
            result = agent.run(prompt)
            
            # Show activity trace
            if result.get("activity"):
                with st.expander("🔍 Agent Activity & Tool Execution Trace", expanded=True):
                    for act in result["activity"]:
                        st.markdown(f"- {act}")

            st.markdown(result["response"])

            # Metric Cards
            tool_data = result.get("tool_outputs", {})
            live_info = tool_data.get("fetch_live_air_quality")
            weather_info = tool_data.get("fetch_weather_forecast")
            health_info = tool_data.get("get_aqi_health_guidance")

            if live_info and live_info.get("status") == "success":
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-label">Air Quality Index</div>'
                        f'<div class="metric-value" style="color: {live_info.get("color", "#1E293B")};">{live_info["aqi"]:.0f}</div>'
                        f'<div>{live_info["category"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    dom = live_info.get("dominant_pollutant", "PM2.5")
                    ratio = live_info.get("dominant_ratio", 1.0)
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-label">Dominant Pollutant</div>'
                        f'<div class="metric-value">{dom}</div>'
                        f'<div>{ratio}x CPCB Limit</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col3:
                    temp = weather_info.get("temperature_c", "N/A") if weather_info else "N/A"
                    disp = weather_info.get("dispersion_analysis", {}).get("pollution_trapping_risk", "Moderate") if weather_info else "N/A"
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-label">Temperature & Stagnation</div>'
                        f'<div class="metric-value">{temp}°C</div>'
                        f'<div>Stagnation Risk: {disp}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col4:
                    adv = health_info.get("advisory", {}) if health_info else {}
                    safe = "✅ Safe" if adv.get("is_safe_for_exercise", True) else "❌ Avoid"
                    mask = "😷 N95 Mask" if adv.get("mask_recommended") else "😊 Clean Air"
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-label">Exercise & Mask</div>'
                        f'<div class="metric-value">{safe}</div>'
                        f'<div>{mask}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            st.session_state.chat_history.append({
                "user": prompt,
                "assistant": result["response"],
                "activity": result.get("activity", []),
                "tool_outputs": result.get("tool_outputs", {})
            })
