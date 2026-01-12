import json
import time
import os
import logging
from typing import Dict, Any, Callable, Optional

# ── Logger Setup ──
logger = logging.getLogger("llm_chunker")

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


def create_openai_caller(model: str = "gpt-4o") -> Callable[[str], str]:
    """
    Factory function to create an OpenAI LLM caller with a specific model.
    
    Args:
        model: The OpenAI model to use (e.g., "gpt-4o", "gpt-5-nano", "gpt-3.5-turbo")
    
    Returns:
        Callable[[str], str]: A function that takes a prompt and returns the LLM response.
    
    Example:
        >>> analyzer = TransitionAnalyzer(
        ...     prompt_generator=get_default_prompt,
        ...     llm_caller=create_openai_caller("gpt-5-nano")
        ... )
    """
    def caller(prompt: str) -> str:
        if not HAS_OPENAI:
            raise ImportError("OpenAI library is not installed. Please run 'pip install openai'.")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set.\n"
                "Set it via: export OPENAI_API_KEY='your-key'\n"
                "Or use Ollama: GenericChunker(analyzer=TransitionAnalyzer(llm_caller=create_ollama_caller()))"
            )

        client = OpenAI(api_key=api_key)
        logger.info(f"[LLM] Using model: {model}")

        try:
            logger.debug(f"[LLM] Sending prompt ({len(prompt)} chars)")
            
            # GPT-5 계열은 temperature 파라미터를 지원하지 않음
            if model.startswith("gpt-5"):
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
            
            content = response.choices[0].message.content
            logger.debug(f"[LLM] Received response ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"[LLM] OpenAI API Call Failed: {e}")
            raise RuntimeError(f"OpenAI API Call Failed: {e}")
    
    return caller


def create_ollama_caller(model: str = "llama3") -> Callable[[str], str]:
    """
    Factory function to create an Ollama LLM caller with a specific model.
    
    Args:
        model: The Ollama model to use (e.g., "llama3", "mistral", "codellama")
    
    Returns:
        Callable[[str], str]: A function that takes a prompt and returns the LLM response.
    
    Example:
        >>> analyzer = TransitionAnalyzer(
        ...     prompt_generator=get_default_prompt,
        ...     llm_caller=create_ollama_caller("mistral")
        ... )
    """
    def caller(prompt: str) -> str:
        if not HAS_OLLAMA:
            raise ImportError("Ollama library is not installed.")
        
        logger.info(f"[LLM] Using Ollama ({model})")
        logger.debug(f"[LLM] Sending prompt ({len(prompt)} chars)")
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        content = response["message"]["content"]
        logger.debug(f"[LLM] Received response ({len(content)} chars)")
        return content
    
    return caller


# ── Legacy functions for backward compatibility ──
def openai_llm_caller(prompt: str) -> str:
    """
    Default OpenAI caller using env var OPENAI_MODEL or 'gpt-4o'.
    For custom models, use create_openai_caller(model_name) instead.
    """
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
    return create_openai_caller(model_name)(prompt)


def ollama_llm_caller(prompt: str) -> str:
    """
    Default Ollama caller using 'llama3'.
    For custom models, use create_ollama_caller(model_name) instead.
    """
    return create_ollama_caller("llama3")(prompt)


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


def _extract_transition_points(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flexibly extract transition points from various schema formats.
    Supports: transition_points, emotional_phases, legal_sections, and any list-type value.
    """
    # Known schema keys (priority order)
    known_keys = ["transition_points", "emotional_phases", "legal_sections", "topic_changes", "sections"]
    
    for key in known_keys:
        if key in data and isinstance(data[key], list):
            logger.debug(f"[Schema] Found key '{key}' with {len(data[key])} items")
            return {"transition_points": data[key]}
    
    # Fallback: find first list-type value
    for key, value in data.items():
        if isinstance(value, list):
            logger.debug(f"[Schema] Fallback: using key '{key}' with {len(value)} items")
            return {"transition_points": value}
    
    logger.warning("[Schema] No transition points found in response")
    return {"transition_points": []}


class TransitionAnalyzer:
    def __init__(self, 
                 prompt_generator: Callable[[str], str], 
                 llm_caller: Callable[[str], str] = None,
                 model: Optional[str] = None):
        """
        Initialize the TransitionAnalyzer.
        
        Args:
            prompt_generator: Function that generates the prompt for a text segment.
            llm_caller: Custom LLM caller function. If None, uses default OpenAI caller.
            model: OpenAI model name (shortcut for create_openai_caller). 
                   Ignored if llm_caller is provided.
        
        Examples:
            # Using default (env var OPENAI_MODEL or gpt-4o)
            >>> analyzer = TransitionAnalyzer(prompt_generator=get_default_prompt)
            
            # Specifying model directly
            >>> analyzer = TransitionAnalyzer(
            ...     prompt_generator=get_default_prompt,
            ...     model="gpt-5-nano"
            ... )
            
            # Using custom caller
            >>> analyzer = TransitionAnalyzer(
            ...     prompt_generator=get_default_prompt,
            ...     llm_caller=create_openai_caller("gpt-4o-mini")
            ... )
        """
        self.prompt_generator = prompt_generator
        
        # Priority: llm_caller > model > default
        if llm_caller:
            self.llm_caller = llm_caller
        elif model:
            self.llm_caller = create_openai_caller(model)
        else:
            self.llm_caller = DEFAULT_LLM_CALLER

    def analyze_segment(self, segment: str) -> Dict[str, Any]:
        prompt = self.prompt_generator(segment)
        logger.info(f"[Analyzer] Analyzing segment ({len(segment)} chars)")
        
        for attempt in range(3):
            try:
                raw_response = self.llm_caller(prompt)
                cleaned = sanitize_json_output(raw_response)
                logger.debug(f"[Analyzer] Cleaned JSON: {cleaned[:200]}...")
                
                try:
                    data = json.loads(cleaned)
                    result = _extract_transition_points(data)
                    logger.info(f"[Analyzer] Found {len(result['transition_points'])} transition points")
                    
                    # Log each transition point
                    for i, tp in enumerate(result['transition_points']):
                        logger.debug(f"  [TP {i+1}] sig={tp.get('significance', '?')}, text='{tp.get('start_text', '')[:30]}...'")
                    
                    return result
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"[Analyzer] JSON parse error (Attempt {attempt+1}): {e}")
                    logger.debug(f"[Analyzer] Raw response: {raw_response[:300]}...")
                    
            except Exception as e:
                logger.error(f"[Analyzer] LLM Error (Attempt {attempt+1}): {e}")
            
            time.sleep(1)
        
        logger.warning("[Analyzer] All attempts failed, returning empty result")
        return {"transition_points": []}
