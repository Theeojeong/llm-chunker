from difflib import SequenceMatcher

def find_best_match(text: str, target: str, threshold: float = 0.8) -> int:
    """
    Find the best matching position for target in text using fuzzy matching.
    Falls back to fuzzy matching when exact match is not found (LLM hallucination tolerance).
    
    Optimized: Uses prefix filtering to reduce search space before full comparison.
    
    Args:
        text: The text to search in
        target: The string to search for
        threshold: Minimum similarity ratio (0.0 ~ 1.0)
    
    Returns:
        int: Position of best match, or -1 if not found
    """
    if not target:
        return -1
    
    # 1. Try exact match first (fastest)
    exact_pos = text.find(target)
    if exact_pos != -1:
        return exact_pos
    
    # 2. Try case-insensitive exact match
    lower_text = text.lower()
    lower_target = target.lower()
    case_insensitive_pos = lower_text.find(lower_target)
    if case_insensitive_pos != -1:
        return case_insensitive_pos
    
    # 3. Optimized fuzzy matching with prefix filtering
    target_len = len(target)
    if target_len < 5:
        # For very short targets, do simple sliding window
        return _sliding_window_match(text, target, threshold)
    
    # Use first few characters as prefix filter to narrow down candidates
    prefix_len = min(8, target_len // 2)
    prefix = target[:prefix_len].lower()
    
    # Find candidate positions where prefix matches (with some tolerance)
    candidates = []
    for i in range(len(text) - target_len + 1):
        window_prefix = text[i:i + prefix_len].lower()
        # Allow 1 character difference in prefix
        if _char_diff(window_prefix, prefix) <= 1:
            candidates.append(i)
    
    # If no candidates from prefix, fall back to sparse sampling
    if not candidates:
        # Sample every 10 characters
        candidates = list(range(0, len(text) - target_len + 1, 10))
    
    # Compare only at candidate positions
    best_pos, best_ratio = -1, 0
    for i in candidates:
        window = text[i:i + target_len]
        ratio = SequenceMatcher(None, window, target).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_pos = i
    
    return best_pos


def _char_diff(s1: str, s2: str) -> int:
    """Count character differences between two strings of same length."""
    return sum(1 for a, b in zip(s1, s2) if a != b)


def _sliding_window_match(text: str, target: str, threshold: float) -> int:
    """Simple sliding window for short targets."""
    target_len = len(target)
    best_pos, best_ratio = -1, 0
    
    for i in range(len(text) - target_len + 1):
        window = text[i:i + target_len]
        ratio = SequenceMatcher(None, window, target).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_pos = i
    
    return best_pos
