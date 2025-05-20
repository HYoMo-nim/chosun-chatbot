import requests
from bs4 import BeautifulSoup
import json
import os

def collect_faq():
    url = "https://iacf.chosun.ac.kr/iacf/information/qna.do"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # FAQ 목록을 찾는 선택자를 조정해야 할 수 있습니다
    faq_list = soup.select('div.faq-list > ul > li')
    
    faqs = []
    
    for faq in faq_list:
        try:
            # 선택자를 페이지 구조에 맞게 조정
            question_elem = faq.select_one('div.faq-q')
            answer_elem = faq.select_one('div.faq-a')
            
            if question_elem and answer_elem:
                question = question_elem.text.strip()
                answer = answer_elem.text.strip()
                
                faqs.append({
                    "question": question,
                    "answer": answer,
                    "type": "faq"  # FAQ 유형 분류
                })
        except Exception as e:
            print(f"FAQ 파싱 오류: {e}")
    
    # 데이터 저장
    os.makedirs('../data/external', exist_ok=True)
    with open('../data/external/faq.json', 'w', encoding='utf-8') as f:
        json.dump({"faqs": faqs}, f, ensure_ascii=False, indent=2)
    
    print(f"{len(faqs)}개의 FAQ 정보를 수집했습니다.")
    return faqs

if __name__ == "__main__":
    collect_faq()