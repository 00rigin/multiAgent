from abc import ABC, abstractmethod
from typing import Any, Dict


class SearchInterface(ABC):
    """
    검색 기능을 위한 추상 인터페이스.
    다양한 검색 엔진(네이버, 구글, 빙 등)을 지원하기 위한 공통 인터페이스입니다.
    """
    
    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> str:
        """
        검색을 수행하고 결과를 반환합니다.
        
        Args:
            query: 검색 쿼리
            **kwargs: 추가 검색 옵션들
            
        Returns:
            검색 결과 문자열
        """
        pass 