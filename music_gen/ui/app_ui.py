
import streamlit as st
import os
import uuid
from datetime import datetime
from modules.db import get_db, Generation, User
# Use absolute imports assuming music_gen is in path
from modules.synthesizer import Synthesizer
from modules.composer import MarkovComposer
from modules import visualizer

def render_sidebar(user):
    with st.sidebar:
        st.subheader(f"👤 {user['username']}")
        if st.button("Logout", type="secondary"):
            st.session_state.user = None
            st.rerun()
            
        st.markdown("---")
        st.title("🎛️ Settings")
        
        st.subheader("APIs")
        env_key = os.getenv("OPENROUTER_API_KEY", "")
        
        if env_key:
            st.success("✅ API Key active")
            if st.checkbox("Override Key"):
                override_key = st.text_input("New Key", type="password", help="Leave empty to use env key")
                if override_key:
                    api_key = override_key
                else:
                    api_key = env_key
            else:
                api_key = env_key
        else:
            api_key = st.text_input("OpenRouter API Key", type="password", help="Required for Agentic AI")
        
        st.subheader("Audio Engine")
        bpm = st.slider("Tempo (BPM)", 60, 240, 120)
        wave_type = st.selectbox("Waveform", ["sine", "square", "sawtooth"])
        
        st.subheader("AI Settings")
        ai_length = st.slider("Composition Length", 8, 64, 16)
        
        st.markdown("---")
        return api_key, bpm, wave_type, ai_length

def render_main_app(user):
    # Sidebar
    api_key, bpm, wave_type, ai_length = render_sidebar(user)
    
    # Init components
    if 'synth' not in st.session_state:
        st.session_state.synth = Synthesizer()

    if 'composer' not in st.session_state:
        st.session_state.composer = MarkovComposer()
        # Load training data
        training_data = []
        if os.path.exists("music_gen/data/songs.txt"):
            with open("music_gen/data/songs.txt", "r") as f:
                training_data.extend([line.strip() for line in f if line.strip()])
        # Defaults
        training_data.extend(st.session_state.composer.load_data())
        st.session_state.composer.train(training_data)

    st.title("🎹 AI Music Composer")
    st.markdown("### Create music from text or let AI invent a melody.")

    col1, col2 = st.columns([1.5, 1])

    with col1:
        tab_manual, tab_ai, tab_agent = st.tabs(["✍️ Manual", "🤖 Markov", "🧠 Agent"])
        
        generated_audio = None
        prompt_used = ""
        
        with tab_manual:
            user_input = st.text_area("Melody String", value="C4:1 E4:1 G4:1 C5:2", height=100)
            if st.button("Generate Audio", key="btn_manual"):
                with st.spinner("Synthesizing..."):
                    generated_audio = st.session_state.synth.generate_audio(user_input, bpm=bpm, wave_type=wave_type)
                    prompt_used = "Manual Input"
        
        with tab_ai:
            if st.button("✨ Compose & Generate", key="btn_ai"):
                with st.spinner("Composing..."):
                    generated_notes = st.session_state.composer.compose(length=ai_length)
                    st.success(f"**Composed:** `{generated_notes}`")
                    generated_audio = st.session_state.synth.generate_audio(generated_notes, bpm=bpm, wave_type=wave_type)
                    prompt_used = "Markov Chain Composition"
                    
        with tab_agent:
            from modules.agent import get_available_models, MusicAgent
            
            @st.cache_data(ttl=3600)
            def fetch_models(key, only_free):
                return get_available_models(key, only_free)
            
            only_free = st.checkbox("Free models only", value=True)
            models = fetch_models(api_key, only_free)
            selected_model = st.selectbox("Model", models)
            agent_prompt = st.text_input("Prompt", placeholder="A sad melody in D minor...")
            
            if st.button("🚀 Agent Generate", key="btn_agent"):
                if not api_key:
                    st.error("API Key required")
                else:
                    try:
                        with st.spinner(f"Agent ({selected_model}) is thinking..."):
                            agent = MusicAgent(api_key=api_key, model_name=selected_model)
                            result = agent.run(agent_prompt)
                            if result['is_valid']:
                                st.success(f"**Generated:** `{result['notes']}`")
                                generated_audio = st.session_state.synth.generate_audio(result['notes'], bpm=bpm, wave_type=wave_type)
                                prompt_used = f"Agent: {agent_prompt}"
                            else:
                                st.error(result.get('error'))
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Save and Output
        if generated_audio is not None:
             handle_output(generated_audio, user, prompt_used)

    with col2:
        render_visualization_and_history(generated_audio, user)

def handle_output(audio, user, prompt):
    st.divider()
    st.subheader("🔊 Playback")
    
    # User specific dir
    OUTPUT_DIR = os.path.join("music_gen/generated", user['username'])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Unique Filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"melody_{timestamp}_{unique_id}.wav"
    path = os.path.join(OUTPUT_DIR, filename)
    
    st.session_state.synth.save_wav(path, audio)
    
    # DB Save
    db = next(get_db())
    new_gen = Generation(user_id=user['id'], filename=filename, prompt=prompt)
    db.add(new_gen)
    db.commit()
    
    st.audio(path)
    with open(path, "rb") as f:
        st.download_button("Download .WAV", f, filename, "audio/wav")

def render_visualization_and_history(audio, user):
    if audio is not None:
        st.subheader("📉 Visualization")
        if 'synth' in st.session_state:
             fig = visualizer.plot_waveform(audio, st.session_state.synth.sample_rate)
             st.pyplot(fig)
    else:
        st.info("Generate audio to see waveform")
        
    st.markdown("### 📜 History")
    db = next(get_db())
    history = db.query(Generation).filter(Generation.user_id == user['id']).order_by(Generation.created_at.desc()).limit(5).all()
    
    for item in history:
        with st.expander(f"{item.created_at.strftime('%H:%M')} - {item.prompt[:30]}..."):
            st.caption(f"Prompt: {item.prompt}")
            user_dir = os.path.join("music_gen/generated", user['username'])
            h_path = os.path.join(user_dir, item.filename)
            if os.path.exists(h_path):
                st.audio(h_path)
            else:
                st.warning("File expired/deleted")
