import json
import os

def test_json_files():
    # 동아리 행사 정보 파일 테스트
    try:
        club_events_path = os.path.join("data", "external", "club_events.json")
        if os.path.exists(club_events_path):
            with open(club_events_path, "r", encoding="utf-8") as f:
                club_data = json.load(f)
            print(f"✅ 동아리 행사 파일 로드 성공: {club_events_path}")
            print(f"   이벤트 수: {len(club_data.get('events', []))}")
            for i, event in enumerate(club_data.get('events', [])[:3], 1):
                print(f"   샘플 이벤트 {i}: {event['title']} - {event.get('date', '날짜 없음')}")
        else:
            print(f"❌ 동아리 행사 파일이 존재하지 않습니다: {club_events_path}")
    except Exception as e:
        print(f"❌ 동아리 행사 파일 로드 실패: {str(e)}")
    
    # FAQ 파일 테스트
    try:
        faq_path = os.path.join("data", "external", "faq.json")
        if os.path.exists(faq_path):
            with open(faq_path, "r", encoding="utf-8") as f:
                faq_data = json.load(f)
            print(f"\n✅ FAQ 파일 로드 성공: {faq_path}")
            print(f"   FAQ 항목 수: {len(faq_data.get('faqs', []))}")
            for i, faq in enumerate(faq_data.get('faqs', [])[:3], 1):
                print(f"   샘플 FAQ {i}: {faq['question']}")
        else:
            print(f"❌ FAQ 파일이 존재하지 않습니다: {faq_path}")
    except Exception as e:
        print(f"❌ FAQ 파일 로드 실패: {str(e)}")

if __name__ == "__main__":
    print("JSON 파일 테스트 시작...\n")
    test_json_files()
    print("\nJSON 파일 테스트 완료!")