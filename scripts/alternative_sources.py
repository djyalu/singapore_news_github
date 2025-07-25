"""
대체 소스를 통한 뉴스 수집
Google Cache, Archive.org, 모바일 URL 등 활용
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote
from datetime import datetime, timedelta
import pytz

KST = pytz.timezone('Asia/Seoul')

class AlternativeSources:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
        })
    
    def get_from_google_cache(self, url):
        """Google 캐시에서 페이지 가져오기"""
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{quote(url)}"
        try:
            response = self.session.get(cache_url, timeout=10)
            if response.status_code == 200:
                return response.text
        except:
            pass
        return None
    
    def get_from_archive_org(self, url):
        """Archive.org에서 최신 스냅샷 가져오기"""
        # 최근 스냅샷 확인
        check_url = f"https://archive.org/wayback/available?url={quote(url)}"
        try:
            response = requests.get(check_url, timeout=10)
            data = response.json()
            
            if data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                snapshot_url = data['archived_snapshots']['closest']['url']
                snapshot_response = requests.get(snapshot_url, timeout=15)
                if snapshot_response.status_code == 200:
                    return snapshot_response.text
        except:
            pass
        return None
    
    def get_mobile_version(self, url):
        """모바일 버전 URL 시도"""
        mobile_variants = [
            lambda u: u.replace('www.', 'm.'),
            lambda u: u.replace('www.', 'mobile.'),
            lambda u: u + '?mobile=1',
            lambda u: u + '&amp=1'  # AMP 페이지
        ]
        
        for variant_func in mobile_variants:
            try:
                mobile_url = variant_func(url)
                response = self.session.get(mobile_url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        return None
    
    def get_via_proxy_services(self, url):
        """프록시 서비스를 통한 접근"""
        proxy_services = [
            f"https://www.proxysite.com/process.php?u={quote(url)}",
            f"https://www.croxyproxy.com/?url={quote(url)}",
            f"https://www.hidemyass-freeproxy.com/proxy/{quote(url)}"
        ]
        
        for proxy_url in proxy_services:
            try:
                # 프록시 서비스는 추가 헤더가 필요할 수 있음
                headers = {
                    'Referer': 'https://www.google.com/',
                    'Origin': proxy_url.split('/')[2]
                }
                response = requests.get(proxy_url, headers=headers, timeout=15)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        return None
    
    def extract_from_social_media(self, site_name):
        """소셜 미디어에서 뉴스 링크 수집"""
        articles = []
        
        # Twitter/X 검색
        if site_name == "TODAY Online":
            twitter_search_url = "https://twitter.com/search?q=from%3Atodayonline&src=typed_query&f=live"
            # Twitter API 없이는 제한적
            
        # Facebook 페이지
        facebook_pages = {
            "Mothership": "https://www.facebook.com/MothershipSG",
            "The Independent Singapore": "https://www.facebook.com/theindependentsg",
            "TODAY Online": "https://www.facebook.com/todayonline"
        }
        
        # Reddit Singapore
        reddit_url = "https://www.reddit.com/r/singapore/search.json?q=site%3A" + site_name.lower().replace(' ', '') + "&sort=new&limit=10"
        
        try:
            response = requests.get(reddit_url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                data = response.json()
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    if post_data.get('url', '').startswith('http'):
                        articles.append({
                            'title': post_data.get('title'),
                            'url': post_data.get('url'),
                            'source': 'reddit'
                        })
        except:
            pass
            
        return articles
    
    def get_alternative_content(self, url, site_name):
        """다양한 대체 방법으로 콘텐츠 시도"""
        methods = [
            ('mobile', self.get_mobile_version),
            ('google_cache', self.get_from_google_cache),
            ('archive_org', self.get_from_archive_org),
            ('proxy', self.get_via_proxy_services)
        ]
        
        for method_name, method_func in methods:
            print(f"[AlternativeSources] Trying {method_name} for {site_name}")
            content = method_func(url)
            if content:
                print(f"[AlternativeSources] Success with {method_name}")
                return content, method_name
                
        return None, None