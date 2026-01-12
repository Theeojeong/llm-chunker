import json
import time
import os
from typing import Dict, Any, Callable

# Optional imports to avoid hard crashes if dependencies are missing
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

def openai_llm_caller(prompt: str) -> str:
    """
    Default implementation using OpenAI (ChatGPT).
    Requires OPENAI_API_KEY environment variable.
    """
    if not HAS_OPENAI:
        raise ImportError("OpenAI library is not installed. Please run 'pip install openai'.")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Fallback: Try to look for it in a local .env file manually if needed, 
        # but standard practice is environment variable.
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)
    
    # Using 'gpt-4o' or 'gpt-3.5-turbo' as generic default
    # You can change this to 'gpt-4-turbo' etc.
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"OpenAI API Call Failed: {e}")

def ollama_llm_caller(prompt: str) -> str:
    """
    Alternative implementation using Ollama.
    """
    if not HAS_OLLAMA:
        raise ImportError("Ollama library is not installed.")
    
    # Defaulting to llama3, can be changed
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# ──────────────────────────────────────────────────────────────
# [Configuration]
# Change this to switch between OpenAI and Ollama globally
# ──────────────────────────────────────────────────────────────
DEFAULT_LLM_CALLER = openai_llm_caller 


def sanitize_json_output(raw_text: str) -> str:
    """
    Cleans up potential markdown formatting from LLM output.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove first line (```json or ```)
        parts = text.split("\n", 1)
        if len(parts) > 1:
            text = parts[1]
        # Remove last line (```)
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
    return text.strip()

class TransitionAnalyzer:
    def __init__(self, 
                 prompt_generator: Callable[[str], str], 
                 llm_caller: Callable[[str], str] = None):
        
        self.prompt_generator = prompt_generator
        # If no caller provided, use the global default (OpenAI)
        self.llm_caller = llm_caller if llm_caller else DEFAULT_LLM_CALLER

    def analyze_segment(self, segment: str) -> Dict[str, Any]:
        prompt = self.prompt_generator(segment)
        
        for attempt in range(3):
            try:
                raw_response = self.llm_caller(prompt)
                cleaned = sanitize_json_output(raw_response)
                try:
                    data = json.loads(cleaned)
                    
                    # Normalize various schema keys to 'transition_points'
                    if "transition_points" in data:
                        return data
                    if "emotional_phases" in data:
                        return {"transition_points": data["emotional_phases"]}
                    if "legal_sections" in data:
                        return {"transition_points": data["legal_sections"]}
                        
                except json.JSONDecodeError:
                    pass
            except Exception as e:
                print(f"LLM Analysis Error (Attempt {attempt+1}): {e}")
            
            time.sleep(1)
            
        return {"transition_points": []}
