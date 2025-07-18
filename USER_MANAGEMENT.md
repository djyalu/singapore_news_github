# 사용자 관리 가이드

## 개요
사용자 정보는 `data/users.json` 파일에 저장되며, 비밀번호는 bcrypt로 해시화됩니다.

## 초기 설정

### 1. 비밀번호 변경
```bash
# Python 환경에서 실행
pip install bcrypt

# 비밀번호 해시 생성 도구 실행
python scripts/hash_password.py
```

### 2. 옵션 선택
- **옵션 1**: 새 비밀번호 해시 생성
  - 비밀번호를 입력하면 해시값 출력
  - 이 해시값을 `data/users.json`에 직접 복사

- **옵션 2**: 기존 사용자 비밀번호 변경
  - 사용자 ID (admin 또는 djyalu) 입력
  - 새 비밀번호 입력
  - 자동으로 `data/users.json` 업데이트

## 수동 사용자 추가

`data/users.json` 파일을 직접 편집:

```json
{
  "users": [
    {
      "id": "admin",
      "password": "$2b$10$...",  // bcrypt 해시
      "name": "관리자",
      "email": "admin@example.com",
      "role": "admin"
    },
    {
      "id": "newuser",
      "password": "$2b$10$...",  // hash_password.py로 생성
      "name": "새 사용자",
      "email": "newuser@example.com",
      "role": "user"
    }
  ]
}
```

## 보안 주의사항

1. **비밀번호 해시화 필수**
   - 평문 비밀번호 저장 금지
   - bcrypt 해시만 사용

2. **파일 권한**
   - `data/users.json`은 민감한 정보 포함
   - 적절한 파일 권한 설정 필요

3. **백업**
   - 사용자 정보 변경 전 백업 권장
   - Git에는 실제 비밀번호 해시 커밋 주의

## 임시 비밀번호 (마이그레이션용)

현재 시스템은 평문 비밀번호도 인식하지만 경고 메시지 출력:
- 가능한 빨리 bcrypt 해시로 변경 필요
- 평문 비밀번호는 보안 위험

## 문제 해결

### 로그인 실패 시
1. `data/users.json` 파일 존재 확인
2. 사용자 ID와 비밀번호 확인
3. Vercel 로그에서 오류 메시지 확인

### API 오류 시
1. Vercel에 배포되었는지 확인
2. `/api/auth-config` 엔드포인트 테스트
3. `data/users.json` 파일 형식 검증