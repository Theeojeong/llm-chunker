"""
프롬프트 빌더 - 커스텀 프롬프트를 쉽게 생성하는 유틸리티
"""
from typing import Callable, List, Optional


class PromptBuilder:
    """
    커스텀 프롬프트를 쉽게 생성하는 빌더 클래스.
    
    Examples:
        # 팟캐스트 주제 변경 감지
        >>> prompt = PromptBuilder.create(
        ...     domain="podcast",
        ...     find="topic changes",
        ...     language="ko"
        ... )
        >>> chunker = GenericChunker(analyzer=TransitionAnalyzer(prompt_generator=prompt))
        
        # 소설 화자 변경 감지
        >>> prompt = PromptBuilder.create(
        ...     domain="novel",
        ...     find="speaker changes",
        ...     extra_fields=["speaker_name"]
        ... )
    """
    
    # 도메인별 기본 설명
    DOMAIN_DESCRIPTIONS = {
        "podcast": {
            "ko": "팟캐스트 대본",
            "en": "podcast transcript"
        },
        "novel": {
            "ko": "소설 텍스트",
            "en": "novel text"
        },
        "legal": {
            "ko": "법률 문서",
            "en": "legal document"
        },
        "news": {
            "ko": "뉴스 기사",
            "en": "news article"
        },
        "meeting": {
            "ko": "회의록",
            "en": "meeting transcript"
        },
        "general": {
            "ko": "텍스트",
            "en": "text"
        }
    }
    
    # 감지 대상별 설명
    FIND_DESCRIPTIONS = {
        "topic changes": {
            "ko": "주제가 바뀌는 지점",
            "en": "points where the topic changes"
        },
        "speaker changes": {
            "ko": "화자가 바뀌는 지점",
            "en": "points where the speaker changes"
        },
        "emotional shifts": {
            "ko": "감정이 바뀌는 지점",
            "en": "points where the emotional tone shifts"
        },
        "scene changes": {
            "ko": "장면이 바뀌는 지점",
            "en": "points where the scene changes"
        },
        "section breaks": {
            "ko": "섹션이 나뉘는 지점",
            "en": "points where a new section begins"
        }
    }
    
    @classmethod
    def create(
        cls,
        domain: str = "general",
        find: str = "topic changes",
        language: str = "en",
        extra_fields: Optional[List[str]] = None,
        custom_instruction: Optional[str] = None
    ) -> Callable[[str], str]:
        """
        커스텀 프롬프트 생성기를 반환합니다.
        
        Args:
            domain: 문서 도메인 (podcast, novel, legal, news, meeting, general)
            find: 감지할 대상 (topic changes, speaker changes, emotional shifts, scene changes, section breaks)
            language: 언어 (ko, en)
            extra_fields: JSON에 추가할 필드 목록 (예: ["speaker_name", "topic_after"])
            custom_instruction: 추가 지시사항
            
        Returns:
            Callable[[str], str]: 프롬프트 생성 함수
        """
        # 도메인 설명 가져오기
        if domain in cls.DOMAIN_DESCRIPTIONS:
            domain_desc = cls.DOMAIN_DESCRIPTIONS[domain]
            domain_text = domain_desc.get(language, domain_desc["en"])
        else:
            # 미리 정의되지 않은 경우 입력값 그대로 사용
            domain_text = domain
        
        # 감지 대상 설명 가져오기
        if find in cls.FIND_DESCRIPTIONS:
            find_desc = cls.FIND_DESCRIPTIONS[find]
            find_text = find_desc.get(language, find_desc["en"])
        else:
            # 미리 정의되지 않은 경우 입력값 그대로 사용
            find_text = find
        
        # 추가 필드 JSON 생성
        extra_json = ""
        if extra_fields:
            extra_json = ",\n          ".join([f'"{field}": "..."' for field in extra_fields])
            extra_json = f",\n          {extra_json}"
        
        # 언어별 프롬프트 템플릿
        if language == "ko":
            def prompt_generator(segment: str) -> str:
                prompt = f"""다음 {domain_text}에서 {find_text}을 찾으세요.

텍스트:
{segment}

다음 JSON 형식으로 반환하세요 (마크다운 없이):
{{
  "transition_points": [
    {{
      "start_text": "변화가 시작되는 정확한 텍스트 (5-15자)",
      "significance": 8{extra_json}
    }}
  ]
}}

중요도 점수 기준:
- 1-3: 미미한 변화
- 4-6: 보통 변화
- 7-10: 중요한 전환점"""
                
                if custom_instruction:
                    prompt += f"\n\n추가 지시: {custom_instruction}"
                
                return prompt
        else:
            def prompt_generator(segment: str) -> str:
                prompt = f"""Analyze the following {domain_text} and find {find_text}.

TEXT:
{segment}

Return JSON (no markdown):
{{
  "transition_points": [
    {{
      "start_text": "Exact text where change occurs (5-15 chars)",
      "significance": 8{extra_json}
    }}
  ]
}}

Significance scoring:
- 1-3: Minor shifts
- 4-6: Moderate changes
- 7-10: Major transitions"""
                
                if custom_instruction:
                    prompt += f"\n\nAdditional instruction: {custom_instruction}"
                
                return prompt
        
        return prompt_generator
    
    @classmethod
    def podcast(cls, language: str = "ko") -> Callable[[str], str]:
        """팟캐스트 주제 변경 감지용 프롬프트"""
        return cls.create(
            domain="podcast",
            find="topic changes",
            language=language,
            extra_fields=["topic_after"]
        )
    
    @classmethod
    def novel_speaker(cls, language: str = "ko") -> Callable[[str], str]:
        """소설 화자 변경 감지용 프롬프트"""
        return cls.create(
            domain="novel",
            find="speaker changes",
            language=language,
            extra_fields=["speaker_name"]
        )
    
    @classmethod
    def novel_scene(cls, language: str = "ko") -> Callable[[str], str]:
        """소설 장면 전환 감지용 프롬프트"""
        return cls.create(
            domain="novel",
            find="scene changes",
            language=language,
            extra_fields=["location", "time"]
        )
    
    @classmethod
    def meeting(cls, language: str = "ko") -> Callable[[str], str]:
        """회의록 주제 변경 감지용 프롬프트"""
        return cls.create(
            domain="meeting",
            find="topic changes",
            language=language,
            extra_fields=["agenda_item"]
        )
