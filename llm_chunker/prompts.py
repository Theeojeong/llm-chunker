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
      "start_text": "Text snippet where the change begins (exact quote from the text)",
      "topic_before": "Summary of the topic/mood BEFORE this point",
      "topic_after": "Summary of the topic/mood AFTER this point",
      "significance": <1-10 integer>,
      "explanation": "Brief explanation of why this is a transition point"
    }}
  ]
}}

SIGNIFICANCE SCORING GUIDE:
- 1-3: Minor shifts (subtle mood change, small topic drift)
- 4-6: Moderate transitions (clear topic change, notable mood shift)
- 7-10: Major turning points (dramatic reversal, critical plot point, complete tone change)

If no significant transitions are found, return {{ "transition_points": [] }}.
""".strip()


def get_legal_prompt(segment: str) -> str:
    return f"""
You are a 'Legal Document Structuring Expert' for RAG chunking.

PRIMARY OBJECTIVE:
Return chunk boundary points that maximize retrieval precision for legal QA.

TEXT SEGMENT:
{segment}

ABSOLUTE RULES (must follow):
A) STRUCTURAL HEADINGS MUST BE BOUNDARIES.
   If you see any of these, treat them as a new chunk start:
   - Korean law headings: "제N조", "제N조의M", "제N장/절/관", "부칙", "별표"
   - English equivalents: "Article N", "Section N", "Chapter", "Part", "Schedule/Appendix"
   For EVERY detected new Article/Section heading (e.g., 제4조 -> 제4조의2),
   output a transition point with:
   - significance = 10
   - explanation mentions "STRUCTURAL HEADING"
   - start_text is the EXACT heading line as it appears in the text (do NOT paraphrase).

B) SIZE SAFETY (to avoid oversized chunks):
   Target chunk size: 900–1500 characters.
   Hard max (do not exceed): 2200 characters.
   If two consecutive structural headings would create an oversized chunk,
   you MUST add extra boundaries inside that range, using:
   - 항/호/목 markers, ①②③…, (1)(2)…,
   - numbered lists "1. 2. 3.",
   - provisos/conditions like "다만", "단서", "예외", "특례",
   - clause-type shifts (below).
   Any size-enforcement boundary should have significance 8–10.

C) CLAUSE-TYPE SHIFTS (often large even within same domain):
   Treat transitions between these legal functions as significant (usually 7–10):
   - Scope / What is taxed (과세대상/정의/요건/범위)
   - Liability / Who pays (납세의무자/연대납부/대리납부)
   - Calculation mechanics (과세표준/세율/가산/공제/한도/산식)
   - Procedure / Deadlines (신고/기한/절차/서류)
   - Jurisdiction / Authority (관할/세무서)
   - Exceptions (비과세/면제/특례/단서)

OUTPUT FORMAT:
Return ONE JSON object (no markdown):
{{
  "transition_points": [
    {{
      "start_text": "Exact quote where the NEW chunk begins (must match text exactly)",
      "topic_before": "Article/section + clause type BEFORE",
      "topic_after": "Article/section + clause type AFTER",
      "significance": <1-10 integer>,
      "explanation": "Reason: (1) structural heading OR (2) clause-type shift OR (3) size enforcement"
    }}
  ]
}}

CRITICAL VALIDATION (before final output):
- Every start_text MUST be an exact substring from the given segment.
- Prefer using heading lines as start_text because they match reliably.
- Do NOT invent text. If unsure, omit that point.
- Ensure all structural headings after the first are included as significance 10 boundaries.

If none, return {{ "transition_points": [] }}.
""".strip()
