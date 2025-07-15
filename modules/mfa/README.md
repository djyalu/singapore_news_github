# MFA (Multi-Factor Authentication) Module

싱가포르 뉴스 스크래퍼의 MFA 모듈입니다.

## 구조

```
modules/mfa/
├── index.js         # 메인 진입점
├── mfa-core.js      # 핵심 TOTP/HOTP 알고리즘
├── mfa-storage.js   # 데이터 저장 및 관리
├── mfa-ui.js        # UI 컴포넌트 및 상호작용
└── README.md        # 문서
```

## 주요 기능

### 1. Core (mfa-core.js)
- **TOTP/HOTP 생성**: RFC 6238 표준 구현
- **Base32 인코딩/디코딩**: Secret 키 처리
- **Secret 생성**: 안전한 랜덤 키 생성
- **QR 코드 URL 생성**: Google Authenticator 호환

### 2. Storage (mfa-storage.js)
- **MFA 활성화/비활성화**: 사용자별 MFA 설정
- **백업 코드 관리**: 10개의 일회용 백업 코드
- **Secret 저장**: 안전한 로컬 스토리지 사용
- **백업 코드 검증**: 일회용 코드 사용 추적

### 3. UI (mfa-ui.js)
- **QR 코드 표시**: QRious 라이브러리 사용
- **설정 마법사**: 단계별 MFA 설정
- **백업 코드 표시**: 안전한 코드 표시 및 관리
- **상태 관리**: MFA 활성화 상태 표시

## 사용법

### MFA 설정
```javascript
// MFA 설정 시작
MFA.setupMFA(getCurrentUser);

// QR 코드 스캔 후 검증
MFA.completeMFASetup(getCurrentUser);
```

### MFA 검증
```javascript
// TOTP 코드 검증
const isValid = await MFA.verifyTOTP(secret, code);

// 백업 코드 사용
const result = MFA.useBackupCode(userId, backupCode);
```

### MFA 관리
```javascript
// MFA 상태 확인
const isEnabled = MFA.isMFAEnabled(userId);

// MFA 비활성화
MFA.disableMFA(userId);

// 백업 코드 재생성
MFA.regenerateBackupCodes(userId);
```

## 보안 고려사항

1. **시간 동기화**: ±2 시간 윈도우 허용 (±60초)
2. **백업 코드**: 일회용, 8자리 숫자
3. **Secret 길이**: 16자 (128비트)
4. **알고리즘**: HMAC-SHA1 (RFC 6238)

## 호환성

- Google Authenticator
- Microsoft Authenticator
- Authy
- 기타 TOTP 호환 앱

## 의존성

- Web Crypto API (브라우저 내장)
- QRious (QR 코드 생성)