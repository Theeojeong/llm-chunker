<div align="center">

# 🔪 LLM Chunker

**LLM 기반 의미론적 텍스트 분할 라이브러리**

[![PyPI version](https://badge.fury.io/py/llm-chunker.svg)](https://badge.fury.io/py/llm-chunker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

_글자 수가 아닌 의미 단위로 문서를 분할합니다._

[설치](#-설치) •
[빠른 시작](#-빠른-시작) •
[예제](#-예제) •
[API 레퍼런스](#-api-레퍼런스) •
[English](README.en.md)

</div>

---

## ✨ 왜 LLM Chunker인가?

기존 청커는 글자 수나 정규식으로 텍스트를 분할해서, 문장 중간에서 잘리는 경우가 많습니다. **LLM Chunker**는 맥락을 이해합니다—소설의 감정 변화, 법률 문서의 조항 경계, 팟캐스트의 주제 전환을 감지합니다.

| 기존 청킹          | LLM Chunker          |
| ------------------ | -------------------- |
| 글자 수로 분할     | 의미 단위로 분할     |
| 문장 중간에서 잘림 | 완전한 문맥 보존     |
| 일률적인 방식      | 도메인 맞춤 프롬프트 |

---

## 📦 설치

```bash
pip install llm-chunker
```

**요구사항:**

- Python 3.8+
- OpenAI API 키 (또는 로컬 LLM용 Ollama)

---

## 🚀 빠른 시작

```python
from llm_chunker import GenericChunker

import os
os.environ["OPENAI_API_KEY"] = "sk-..."

chunker = GenericChunker()
chunks = chunker.split_text(your_text)

for i, chunk in enumerate(chunks):
    print(f"[청크 {i+1}] {chunk[:100]}...")
```

---

## 📖 예제

### 모델 선택하기

```python
from llm_chunker import GenericChunker
from llm_chunker.analyzer import TransitionAnalyzer, create_openai_caller
from llm_chunker.prompts import get_default_prompt

# 방법 1: model 파라미터로 직접 지정
analyzer = TransitionAnalyzer(
    prompt_generator=get_default_prompt,
    model="gpt-4o"  # 또는 "gpt-5-nano", "gpt-3.5-turbo"
)

# 방법 2: 팩토리 함수 사용
analyzer = TransitionAnalyzer(
    prompt_generator=get_default_prompt,
    llm_caller=create_openai_caller("gpt-4o-mini")
)

chunker = GenericChunker(analyzer=analyzer)
```

### 법률 문서 청킹

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
    significance_threshold=6,  # 낮을수록 더 많이 분할
    min_chunk_gap=500          # 청크 간 최소 거리 (글자수)
)

chunks = chunker.split_text(legal_document)
```

### 로컬 LLM 사용 (Ollama)

```python
from llm_chunker import GenericChunker
from llm_chunker.analyzer import TransitionAnalyzer, create_ollama_caller

analyzer = TransitionAnalyzer(
    prompt_generator=get_default_prompt,
    llm_caller=create_ollama_caller("llama3")  # 또는 "mistral", "codellama"
)

chunker = GenericChunker(analyzer=analyzer)
```

### 커스텀 프롬프트 만들기

도메인에 맞는 분할 로직을 직접 정의할 수 있습니다:

```python
def podcast_prompt(segment: str) -> str:
    return f"""
    팟캐스트에서 주제가 바뀌는 지점을 찾으세요.

    텍스트: {segment}

    다음 JSON 형식으로 반환하세요:
    {{
      "transition_points": [
        {{
          "start_text": "주제가 바뀌는 정확한 텍스트",
          "topic_after": "새로운 주제명",
          "significance": 8
        }}
      ]
    }}
    """

analyzer = TransitionAnalyzer(prompt_generator=podcast_prompt)
chunker = GenericChunker(analyzer=analyzer)
```

---

## 📚 API 레퍼런스

### `GenericChunker`

| 파라미터                 | 타입                 | 기본값  | 설명                    |
| ------------------------ | -------------------- | ------- | ----------------------- |
| `analyzer`               | `TransitionAnalyzer` | `None`  | 커스텀 분석기           |
| `significance_threshold` | `int`                | `7`     | 최소 중요도 점수 (1-10) |
| `min_chunk_gap`          | `int`                | `200`   | 분할 지점 간 최소 거리  |
| `max_chunk_size`         | `int`                | `5000`  | 폴백 청크 크기          |
| `verbose`                | `bool`               | `False` | 상세 로그 출력          |

### `TransitionAnalyzer`

| 파라미터           | 타입       | 기본값 | 설명                   |
| ------------------ | ---------- | ------ | ---------------------- |
| `prompt_generator` | `Callable` | 필수   | LLM 프롬프트 생성 함수 |
| `model`            | `str`      | `None` | OpenAI 모델명          |
| `llm_caller`       | `Callable` | `None` | 커스텀 LLM 호출 함수   |

### 팩토리 함수

```python
# OpenAI
create_openai_caller(model="gpt-4o") -> Callable

# Ollama (로컬)
create_ollama_caller(model="llama3") -> Callable
```

---

## 🏗️ 작동 원리

```
┌─────────────────────────────────────────────────────────────┐
│                      긴 텍스트 입력                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 분할      LLM 컨텍스트 크기에 맞게 윈도우 분할 (~2600자)   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 분석      LLM이 전환점 감지                               │
│              "여기서 기쁨에서 슬픔으로 감정이 바뀜"           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 필터링    낮은 중요도 & 중복 포인트 제거                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 슬라이싱  검증된 전환점에서 텍스트 분할                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
               [청크 1] [청크 2] [청크 3] ...
```

---

## 📄 라이선스

MIT License - [LICENSE](LICENSE) 참조

---

<div align="center">

**더 나은 RAG 파이프라인을 위해 ❤️**

유용하셨다면 [⭐ 스타](https://github.com/Theeojeong/llm-chunker)를 눌러주세요!

</div>
