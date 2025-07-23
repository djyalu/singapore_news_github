# AI 스크래핑 최적화 가이드

## 현재 문제점
- 16개 사이트 × 10개 링크 = 160개 URL → 240+ API 호출
- Gemini 무료 제한: 분당 15회
- 소요 시간: 17-20분 (타임아웃 위험)

## 최적화 전략

### 1. 사이트 우선순위 설정
**High Priority (4개 링크)**
- The Straits Times
- Channel NewsAsia

**Medium Priority (2-3개 링크)**
- The Business Times
- Yahoo Singapore News
- Mothership

**Low Priority (1-2개 링크)**
- 나머지 사이트들

### 2. API 호출 절감
**이전**: 
- 총 URL: 160개
- API 호출: 240회
- 시간: 17분

**최적화 후**:
- 총 URL: 40-50개
- API 호출: 80-100회
- 시간: 6-8분

### 3. 구현된 최적화

#### Traditional 스크래핑
```python
priority_limits = {
    'The Straits Times': 3,
    'Channel NewsAsia': 3,
    'The Business Times': 2,
    'Yahoo Singapore News': 2,
    'Mothership': 2
}
max_links = priority_limits.get(site['name'], 1)  # 기본값 1개
```

#### AI 스크래핑
```python
priority_limits = {
    'The Straits Times': 4,
    'Channel NewsAsia': 4,
    'The Business Times': 3,
    'Yahoo Singapore News': 3,
    'Mothership': 3
}
max_links = priority_limits.get(site['name'], 2)  # 기본값 2개
```

### 4. 추가 최적화 방안

1. **캐시 활용 강화**
   - URL 패턴 캐시
   - 컨텐츠 분류 캐시
   - 1시간 유효

2. **배치 처리**
   - 5개 URL씩 묶어서 처리
   - 병렬 처리 가능

3. **스마트 필터링**
   - 명백한 비기사 URL 사전 제외
   - 날짜가 오래된 기사 제외

4. **동적 조정**
   - API 잔여 한도에 따라 링크 수 조정
   - 시간대별 우선순위 조정

### 5. 성능 비교

| 항목 | 최적화 전 | 최적화 후 | 개선율 |
|------|-----------|-----------|--------|
| 총 URL 검사 | 160개 | 45개 | 72% 감소 |
| API 호출 | 240회 | 90회 | 63% 감소 |
| 소요 시간 | 17분 | 7분 | 59% 단축 |
| 수집 기사 | 10-15개 | 8-12개 | 80% 유지 |

### 6. 향후 개선 사항

1. **사이트별 품질 점수**
   - 과거 성공률 기반 동적 조정
   - 중복 기사가 많은 사이트 우선순위 하향

2. **시간대별 최적화**
   - 오전: 주요 뉴스 사이트 집중
   - 오후: 라이프스타일, 문화 사이트

3. **키워드 기반 필터링**
   - 중요 키워드 포함 기사 우선
   - 차단 키워드 사전 필터링