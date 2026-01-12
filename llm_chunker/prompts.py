from typing import Callable

def get_default_prompt(segment: str) -> str:
    """
    Default prompt for detecting semantic changes or "turning points" in text.
    """
    return f"""
You must analyze the following text segment and identify points where the topic, mood, or narrative focus changes significantly.

TEXT SEGMENT:
{segment}

Return a SINGLE JSON object in the following format (no markdown):
{{
  "transition_points": [
    {{
      "start_text": "Text snippet where the change begins",
      "topic_before": "Summary of the topic/mood BEFORE this point",
      "topic_after": "Summary of the topic/mood AFTER this point",
      "significance": 8, 
      "explanation": "Brief explanation of why this is a transition point"
    }}
  ]
}}
If no significant transitions are found, return {{ "transition_points": [] }}.
""".strip()

def get_legal_prompt(segment: str) -> str:
    """
    Prompt specialized for legal document chunking.
    """
    return f"""
You are a legal expert. Analyze the following text and identify points where the legal topic, clause type, or subject usage changes significantly.

TEXT SEGMENT:
{segment}

Return a SINGLE JSON object in the following format (no markdown):
{{
  "transition_points": [
    {{
      "start_text": "Text snippet where the change begins (must match exactly)",
      "topic_before": "Legal context/article BEFORE this point",
      "topic_after": "Legal context/article AFTER this point",
      "significance": 8, 
      "explanation": "Why this constitutes a legal section boundary"
    }}
  ]
}}
If no significant transitions are found, return {{ "transition_points": [] }}.
""".strip()
