import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def collect_club_events():
    url = "https://www3.chosun.ac.kr/chosun/757/subview.do"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 이벤트 목록을 찾는 선택자를 조정해야 할 수 있습니다
    event_list = soup.select('table.board-table tbody tr')
    
    events = []
    
    for event in event_list:
        try:
            # 선택자를 페이지 구조에 맞게 조정
            title_elem = event.select_one('td.subject a')
            date_elem = event.select('td')[4] if len(event.select('td')) > 4 else None
            
            if title_elem and date_elem:
                title = title_elem.text.strip()
                date = date_elem.text.strip()
                link = "https://www3.chosun.ac.kr" + title_elem['href'] if title_elem.has_attr('href') else ""
                
                # 클릭해서 세부 정보를 더 수집할 수도 있습니다
                # detail_response = requests.get(link)
                # detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                # description = detail_soup.select_one('div.content').text.strip()
                
                events.append({
                    "title": title,
                    "date": date,
                    "link": link,
                    "type": "event"  # 이벤트 유형 분류
                })
        except Exception as e:
            print(f"이벤트 파싱 오류: {e}")
    
    # 데이터 저장
    os.makedirs('../data/external', exist_ok=True)
    with open('../data/external/club_events.json', 'w', encoding='utf-8') as f:
        json.dump({"events": events}, f, ensure_ascii=False, indent=2)
    
    print(f"{len(events)}개의 이벤트 정보를 수집했습니다.")
    return events

if __name__ == "__main__":
    collect_club_events()