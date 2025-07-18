"""
비밀번호 해시 생성 도구
사용법: python scripts/hash_password.py
"""

import bcrypt
import json

def hash_password(password):
    """비밀번호를 bcrypt로 해시화"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """비밀번호 검증"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def update_user_password(user_id, new_password):
    """사용자 비밀번호 업데이트"""
    # users.json 읽기
    with open('data/users.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 사용자 찾기
    for user in data['users']:
        if user['id'] == user_id:
            # 비밀번호 해시화
            user['password'] = hash_password(new_password)
            print(f"✅ {user_id} 비밀번호가 업데이트되었습니다.")
            break
    else:
        print(f"❌ {user_id} 사용자를 찾을 수 없습니다.")
        return
    
    # 파일 저장
    with open('data/users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("=== 비밀번호 해시 생성 도구 ===")
    print("1. 새 비밀번호 해시 생성")
    print("2. 기존 사용자 비밀번호 변경")
    
    choice = input("\n선택 (1 또는 2): ").strip()
    
    if choice == "1":
        password = input("해시화할 비밀번호 입력: ")
        hashed = hash_password(password)
        print(f"\n해시된 비밀번호:\n{hashed}")
        print("\n이 값을 data/users.json 파일의 password 필드에 넣으세요.")
        
    elif choice == "2":
        user_id = input("사용자 ID (admin 또는 djyalu): ").strip()
        new_password = input("새 비밀번호: ")
        update_user_password(user_id, new_password)
        
    else:
        print("잘못된 선택입니다.")