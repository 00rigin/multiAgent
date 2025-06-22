"""
LLM 가드레일 시스템

입력 검증과 안전성을 위한 가드레일을 제공합니다.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from app.config.guardrail_patterns import (
    FORBIDDEN_PATTERNS,
    WARNING_PATTERNS,
    SPAM_PATTERNS,
    EMAIL_SPECIFIC_PATTERNS,
    CALENDAR_SPECIFIC_PATTERNS,
    SEARCH_SPECIFIC_PATTERNS,
    GUARDRAIL_CONFIG
)


@dataclass
class GuardrailResult:
    """가드레일 검사 결과"""
    is_safe: bool
    reason: str = ""
    blocked_keywords: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.blocked_keywords is None:
            self.blocked_keywords = []
        if self.suggestions is None:
            self.suggestions = []


class GuardrailSystem:
    """LLM 가드레일 시스템"""
    
    def __init__(self):
        # Config에서 패턴 가져오기
        self.forbidden_patterns = FORBIDDEN_PATTERNS
        self.warning_patterns = WARNING_PATTERNS
        self.spam_patterns = SPAM_PATTERNS
        
        # 설정값 가져오기
        self.spam_threshold = GUARDRAIL_CONFIG["spam_threshold"]
        self.warning_threshold = GUARDRAIL_CONFIG["warning_threshold"]
        self.response_templates = GUARDRAIL_CONFIG["response_templates"]
        self.suggestions = GUARDRAIL_CONFIG["suggestions"]
        
        # 이메일 특화 설정
        self.email_pattern = EMAIL_SPECIFIC_PATTERNS["email_pattern"]
        self.max_recipients = EMAIL_SPECIFIC_PATTERNS["max_recipients"]
        self.email_forbidden = EMAIL_SPECIFIC_PATTERNS["email_forbidden"]
        
        # 캘린더 특화 설정
        self.calendar_forbidden = CALENDAR_SPECIFIC_PATTERNS["calendar_forbidden"]
        
        # 검색 특화 설정
        self.search_forbidden = SEARCH_SPECIFIC_PATTERNS["search_forbidden"]
    
    def check_input_safety(self, text: str) -> GuardrailResult:
        """
        입력 텍스트의 안전성을 검사합니다.
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            GuardrailResult: 검사 결과
        """
        text_lower = text.lower()
        blocked_keywords = []
        
        # 금지 패턴 검사
        for pattern in self.forbidden_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                blocked_keywords.extend(matches)
        
        # 스팸 패턴 검사
        spam_matches = []
        for pattern in self.spam_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                spam_matches.extend(matches)
        
        # 경고 패턴 검사
        warning_matches = []
        for pattern in self.warning_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                warning_matches.extend(matches)
        
        # 결과 판정
        if blocked_keywords:
            return GuardrailResult(
                is_safe=False,
                reason="금지된 키워드가 포함되어 있습니다.",
                blocked_keywords=blocked_keywords,
                suggestions=self.suggestions["forbidden"]
            )
        
        if len(spam_matches) >= self.spam_threshold:
            return GuardrailResult(
                is_safe=False,
                reason="스팸/피싱 의심 키워드가 다수 포함되어 있습니다.",
                blocked_keywords=spam_matches,
                suggestions=self.suggestions["spam"]
            )
        
        if len(warning_matches) >= self.warning_threshold:
            return GuardrailResult(
                is_safe=True,
                reason="전문가 조언이 필요한 내용이 포함되어 있습니다.",
                blocked_keywords=warning_matches,
                suggestions=self.suggestions["warning"]
            )
        
        return GuardrailResult(
            is_safe=True,
            reason="안전한 입력입니다."
        )
    
    def check_email_safety(self, to: str, subject: str, body: str) -> GuardrailResult:
        """
        이메일 발송의 안전성을 검사합니다.
        
        Args:
            to: 수신자
            subject: 제목
            body: 내용
            
        Returns:
            GuardrailResult: 검사 결과
        """
        # 수신자 검증
        if not self._is_valid_email_list(to):
            return GuardrailResult(
                is_safe=False,
                reason=self.response_templates["email_invalid"],
                suggestions=self.suggestions["email"]
            )
        
        # 제목과 내용 검사
        subject_result = self.check_input_safety(subject)
        body_result = self.check_input_safety(body)
        
        if not subject_result.is_safe:
            return subject_result
        
        if not body_result.is_safe:
            return body_result
        
        # 이메일 특화 금지 키워드 검사
        email_text = f"{subject} {body}".lower()
        for pattern in self.email_forbidden:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                return GuardrailResult(
                    is_safe=False,
                    reason="이메일 특화 금지 키워드가 포함되어 있습니다.",
                    blocked_keywords=matches,
                    suggestions=self.suggestions["forbidden"]
                )
        
        # 대량 발송 방지
        recipient_count = len([email.strip() for email in to.split(',')])
        if recipient_count > self.max_recipients:
            return GuardrailResult(
                is_safe=False,
                reason=self.response_templates["email_bulk"].format(
                    max_recipients=self.max_recipients
                ),
                suggestions=[f"수신자를 {self.max_recipients}명 이하로 제한해주세요."]
            )
        
        return GuardrailResult(
            is_safe=True,
            reason="안전한 이메일입니다."
        )
    
    def check_calendar_safety(self, title: str, description: str) -> GuardrailResult:
        """
        캘린더 일정의 안전성을 검사합니다.
        
        Args:
            title: 일정 제목
            description: 일정 설명
            
        Returns:
            GuardrailResult: 검사 결과
        """
        # 기본 안전성 검사
        title_result = self.check_input_safety(title)
        description_result = self.check_input_safety(description)
        
        if not title_result.is_safe:
            return title_result
        
        if not description_result.is_safe:
            return description_result
        
        # 캘린더 특화 금지 키워드 검사
        calendar_text = f"{title} {description}".lower()
        for pattern in self.calendar_forbidden:
            matches = re.findall(pattern, calendar_text, re.IGNORECASE)
            if matches:
                return GuardrailResult(
                    is_safe=False,
                    reason="캘린더 특화 금지 키워드가 포함되어 있습니다.",
                    blocked_keywords=matches,
                    suggestions=self.suggestions["forbidden"]
                )
        
        return GuardrailResult(
            is_safe=True,
            reason="안전한 일정입니다."
        )
    
    def check_search_safety(self, query: str) -> GuardrailResult:
        """
        검색 쿼리의 안전성을 검사합니다.
        
        Args:
            query: 검색 쿼리
            
        Returns:
            GuardrailResult: 검사 결과
        """
        # 기본 안전성 검사
        basic_result = self.check_input_safety(query)
        
        if not basic_result.is_safe:
            return basic_result
        
        # 검색 특화 금지 키워드 검사
        query_lower = query.lower()
        for pattern in self.search_forbidden:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            if matches:
                return GuardrailResult(
                    is_safe=False,
                    reason="검색 특화 금지 키워드가 포함되어 있습니다.",
                    blocked_keywords=matches,
                    suggestions=self.suggestions["forbidden"]
                )
        
        return GuardrailResult(
            is_safe=True,
            reason="안전한 검색 쿼리입니다."
        )
    
    def _is_valid_email_list(self, email_list: str) -> bool:
        """
        이메일 주소 리스트의 유효성을 검사합니다.
        
        Args:
            email_list: 쉼표로 구분된 이메일 주소들
            
        Returns:
            bool: 유효성 여부
        """
        emails = [email.strip() for email in email_list.split(',')]
        
        for email in emails:
            if not re.match(self.email_pattern, email):
                return False
        
        return True
    
    def get_safe_response(self, reason: str, response_type: str = "forbidden") -> str:
        """
        안전하지 않은 요청에 대한 표준 응답을 반환합니다.
        
        Args:
            reason: 거부 이유
            response_type: 응답 타입 (forbidden, spam, warning)
            
        Returns:
            str: 표준 응답 메시지
        """
        template = self.response_templates.get(response_type, self.response_templates["forbidden"])
        return template.format(reason=reason)
    

# 전역 가드레일 시스템 인스턴스
guardrail_system = GuardrailSystem() 