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
from llm_chunker import GenericChunker

# Set your API key
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

# Create chunker and split text
chunker = GenericChunker()
chunks = chunker.split_text(your_text)

for i, chunk in enumerate(chunks):
    print(f"[Chunk {i+1}] {chunk[:100]}...")
```

---

## 📖 Examples

### Choose Your Model

```python
from llm_chunker import GenericChunker
from llm_chunker.analyzer import TransitionAnalyzer, create_openai_caller

# Option 1: Specify model directly
analyzer = TransitionAnalyzer(
    prompt_generator=get_default_prompt,
    model="gpt-4o"  # or "gpt-5-nano", "gpt-3.5-turbo"
)

# Option 2: Use factory function
analyzer = TransitionAnalyzer(
    prompt_generator=get_default_prompt,
    llm_caller=create_openai_caller("gpt-4o-mini")
)

chunker = GenericChunker(analyzer=analyzer)
```

### Legal Documents

```python
from llm_chunker import GenericChunker
from llm_chunker.analyzer import TransitionAnalyzer
from llm_chunker.prompts import get_legal_prompt

analyzer = TransitionAnalyzer(
    prompt_generator=get_legal_prompt,
    model="gpt-4o"
)

chunker = GenericChunker(
    analyzer=analyzer,
    significance_threshold=6,  # Lower for more splits
    min_chunk_gap=500          # Minimum chars between splits
)

chunks = chunker.split_text(legal_document)
```

### Custom Prompts (PromptBuilder)

Use `PromptBuilder` to easily create custom prompts without writing functions manually:

```python
from llm_chunker import GenericChunker, TransitionAnalyzer, PromptBuilder

# Option 1: Use built-in presets
prompt = PromptBuilder.podcast(language="en")
chunker = GenericChunker(analyzer=TransitionAnalyzer(prompt_generator=prompt))

# Option 2: Create with custom options
prompt = PromptBuilder.create(
    domain="novel",           # podcast, novel, legal, news, meeting
    find="speaker changes",   # topic changes, emotional shifts, scene changes
    language="en",
    extra_fields=["speaker_name"]
)
```

**Available Presets:**

| Method                          | Use Case                |
| ------------------------------- | ----------------------- |
| `PromptBuilder.podcast()`       | Podcast topic changes   |
| `PromptBuilder.novel_speaker()` | Novel speaker changes   |
| `PromptBuilder.novel_scene()`   | Novel scene transitions |
| `PromptBuilder.meeting()`       | Meeting agenda changes  |

---

## 📚 API Reference

### `GenericChunker`

| Parameter                | Type                 | Default | Description                       |
| ------------------------ | -------------------- | ------- | --------------------------------- |
| `analyzer`               | `TransitionAnalyzer` | `None`  | Custom analyzer with prompt/model |
| `significance_threshold` | `int`                | `7`     | Min significance score (1-10)     |
| `min_chunk_gap`          | `int`                | `200`   | Min characters between splits     |
| `max_chunk_size`         | `int`                | `5000`  | Fallback chunk size               |
| `verbose`                | `bool`               | `False` | Enable detailed logging           |

### `TransitionAnalyzer`

| Parameter          | Type       | Default  | Description                        |
| ------------------ | ---------- | -------- | ---------------------------------- |
| `prompt_generator` | `Callable` | Required | Function that generates LLM prompt |
| `model`            | `str`      | `None`   | OpenAI model name                  |
| `llm_caller`       | `Callable` | `None`   | Custom LLM calling function        |

### Factory Functions

````python

```python
# OpenAI
create_openai_caller(model="gpt-4o") -> Callable
````

---

## 🏗️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Long Text                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. SEGMENT     Split into LLM-sized windows (~2600 chars)   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ANALYZE     LLM finds transition points                  │
│                "Here the mood shifts from joy to sadness"   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FILTER      Remove low-significance & duplicate points   │
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
