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

### 4. Advanced: Writing Custom Prompts

You can define your own logic for splitting text (e.g., by speaker, by scene, or by timestamp) by writing a custom prompt generator.

**Important**: Your prompt **MUST** instruct the LLM to return a JSON object with a `transition_points` key. Each point must have a `start_text` field that exactly matches a snippet in the segment.

```python
from llm_chunker import GenericChunker, TransitionAnalyzer

def my_custom_prompt(segment: str) -> str:
    return f"""
    Analyze the text and find where a new speaker starts speaking.

    TEXT:
    {segment}

    Return JSON:
    {{
      "transition_points": [
        {{
          "start_text": "First 5-10 chars of the new speaker's sentence",
          "speaker": "Name of speaker",
          "significance": 10
        }}
      ]
    }}
    """

chunker = GenericChunker(analyzer=TransitionAnalyzer(prompt_generator=my_custom_prompt))
chunks = chunker.split_text(dialogue_text)
```

#### Example 2: Markdown Header Splitter

```python
def markdown_header_prompt(segment: str) -> str:
    return f"""
    Find where a new Markdown header (starts with #, ##, ###) appears.

    TEXT:
    {segment}

    Return JSON:
    {{
      "transition_points": [
        {{
          "start_text": "# Header Title",
          "significance": 10
        }}
      ]
    }}
    """
```

#### Example 3: Podcast Topic Switch

```python
def podcast_topic_prompt(segment: str) -> str:
    return f"""
    The following is a podcast transcript. Find where the host moves to a completely new topic or segment (e.g., "Moving on...", "Next topic...").

    TEXT:
    {segment}

    Return JSON:
    {{
      "transition_points": [
        {{
          "start_text": "Moving on to our next news item...",
          "topic_after": "Tech News Segment",
          "significance": 9
        }}
      ]
    }}
    """
```

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

### 4. 심화: 커스텀 프롬프트 작성법 (나만의 기준 만들기)

화자(Speaker)가 바뀔 때, 혹은 소설의 장면(Scene)이 전환될 때 등 나만의 기준으로 자르고 싶다면 프롬프트 함수를 직접 작성하세요.

**중요**: 프롬프트는 반드시 LLM에게 `transition_points` 키를 포함한 JSON을 반환하도록 지시해야 하며, 각 포인트는 원본 텍스트와 정확히 일치하는 `start_text`를 포함해야 합니다.

```python
from llm_chunker import GenericChunker, TransitionAnalyzer

def my_scene_prompt(segment: str) -> str:
    return f"""
    다음 소설 텍스트에서 '장면(Scene)'이 전환되는 지점을 찾으세요.
    시간이나 장소가 바뀌는 문장을 찾으면 됩니다.

    텍스트:
    {segment}

    다음 JSON 포맷으로 반환하세요 (마크다운 없이):
    {{
      "transition_points": [
        {{
          "start_text": "장면이 바뀌는 문장의 첫 5~10글자 (정확히 일치해야 함)",
          "reason": "장소가 거실에서 부엌으로 바뀜",
          "significance": 10
        }}
      ]
    }}
    """

# 내맘대로 프롬프트 적용
my_analyzer = TransitionAnalyzer(prompt_generator=my_scene_prompt)
chunker = GenericChunker(analyzer=my_analyzer)

chunks = chunker.split_text(novel_text)
```

#### 예시 2: 마크다운 헤더(Header) 기준 분할

```python
def markdown_header_prompt(segment: str) -> str:
    return f"""
    텍스트에서 마크다운 헤더(#, ##, ### 등)가 시작되는 지점을 모두 찾으세요.

    텍스트:
    {segment}

    JSON 반환:
    {{
      "transition_points": [
        {{
          "start_text": "## 2. 설치 방법",
          "significance": 10
        }}
      ]
    }}
    """
```

#### 예시 3: 팟캐스트/유튜브 주제 전환

```python
def podcast_topic_prompt(segment: str) -> str:
    return f"""
    다음 팟캐스트 대본에서 대화의 주제가 완전히 바뀌거나 새로운 코너로 넘어가는 지점을 찾으세요.
    (예: "자, 다음 주제로 넘어가 볼까요?", "이제 광고 듣고 오겠습니다" 등)

    텍스트:
    {segment}

    JSON 반환:
    {{
      "transition_points": [
        {{
          "start_text": "자, 그럼 이제 경제 뉴스를 살펴볼까요?",
          "topic_after": "경제 뉴스 코너",
          "significance": 9
        }}
      ]
    }}
    """
```

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
