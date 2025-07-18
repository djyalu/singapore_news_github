# 보안 업데이트 가이드

## 하드코딩된 자격 증명 제거 완료

모든 하드코딩된 API 키와 비밀번호를 환경 변수로 이동했습니다.

### 필요한 환경 변수 설정

#### 1. GitHub Secrets (Actions용)
- `GOOGLE_GEMINI_API_KEY`: Google Gemini API 키
- `WHATSAPP_API_KEY`: WhatsApp API 키 (새로 발급 필요)

#### 2. Vercel 환경 변수
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `GITHUB_OWNER`: djyalu
- `GITHUB_REPO`: singapore_news_github
- `WHATSAPP_API_KEY`: WhatsApp API 키 (GitHub Secrets와 동일)
- `ADMIN_PASSWORD`: admin 계정 비밀번호
- `DJYALU_PASSWORD`: djyalu 계정 비밀번호

### 변경 사항

1. **WhatsApp API 키**
   - 기존: 하드코딩된 키 `ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq`
   - 변경: 환경 변수 `WHATSAPP_API_KEY` 사용
   - 영향 파일:
     - `scripts/send_whatsapp.py`
     - `api/send-whatsapp.js`
     - `js/app.js` (백엔드 API 경유)

2. **로그인 인증**
   - 기존: 하드코딩된 비밀번호 (admin/Admin@123, djyalu/djyalu123)
   - 변경: Vercel 환경 변수 사용
   - 새 API 엔드포인트:
     - `/api/auth-login`: 로그인 처리
     - `/api/auth-config`: 인증 설정 확인

### 즉시 필요한 조치

1. **WhatsApp API 키 교체**
   ```bash
   # 기존 키 폐기하고 새 키 발급 받기
   # https://gate.whapi.cloud 에서 새 API 키 발급
   ```

2. **GitHub Secrets 설정**
   ```bash
   # Repository Settings > Secrets and variables > Actions
   # WHATSAPP_API_KEY 추가
   ```

3. **Vercel 환경 변수 설정**
   ```bash
   # Vercel Dashboard > Project Settings > Environment Variables
   # 위에 나열된 모든 환경 변수 추가
   ```

### 보안 개선 사항

- API 키가 소스 코드에 노출되지 않음
- 프론트엔드에서 직접 API 호출하지 않음
- 모든 민감한 작업은 백엔드 API 경유
- 개발 환경에서만 임시 로그인 허용

### 테스트 방법

1. 로그인 테스트: Vercel에 비밀번호 설정 후 로그인
2. WhatsApp 전송: 새 API 키로 메시지 전송 테스트
3. API 상태: `/api/test-env` 엔드포인트로 환경 변수 확인