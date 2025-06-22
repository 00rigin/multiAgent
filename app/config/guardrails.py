"""
LLM 가드레일 시스템

입력 검증과 안전성을 위한 가드레일을 제공합니다.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


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
        # 금지 키워드 패턴
        self.forbidden_patterns = [
            # 개인정보 관련
            r'\b(주민번호|주민등록번호|주민등록번호앞자리|주민등록번호뒤자리)\b',
            r'\b(신용카드|카드번호|카드번호앞자리|카드번호뒤자리)\b',
            r'\b(계좌번호|은행계좌|계좌정보)\b',
            r'\b(비밀번호|패스워드|password|pw|pwd)\b',
            
            # 불법/유해 내용
            r'\b(마약|대마|코카인|헤로인|암페타민)\b',
            r'\b(자살|자해|목매달기|약물중독)\b',
            r'\b(테러|폭탄|폭발물|무기제조)\b',
            r'\b(해킹|크래킹|불법침입|바이러스제조)\b',
            
            # 성적/외설적 내용
            r'\b(포르노|야동|성인영상|음란물)\b',
            r'\b(성매매|매춘|창녀|남창)\b',
            
            # 폭력/차별
            r'\b(살인|폭력|구타|폭행)\b',
            r'\b(인종차별|성차별|장애인차별|연령차별)\b',
            r'\b(혐오|증오|비하|모욕)\b',
        ]
        
        # 경고 키워드 패턴 (더 세밀한 검사 필요)
        self.warning_patterns = [
            # 의학적 조언
            r'\b(진단|처방|약물|치료방법)\b',
            r'\b(병원|의사|약사|의료진)\b',
            
            # 법률 조언
            r'\b(소송|고소|고발|법적조치)\b',
            r'\b(변호사|법무사|법원|재판)\b',
            
            # 금융 조언
            r'\b(투자|주식|부동산|재테크)\b',
            r'\b(대출|이자|금리|수익률)\b',
        ]
        
        # 스팸/피싱 패턴
        self.spam_patterns = [
            r'\b(당첨|상금|로또|복권당첨)\b',
            r'\b(상속|유산|돈|재산)\b',
            r'\b(비밀|기밀|특별|한정)\b',
            r'\b(무료|공짜|할인|특가)\b',
        ]
    
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
                suggestions=["안전한 주제로 대화를 이어가주세요."]
            )
        
        if len(spam_matches) >= 2:  # 스팸 패턴이 2개 이상
            return GuardrailResult(
                is_safe=False,
                reason="스팸/피싱 의심 키워드가 다수 포함되어 있습니다.",
                blocked_keywords=spam_matches,
                suggestions=["정상적인 요청으로 다시 시도해주세요."]
            )
        
        if warning_matches:
            return GuardrailResult(
                is_safe=True,
                reason="전문가 조언이 필요한 내용이 포함되어 있습니다.",
                blocked_keywords=warning_matches,
                suggestions=["전문가와 상담하시는 것을 권장합니다."]
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
                reason="유효하지 않은 이메일 주소가 포함되어 있습니다.",
                suggestions=["올바른 이메일 주소를 입력해주세요."]
            )
        
        # 제목과 내용 검사
        subject_result = self.check_input_safety(subject)
        body_result = self.check_input_safety(body)
        
        if not subject_result.is_safe:
            return subject_result
        
        if not body_result.is_safe:
            return body_result
        
        # 대량 발송 방지
        recipient_count = len([email.strip() for email in to.split(',')])
        if recipient_count > 10:
            return GuardrailResult(
                is_safe=False,
                reason="대량 이메일 발송은 제한됩니다.",
                suggestions=["수신자를 10명 이하로 제한해주세요."]
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
        title_result = self.check_input_safety(title)
        description_result = self.check_input_safety(description)
        
        if not title_result.is_safe:
            return title_result
        
        if not description_result.is_safe:
            return description_result
        
        return GuardrailResult(
            is_safe=True,
            reason="안전한 일정입니다."
        )
    
    def _is_valid_email_list(self, email_list: str) -> bool:
        """
        이메일 주소 리스트의 유효성을 검사합니다.
        
        Args:
            email_list: 쉼표로 구분된 이메일 주소들
            
        Returns:
            bool: 유효성 여부
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        emails = [email.strip() for email in email_list.split(',')]
        
        for email in emails:
            if not re.match(email_pattern, email):
                return False
        
        return True
    
    def get_safe_response(self, reason: str) -> str:
        """
        안전하지 않은 요청에 대한 표준 응답을 반환합니다.
        
        Args:
            reason: 거부 이유
            
        Returns:
            str: 표준 응답 메시지
        """
        return f"죄송합니다. {reason} 안전상의 이유로 해당 요청을 처리할 수 없습니다."


# 전역 가드레일 시스템 인스턴스
guardrail_system = GuardrailSystem() 