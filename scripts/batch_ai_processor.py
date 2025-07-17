"""
배치 AI 프로세서 - 여러 URL을 한 번의 AI 요청으로 처리
"""
import json
from typing import List, Dict, Tuple

class BatchAIProcessor:
    def __init__(self, ai_model):
        self.model = ai_model
        
    def validate_urls_batch(self, urls_with_context: List[Tuple[str, str, str]]) -> Dict[str, bool]:
        """여러 URL을 한 번에 검증"""
        if not self.model or not urls_with_context:
            return {}
            
        # URL 리스트 준비
        url_list = []
        for i, (url, title, text) in enumerate(urls_with_context[:10]):  # 최대 10개씩
            url_list.append(f"{i+1}. URL: {url}\n   제목: {title}\n   텍스트: {text[:50]}")
        
        prompt = f"""
다음 URL들이 실제 뉴스 기사인지 판단해주세요. 각 번호별로 YES 또는 NO로 답하세요.

{chr(10).join(url_list)}

답변 형식:
1. YES
2. NO
3. YES
...

판단 기준:
- 실제 뉴스 기사면 YES
- 메뉴, 광고, 로그인 페이지 등이면 NO
"""
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                results = {}
                lines = response.text.strip().split('\n')
                for i, line in enumerate(lines):
                    if i < len(urls_with_context):
                        url = urls_with_context[i][0]
                        # YES/NO 추출
                        if 'YES' in line.upper():
                            results[url] = True
                        else:
                            results[url] = False
                return results
        except Exception as e:
            print(f"Batch AI validation error: {e}")
            
        return {}
    
    def classify_content_batch(self, contents: List[Tuple[str, str]]) -> Dict[str, Dict]:
        """여러 콘텐츠를 한 번에 분류"""
        if not self.model or not contents:
            return {}
            
        # 콘텐츠 리스트 준비
        content_list = []
        for i, (url, html_text) in enumerate(contents[:5]):  # 최대 5개씩
            content_list.append(f"{i+1}. URL: {url}\n   내용: {html_text[:300]}...")
        
        prompt = f"""
다음 웹페이지들을 분류해주세요:

{chr(10).join(content_list)}

각 번호별로 다음 중 하나로 분류:
- ARTICLE (뉴스 기사)
- MENU (메뉴/네비게이션)
- LANDING (홈페이지/섹션 메인)
- OTHER (기타)

답변 형식:
1. ARTICLE
2. MENU
3. ARTICLE
...
"""
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                results = {}
                lines = response.text.strip().split('\n')
                for i, line in enumerate(lines):
                    if i < len(contents):
                        url = contents[i][0]
                        # 분류 추출
                        line_upper = line.upper()
                        if 'ARTICLE' in line_upper:
                            results[url] = {'type': 'NEWS_ARTICLE', 'is_article': True}
                        elif 'MENU' in line_upper:
                            results[url] = {'type': 'MENU_PAGE', 'is_article': False}
                        elif 'LANDING' in line_upper:
                            results[url] = {'type': 'LANDING_PAGE', 'is_article': False}
                        else:
                            results[url] = {'type': 'OTHER', 'is_article': False}
                return results
        except Exception as e:
            print(f"Batch AI classification error: {e}")
            
        return {}