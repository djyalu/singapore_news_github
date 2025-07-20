# 스크래퍼 통합 개선 가이드

## 주요 개선 사항 요약

### 1. 중복 제거 개선
- **현재**: 제목만으로 중복 판단
- **개선**: 제목 + 내용 유사도 기반 중복 제거
- **구현**: `deduplication.py`의 `ArticleDeduplicator` 클래스 사용

### 2. 문장 잘림 방지
- **현재**: 단순 문자열 슬라이싱으로 내용 자름
- **개선**: 문장 경계를 인식하여 안전하게 자름
- **구현**: `text_processing.py`의 `TextProcessor.safe_truncate()` 사용

### 3. AI 요약 개선
- **현재**: 800자로 자른 내용을 AI에 전달
- **개선**: 완전한 문장으로 자른 내용 전달
- **구현**: `scraper_improvements.py`의 `create_summary_improved()` 사용

### 4. 동적 셀렉터 관리
- **현재**: 하드코딩된 CSS 셀렉터
- **개선**: 사이트별 셀렉터 중앙 관리 및 폴백 지원
- **구현**: `site_selectors.py`의 `SiteSelectors` 클래스 사용

## 통합 방법

### 1. scraper.py 수정사항

```python
# 파일 상단에 import 추가
from text_processing import TextProcessor
from deduplication import ArticleDeduplicator
from site_selectors import SiteSelectors
from scraper_improvements import (
    extract_article_content_improved,
    create_summary_improved,
    consolidate_articles_improved
)

# extract_article_content 함수 대체
def extract_article_content(url):
    """개선된 버전으로 대체"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 도메인 추출
        domain = urlparse(url).netloc.lower()
        
        # 개선된 추출 함수 사용
        article_data = extract_article_content_improved(url, soup)
        
        return article_data
            
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

# create_summary 함수 대체
def create_summary(article_data, settings):
    """개선된 버전으로 대체"""
    return create_summary_improved(article_data, settings)

# 그룹별 기사 통합 부분 수정 (line 1549-1578)
# consolidated_articles = [] 부분을
# consolidated_articles = consolidate_articles_improved(articles_by_group) 로 대체
```

### 2. ai_summary_free.py 수정사항

```python
# translate_to_korean_summary_gemini 함수 수정 (line 23)
# content_preview = content[:800] 를
content_preview = TextProcessor.safe_truncate(content, 800)
```

### 3. sites.json 업데이트 제안

```json
[
  {
    "group": "News",
    "name": "The Straits Times",
    "url": "https://www.straitstimes.com/singapore",  // /global → /singapore
    "period": "daily",
    "selector_version": "2024-01"  // 셀렉터 버전 추가
  },
  {
    "group": "News", 
    "name": "Channel NewsAsia",
    "url": "https://www.channelnewsasia.com/singapore",  // 메인 대신 싱가포르 섹션
    "period": "daily",
    "selector_version": "2024-01"
  }
  // ... 나머지 사이트들도 구체적인 섹션 URL로 변경
]
```

## 환경 변수 확인

1. **Vercel 환경변수** (이미 설정됨)
   - GITHUB_TOKEN
   - GITHUB_OWNER
   - GITHUB_REPO
   - WHATSAPP_API_KEY

2. **GitHub Secrets 추가 필요**
   - GOOGLE_GEMINI_API_KEY (AI 요약용)

## 모니터링 및 디버깅

### 1. 셀렉터 실패 감지
```python
# 각 사이트 스크래핑 후 추가
selector_test = SiteSelectors.test_selectors(soup, domain)
if not all(selector_test.values()):
    print(f"WARNING: Some selectors failed for {domain}: {selector_test}")
```

### 2. 중복 제거 통계
```python
# 그룹별 통합 후 로그
for group_summary in consolidated_articles:
    print(f"Group {group_summary['group']}: "
          f"{group_summary['total_found']} found, "
          f"{group_summary['duplicates_removed']} duplicates removed")
```

### 3. AI 요약 성공률
```python
# AI 요약 후 통계 수집
ai_success = sum(1 for a in articles if 'gemini' in a.get('summary_method', ''))
total = len(articles)
print(f"AI Summary success rate: {ai_success}/{total} ({ai_success/total*100:.1f}%)")
```

## 단계별 적용 권장사항

1. **1단계**: 텍스트 처리 개선 (text_processing.py) 적용
   - 문장 잘림 문제 즉시 해결

2. **2단계**: 중복 제거 개선 (deduplication.py) 적용
   - 콘텐츠 품질 향상

3. **3단계**: 사이트 셀렉터 개선 (site_selectors.py) 적용
   - 사이트 구조 변경 대응력 향상

4. **4단계**: 전체 통합 및 테스트
   - 모든 개선사항 통합 적용

## 테스트 방법

```bash
# 로컬 테스트
python scripts/scraper.py

# 특정 사이트만 테스트
python -c "from scraper import *; print(extract_article_content('https://www.straitstimes.com/...'))"

# AI 요약 테스트
python test_korean_summary.py
```