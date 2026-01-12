# LLM Chunker

[![PyPI version](https://badge.fury.io/py/llm-chunker.svg)](https://badge.fury.io/py/llm-chunker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LLM Chunker** is a flexible, LLM-based text chunker capable of splitting documents based on semantic shifts, legal topics, or emotional flows.  
**LLM Chunker**는단순 텍스트 길이가 아닌, 의미의 변화, 법적 조항, 또는 감정의 흐름을 파악하여 문서를 논리적으로 분할해주는 도구입니다.

---

## 🌍 Language / 언어

- [English](#english)
- [한국어 (Korean)](#korean)

---

<a name="english"></a>

## English

### Features

- **Semantic Chunking**: Splits text where topics actually change, not just by token count.
- **Legal Document Support**: Specialized prompts for detecting "Purpose", "Definition", "Article" boundaries.
- **Pluggable Backend**: Supports OpenAI (ChatGPT) by default, but can be used with Ollama or any custom LLM function.

### Installation

```bash
pip install llm-chunker
```

### Quick Start

```python
import os
from llm_chunker import GenericChunker

# Ensure OPENAI_API_KEY is set in your environment
# os.environ["OPENAI_API_KEY"] = "sk-..."

# Initialize with default settings (OpenAI GPT-4o)
chunker = GenericChunker()

text = """
Section 1. Purpose
The purpose of this agreement is to...
(content continues)

Section 2. Definitions
For the purposes of this agreement, the following terms...
(content continues)
"""

# Split text based on logical sections
chunks = chunker.split_text(text)

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ---")
    print(chunk)
```

---

<a name="korean"></a>

## 한국어 (Korean)

### 주요 기능

- **의미 기반 청킹 (Semantic Chunking)**: 단순 글자 수가 아닌, 주제나 맥락이 바뀌는 지점을 파악하여 문서를 분할합니다.
- **법률 문서 최적화**: "목적", "정의", "조항" 등 법률 문서 특유의 구조적 변화를 감지하는 전용 프롬프트를 제공합니다.
- **유연한 백엔드 설정**: 기본적으로 OpenAI 를 지원하며, Ollama나 사용자 정의 LLM 함수도 손쉽게 연결할 수 있습니다.

### 설치 방법

```bash
pip install llm-chunker
```

### 사용 예시

```python
import os
from llm_chunker import GenericChunker

# 환경 변수에 OPENAI_API_KEY가 설정되어 있어야 합니다.
# os.environ["OPENAI_API_KEY"] = "sk-..."

# 기본 설정(OpenAI GPT-4o)으로 청커 초기화
chunker = GenericChunker()

text = """
제1조(목적)
이 법은 대한민국 헌법에 따라... (내용)

제2조(정의)
이 법에서 사용하는 용어의 뜻은 다음과 같다... (내용)
"""

# 논리적 구간에 따라 텍스트 분할
chunks = chunker.split_text(text)

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ---")
    print(chunk)
```

---

## License

This project is licensed under the MIT License.

## Star History

<a href="https://star-history.com/#Theeojeong/llm-chunker&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date" />
 </picture>
</a>
