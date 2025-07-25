"""
사이트별 접근 전략 모듈
각 뉴스 사이트의 특성에 맞는 접근 방법 정의
"""
import random
import time

class SiteAccessStrategy:
    """사이트별 맞춤 접근 전략"""
    
    # 브라우저별 User-Agent 목록
    USER_AGENTS = {
        'desktop_chrome': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ],
        'desktop_firefox': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0'
        ],
        'desktop_safari': [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ],
        'mobile': [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
        ],
        'bot_friendly': [
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
        ]
    }
    
    # 사이트별 전략
    SITE_STRATEGIES = {
        'straitstimes.com': {
            'user_agent_type': 'desktop_chrome',
            'delay_range': (2, 4),
            'cookies': {
                'gdpr_consent': 'accepted',
                'subscription': 'free_tier'
            },
            'headers': {
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site'
            },
            'retry_count': 3,
            'use_session': True
        },
        'channelnewsasia.com': {
            'user_agent_type': 'desktop_chrome',
            'delay_range': (1, 3),
            'headers': {
                'Referer': 'https://www.channelnewsasia.com/',
                'X-Requested-With': 'XMLHttpRequest'
            },
            'retry_count': 2,
            'use_session': True
        },
        'businesstimes.com.sg': {
            'user_agent_type': 'desktop_chrome',
            'delay_range': (2, 4),
            'cookies': {
                'consent': 'yes'
            },
            'headers': {
                'Referer': 'https://www.businesstimes.com.sg/'
            },
            'retry_count': 3,
            'use_session': True
        },
        'mothership.sg': {
            'user_agent_type': 'mobile',  # Mothership은 모바일 UA가 더 잘 작동
            'delay_range': (1, 2),
            'headers': {
                'Referer': 'https://mothership.sg/',
                'X-Forwarded-For': f'103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'  # 싱가포르 IP 범위
            },
            'retry_count': 2,
            'use_session': False
        },
        'yahoo.com': {
            'user_agent_type': 'desktop_chrome',
            'delay_range': (1, 2),
            'headers': {
                'Referer': 'https://sg.yahoo.com/'
            },
            'retry_count': 2,
            'use_session': True
        },
        'todayonline.com': {
            'user_agent_type': 'desktop_firefox',
            'delay_range': (2, 3),
            'headers': {
                'Referer': 'https://www.todayonline.com/'
            },
            'retry_count': 2,
            'use_session': True
        },
        'theindependent.sg': {
            'user_agent_type': 'desktop_chrome',
            'delay_range': (1, 2),
            'headers': {
                'Referer': 'https://theindependent.sg/'
            },
            'retry_count': 2,
            'use_session': False
        }
    }
    
    @classmethod
    def get_strategy(cls, url):
        """URL에 따른 접근 전략 반환"""
        domain = cls._extract_domain(url)
        
        # 사이트별 전략 찾기
        for site_domain, strategy in cls.SITE_STRATEGIES.items():
            if site_domain in domain:
                return cls._prepare_strategy(strategy, domain)
        
        # 기본 전략
        return cls._prepare_strategy({
            'user_agent_type': 'desktop_chrome',
            'delay_range': (1, 3),
            'headers': {},
            'retry_count': 2,
            'use_session': False
        }, domain)
    
    @classmethod
    def _prepare_strategy(cls, strategy, domain):
        """전략 준비 및 User-Agent 선택"""
        # User-Agent 선택
        ua_type = strategy.get('user_agent_type', 'desktop_chrome')
        user_agents = cls.USER_AGENTS.get(ua_type, cls.USER_AGENTS['desktop_chrome'])
        selected_ua = random.choice(user_agents)
        
        # 기본 헤더 설정
        headers = {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 사이트별 추가 헤더
        if 'headers' in strategy:
            headers.update(strategy['headers'])
        
        # 딜레이 계산
        delay_min, delay_max = strategy.get('delay_range', (1, 3))
        delay = random.uniform(delay_min, delay_max)
        
        return {
            'headers': headers,
            'cookies': strategy.get('cookies', {}),
            'delay': delay,
            'retry_count': strategy.get('retry_count', 2),
            'use_session': strategy.get('use_session', False),
            'user_agent': selected_ua
        }
    
    @classmethod
    def _extract_domain(cls, url):
        """URL에서 도메인 추출"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    
    @classmethod
    def apply_delay(cls, strategy):
        """접근 전 딜레이 적용"""
        delay = strategy.get('delay', 1)
        time.sleep(delay)
    
    @classmethod
    def get_alternative_methods(cls, domain):
        """차단된 사이트를 위한 대체 접근 방법"""
        alternatives = {
            'mothership.sg': [
                {
                    'method': 'rss',
                    'url': 'https://mothership.sg/feed/',
                    'description': 'RSS 피드 사용'
                },
                {
                    'method': 'api',
                    'url': 'https://mothership.sg/api/articles',
                    'description': 'API 엔드포인트 (비공식)'
                }
            ],
            'todayonline.com': [
                {
                    'method': 'archive',
                    'url': 'https://web.archive.org/web/*/https://www.todayonline.com/',
                    'description': 'Internet Archive 사용'
                }
            ]
        }
        
        for site_domain, methods in alternatives.items():
            if site_domain in domain:
                return methods
        
        return []