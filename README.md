# 🎵 AI Music Composer

A Python-based AI Music Generation System that creates melodies using:
1.  **Algorithmic Synthesis**: Basic sine/square/sawtooth waveforms.
2.  **Markov Chains**: Learns from existing songs to generate new ones.
3.  **Agentic AI**: Uses LLMs (via OpenRouter) to compose music from natural language descriptions (e.g., "A sad melody").

## 🚀 Features
- **Web UI**: Interactive dashboard built with Streamlit.
- **Waveform Visualizer**: Real-time plotting of generated audio.
- **Multiple Engines**: Switch between manual input, Markov Chain, and Agentic AI.
- **Customizable**: Adjust BPM, Waveform (Sine/Square/Sawtooth), and composition length.

## 📦 Installation

### Prerequisites
- Python 3.10+
- [Optional] Docker

### Local Setup
1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd ai-music-composer
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys (Optional)**:
    - Create a `.env` file in the root directory.
    - Add your OpenRouter API Key:
      ```env
      OPENROUTER_API_KEY=sk-or-v1-......
      ```

5.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## 🐳 Running with Docker

1.  **Build the image**:
    ```bash
    docker build -t ai-music-composer .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 8501:8501 --env-file .env ai-music-composer
    ```

3.  Access the app at `http://localhost:8501`.

## 📂 Project Structure
- `src/`: Core logic modules.
  - `synthesizer.py`: Audio generation engine.
  - `composer.py`: Markov Chain logic.
  - `agent.py`: LangGraph agent for LLM composition.
  - `visualizer.py`: Matplotlib plotting tools.
- `data/`: Data files.
  - `songs.txt`: Training data for the Markov Chain.
- `app.py`: Streamlit entry point.
- `main.py`: Command-line interface entry point.

## 📝 Usage

### Data format relative to music
- **Notes**: Standard notation `C4`, `A#3`, `Db5`.
- **Rhythm**: Add duration with colon `Note:Duration`.
  - `C4:1` (Quarter note)
  - `C4:0.5` (Eighth note)
  - `R:1` (Rest)

### Agentic AI
- Go to "Agentic AI" tab.
- Enter a prompt: *"Create a fast-paced electronic melody."*
- The agent will generate, validate, and play the result!

---
*Created with ❤️ by Antigravity*
