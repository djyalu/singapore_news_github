"""
하이브리드 스크래퍼 - 전통적 방식 + 최소한의 AI
일일 50개 할당량을 고려한 효율적인 스크래핑
"""
import json
import os
from datetime import datetime
from collections import defaultdict
from ai_scraper import ai_scraper

class HybridScraper:
    def __init__(self):
        self.daily_ai_calls = 0
        self.max_daily_ai_calls = 40  # 50개 중 10개는 여유분
        self.ai_call_log_file = 'data/ai_usage_log.json'
        self.load_ai_usage()
        
    def load_ai_usage(self):
        """오늘의 AI 사용량 로드"""
        if os.path.exists(self.ai_call_log_file):
            with open(self.ai_call_log_file, 'r') as f:
                log = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                self.daily_ai_calls = log.get(today, 0)
        
    def save_ai_usage(self):
        """AI 사용량 저장"""
        today = datetime.now().strftime('%Y-%m-%d')
        log = {}
        if os.path.exists(self.ai_call_log_file):
            with open(self.ai_call_log_file, 'r') as f:
                log = json.load(f)
        log[today] = self.daily_ai_calls
        
        # 7일 이상 된 로그 삭제
        cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        log = {k: v for k, v in log.items() 
               if datetime.strptime(k, '%Y-%m-%d').timestamp() > cutoff}
        
        with open(self.ai_call_log_file, 'w') as f:
            json.dump(log, f)
    
    def can_use_ai(self):
        """AI 사용 가능 여부 확인"""
        return self.daily_ai_calls < self.max_daily_ai_calls
    
    def use_ai_sparingly(self, func, *args, **kwargs):
        """AI를 제한적으로 사용"""
        if not self.can_use_ai():
            print(f"[HYBRID] Daily AI limit reached ({self.daily_ai_calls}/{self.max_daily_ai_calls})")
            return None
            
        result = func(*args, **kwargs)
        self.daily_ai_calls += 1
        self.save_ai_usage()
        print(f"[HYBRID] AI call used ({self.daily_ai_calls}/{self.max_daily_ai_calls})")
        return result
    
    def smart_content_filter(self, articles):
        """
        스마트 필터링 - AI를 최소한으로 사용
        1. 전통적 방식으로 대부분 필터링
        2. 애매한 케이스만 AI로 검증
        """
        filtered_articles = []
        uncertain_articles = []
        
        for article in articles:
            # 확실한 기사 (날짜 패턴 + 충분한 길이)
            if (len(article.get('content', '')) > 200 and 
                any(pattern in article.get('url', '') for pattern in ['/2024/', '/2025/', '/singapore/', '/asia/'])):
                filtered_articles.append(article)
            # 확실한 비기사 (너무 짧거나 메뉴 텍스트)
            elif (len(article.get('content', '')) < 50 or 
                  any(word in article.get('title', '').lower() for word in ['menu', 'login', 'search', 'subscribe'])):
                continue
            # 애매한 케이스
            else:
                uncertain_articles.append(article)
        
        # 애매한 케이스 중 상위 5개만 AI로 검증 (할당량 절약)
        if uncertain_articles and self.can_use_ai():
            for article in uncertain_articles[:5]:
                if self.can_use_ai():
                    # AI 검증 로직
                    is_valid = self.use_ai_sparingly(
                        self._verify_article_with_ai, 
                        article
                    )
                    if is_valid:
                        filtered_articles.append(article)
                else:
                    # AI 할당량 소진 시 보수적으로 판단
                    if len(article.get('content', '')) > 100:
                        filtered_articles.append(article)
        
        return filtered_articles
    
    def _verify_article_with_ai(self, article):
        """AI로 기사 검증 (실제 구현은 ai_scraper 사용)"""
        # 간단한 검증만 수행
        content = article.get('content', '')[:500]  # 처음 500자만
        prompt = f"Is this a news article? Answer YES or NO only: {content}"
        
        try:
            if ai_scraper.model:
                response = ai_scraper.model.generate_content(prompt)
                return 'YES' in response.text.upper()
        except:
            pass
        
        return False