# LLM Chunker

[![PyPI version](https://badge.fury.io/py/llm-chunker.svg)](https://badge.fury.io/py/llm-chunker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/llm-chunker.svg)](https://pypi.org/project/llm-chunker/)

**LLM Chunker** is a semantic text splitting library that leverages Large Language Models (LLMs) to detect logical boundaries in documents. Unlike traditional chunkers that split by character count or regex, **LLM Chunker** understands the context—whether it's a shift in emotion, a new legal article, or a change in topic.

---

## 🌍 Language / 언어

- [**English**](#english)
- [**한국어 (Korean)**](#korean)

---

<div id="english"></div>

# English Description

## 🚀 Key Features

- **Semantic Intelligence**: Uses LLMs to find "turning points" in text where the meaning actually shifts.
- **Domain Adaptable**: Comes with specialized prompts for **Legal**, **General**, and **Narrative** texts.
- **Model Agnostic**: Built with a pluggable architecture. Use **OpenAI (default)**, **Ollama**, **Claude**, or any custom LLM function.
- **Context-Aware Overlap**: Intelligently manages overlap to preserve context across chunks.

## 📦 Installation

```bash
pip install llm-chunker
```

## 🛠 Usage

### 1. Basic Usage (OpenAI)

By default, `llm-chunker` uses OpenAI's models (`gpt-4o` or `gpt-3.5-turbo`).

```python
import os
from llm_chunker import GenericChunker

# 1. Set your API Key
os.environ["OPENAI_API_KEY"] = "sk-..."

# 2. Initialize Chunker
chunker = GenericChunker()

# 3. Split Text
long_text = "..."
chunks = chunker.split_text(long_text)

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ---")
    print(chunk)
```

### 2. Advanced: Legal Document Chunking

Use specialized prompts to detect legal sections (Articles, Definitions, Purposes).

```python
from llm_chunker import GenericChunker, TransitionAnalyzer
from llm_chunker.prompts import get_legal_prompt

# Initialize Analyzer with Legal Prompt
legal_analyzer = TransitionAnalyzer(prompt_generator=get_legal_prompt)
chunker = GenericChunker(analyzer=legal_analyzer)

chunks = chunker.split_text(legal_document_text)
```

### 3. Advanced: Using Local LLM (Ollama)

Save costs and ensure privacy by running completely locally with Ollama.

```python
import ollama
from llm_chunker import GenericChunker, TransitionAnalyzer

# Define custom caller for Ollama
def ollama_caller(prompt: str) -> str:
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Inject custom caller
local_analyzer = TransitionAnalyzer(
    llm_caller=ollama_caller
)

chunker = GenericChunker(analyzer=local_analyzer)
```

## 🏗 Architecture

The library operates in three stages:

1.  **Scanning**: The text is scanned in large windows (optimized for LLM context limits).
2.  **Analysis**: The LLM analyzes the text to find "transition points" based on the provided prompt (e.g., "Find where the legal topic changes").
3.  **Slicing**: The original text is sliced precisely at these detected points, ensuring logical continuity.

---

<div id="korean"></div>

# 한국어 설명 (Korean)

## 🚀 주요 기능

- **의미 기반 청킹 (Semantic Chunking)**: 단순 글자 수가 아닌, 주제나 맥락이 바뀌는 '전환점'을 파악하여 문서를 분할합니다.
- **도메인 특화 프롬프트**: 법률 문서(조항 구분), 소설(감정선 변화), 기술 문서 등 분야별 최적화된 프롬프트를 제공합니다.
- **유연한 백엔드 설정**: 기본적으로 **OpenAI**를 지원하며, **Ollama(로컬 LLM)**나 **Claude** 등 원하는 모델을 연결하여 사용할 수 있습니다.

## 📦 설치 방법

```bash
pip install llm-chunker
```

## 🛠 사용 방법

### 1. 기본 사용 (OpenAI)

별도 설정 없이 바로 OpenAI 모델을 사용하여 텍스트를 분석합니다.

```python
import os
from llm_chunker import GenericChunker

# 1. API 키 설정
os.environ["OPENAI_API_KEY"] = "sk-..."

# 2. 청커 초기화
chunker = GenericChunker()

# 3. 텍스트 분할
text = "매우 긴 텍스트..."
chunks = chunker.split_text(text)

for chunk in chunks:
    print(chunk)
```

### 2. 심화: 법률 문서 최적화

법률 문서의 '조(Article)', '항(Paragraph)' 구분을 정확히 인식하고 싶을 때 사용합니다.

```python
from llm_chunker import GenericChunker, TransitionAnalyzer
from llm_chunker.prompts import get_legal_prompt

# 법률 전용 분석기 생성
legal_analyzer = TransitionAnalyzer(prompt_generator=get_legal_prompt)
chunker = GenericChunker(analyzer=legal_analyzer)

chunks = chunker.split_text(legal_text)
```

### 3. 심화: 로컬 LLM 사용 (Ollama)

API 비용 없이 로컬에서 Llama3 등을 사용하여 처리할 수 있습니다.

```python
import ollama
from llm_chunker import GenericChunker, TransitionAnalyzer

# Ollama 호출 함수 정의
def my_ollama_caller(prompt: str) -> str:
    resp = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return resp["message"]["content"]

# 로컬 분석기 생성
local_analyzer = TransitionAnalyzer(
    llm_caller=my_ollama_caller
)

chunker = GenericChunker(analyzer=local_analyzer)
```

## 🏗 작동 원리

1.  **스캐닝 (Scanning)**: 전체 텍스트를 LLM 컨텍스트 윈도우에 맞는 크기로 훑습니다.
2.  **분석 (Analysis)**: LLM에게 현재 텍스트의 흐름이 바뀌는 지점(법적 조항 변경, 감정 변화 등)을 찾도록 요청합니다.
3.  **분할 (Slicing)**: LLM이 찾아낸 정확한 위치를 기반으로 원본 텍스트를 자릅니다. 이를 통해 문장이 중간에 잘리거나 문맥이 끊기는 현상을 방지합니다.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Star History

<a href="https://star-history.com/#Theeojeong/llm-chunker&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Theeojeong/llm-chunker&type=Date" />
 </picture>
</a>
