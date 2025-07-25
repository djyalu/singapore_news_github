"""
사이트별 CSS 셀렉터 관리
각 사이트의 구조 변경에 유연하게 대응
"""

from typing import Dict, List
from datetime import datetime

class SiteSelectors:
    """사이트별 셀렉터 관리 클래스"""
    
    # 사이트별 셀렉터 정의
    SELECTORS = {
        'straitstimes.com': {
            'title': [
                'h1.headline',
                'h1[data-testid="headline"]',
                'meta[property="og:title"]',
                '.article-headline h1',
                'h1.display-3',  # 새로운 디자인
                'h1.display-4',  # 2025년 디자인
                '.st-article-headline',
                'h1'
            ],
            'content': [
                'div[data-testid="article-body"]',
                '.article-content',
                '.paywall-content',
                '.story-content',
                'div.content-body',
                'article[role="article"]',
                '.st-article-content',  # 2025년 추가
                '[class*="RichTextContainer"]',  # React 컴포넌트
                'div[class*="article__body"]'
            ],
            'date': [
                'time[datetime]',
                'meta[property="article:published_time"]',
                '.published-date',
                '[data-testid="publish-date"]'
            ],
            'links': [
                'a[href*="/singapore/"]',
                'a[href*="/asia/"]',
                'a[href*="/world/"]',
                'a[href*="/business/"]',
                'article a[href]',
                '.headline a[href]'
            ]
        },
        
        'channelnewsasia.com': {
            'title': [
                'h1.headline',
                'h1.article-title',
                'meta[property="og:title"]',
                '.h1--page-title',
                'h1'
            ],
            'content': [
                '.text-long',
                '.article-content',
                '.content__detail',
                'div[class*="article-body"]',
                '.story-content'
            ],
            'date': [
                'time[datetime]',
                '.article-publish-date',
                'meta[name="publish_date"]'
            ],
            'links': [
                'a[href*="/singapore/"]',
                'a[href*="/asia/"]',
                'a[href*="/world/"]',
                'a[href*="/business/"]',
                '.media__link',
                'h3 a[href]'
            ]
        },
        
        'businesstimes.com.sg': {
            'title': [
                'h1.headline',
                'h1.article-title',
                'meta[property="og:title"]',
                '.story-headline h1',
                'h1'
            ],
            'content': [
                '.article-content',
                '.story-content',
                '.content-body',
                'div[itemprop="articleBody"]',
                'article .text'
            ],
            'date': [
                'time[datetime]',
                '.article-date',
                'meta[property="article:published_time"]'
            ],
            'links': [
                'a[href*="/companies/"]',
                'a[href*="/banking-finance/"]',
                'a[href*="/economy/"]',
                'article a[href]',
                '.headline-link'
            ]
        },
        
        'mothership.sg': {
            'title': [
                'h1.title',
                'h1.article-title',
                'meta[property="og:title"]',
                '.content-title h1',
                'h1'
            ],
            'content': [
                '.content-article',
                '.article-body',
                '.post-content',
                'div.content',
                'article .text-content'
            ],
            'date': [
                'time[datetime]',
                '.date-published',
                'meta[property="article:published_time"]'
            ],
            'links': [
                'a.article-link',
                '.feed-item a[href]',
                'article a[href]',
                'h2 a[href]'
            ]
        },
        
        'todayonline.com': {
            'title': [
                'h1.article-title',
                'h1.node__title',
                'meta[property="og:title"]',
                '.article-header h1',
                'h1'
            ],
            'content': [
                '.article-body',
                '.node__content',
                '.field--name-body',
                'div[property="content:encoded"]',
                'article .content'
            ],
            'date': [
                'time[datetime]',
                '.article-date',
                'meta[property="article:published_time"]'
            ],
            'links': [
                'a.article-link',
                '.view-content a[href]',
                'h3 a[href]',
                'article a[href]'
            ]
        },
        
        # 정부 사이트들
        'moe.gov.sg': {
            'title': [
                'h1.page-title',
                'h1.content-title',
                'meta[property="og:title"]',
                '.title-row h1',
                'h1'
            ],
            'content': [
                '.content-area',
                '.page-content',
                '.field-content',
                'main .content',
                'article'
            ],
            'date': [
                '.date-display',
                'time[datetime]',
                '.posted-date'
            ],
            'links': [
                'a[href*="/news/"]',
                'a[href*="/press-releases/"]',
                'a[href*="/speeches/"]',
                '.news-item a[href]'
            ]
        }
    }
    
    @classmethod
    def get_selectors(cls, domain: str) -> Dict[str, List[str]]:
        """도메인에 맞는 셀렉터 반환"""
        # 도메인에서 주요 부분 추출
        for key in cls.SELECTORS:
            if key in domain:
                return cls.SELECTORS[key]
                
        # 기본 셀렉터
        return {
            'title': ['h1', 'meta[property="og:title"]', '.title', '.headline'],
            'content': ['article', '.content', '.article-body', 'main'],
            'date': ['time[datetime]', '.date', '.published'],
            'links': ['article a[href]', 'h2 a[href]', 'h3 a[href]', 'a.article-link']
        }
    
    @classmethod
    def update_selector(cls, domain: str, selector_type: str, new_selectors: List[str]):
        """셀렉터 업데이트 (실패시 대비)"""
        if domain not in cls.SELECTORS:
            cls.SELECTORS[domain] = {}
        
        if selector_type not in cls.SELECTORS[domain]:
            cls.SELECTORS[domain][selector_type] = []
            
        # 새 셀렉터를 앞에 추가 (우선순위)
        cls.SELECTORS[domain][selector_type] = new_selectors + cls.SELECTORS[domain][selector_type]
        
    @classmethod
    def test_selectors(cls, soup, domain: str) -> Dict[str, bool]:
        """셀렉터 테스트 - 어떤 셀렉터가 작동하는지 확인"""
        selectors = cls.get_selectors(domain)
        results = {}
        
        for selector_type, selector_list in selectors.items():
            results[selector_type] = False
            for selector in selector_list:
                try:
                    if selector.startswith('meta'):
                        elem = soup.select_one(selector)
                        if elem and elem.get('content'):
                            results[selector_type] = True
                            break
                    else:
                        elem = soup.select_one(selector)
                        if elem and elem.get_text().strip():
                            results[selector_type] = True
                            break
                except:
                    continue
                    
        return results