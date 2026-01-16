"""
프롬프트 빌더 - 커스텀 프롬프트를 생성하는 유틸리티
"""
from typing import Callable, List, Optional


class PromptBuilder:
    """
    커스텀 프롬프트를 생성하는 빌더 클래스.
    
    Examples:
        >>> prompt = PromptBuilder.create(
        ...     domain="법률 문서",
        ...     find="조항이 변경되는 부분",
        ...     language="ko"
        ... )
    """
    
    @classmethod
    def create(
        cls,
        domain: str = "text",
        find: str = "semantic changes",
        language: str = "en",
        extra_fields: Optional[List[str]] = None,
        custom_instruction: Optional[str] = None
    ) -> Callable[[str], str]:
        """
        커스텀 프롬프트 생성기를 반환합니다.
        
        Args:
            domain: 문서 도메인 (예: "팟캐스트 대본", "소설", "legal document")
            find: 감지할 대상 (예: "주제가 바뀌는 지점", "topic changes")
            language: 언어 (ko, en) - 템플릿 언어 결정
            extra_fields: JSON 결과에 추가할 필드 목록
            custom_instruction: 프롬프트 하단에 추가할 지시사항
            
        Returns:
            Callable[[str], str]: 프롬프트 생성 함수
        """
        # 추가 필드 JSON 생성
        extra_json = ""
        if extra_fields:
            extra_json = ",\n          ".join([f'"{field}": "..."' for field in extra_fields])
            extra_json = f",\n          {extra_json}"
        
        # 언어별 프롬프트 템플릿
        if language == "ko":
            def prompt_generator(segment: str) -> str:
                prompt = f"""다음 {domain}에서 {find}을(를) 찾으세요.

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
                prompt = f"""Analyze the following {domain} and find {find}.

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
