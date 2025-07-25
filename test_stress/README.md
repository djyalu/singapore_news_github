# Singapore News Scraper 스트레스 테스트 가이드

## 📋 개요

이 디렉토리는 Singapore News Scraper 시스템의 대규모 스트레스 테스트를 위한 도구와 결과를 포함합니다.

## 🔧 구성 요소

### 1. 테스트 프로그램
- `stress_test.py` - 메인 스트레스 테스트 엔진
- `mock_server.py` - 로컬 테스트용 모의 서버
- `run_test.py` - 테스트 실행 스크립트
- `simulate_test_results.py` - 시뮬레이션 결과 생성
- `visualize_results.py` - 결과 시각화

### 2. 결과 파일
- `stress_test_10k_users_simulation.json` - 10,000명 테스트 시뮬레이션 결과
- `STRESS_TEST_REPORT.md` - 상세 분석 보고서

## 🚀 테스트 실행 방법

### 1. 환경 설정
```bash
# 필요한 패키지 설치
pip3 install -r requirements.txt
```

### 2. 로컬 모의 서버 테스트
```bash
# 로컬 환경에서 안전하게 테스트
python3 run_test.py --target local --mode progressive
```

### 3. 실제 서버 테스트 (주의!)
```bash
# 실제 Vercel 서버 테스트 (서비스에 영향 가능)
python3 run_test.py --target vercel --mode quick
```

### 4. 테스트 모드
- `quick` - 빠른 테스트 (100명)
- `progressive` - 점진적 증가 (10명 → 10,000명)
- `spike` - 급증 테스트
- `endurance` - 지속성 테스트

## 📊 주요 발견사항

### 시스템 한계
- **안정적 운영**: 최대 1,000명
- **성능 저하**: 1,000-5,000명
- **시스템 과부하**: 5,000명 이상

### 주요 병목 지점
1. **스크래핑 트리거** - 64.95% 성공률 (GitHub Actions API 제한)
2. **설정 업데이트** - 71.99% 성공률 (파일 시스템 경합)
3. **기사 검색** - 느린 응답 시간 (비효율적 쿼리)

## 💰 비용 대비 효과

| 투자 | 지원 사용자 | 월 비용 | 성능 향상 |
|------|------------|---------|-----------|
| 현재 | 1,000명 | $0 | 기준선 |
| 단기 | 5,000명 | $35 | 400% |
| 전체 | 10,000명 | $70 | 900% |

## 📈 권장 개선 로드맵

### Phase 1 (즉시)
- Redis 캐싱 구현
- 데이터베이스 쿼리 최적화
- API Rate Limiting

### Phase 2 (1개월)
- 비동기 큐 시스템
- CDN 적용
- 모니터링 도구

### Phase 3 (3개월)
- 마이크로서비스 전환
- Auto-scaling
- 글로벌 배포

## 🔍 결과 확인

### 시뮬레이션 결과 보기
```bash
python3 simulate_test_results.py
```

### 시각화 결과 보기
```bash
python3 visualize_results.py
```

### 상세 보고서
[STRESS_TEST_REPORT.md](./STRESS_TEST_REPORT.md) 참조

## ⚠️ 주의사항

1. **실제 서버 테스트 시 주의**
   - 서비스 중단 가능성
   - API rate limit 소진
   - 비용 발생 가능

2. **테스트 시간대**
   - 사용자가 적은 시간대 선택
   - 백업 준비
   - 모니터링 활성화

3. **결과 해석**
   - 시뮬레이션은 예상치
   - 실제 환경은 다를 수 있음
   - 네트워크 상황 고려

## 📞 문의

테스트 관련 문의사항은 프로젝트 관리자에게 연락하세요.