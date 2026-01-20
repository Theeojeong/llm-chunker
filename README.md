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

## ✨ 왜 llm-chunker인가요?

기존 청커는 글자 수나 정규식으로 텍스트를 분할해서, 문장 중간에서 잘리는 경우가 많습니다. **llm-chunker**는 맥락을 이해합니다—법률 문서의 조항 경계, 소설의 감정 변화, 주제 전환 등을 감지합니다.

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
- OpenAI API 키

---

## 🚀 빠른 시작

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from llm_chunker import GenericChunker

chunker = GenericChunker()
chunks = chunker.split_text(your_text)  # list[str] 반환
```

---

## 📖 기본 예제

```python
from llm_chunker import GenericChunker

chunker = GenericChunker(
    model="gpt-4o",
    significance_threshold=7,  # 중요도 7 이상만 분할
    min_chunk_gap=200,         # 분할 지점 간 최소 거리
    verbose=True,              # 상세 로그 출력
    show_progress=True,        # 진행률 + 결과 출력
)

chunks = chunker.split_text(your_text)  # list[str]
```

---

## 📖 커스텀 프롬프트 예제

### 방법 1: PromptBuilder 사용

```python
from llm_chunker import GenericChunker, TransitionAnalyzer, PromptBuilder

# 도메인과 찾을 내용만 지정하면 프롬프트 자동 생성
prompt = PromptBuilder.create(
    domain="소설",
    find="감정 변화나 장면 전환", # 전환점 판정 기준을 상세히 기술
)

analyzer = TransitionAnalyzer(
    prompt_generator=prompt,
    model="gpt-4o",
)

chunker = GenericChunker(analyzer=analyzer)
chunks = chunker.split_text(novel_text)
```

**PromptBuilder.create() 파라미터:**

| 파라미터             | 타입  | 기본값               | 설명                 |
| -------------------- | ----- | -------------------- | -------------------- |
| `domain`             | `str` | `"text"`             | 분석할 텍스트 도메인 |
| `find`               | `str` | `"semantic changes"` | 찾을 전환점 유형     |
| `custom_instruction` | `str` | `None`               | 추가 지시사항        |

### 방법 2: 내장 프롬프트 사용 (법률 문서에 특화) 추천

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

추가 내장 프롬프트 업데이트 예정

### 방법 3: 커스텀 프롬프트 함수 직접 작성

예)

```python
from llm_chunker import GenericChunker, TransitionAnalyzer

def my_custom_prompt(segment: str) -> str:
    return f"""
You are a 'Legal Document Structuring Expert' for RAG chunking.

PRIMARY OBJECTIVE:
Return chunk boundary points that maximize retrieval precision for legal QA.

TEXT SEGMENT:
{segment}

ABSOLUTE RULES (must follow):
A) STRUCTURAL HEADINGS MUST BE BOUNDARIES.
   If you see any of these, treat them as a new chunk start:
   - Korean law headings: "제N조", "제N조의M", "제N장/절/관", "부칙", "별표"
   - English equivalents: "Article N", "Section N", "Chapter", "Part", "Schedule/Appendix"
   For EVERY detected new Article/Section heading (e.g., 제4조 -> 제4조의2),
   output a transition point with:
   - significance = 10
   - explanation mentions "STRUCTURAL HEADING"
   - start_text is the EXACT heading line as it appears in the text (do NOT paraphrase).

B) SIZE SAFETY (to avoid oversized chunks):
   Target chunk size: 900–1500 characters.
   Hard max (do not exceed): 2200 characters.
   If two consecutive structural headings would create an oversized chunk,
   you MUST add extra boundaries inside that range, using:
   - 항/호/목 markers, ①②③…, (1)(2)…,
   - numbered lists "1. 2. 3.",
   - provisos/conditions like "다만", "단서", "예외", "특례",
   - clause-type shifts (below).
   Any size-enforcement boundary should have significance 8–10.

C) CLAUSE-TYPE SHIFTS (often large even within same domain):
   Treat transitions between these legal functions as significant (usually 7–10):
   - Scope / What is taxed (과세대상/정의/요건/범위)
   - Liability / Who pays (납세의무자/연대납부/대리납부)
   - Calculation mechanics (과세표준/세율/가산/공제/한도/산식)
   - Procedure / Deadlines (신고/기한/절차/서류)
   - Jurisdiction / Authority (관할/세무서)
   - Exceptions (비과세/면제/특례/단서)

OUTPUT FORMAT:
Return ONE JSON object (no markdown):
{{
  "transition_points": [
    {{
      "start_text": "Exact quote where the NEW chunk begins (must match text exactly)",
      "topic_before": "Article/section + clause type BEFORE",
      "topic_after": "Article/section + clause type AFTER",
      "significance": <1-10 integer>,
      "explanation": "Reason: (1) structural heading OR (2) clause-type shift OR (3) size enforcement"
    }}
  ]
}}

CRITICAL VALIDATION (before final output):
- Every start_text MUST be an exact substring from the given segment.
- Prefer using heading lines as start_text because they match reliably.
- Do NOT invent text. If unsure, omit that point.
- Ensure all structural headings after the first are included as significance 10 boundaries.

If none, return {{ "transition_points": [] }}.
""".strip()

