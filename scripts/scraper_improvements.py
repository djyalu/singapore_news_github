"""
스크래퍼 개선 사항 모음
기존 scraper.py에 통합할 수 있는 개선 함수들
"""

import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from text_processing import TextProcessor
from deduplication import ArticleDeduplicator

def extract_article_content_improved(url: str, soup: BeautifulSoup) -> Dict:
    """개선된 기사 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': datetime.now(),
        'raw_content': '',  # 원본 콘텐츠 보존
    }
    
    # 제목 추출 (개선)
    title_selectors = [
        'h1.headline',
        'h1[data-testid="headline"]',
        'h1[itemprop="headline"]',
        'meta[property="og:title"]',  # Open Graph 태그 활용
        '.article-headline h1',
        'article h1',
        'main h1',
        'h1'
    ]
    
    for selector in title_selectors:
        if selector.startswith('meta'):
            elem = soup.select_one(selector)
            if elem and elem.get('content'):
                article['title'] = TextProcessor.clean_menu_text(elem['content'])
                break
        else:
            elem = soup.select_one(selector)
            if elem:
                title_text = elem.get_text().strip()
                if len(title_text) > 10 and not is_menu_text(title_text):
                    article['title'] = TextProcessor.clean_menu_text(title_text)
                    break
    
    # 날짜 추출 (개선)
    date_selectors = [
        'time[datetime]',
        'meta[property="article:published_time"]',
        'meta[name="publish_date"]',
        '.publish-date',
        '.article-date',
        '[data-testid="publish-date"]'
    ]
    
    for selector in date_selectors:
        elem = soup.select_one(selector)
        if elem:
            date_str = elem.get('datetime') or elem.get('content') or elem.get_text()
            if date_str:
                try:
                    article['publish_date'] = parse_date_flexible(date_str)
                    break
                except:
                    continue
    
    # 본문 추출 (개선)
    content_selectors = [
        'div[itemprop="articleBody"]',
        'div[data-testid="article-body"]',
        '.article-content',
        '.story-content',
        '.content-body',
        'article[role="article"]',
        '.post-content',
        'main article',
        'article'
    ]
    
    # 불필요한 요소 제거
    remove_selectors = [
        'script', 'style', 'nav', 'header', 'footer', 'aside',
        '.social-share', '.advertisement', '.related-articles',
        '.newsletter-signup', '.comments', '.author-bio',
        '[class*="menu"]', '[class*="nav"]', '[id*="menu"]'
    ]
    
    for selector in remove_selectors:
        for elem in soup.select(selector):
            elem.decompose()
    
    # 콘텐츠 추출
    best_content = ""
    best_score = 0
    
    for selector in content_selectors:
        elem = soup.select_one(selector)
        if elem:
            # 단락 추출
            paragraphs = []
            for p in elem.find_all(['p', 'div'], recursive=True):
                # 중첩된 div 제외
                if p.name == 'div' and p.find('p'):
                    continue
                    
                text = p.get_text().strip()
                cleaned_text = TextProcessor.clean_menu_text(text)
                
                # 의미있는 단락인지 확인
                if len(cleaned_text) > 30 and not is_menu_text(cleaned_text):
                    paragraphs.append(cleaned_text)
            
            # 점수 계산 (단락 수와 총 길이 기반)
            content = TextProcessor.merge_paragraphs(paragraphs, max_length=2000)
            score = len(paragraphs) * 10 + len(content)
            
            if score > best_score:
                best_score = score
                best_content = content
                article['raw_content'] = '\n\n'.join(paragraphs)  # 원본 보존
    
    article['content'] = best_content
    return article

def parse_date_flexible(date_str: str) -> datetime:
    """유연한 날짜 파싱"""
    # ISO 형식
    if 'T' in date_str:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    # 일반적인 형식들
    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%d %b %Y',
        '%d %B %Y',
        '%B %d, %Y',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y年%m月%d日',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
            
    # 상대적 시간 (e.g., "2 hours ago")
    relative_patterns = {
        r'(\d+)\s*hours?\s*ago': lambda m: datetime.now() - timedelta(hours=int(m.group(1))),
        r'(\d+)\s*days?\s*ago': lambda m: datetime.now() - timedelta(days=int(m.group(1))),
        r'(\d+)\s*minutes?\s*ago': lambda m: datetime.now() - timedelta(minutes=int(m.group(1))),
        r'yesterday': lambda m: datetime.now() - timedelta(days=1),
        r'today': lambda m: datetime.now(),
    }
    
    for pattern, func in relative_patterns.items():
        match = re.search(pattern, date_str.lower())
        if match:
            return func(match)
            
    return datetime.now()

def create_summary_improved(article_data: Dict, settings: Dict) -> str:
    """개선된 요약 생성 - 문장 잘림 방지"""
    from ai_summary_free import translate_to_korean_summary_gemini, enhanced_keyword_summary
    
    # AI 요약 시도
    if settings.get('scrapingMethodOptions', {}).get('ai', {}).get('provider') == 'gemini':
        if os.environ.get('GOOGLE_GEMINI_API_KEY'):
            try:
                # 안전하게 자른 콘텐츠 전달
                safe_content = TextProcessor.safe_truncate(article_data['content'], 800)
                summary = translate_to_korean_summary_gemini(
                    article_data['title'],
                    safe_content
                )
                if summary:
                    return summary
            except Exception as e:
                print(f"Gemini API error: {e}")
    
    # 폴백: 향상된 키워드 요약
    # 원본 콘텐츠가 있으면 사용, 없으면 일반 콘텐츠 사용
    content_for_summary = article_data.get('raw_content', article_data['content'])
    
    # 첫 3개 문장만 추출하여 요약에 사용
    sentences = TextProcessor.extract_sentences(content_for_summary)
    summary_content = '. '.join(sentences[:3]) if sentences else content_for_summary[:500]
    
    return enhanced_keyword_summary(article_data['title'], summary_content)

def consolidate_articles_improved(articles_by_group: Dict[str, List[Dict]]) -> List[Dict]:
    """개선된 기사 통합 - 중복 제거 강화"""
    deduplicator = ArticleDeduplicator(similarity_threshold=0.85)
    consolidated_articles = []
    
    for group, group_articles in articles_by_group.items():
        if not group_articles:
            continue
        
        # 1. 그룹 내 중복 제거
        unique_articles = deduplicator.deduplicate_articles(group_articles)
        
        # 2. 최신순 정렬
        unique_articles.sort(
            key=lambda x: x.get('publish_date', datetime.now()),
            reverse=True
        )
        
        # 3. 상위 5개 선택 (3개에서 증가)
        selected_articles = unique_articles[:5]
        
        # 4. 그룹 요약 생성
        group_summary = {
            'group': group,
            'articles': selected_articles,
            'article_count': len(selected_articles),
            'total_found': len(group_articles),
            'duplicates_removed': len(group_articles) - len(unique_articles),
            'sites': list(set(article['site'] for article in selected_articles)),
            'timestamp': datetime.now().isoformat(),
            'scraping_method': 'traditional_improved'
        }
        
        consolidated_articles.append(group_summary)
    
    return consolidated_articles

def validate_and_fix_urls(sites: List[Dict]) -> List[Dict]:
    """사이트 URL 검증 및 수정"""
    import requests
    
    fixed_sites = []
    
    for site in sites:
        try:
            # URL 접근 가능한지 확인
            response = requests.head(site['url'], timeout=5, allow_redirects=True)
            
            # 리다이렉트된 경우 새 URL 사용
            if response.url != site['url']:
                print(f"URL redirected: {site['url']} -> {response.url}")
                site['url'] = response.url
                
            # HTTPS 강제
            if site['url'].startswith('http://'):
                site['url'] = site['url'].replace('http://', 'https://')
                
            fixed_sites.append(site)
            
        except Exception as e:
            print(f"Error checking {site['name']}: {e}")
            # 에러가 나도 일단 포함
            fixed_sites.append(site)
            
    return fixed_sites

# 메뉴 텍스트 판별 함수 (기존 함수 참조용)
def is_menu_text(text: str) -> bool:
    """개선된 메뉴 텍스트 판별"""
    if not text or len(text) < 5:
        return True
        
    menu_indicators = [
        # 명확한 메뉴 지표
        'sign in', 'log in', 'my account', 'my feed',
        'search menu', 'main menu', 'navigation',
        'subscribe', 'newsletter', 'follow us',
        
        # 섹션 나열
        'singapore indonesia malaysia thailand',
        'business sport lifestyle technology',
        'home news opinion features',
        
        # 기술적 요소
        'type landing_page', 'news id', 'article id',
        'javascript:', 'void(0)', 'return false',
        
        # 한글 메뉴
        '로그인', '계정', '메뉴', '검색',
        '구독', '뉴스레터', '최신 뉴스'
    ]
    
    text_lower = text.lower().strip()
    
    # 지표 매칭
    matches = sum(1 for indicator in menu_indicators if indicator in text_lower)
    if matches >= 2:  # 2개 이상 매치되면 메뉴
        return True
        
    # 단어 비율 체크
    words = text_lower.split()
    if len(words) > 0:
        short_words = [w for w in words if len(w) <= 3]
        if len(short_words) / len(words) > 0.7:  # 70% 이상이 짧은 단어
            return True
            
    # URL이나 특수문자가 너무 많은 경우
    special_chars = sum(1 for c in text if c in '|/:@#$%^&*')
    if len(text) > 0 and special_chars / len(text) > 0.2:
        return True
        
    return False