"""
완전 오프라인 한글 요약 시스템
외부 API 없이 사전과 규칙 기반으로 한글 요약 생성
"""

import re
from typing import Dict, List

class OfflineKoreanSummarizer:
    def __init__(self):
        # 영한 사전 (확장 가능)
        self.word_dict = {
            # 일반 단어
            'the': '그', 'a': '한', 'an': '한', 'and': '그리고', 'or': '또는',
            'is': '이다', 'are': '이다', 'was': '였다', 'were': '였다',
            'will': '할 것이다', 'would': '할 것이다', 'can': '할 수 있다',
            'new': '새로운', 'old': '오래된', 'good': '좋은', 'bad': '나쁜',
            'big': '큰', 'small': '작은', 'high': '높은', 'low': '낮은',
            'first': '첫 번째', 'last': '마지막', 'next': '다음',
            'people': '사람들', 'person': '사람', 'man': '남자', 'woman': '여자',
            'year': '년', 'month': '월', 'day': '일', 'time': '시간',
            'government': '정부', 'minister': '장관', 'president': '대통령',
            'company': '회사', 'business': '사업', 'market': '시장',
            'money': '돈', 'cost': '비용', 'price': '가격', 'pay': '지불',
            'house': '집', 'home': '집', 'school': '학교', 'hospital': '병원',
            'police': '경찰', 'court': '법원', 'law': '법', 'rule': '규칙',
            'work': '일', 'job': '직업', 'worker': '직장인', 'student': '학생',
            'report': '보고서', 'news': '뉴스', 'information': '정보',
            'system': '시스템', 'service': '서비스', 'program': '프로그램',
            'problem': '문제', 'issue': '이슈', 'solution': '해결책',
            'increase': '증가', 'decrease': '감소', 'change': '변화',
            'develop': '개발', 'build': '건설', 'create': '창조',
            'start': '시작', 'begin': '시작', 'end': '끝', 'finish': '완료',
            'help': '도움', 'support': '지원', 'provide': '제공',
            
            # 싱가포르 관련
            'singapore': '싱가포르', 'singaporean': '싱가포르인',
            'mrt': 'MRT', 'lta': '육상교통청', 'hdb': 'HDB',
            'cpf': 'CPF', 'mas': '통화청', 'moe': '교육부',
            'changi': '창이', 'marina': '마리나', 'sentosa': '센토사',
            'orchard': '오차드', 'raffles': '래플스',
            
            # 경제/금융
            'economy': '경제', 'economic': '경제적',
            'gdp': 'GDP', 'inflation': '인플레이션',
            'investment': '투자', 'investor': '투자자',
            'stock': '주식', 'share': '주식', 'bond': '채권',
            'bank': '은행', 'banking': '은행업',
            'finance': '금융', 'financial': '금융의',
            'dollar': '달러', 'currency': '통화',
            
            # 교통
            'transport': '교통', 'transportation': '교통',
            'bus': '버스', 'taxi': '택시', 'train': '기차',
            'car': '자동차', 'vehicle': '차량', 'traffic': '교통',
            'road': '도로', 'street': '거리', 'highway': '고속도로',
            
            # 의료/건강
            'health': '건강', 'healthy': '건강한',
            'doctor': '의사', 'nurse': '간호사',
            'patient': '환자', 'medicine': '의약품',
            'treatment': '치료', 'hospital': '병원',
            'covid': '코로나', 'virus': '바이러스',
            'vaccine': '백신', 'vaccination': '백신접종',
            
            # 교육
            'education': '교육', 'educational': '교육적',
            'school': '학교', 'university': '대학교',
            'college': '대학', 'student': '학생',
            'teacher': '교사', 'professor': '교수',
            'study': '공부', 'learn': '배우다',
            'exam': '시험', 'test': '시험',
            
            # 기술
            'technology': '기술', 'tech': '기술',
            'digital': '디지털', 'online': '온라인',
            'internet': '인터넷', 'computer': '컴퓨터',
            'software': '소프트웨어', 'app': '앱',
            'data': '데이터', 'information': '정보',
            'artificial': '인공', 'intelligence': '지능',
            'ai': 'AI', 'robot': '로봇',
            
            # 환경
            'environment': '환경', 'environmental': '환경의',
            'climate': '기후', 'weather': '날씨',
            'green': '녹색', 'energy': '에너지',
            'pollution': '오염', 'clean': '깨끗한',
            'water': '물', 'air': '공기',
            
            # 동작
            'announce': '발표하다', 'launch': '출시하다',
            'introduce': '도입하다', 'implement': '시행하다',
            'plan': '계획하다', 'expect': '기대하다',
            'rise': '상승하다', 'fall': '하락하다',
            'grow': '성장하다', 'expand': '확장하다',
            'reduce': '줄이다', 'cut': '삭감하다',
            'open': '개방하다', 'close': '폐쇄하다',
            'buy': '구매하다', 'sell': '판매하다',
            'give': '주다', 'take': '받다',
            'make': '만들다', 'do': '하다',
            'say': '말하다', 'tell': '말하다',
            'show': '보여주다', 'see': '보다',
            'find': '찾다', 'get': '얻다',
            'use': '사용하다', 'need': '필요하다',
            'want': '원하다', 'like': '좋아하다',
            'know': '알다', 'think': '생각하다',
            'believe': '믿다', 'feel': '느끼다',
            'try': '시도하다', 'attempt': '시도하다',
            'continue': '계속하다', 'stop': '멈추다',
            'move': '이동하다', 'go': '가다',
            'come': '오다', 'arrive': '도착하다',
            'leave': '떠나다', 'return': '돌아오다',
        }
        
        # 숫자 변환
        self.number_dict = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'hundred': '백', 'thousand': '천', 'million': '백만', 'billion': '10억'
        }
    
    def translate_word(self, word: str) -> str:
        """단어 번역"""
        word_lower = word.lower()
        
        # 숫자 확인
        if word_lower in self.number_dict:
            return self.number_dict[word_lower]
        
        # 사전 확인
        if word_lower in self.word_dict:
            return self.word_dict[word_lower]
        
        # 고유명사는 그대로
        if word[0].isupper():
            return word
        
        # 숫자, 날짜, 퍼센트는 그대로
        if re.match(r'^\d+$', word) or '%' in word or '$' in word:
            return word
        
        # 번역 불가능한 경우 원문 반환
        return word
    
    def extract_key_info(self, text: str) -> Dict:
        """핵심 정보 추출"""
        # 날짜 추출
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b', text)
        
        # 숫자 추출
        numbers = re.findall(r'\$?[\d,]+\.?\d*%?', text)
        
        # 인명 추출 (대문자로 시작하는 2-3 단어)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b', text)
        
        # 기관명 추출
        organizations = re.findall(r'\b[A-Z]{2,}\b', text)
        
        return {
            'dates': dates[:3],
            'numbers': numbers[:3],
            'names': names[:2],
            'organizations': organizations[:3]
        }
    
    def create_korean_summary(self, title: str, content: str) -> str:
        """한글 요약 생성"""
        # 제목 번역
        title_words = re.findall(r'\b\w+\b', title)
        korean_title_words = [self.translate_word(word) for word in title_words]
        korean_title = ' '.join(korean_title_words)
        
        # 핵심 정보 추출
        key_info = self.extract_key_info(content)
        
        # 첫 문장 번역 (간단하게)
        first_sentence = content.split('.')[0] if content else ""
        first_words = re.findall(r'\b\w+\b', first_sentence)[:20]  # 첫 20단어만
        korean_words = [self.translate_word(word) for word in first_words]
        korean_content = ' '.join(korean_words)
        
        # 요약 구성
        summary = f"📰 제목: {korean_title}\n"
        
        # 핵심 정보 추가
        if key_info['dates']:
            summary += f"📅 날짜: {', '.join(key_info['dates'])}\n"
        
        if key_info['numbers']:
            summary += f"📊 주요 수치: {', '.join(key_info['numbers'])}\n"
        
        if key_info['names']:
            summary += f"👤 관련 인물: {', '.join(key_info['names'])}\n"
        
        if key_info['organizations']:
            summary += f"🏢 관련 기관: {', '.join(key_info['organizations'])}\n"
        
        summary += f"📝 내용: {korean_content}"
        
        return summary

# 사용 예시
def get_offline_summary(title: str, content: str) -> str:
    """오프라인 한글 요약 생성"""
    summarizer = OfflineKoreanSummarizer()
    return summarizer.create_korean_summary(title, content)

# 테스트
if __name__ == "__main__":
    title = "Singapore government announces new transport policy"
    content = "The Singapore government will introduce new transport policy from July 2025. Minister Lee said the policy will help reduce traffic."
    
    print("=== 오프라인 한글 요약 테스트 ===")
    print(get_offline_summary(title, content))