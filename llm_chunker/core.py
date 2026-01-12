from typing import List, Tuple, Dict, Any, Optional
from .text_utils import split_text_into_processing_segments
from .analyzer import TransitionAnalyzer
from .prompts import get_default_prompt

class GenericChunker:
    def __init__(self, analyzer: Optional[TransitionAnalyzer] = None):
        """
        Args:
            analyzer: Instance of TransitionAnalyzer. 
                      If None, uses default settings (Ollama/llama3 + default prompt).
        """
        if analyzer is None:
            # Default setup
            self.analyzer = TransitionAnalyzer(prompt_generator=get_default_prompt)
        else:
            self.analyzer = analyzer

    def split_text(self, text: str) -> List[str]:
        """
        Splits the text into chunks based on the configured transition logic.
        
        Returns:
            List[str]: A list of text chunks.
        """
        if not text:
            return []
            
        # 1. First, find all transition points
        all_points = self._find_transition_points(text)
        
        # 2. Slice the text based on these points
        chunks = []
        last_pos = 0
        
        for p in all_points:
            pos = p["position_in_full_text"]
            # Avoid empty slices or very small fragments if desired
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

    def _find_transition_points(self, text: str) -> List[Dict[str, Any]]:
        """
        Internal method to detecting turning points.
        """
        points = []
        seg_idx = 0
        
        # Iterate over large segments to fit in LLM context
        for seg, seg_start in split_text_into_processing_segments(text):
            seg_idx += 1
            # print(f"Processing segment {seg_idx}...")
            
            # Analyze segment with LLM
            analysis = self.analyzer.analyze_segment(seg)
            
            # Map relative positions to absolute positions
            for p in analysis.get("transition_points", []):
                snippet = p.get("start_text", "")[:50]
                if not snippet:
                    continue
                    
                # Find exact position of the snippet in the segment
                rel_pos = seg.find(snippet)
                if rel_pos != -1:
                    p["position_in_full_text"] = seg_start + rel_pos
                    points.append(p)
                else:
                    # Fallback: if snippet not found exact match (due to LLM hallucination), 
                    # one might try fuzzy match. For now, skip.
                    pass

        # Sort and Filter (simple logic: deduplicate close points)
        points.sort(key=lambda x: x["position_in_full_text"])
        
        # Filter by significance first
        high_sig_points = [p for p in points if p.get("significance", 0) >= 7]
        
        filtered = []
        last_pos = -9999
        min_gap = 200 # Minimum characters between chunks
        
        for p in high_sig_points:
            pos = p["position_in_full_text"]
            
            if pos - last_pos >= min_gap:
                filtered.append(p)
                last_pos = pos
                
        return filtered
