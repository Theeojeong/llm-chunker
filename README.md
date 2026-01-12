# LLM Chunker

A flexible, LLM-based text chunker capable of splitting documents based on semantic shifts, legal topics, or emotional flows.

## Features

- **Semantic Chunking**: Splits text where topics actually change, not just by token count.
- **Legal Document Support**: Specialized prompts for detecting "Purpose", "Definition", "Article" boundaries.
- **Pluggable Backend**: Supports OpenAI (ChatGPT) by default, but can be used with Ollama or any custom LLM function.

## Installation

```bash
pip install llm-chunker
```

## Quick Start

```python
import os
from llm_chunker import GenericChunker

# Ensure OPENAI_API_KEY is set
# os.environ["OPENAI_API_KEY"] = "sk-..."

chunker = GenericChunker()
text = "Section 1. Purpose... Section 2. Definitions..."

chunks = chunker.split_text(text)
for chunk in chunks:
    print("--- CHUNK ---")
    print(chunk)
```
