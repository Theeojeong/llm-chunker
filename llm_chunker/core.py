from typing import List, Tuple, Dict, Any, Optional
from .text_utils import split_text_into_processing_segments
from .analyzer import TransitionAnalyzer
from .prompts import get_default_prompt
from .fuzzy_match import find_best_match

# ── Default Constants (can be overridden in __init__) ──
DEFAULT_SIGNIFICANCE_THRESHOLD = 7
DEFAULT_MIN_CHUNK_GAP = 200
DEFAULT_FUZZY_MATCH_THRESHOLD = 0.8
DEFAULT_MAX_CHUNK_SIZE = 5000  # Fallback chunk size when no transitions found


class GenericChunker:
    def __init__(self, 
                 analyzer: Optional[TransitionAnalyzer] = None,
                 significance_threshold: int = DEFAULT_SIGNIFICANCE_THRESHOLD,
                 min_chunk_gap: int = DEFAULT_MIN_CHUNK_GAP,
                 fuzzy_match_threshold: float = DEFAULT_FUZZY_MATCH_THRESHOLD,
                 max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE):
        """
        Initialize the GenericChunker with configurable parameters.
        
        Args:
            analyzer: Instance of TransitionAnalyzer. 
                      If None, uses default settings (OpenAI/gpt-4o + default prompt).
            significance_threshold: Minimum significance score (1-10) for a transition point.
            min_chunk_gap: Minimum characters between chunk boundaries.
            fuzzy_match_threshold: Minimum similarity ratio for fuzzy text matching.
            max_chunk_size: Maximum chunk size for fallback when no transitions are found.
        """
        if analyzer is None:
            self.analyzer = TransitionAnalyzer(prompt_generator=get_default_prompt)
        else:
            self.analyzer = analyzer
        
        self.significance_threshold = significance_threshold
        self.min_chunk_gap = min_chunk_gap
        self.fuzzy_match_threshold = fuzzy_match_threshold
        self.max_chunk_size = max_chunk_size

    def split_text(self, text: str) -> List[str]:
        """
        Splits the text into chunks based on the configured transition logic.
        
        Returns:
            List[str]: A list of text chunks.
        """
        if not text:
            return []
            
        # 1. Find all transition points
        all_points = self._find_transition_points(text)
        
        # 2. Handle no transition points case with fallback
        if not all_points:
            return self._fallback_chunk(text)
        
        # 3. Slice the text based on these points
        chunks = []
        last_pos = 0
        
        for p in all_points:
            pos = p["position_in_full_text"]
            if pos > last_pos:
                chunk = text[last_pos:pos].strip()
                if chunk:
                    chunks.append(chunk)
                last_pos = pos
                
        # Last chunk
        final_chunk = text[last_pos:].strip()
        if final_chunk:
            chunks.append(final_chunk)
            
        return chunks
    
    def _fallback_chunk(self, text: str) -> List[str]:
        """
        Fallback chunking when no transition points are detected.
        Splits text into chunks of max_chunk_size, respecting sentence boundaries.
        """
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        for start in range(0, len(text), self.max_chunk_size):
            end = min(start + self.max_chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
        
        return chunks

    def _find_transition_points(self, text: str) -> List[Dict[str, Any]]:
        """
        Internal method to detect turning points with improved filtering.
        """
        points = []
        seg_idx = 0
        
        # Iterate over large segments to fit in LLM context
        for seg, seg_start in split_text_into_processing_segments(text):
            seg_idx += 1
            
            # Analyze segment with LLM
            analysis = self.analyzer.analyze_segment(seg)
            
            # Map relative positions to absolute positions
            for p in analysis.get("transition_points", []):
                snippet = p.get("start_text", "")[:50]
                if not snippet:
                    continue
                    
                # Use fuzzy matching to handle LLM hallucination
                rel_pos = find_best_match(seg, snippet, self.fuzzy_match_threshold)
                if rel_pos == -1:
                    continue
                
                abs_pos = seg_start + rel_pos
                
                # Duplicate check: skip if similar position already exists
                if any(abs(existing["position_in_full_text"] - abs_pos) < 50 for existing in points):
                    continue
                
                p["position_in_full_text"] = abs_pos
                points.append(p)

        # ── Filtering Pipeline ──
        
        # 1. Sort by position
        points.sort(key=lambda x: x["position_in_full_text"])
        
        # 2. Filter by significance
        high_sig_points = [p for p in points if p.get("significance", 0) >= self.significance_threshold]
        
        # 3. Filter by minimum gap
        filtered = []
        last_pos = -float("inf")
        
        for p in high_sig_points:
            pos = p["position_in_full_text"]
            
            if pos - last_pos >= self.min_chunk_gap:
                filtered.append(p)
                last_pos = pos
        
        return filtered
