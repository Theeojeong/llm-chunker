<div align="center">

# 🔪 LLM Chunker

**Semantic text splitting powered by Large Language Models**

[![PyPI version](https://badge.fury.io/py/llm-chunker.svg)](https://badge.fury.io/py/llm-chunker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

_Split documents by meaning, not by character count._

[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Examples](#-examples) •
[API Reference](#-api-reference) •
[한국어](README.md)

</div>

---

## ✨ Why LLM Chunker?

Traditional chunkers split text by character count or regex patterns, often cutting sentences mid-thought. **LLM Chunker** understands context—detecting emotional shifts in novels, article boundaries in legal documents, or topic changes in podcasts.

| Traditional Chunking      | LLM Chunker                 |
| ------------------------- | --------------------------- |
| Splits by character count | Splits by semantic meaning  |
| Cuts sentences mid-word   | Preserves complete thoughts |
| One-size-fits-all         | Domain-specific prompts     |

---

## 📦 Installation

```bash
pip install llm-chunker
```

**Requirements:**

- Python 3.8+
- OpenAI API key

---

## 🚀 Quick Start

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from llm_chunker import GenericChunker

chunker = GenericChunker()
chunks = chunker.split_text(your_text)  # Returns list[str]
```

---

## 📖 Basic Example

```python
from llm_chunker import GenericChunker

chunker = GenericChunker(
    model="gpt-4o",
    significance_threshold=7,  # Only split at significance 7+
    min_chunk_gap=200,         # Min chars between splits
    verbose=True,              # Enable detailed logging
    show_progress=True,        # Show progress + chunk results
)

chunks = chunker.split_text(your_text)  # list[str]
```

---

## 📖 Custom Prompt Examples

### Method 1: Use PromptBuilder (Recommended)

```python
from llm_chunker import GenericChunker, TransitionAnalyzer, PromptBuilder

# Just specify domain and what to find - prompt is auto-generated
prompt = PromptBuilder.create(
    domain="novel",
    find="emotional shifts or scene changes",
)

analyzer = TransitionAnalyzer(
    prompt_generator=prompt,
    model="gpt-4o",
)

chunker = GenericChunker(analyzer=analyzer)
chunks = chunker.split_text(novel_text)
```

**PromptBuilder.create() Parameters:**

| Parameter            | Type  | Default              | Description                 |
| -------------------- | ----- | -------------------- | --------------------------- |
| `domain`             | `str` | `"text"`             | Domain of text to analyze   |
| `find`               | `str` | `"semantic changes"` | Type of transitions to find |
| `custom_instruction` | `str` | `None`               | Additional instructions     |

### Method 2: Use Built-in Prompts (Legal)

```python
from llm_chunker import GenericChunker, TransitionAnalyzer
from llm_chunker.prompts import get_legal_prompt

analyzer = TransitionAnalyzer(
    prompt_generator=get_legal_prompt,
    model="gpt-4o",
)

chunker = GenericChunker(analyzer=analyzer)
chunks = chunker.split_text(legal_document)
```

Additional built-in prompts to be updated

### Method 3: Write Custom Prompt Function

```python
from llm_chunker import GenericChunker, TransitionAnalyzer

def my_custom_prompt(segment: str) -> str:
    return f"""
Analyze the following text and identify points where the topic changes.

Text:
{segment}

Return JSON format:
{{
  "transition_points": [
    {{
      "start_text": "Exact quote where change begins",
      "topic_before": "Topic before this point",
      "topic_after": "Topic after this point",
      "significance": 1-10 integer,
      "explanation": "Brief explanation"
    }}
  ]
}}
""".strip()

analyzer = TransitionAnalyzer(
    prompt_generator=my_custom_prompt,
    model="gpt-4o",
)

chunker = GenericChunker(analyzer=analyzer)
chunks = chunker.split_text(your_text)
```

---

## 📚 API Reference

### `GenericChunker`

| Parameter                | Type                 | Default | Description                          |
| ------------------------ | -------------------- | ------- | ------------------------------------ |
| `analyzer`               | `TransitionAnalyzer` | `None`  | Custom analyzer (prompt/model)       |
| `model`                  | `str`                | `None`  | OpenAI model name (when no analyzer) |
| `significance_threshold` | `int`                | `7`     | Min significance score (1-10)        |
| `min_chunk_gap`          | `int`                | `200`   | Min characters between splits        |
| `max_segment_size`       | `int`                | `5000`  | Segment size for LLM processing      |
| `overlap_size`           | `int`                | `400`   | Overlap between segments             |
| `verbose`                | `bool`               | `False` | Enable detailed logging              |
| `show_progress`          | `bool`               | `False` | Show progress + chunk results        |

### `TransitionAnalyzer`

| Parameter          | Type                   | Default              | Description               |
| ------------------ | ---------------------- | -------------------- | ------------------------- |
| `prompt_generator` | `Callable[[str], str]` | `get_default_prompt` | Prompt generator function |
| `model`            | `str`                  | `None`               | OpenAI model name         |

---

## 🏗️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Long Text                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. SEGMENT     Split into LLM-sized windows                 │
│                (max_segment_size, overlap_size applied)     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ANALYZE     LLM finds transition points                  │
│                (Custom prompts for domain-specific analysis)│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FILTER      Remove low-significance & duplicate points   │
│                (significance_threshold, min_chunk_gap)      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. SLICE       Split text at validated transition points    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              [Chunk 1] [Chunk 2] [Chunk 3] ...
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## ⭐ Star History

<a href="https://star-history.com/#Theeojeong/llm-chunker&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date" />
 </picture>
</a>

---

<div align="center">

**Made with ❤️ for better RAG pipelines**

[⭐ Star this repo](https://github.com/Theeojeong/llm-chunker) if you find it useful!

</div>
