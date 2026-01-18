# 🎵 AI Music Composer

A full-stack AI Music Generation System featuring secure authentication, visualizing tools, and a powerful multi-engine composer.

## 🚀 Features
- **Core Engines**:
    - **Manual**: Compose using simple notation (`C4:1` etc).
    - **Markov Chain**: Stochastic generation learned from training data.
    - **Agentic AI**: Text-to-music translation using LLMs (OpenRouter/OpenAI).
- **Web UI**: Modern Streamlit interface with a premium dark theme.
- **Visualizer**: High-quality waveform plotting and image saving.
- **User Management**:
    - Secure Login/Register (bcrypt hashing, SQLite).
    - Personal generation history and file management.
- **Robustness**:
    - Background scheduler handles file cleanup (files kept for **24 hours**).
    - Modular architecture for scalability.

## 📦 Installation

### Prerequisites
- Python 3.10+
- [Optional] Docker

### Setup
1.  **Clone & Install**:
    ```bash
    git clone https://github.com/Amanbig/AI-composer.git
    cd AI-composer
    # Create env
    python -m venv venv
    venv\Scripts\activate # Windows
    # Install
    pip install -r requirements.txt
    ```

2.  **Environment Config**:
    Create `.env` in root:
    ```env
    OPENROUTER_API_KEY=sk-or-v1-...
    ```

3.  **Run**:
    ```bash
    streamlit run music_gen/app.py
    ```

## 🐳 Running with Docker

```bash
docker build -t ai-composer .
docker run -p 8501:8501 --env-file .env ai-composer
```
Access at `http://localhost:8501`

## 📂 Structure
- `music_gen/`: Main package
  - `app.py`: Application entry point
  - `modules/`: Core logic (Auth, DB, Cron, Agents)
  - `ui/`: Frontend components
  - `generated/`: Output files per user
  - `data/`: SQLite DB and training sets

## 📝 Usage
- **Sign Up**: Create an account to access the tools.
- **Compose**: Use the "Agentic AI" tab to describe your song in English.
- **History**: View, download, and see visualizations of your past creations.

---
*Created with ❤️ by Antigravity*
