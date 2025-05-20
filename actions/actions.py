from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
import os
import re
from difflib import get_close_matches

class ActionShowClubEvents(Action):
    def name(self) -> Text:
        return "action_show_club_events"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # JSON 파일에서 이벤트 데이터 로드
            filepath = os.path.join("data", "external", "club_events.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            events = data.get("events", [])
            
            if not events:
                dispatcher.utter_message(text="현재 등록된 행사 정보가 없습니다.")
                return []
            
            # 최대 5개의 이벤트만 표시
            limited_events = events[:5]
            
            # 응답 메시지 구성
            message = "현재 진행 중이거나 예정된 행사 목록입니다:\n\n"
            
            for idx, event in enumerate(limited_events, 1):
                message += f"{idx}. {event['title']} - {event['date']}\n"
            
            if len(events) > 5:
                message += f"\n... 외 {len(events) - 5}개의 행사가 더 있습니다. 특정 행사에 대해 더 알고 싶으시면 행사명을 말씀해주세요."
            
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            dispatcher.utter_message(text=f"행사 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
        
        return []


class ActionShowClubEventDetail(Action):
    def name(self) -> Text:
        return "action_show_club_event_detail"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # 슬롯에서 이벤트 이름 가져오기
            event_name = tracker.get_slot("event_name")
            
            if not event_name:
                dispatcher.utter_message(text="어떤 행사에 대해 알고 싶으신가요?")
                return []
            
            # JSON 파일에서 이벤트 데이터 로드
            filepath = os.path.join("data", "external", "club_events.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            events = data.get("events", [])
            
            # 이벤트 이름과 가장 일치하는 항목 찾기
            event_titles = [event["title"] for event in events]
            matches = get_close_matches(event_name, event_titles, n=1, cutoff=0.6)
            
            if not matches:
                dispatcher.utter_message(text=f"'{event_name}' 행사에 대한 정보를 찾을 수 없습니다.")
                return []
            
            matched_title = matches[0]
            matched_event = next((event for event in events if event["title"] == matched_title), None)
            
            if not matched_event:
                dispatcher.utter_message(text=f"'{event_name}' 행사에 대한 정보를 찾을 수 없습니다.")
                return []
            
            # 응답 메시지 구성
            message = f"'{matched_title}' 행사 정보입니다:\n\n"
            message += f"날짜: {matched_event['date']}\n"
            if matched_event.get('link'):
                message += f"자세한 정보: {matched_event['link']}\n"
            
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            dispatcher.utter_message(text=f"행사 세부 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
        
        return []


class ActionShowFaqList(Action):
    def name(self) -> Text:
        return "action_show_faq_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # JSON 파일에서 FAQ 데이터 로드
            filepath = os.path.join("data", "external", "faq.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            faqs = data.get("faqs", [])
            
            if not faqs:
                dispatcher.utter_message(text="현재 등록된 FAQ가 없습니다.")
                return []
            
            # 최대 5개의 FAQ 질문만 표시
            limited_faqs = faqs[:5]
            
            # 응답 메시지 구성
            message = "자주 묻는 질문 목록입니다:\n\n"
            
            for idx, faq in enumerate(limited_faqs, 1):
                message += f"{idx}. {faq['question']}\n"
            
            if len(faqs) > 5:
                message += f"\n... 외 {len(faqs) - 5}개의 FAQ가 더 있습니다. 원하시는 질문을 직접 물어보세요."
            
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            dispatcher.utter_message(text=f"FAQ 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")
        
        return []


class ActionAnswerFaq(Action):
    def name(self) -> Text:
        return "action_answer_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # 사용자의 질문 가져오기
            user_question = tracker.latest_message.get("text", "")
            
            # JSON 파일에서 FAQ 데이터 로드
            filepath = os.path.join("data", "external", "faq.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            faqs = data.get("faqs", [])
            
            if not faqs:
                dispatcher.utter_message(text="현재 등록된 FAQ가 없습니다.")
                return []
            
            # 질문 목록 추출
            questions = [faq["question"] for faq in faqs]
            
            # 가장 유사한 질문 찾기
            matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
            
            if not matches:
                dispatcher.utter_message(text="죄송합니다. 질문에 맞는 답변을 찾을 수 없습니다. 다른 방식으로 질문해 주시겠어요?")
                return []
            
            matched_question = matches[0]
            matched_faq = next((faq for faq in faqs if faq["question"] == matched_question), None)
            
            if not matched_faq:
                dispatcher.utter_message(text="죄송합니다. 질문에 맞는 답변을 찾을 수 없습니다.")
                return []
            
            # 응답 메시지 구성
            message = f"Q: {matched_faq['question']}\n\nA: {matched_faq['answer']}"
            
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            dispatcher.utter_message(text=f"FAQ 답변을 찾는 중 오류가 발생했습니다: {str(e)}")
        
        return []