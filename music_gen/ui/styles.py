
CUSTOM_CSS = """
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(to bottom right, #0F172A, #1E293B);
        color: #F8FAFC;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #60A5FA !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    .stSelectbox>div>div>div {
        background-color: #1E293B;
        color: #F8FAFC;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    /* Cards/Containers */
    div[data-testid="stMetricValue"] {
        color: #60A5FA;
    }
    
    .history-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    .history-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.3);
    }

    /* General Glass Card */
    .glass-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #93C5FD;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        padding-bottom: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        padding-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding-left: 1rem;
        padding-right: 1rem;
        border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B;
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.3);
        border-bottom: 1px solid rgba(96, 165, 250, 0.3); /* Override default bottom border */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
"""
