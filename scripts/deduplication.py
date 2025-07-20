import re
from difflib import SequenceMatcher
from typing import List, Dict
import hashlib

class ArticleDeduplicator:
    """기사 중복 제거를 위한 유틸리티 클래스"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes = set()
        
    def normalize_text(self, text: str) -> str:
        """텍스트 정규화 - 비교를 위한 표준화"""
        # 소문자 변환
        text = text.lower()
        # 특수문자, 공백 정규화
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s가-힣]', '', text)
        return text.strip()
    
    def calculate_content_hash(self, title: str, content: str) -> str:
        """제목과 내용 기반 해시 생성"""
        normalized = self.normalize_text(f"{title} {content[:500]}")
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트의 유사도 계산 (0-1)"""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def is_duplicate(self, article: Dict, existing_articles: List[Dict]) -> bool:
        """기사가 기존 기사들과 중복인지 확인"""
        # 1. 해시 기반 빠른 체크
        content_hash = self.calculate_content_hash(
            article.get('title', ''), 
            article.get('content', '')
        )
        
        if content_hash in self.seen_hashes:
            return True
            
        # 2. 제목 유사도 체크
        for existing in existing_articles:
            title_similarity = self.calculate_similarity(
                article.get('title', ''),
                existing.get('title', '')
            )
            
            if title_similarity > self.similarity_threshold:
                return True
                
            # 3. 내용 유사도 체크 (제목이 다른 경우)
            if title_similarity > 0.5:  # 제목이 어느정도 비슷하면
                content_similarity = self.calculate_similarity(
                    article.get('content', '')[:500],
                    existing.get('content', '')[:500]
                )
                
                if content_similarity > self.similarity_threshold:
                    return True
        
        # 중복이 아니면 해시 저장
        self.seen_hashes.add(content_hash)
        return False
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """기사 목록에서 중복 제거"""
        unique_articles = []
        
        for article in articles:
            if not self.is_duplicate(article, unique_articles):
                unique_articles.append(article)
                
        return unique_articles