import re
from typing import List, Tuple

class TextProcessor:
    """텍스트 처리를 위한 유틸리티 클래스"""
    
    @staticmethod
    def safe_truncate(text: str, max_length: int) -> str:
        """문장을 자르지 않고 안전하게 텍스트 절단"""
        if len(text) <= max_length:
            return text
            
        # 문장 끝 패턴
        sentence_endings = ['. ', '! ', '? ', '。', '！', '？']
        
        # max_length 이전의 마지막 문장 끝 찾기
        last_end = -1
        for ending in sentence_endings:
            pos = text.rfind(ending, 0, max_length)
            if pos > last_end:
                last_end = pos
        
        # 문장 끝을 찾았으면 거기까지 자르기 (문장 부호 포함)
        if last_end > 0:
            # 문장 부호가 이미 있는지 확인
            if text[last_end] in '.!?。！？':
                return text[:last_end + 1]
            else:
                return text[:last_end + 1].rstrip() + '.'
        
        # 못 찾았으면 단어 단위로 자르기
        space_pos = text.rfind(' ', 0, max_length)
        if space_pos > 0:
            return text[:space_pos] + '...'
            
        # 그마저도 없으면 그냥 자르기
        return text[:max_length] + '...'
    
    @staticmethod
    def extract_sentences(text: str, min_length: int = 15) -> List[str]:
        """텍스트에서 완전한 문장만 추출"""
        # 문장 분리 패턴 (개선된 버전)
        sentence_pattern = r'[.!?。！？]\s+'
        
        # 약어 보호 (Dr., Mr., etc.)
        abbreviations = ['Dr', 'Mr', 'Mrs', 'Ms', 'Prof', 'Sr', 'Jr', 'Ltd', 'Inc', 'Co']
        for abbr in abbreviations:
            text = text.replace(f'{abbr}.', f'{abbr}__DOT__')
        
        # 문장 분리
        sentences = re.split(sentence_pattern, text)
        
        # 약어 복원 및 필터링
        valid_sentences = []
        for sentence in sentences:
            sentence = sentence.replace('__DOT__', '.').strip()
            if len(sentence) >= min_length:
                valid_sentences.append(sentence)
                
        return valid_sentences
    
    @staticmethod
    def merge_paragraphs(paragraphs: List[str], max_length: int = 1000) -> str:
        """단락들을 병합하되 문장이 잘리지 않도록 처리"""
        merged = ""
        
        for para in paragraphs:
            # 현재 단락을 추가해도 길이를 초과하지 않으면
            if len(merged) + len(para) + 2 <= max_length:  # +2는 '. ' 공백
                if merged:
                    merged += '. ' if not merged.endswith('.') else ' '
                merged += para
            else:
                # 초과하면 남은 공간만큼만 추가
                remaining = max_length - len(merged)
                if remaining > 50:  # 최소 50자는 남아있어야 의미있음
                    truncated = TextProcessor.safe_truncate(para, remaining - 2)
                    if truncated:
                        if merged:
                            merged += '. ' if not merged.endswith('.') else ' '
                        merged += truncated
                break
                
        return merged
    
    @staticmethod
    def clean_menu_text(text: str) -> str:
        """메뉴/네비게이션 텍스트 제거"""
        # 메뉴 패턴들
        menu_patterns = [
            r'Sign In\s+Account\s+My Feed.*?Menu',
            r'Edition:\s+Singapore.*?Asia',
            r'Search\s+Menu\s+Search',
            r'Top Stories.*?Latest News.*?Live TV',
            r'News Id \d+ Type landing_page',
            r'CNA.*?Lifestyle.*?Luxury.*?TODAY',
            r'내 피드 에디션 메뉴.*?계정',
            r'싱가포르 인도네시아 아시아',
        ]
        
        cleaned = text
        for pattern in menu_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
            
        # 연속된 공백 제거
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()