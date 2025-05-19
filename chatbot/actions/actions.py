import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class Answerlecture:
    def name(self) -> Text:
        return "answer_lecture"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 사용자의 마지막 발화
        user_message = tracker.latest_message.get('text', "").lower()

        # JSON 파일 로드
        try:
            with open("data/schedule.json", encoding="utf-8") as f:
                schedule = json.load(f)
        except Exception as e:
            dispatcher.utter_message(text="일정을 불러오는 데 문제가 발생했습니다.")
            return []

        # 키워드를 기준으로 응답 선택
        for key in schedule:
            if key in user_message:
                dispatcher.utter_message(text=f"{key}은(는) {schedule[key]}입니다.")
                return []

        dispatcher.utter_message(text="요청하신 일정 정보를 찾을 수 없습니다.")
        return []
        
class Answerschedule:
    def name(self) -> Text:
        return "answer_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 사용자 발화 가져오기
        user_message = tracker.latest_message.get('text', "").lower()

        # JSON 파일 로드
        try:
            with open("data/lectures.json", encoding="utf-8") as f:
                lectures_data = json.load(f)["lectures"]
        except Exception as e:
            dispatcher.utter_message(text="강의 정보를 불러오는 데 문제가 발생했습니다.")
            return []

        # 사용자 질문에서 어떤 강의 정보를 요청하는지 판단
        for lecture in lectures_data:
            subject = lecture["subject"].lower()
            if subject in user_message:
                # 어떤 정보가 필요한지 판단
                if "강의실" in user_message or "어디" in user_message:
                    dispatcher.utter_message(text=f"{lecture['subject']} 수업은 {lecture['classroom']}에서 진행됩니다.")
                elif "교수" in user_message:
                    dispatcher.utter_message(text=f"{lecture['subject']} 수업의 교수님은 {lecture['professor']}입니다.")
                elif "코드" in user_message:
                    dispatcher.utter_message(text=f"{lecture['subject']} 수업의 강의 코드는 {lecture['code']}입니다.")
                else:
                    # 전체 정보 응답
                    dispatcher.utter_message(
                        text=f"{lecture['subject']} 수업은 {lecture['classroom']}에서 열리고, "
                             f"{lecture['professor']} 교수님이 강의하며, 강의 코드는 {lecture['code']}입니다."
                    )
                return []

        dispatcher.utter_message(text="해당 강의 정보를 찾을 수 없습니다.")
        return []
