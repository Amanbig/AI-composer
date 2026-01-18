
import os
from .composer import MarkovComposer # Relative import inside modules package
from typing import TypedDict, Annotated, List
from .synthesizer import Synthesizer
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Define the State
class AgentState(TypedDict):
    topic: str
    notes: str
    is_valid: bool
    error: str
    retries: int

class MusicAgent:
    def __init__(self, api_key, model_name="google/gemini-2.0-flash-001"):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model=model_name,
            temperature=0.7
        )
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("generate", self.generate_step)
        workflow.add_node("validate", self.validate_step)
        
        workflow.set_entry_point("generate")
        
        workflow.add_edge("generate", "validate")
        workflow.add_conditional_edges(
            "validate",
            self.should_continue,
            {
                "end": END,
                "retry": "generate"
            }
        )
        
        return workflow.compile()

    def generate_step(self, state: AgentState):
        topic = state["topic"]
        error = state.get("error", "")
        retries = state.get("retries", 0)
        
        print(f"--- Generating (Attempt {retries + 1}) ---")
        
        system_prompt = """You are a music composer AI. 
        Your goal is to generate a melody based on the user's description.
        
        OUTPUT FORMAT RULES:
        1. Return ONLY a string of notes separated by spaces.
        2. Format: Note:Duration (e.g. C4:1, D#4:0.5, R:1 for rest).
        3. Do not include any explanations, markdown, or code blocks. Just the raw string.
        4. Use standard scientific pitch notation (C4, F#5, Bb3).
        5. Duration is in beats (0.5 = eighth note, 1 = quarter note, 2 = half note).
        
        Example Output:
        C4:1 E4:1 G4:1 C5:2 G4:1 E4:1 C4:2
        """
        
        user_msg = f"Compose a melody for: {topic}"
        if error:
            user_msg += f"\n\nPREVIOUS ERROR: {error}\nPlease fix the format."

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ]
        
        response = self.llm.invoke(messages)
        content = response.content.strip().replace("`", "").replace("python", "")
        
        return {"notes": content, "retries": retries + 1}

    def validate_step(self, state: AgentState):
        notes = state["notes"]
        print(f"--- Validating: {notes[:20]}... ---")
        
        if not notes:
            return {"is_valid": False, "error": "Output was empty"}
            
        # Basic validation logic
        valid_notes = True
        invalid_tokens = []
        
        tokens = notes.split()
        if len(tokens) < 2:
             return {"is_valid": False, "error": "Melody too short"}

        for token in tokens:
            if ":" not in token:
                valid_notes = False
                invalid_tokens.append(f"{token} (missing duration)")
                continue
                
            parts = token.split(":")
            if len(parts) != 2:
                valid_notes = False
                invalid_tokens.append(f"{token} (bad format)")
                continue
                
            note, duration = parts
            # Check note format (roughly)
            if note.upper() not in ["R", "REST"] and len(note) < 2:
                 valid_notes = False
                 invalid_tokens.append(f"{token} (invalid note)")
            
            try:
                float(duration)
            except ValueError:
                valid_notes = False
                invalid_tokens.append(f"{token} (invalid duration)")

        if valid_notes:
            return {"is_valid": True, "error": ""}
        else:
            return {"is_valid": False, "error": f"Invalid tokens: {', '.join(invalid_tokens[:3])}"}

    def should_continue(self, state: AgentState):
        if state["is_valid"]:
            return "end"
        if state["retries"] > 3:
            return "end" # Give up after 3 retries
        return "retry"

    def run(self, topic):
        initial_state = {
            "topic": topic,
            "notes": "",
            "is_valid": False,
            "error": "",
            "retries": 0
        }
        result = self.workflow.invoke(initial_state)
        return result

def get_available_models(api_key: str = None, only_free: bool = True) -> List[str]:
    """
    Fetches the list of available models from OpenRouter.
    Returns a list of model IDs to be used in the UI.
    Falls back to a default list if fetching fails.
    """
    default_free_models = [
        "google/gemini-2.0-flash-exp:free",
        "google/gemini-exp-1206:free",
        "meta-llama/llama-3.2-11b-vision-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "microsoft/phi-3-medium-128k-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free",
    ]
    
    if not api_key:
        return default_free_models

    import requests
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            all_models = data.get("data", [])
            
            filtered_models = []
            for m in all_models:
                mid = m.get("id")
                pricing = m.get("pricing", {})
                
                # Check for free
                is_free = False
                if mid.endswith(":free"):
                    is_free = True
                else:
                    try:
                        p_prompt = float(pricing.get("prompt", -1))
                        p_completion = float(pricing.get("completion", -1))
                        if p_prompt == 0 and p_completion == 0:
                            is_free = True
                    except (ValueError, TypeError):
                        pass
                
                if only_free:
                    if is_free:
                        filtered_models.append(mid)
                else:
                    filtered_models.append(mid)
            
            filtered_models.sort()
            
            # If search succeeded but returned empty, use defaults.
            if not filtered_models and only_free:
                return default_free_models
                
            return filtered_models
        else:
            print(f"Failed to fetch models: {response.status_code}")
            return default_free_models
            
    except Exception as e:
        print(f"Error fetching models: {e}")
        return default_free_models
