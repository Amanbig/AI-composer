
import streamlit as st
import os
import uuid
from datetime import datetime
from modules.db import get_db, Generation, User
# Use absolute imports assuming music_gen is in path
from modules.synthesizer import Synthesizer
from modules.composer import MarkovComposer
from modules import visualizer

# from modules import session_manager

def render_sidebar(user):
    with st.sidebar:
        # User Profile
        col_p1, col_p2 = st.columns([1, 3])
        with col_p1:
            st.markdown("<h2 style='text-align: center; margin: 0;'>👤</h2>", unsafe_allow_html=True)
        with col_p2:
            st.markdown(f"**{user['username']}**")
            st.caption("Pro Member") # Placeholder
            
        if st.button("Logout", type="secondary", width="stretch"):
            # session_manager.clear_session()
            st.session_state.user = None
            st.rerun()
            
        st.markdown("---")
        
        # Settings Groups with Expander
        with st.expander("🔑 API Configuration", expanded=True):
            env_key = os.getenv("OPENROUTER_API_KEY", "")
            if env_key:
                st.success("✅ System Key Active")
                if st.checkbox("Use Custom Key"):
                   api_key = st.text_input("Custom API Key", type="password")
                else:
                    api_key = env_key
            else:
                api_key = st.text_input("API Key", type="password")
        
        st.markdown("### 🎛️ Audio Engine")
        bpm = st.slider("Tempo", 60, 240, 120, help="Beats Per Minute")
        wave_type = st.selectbox("Oscillator", ["sine", "square", "sawtooth"], format_func=lambda x: x.capitalize())
        
        st.markdown("### 🧠 AI Model")
        ai_length = st.number_input("Sequence Length", min_value=4, max_value=128, value=16, step=4)
        
        st.info("💡 **Tip:** Try mixing manual inputs with AI generation!")
        
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
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🎹 Composition Engine</div>', unsafe_allow_html=True)
        
        tab_manual, tab_ai, tab_agent = st.tabs(["Manual Input", "Markov Chain", "Agentic AI"])
        
        generated_audio = None
        prompt_used = ""
        
        with tab_manual:
            user_input = st.text_area("Melody String", value="C4:1 E4:1 G4:1 C5:2", height=100)
            st.caption("Format: `Note:Duration` (e.g. `C4:1`)")
            if st.button("Generate Audio", key="btn_manual"):
                with st.spinner("Synthesizing..."):
                    generated_audio = st.session_state.synth.generate_audio(user_input, bpm=bpm, wave_type=wave_type)
                    prompt_used = "Manual Input"
        
        with tab_ai:
            st.info(f"Learned Transitions: **{len(st.session_state.composer.chain)}**")
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
        st.markdown('</div>', unsafe_allow_html=True)

        # Save and Output
        if generated_audio is not None:
             handle_output(generated_audio, user, prompt_used)

    with col2:
        render_visualization_and_history(generated_audio, user)

def handle_output(audio, user, prompt):
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔊 Playback Studio</div>', unsafe_allow_html=True)
    
    # User specific dir
    OUTPUT_DIR = os.path.join("music_gen/generated", user['username'])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Unique Filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"melody_{timestamp}_{unique_id}.wav"
    img_filename = f"viz_{timestamp}_{unique_id}.png"
    
    path = os.path.join(OUTPUT_DIR, filename)
    img_path = os.path.join(OUTPUT_DIR, img_filename)
    
    # Save Audio
    st.session_state.synth.save_wav(path, audio)
    
    # Save Visualization
    if 'synth' in st.session_state:
         fig = visualizer.plot_waveform(audio, st.session_state.synth.sample_rate)
         fig.savefig(img_path, facecolor='#0E1117', bbox_inches='tight', pad_inches=0.1)
         # Clean up memory
         import matplotlib.pyplot as plt
         plt.close(fig)
    
    # DB Save
    db = next(get_db())
    new_gen = Generation(user_id=user['id'], filename=filename, image_filename=img_filename, prompt=prompt)
    db.add(new_gen)
    db.commit()
    
    col_play, col_dl = st.columns([3, 1])
    with col_play:
        st.audio(path)
    with col_dl:
        with open(path, "rb") as f:
            st.download_button("Download", f, filename, "audio/wav", width="stretch")
            
    st.markdown('</div>', unsafe_allow_html=True)

def render_visualization_and_history(audio, user):
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📉 Visualization</div>', unsafe_allow_html=True)
    
    if audio is not None:
        if 'synth' in st.session_state:
             fig = visualizer.plot_waveform(audio, st.session_state.synth.sample_rate)
             st.pyplot(fig, width="stretch")
    else:
        st.info("Generate audio to see waveform")
    st.markdown('</div>', unsafe_allow_html=True)
        
    # Removed duplicate header
    db = next(get_db())
    history = db.query(Generation).filter(Generation.user_id == user['id']).order_by(Generation.created_at.desc()).limit(10).all()
    
    if not history:
        st.info("No music generated yet. Create something!")
        
    for item in history:
        user_dir = os.path.join("music_gen/generated", user['username'])
        h_path = os.path.join(user_dir, item.filename)
        file_exists = os.path.exists(h_path)
        
        # Check for visualization image
        img_path = None
        if item.image_filename:
            possible_path = os.path.join(user_dir, item.image_filename)
            if os.path.exists(possible_path):
                img_path = possible_path
            
        with st.container():
            st.markdown(f"""
            <div class="history-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="width: 100%;">
                        <span style="font-weight: 600; color: #E2E8F0; font-size: 1rem;">🎵 {item.prompt[:40] or 'Melody'}...</span>
                        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">Created at {item.created_at.strftime('%H:%M • %d %b')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Layout: Image (Accordion/Expander or just inline) -> Audio -> Actions
            # Let's put image inside an expander to keep it clean, or just show it small.
            # User asked to "save the visualization", presumably to see it.
            
            if img_path:
                with st.expander("See Waveform"):
                    st.image(img_path, width="stretch")
            
            # Action Row
            col_audio, col_actions = st.columns([3, 1])
            
            with col_audio:
                if file_exists:
                    st.audio(h_path)
                else:
                    st.error("File not found")
            
            with col_actions:
                if file_exists:
                    with open(h_path, "rb") as f:
                        st.download_button("⬇️", f, item.filename, "audio/wav", key=f"dl_{item.id}", help="Download WAV")
            
            st.markdown("---")
