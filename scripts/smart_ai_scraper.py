"""
스마트 AI 스크래퍼 - AI 호출을 최소화하는 전략
"""
import re
from typing import List, Dict, Set
from urllib.parse import urlparse

class SmartAIScraper:
    """AI 호출을 최소화하는 스마트 스크래퍼"""
    
    def __init__(self):
        # 사이트별 학습된 패턴 저장
        self.site_patterns = {
            'straitstimes.com': {
                'article_patterns': [r'/singapore/[^/]+', r'/asia/[^/]+', r'/world/[^/]+'],
                'exclude_patterns': ['/multimedia/', '/tags/', '/authors/']
            },
            'channelnewsasia.com': {
                'article_patterns': [r'/singapore/[^/]+-\d+', r'/asia/[^/]+-\d+'],
                'exclude_patterns': ['/watch/', '/brandstudio/']
            },
            'businesstimes.com.sg': {
                'article_patterns': [r'/[^/]+-\d+$'],
                'exclude_patterns': ['/opinion/', '/lifestyle/']
            }
        }
        
        # 이미 확인된 패턴 저장
        self.confirmed_patterns = set()
        self.rejected_patterns = set()
        
    def learn_from_ai_result(self, url: str, is_valid: bool):
        """AI 결과로부터 패턴 학습"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path
        
        # URL 패턴 추출
        # 숫자를 \d+로, 특정 문자열을 [^/]+로 변환
        pattern = re.sub(r'/\d+', r'/\\d+', path)
        pattern = re.sub(r'/[a-z0-9-]{10,}', r'/[^/]+', pattern)
        
        if is_valid:
            self.confirmed_patterns.add((domain, pattern))
        else:
            self.rejected_patterns.add((domain, pattern))
    
    def predict_url_validity(self, url: str) -> tuple[bool, float]:
        """
        학습된 패턴으로 URL 유효성 예측
        Returns: (is_valid, confidence)
        """
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path
        
        # 도메인별 패턴 확인
        if domain in self.site_patterns:
            patterns = self.site_patterns[domain]
            
            # 제외 패턴 확인
            for pattern in patterns['exclude_patterns']:
                if re.search(pattern, path):
                    return False, 0.9
            
            # 포함 패턴 확인
            for pattern in patterns['article_patterns']:
                if re.search(pattern, path):
                    return True, 0.8
        
        # 학습된 패턴 확인
        for learned_domain, pattern in self.confirmed_patterns:
            if domain == learned_domain and re.match(pattern, path):
                return True, 0.7
                
        for learned_domain, pattern in self.rejected_patterns:
            if domain == learned_domain and re.match(pattern, path):
                return False, 0.7
        
        # 기본 패턴
        if re.search(r'/\d{4}/\d{2}/\d{2}/', url):  # 날짜 패턴
            return True, 0.6
        
        return None, 0.0  # 확실하지 않음
    
    def get_ai_call_priority(self, urls: List[str]) -> List[tuple[str, float]]:
        """
        AI 호출 우선순위 결정
        확실하지 않은 URL만 AI로 검증
        """
        uncertain_urls = []
        
        for url in urls:
            is_valid, confidence = self.predict_url_validity(url)
            
            # 확실하지 않은 경우만 AI 검증 필요
            if confidence < 0.7:
                uncertain_urls.append((url, confidence))
        
        # 불확실성이 높은 순으로 정렬
        uncertain_urls.sort(key=lambda x: x[1])
        
        return uncertain_urls
    
    def should_use_ai(self, url: str) -> bool:
        """AI 사용 여부 결정"""
        _, confidence = self.predict_url_validity(url)
        return confidence < 0.7  # 70% 미만 확신도일 때만 AI 사용