analyzer = TransitionAnalyzer(
    prompt_generator=my_custom_prompt,
    model="gpt-4o",
)

chunker = GenericChunker(analyzer=analyzer)
chunks = chunker.split_text(your_text)
```

---

## 📚 API 레퍼런스

### `GenericChunker`

| 파라미터                 | 타입                 | 기본값  | 설명                             |
| ------------------------ | -------------------- | ------- | -------------------------------- |
| `analyzer`               | `TransitionAnalyzer` | `None`  | 커스텀 분석기 (프롬프트/모델)    |
| `model`                  | `str`                | `None`  | OpenAI 모델명 (analyzer 없을 때) |
| `significance_threshold` | `int`                | `7`     | 최소 중요도 점수 (1-10)          |
| `min_chunk_gap`          | `int`                | `200`   | 분할 지점 간 최소 거리 (글자)    |
| `max_segment_size`       | `int`                | `5000`  | LLM에 보낼 세그먼트 크기         |
| `overlap_size`           | `int`                | `400`   | 세그먼트 간 오버랩 크기          |
| `verbose`                | `bool`               | `False` | 상세 로그 출력                   |
| `show_progress`          | `bool`               | `False` | 진행률 표시 + 청크 결과 출력     |

### `TransitionAnalyzer`

| 파라미터           | 타입                   | 기본값               | 설명               |
| ------------------ | ---------------------- | -------------------- | ------------------ |
| `prompt_generator` | `Callable[[str], str]` | `get_default_prompt` | 프롬프트 생성 함수 |
| `model`            | `str`                  | `None`               | OpenAI 모델명      |

---

## 🏗️ 작동 원리

```
┌─────────────────────────────────────────────────────────────┐
│                      긴 텍스트 입력                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 분할      LLM 컨텍스트 크기에 맞게 윈도우 분할            │
│              (max_segment_size, overlap_size 적용)          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 분석      LLM 기반 전환점 탐지                            │
│              (커스텀 프롬프트로 도메인 맞춤 분석)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 필터링    낮은 중요도 & 중복 포인트 제거                  │
│              (significance_threshold, min_chunk_gap 적용)   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 슬라이싱  검증된 전환점에서 텍스트 분할                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              [청크 1] [청크 2] [청크 3] ...
```

---

## 📄 라이선스

MIT License - [LICENSE](LICENSE) 참조

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

**더 나은 RAG 파이프라인을 위해 ❤️**

유용하셨다면 [⭐ 스타](https://github.com/Theeojeong/llm-chunker)를 눌러주세요!

</div>
