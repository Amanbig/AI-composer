
import streamlit as st
import numpy as np
import visualizer
import os
from src.synthesizer import Synthesizer
from src.composer import MarkovComposer
import src.visualizer as visualizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Music Composer",
    page_icon="🎹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
        transform: translateY(-2px);
    }
    h1, h2, h3 {
        color: #FF4B4B !important;
    }
    .stTextInput>div>div>input {
        color: #FAFAFA;
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
if 'synth' not in st.session_state:
    st.session_state.synth = Synthesizer()

if 'composer' not in st.session_state:
    st.session_state.composer = MarkovComposer()
    
    # Load training data
    training_data = []
    
    # 1. Load from file
    if os.path.exists("data/songs.txt"):
        with open("data/songs.txt", "r") as f:
            file_songs = [line.strip() for line in f if line.strip()]
            training_data.extend(file_songs)
            
    # 2. Load internal defaults
    default_songs = st.session_state.composer.load_data()
    training_data.extend(default_songs)
    
    # Train
    st.session_state.composer.train(training_data)

# --- Sidebar ---
with st.sidebar:
    st.title("🎛️ Settings")
    
    st.subheader("APIs")
    # Tries to get key from env
    env_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if env_key:
        st.success("✅ API Key loaded from Environment")
        # Checkbox to override if needed
        if st.checkbox("Override API Key"):
            api_key = st.text_input("OpenRouter API Key", value=env_key, type="password")
        else:
            api_key = env_key
    else:
        api_key = st.text_input("OpenRouter API Key", type="password", help="Required for Agentic AI. Add OPENROUTER_API_KEY to .env to hide this.")
    
    st.subheader("Audio Engine")
    bpm = st.slider("Tempo (BPM)", 60, 240, 120, help="Speed of the music")
    wave_type = st.selectbox("Waveform", ["sine", "square", "sawtooth"], help="Timbre of the sound")
    
    st.divider()
    
    st.subheader("AI Settings")
    ai_length = st.slider("Composition Length", 8, 64, 16, help="Number of notes to generate")

    st.markdown("---")
    st.caption("AI Music Gen v1.0")

# --- Main Content ---
st.title("🎹 AI Music Composer")
st.markdown("### Create music from text or let AI invent a melody.")

col1, col2 = st.columns([1.5, 1])

with col1:
    tab_manual, tab_ai, tab_agent = st.tabs(["✍️ Manual Input", "🤖 Markov Composer", "🧠 Agentic AI"])
    
    generated_audio = None
    generated_notes = ""
    
    with tab_manual:
        st.markdown("Enter notes separated by spaces. Use `Note:Duration` for rhythm.")
        user_input = st.text_area(
            "Melody String", 
            value="C4:1 E4:1 G4:1 C5:2", 
            height=100,
            help="Example: C4:1 D4:0.5 E4:0.5"
        )
        
        if st.button("Generate Audio", key="btn_manual"):
            generated_notes = user_input
            if generated_notes:
                with st.spinner("Synthesizing..."):
                    generated_audio = st.session_state.synth.generate_audio(
                        generated_notes, bpm=bpm, wave_type=wave_type
                    )
    
    with tab_ai:
        st.markdown(f"Markov Chain: Generates melody based on **{len(st.session_state.composer.chain)}** learned pitch transitions.")
        
        if st.button("✨ Compose & Generate", key="btn_ai"):
            with st.spinner("Composing..."):
                generated_notes = st.session_state.composer.compose(length=ai_length)
                st.success(f"**Composed:** `{generated_notes}`")
                
                generated_audio = st.session_state.synth.generate_audio(
                    generated_notes, bpm=bpm, wave_type=wave_type
                )
                
    with tab_agent:
        st.markdown("Describe the feeling or style, and the Agent will write it for you.")
        
        # Free model list for OpenRouter
        free_models = [
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-exp-1206:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "microsoft/phi-3-medium-128k-instruct:free",
            "huggingfaceh4/zephyr-7b-beta:free",
        ]
        
        selected_model = st.selectbox(
            "Select AI Model (Free Tier)", 
            free_models, 
            index=0,
            help="Choose a free model from OpenRouter"
        )
        
        agent_prompt = st.text_input("Prompt", placeholder="A sad melody in D minor...")
        
        if st.button("🚀 Agent Generate", key="btn_agent"):
            if not api_key:
                st.error("Please enter an OpenRouter API Key in the sidebar.")
            else:
                try:
                    from src.agent import MusicAgent
                    with st.spinner(f"Agent ({selected_model}) is thinking..."):
                        agent = MusicAgent(api_key=api_key, model_name=selected_model)
                        result = agent.run(agent_prompt)
                        
                        if result['is_valid']:
                            generated_notes = result['notes']
                            st.success(f"**Agent Generated:** `{generated_notes}`")
                             # Attempt to synthesize
                            generated_audio = st.session_state.synth.generate_audio(
                                generated_notes, bpm=bpm, wave_type=wave_type
                            )
                        else:
                            st.error(f"Agent failed to generate valid notes after retries. Last error: {result.get('error')}")
                            st.warning(f"Raw Output: {result.get('notes')}")
                            
                except Exception as e:
                    st.error(f"Agent Error: {str(e)}")
    
    # --- Output Section ---
    if generated_audio is not None:
        st.divider()
        st.subheader("🔊 Playback")
        
        # Save to temp file for playback
        # In a real app we might use io.BytesIO to avoid disk writes,
        # but saving file is robust for st.audio
        output_file = "streamlit_output.wav"
        st.session_state.synth.save_wav(output_file, generated_audio)
        
        st.audio(output_file)
        
        st.download_button(
            label="Download .WAV",
            data=open(output_file, 'rb'),
            file_name="my_melody.wav",
            mime="audio/wav"
        )

with col2:
    if generated_audio is not None:
        st.subheader("📉 Visualization")
        fig = visualizer.plot_waveform(generated_audio, st.session_state.synth.sample_rate)
        st.pyplot(fig)
    else:
        # Placeholder or empty state
        st.info("Generate audio to see the waveform.")
        
