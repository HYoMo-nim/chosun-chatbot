import pandas as pd
import json
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# 파일 경로
PROFESSOR_FILE = "data/professor_data.xlsx"
LECTURE_FILE = "data/lecture_data.xlsx"
ACADEMIC_JSON = "data/academic_schedule.json"


# 교수 정보 조회
class ActionProfessorInfo(Action):
    def name(self) -> Text:
        return "action_professor_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_text = tracker.latest_message.get("text", "").strip()
        df = pd.read_excel(PROFESSOR_FILE)

        for _, row in df.iterrows():
            professor_name = str(row["교수명"])
            if professor_name != "nan" and professor_name in user_text:
                response = (
                    f"🔹 학과: {row['학과']}\n"
                    f"🔹 직책: {row['직책']}\n"
                    f"🔹 연구실: {row['연구실']}\n"
                    f"🔹 이메일: {row['이메일']}\n"
                    f"🔹 담당과목: {row['담당과목']}"
                )
                dispatcher.utter_message(text=response)
                return []

        dispatcher.utter_message(text="해당 교수님 정보를 찾을 수 없습니다.")
        return []


# 과목명 기반 강의 정보 조회
class ActionCourseByName(Action):
    def name(self) -> Text:
        return "action_course_by_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_text = tracker.latest_message.get("text", "").strip()
        df = pd.read_excel(LECTURE_FILE)

        matched_rows = df[df["교과목명"].astype(str).apply(lambda x: x in user_text)]

        if matched_rows.empty:
            dispatcher.utter_message(text=f"'{user_text}' 과목 정보를 찾을 수 없습니다.")
            return []

        messages = []
        for _, row in matched_rows.iterrows():
            msg = (
                f"📌 개설대학: {row['개설대학']}\n"
                f"📌 개설학과: {row['개설학과']}\n"
                f"📌 이수구분: {row['이수구분']}\n"
                f"📌 과목코드: {row['과목코드']}\n"
                f"📌 분반: {row['분반']}\n"
                f"📌 교과목명: {row['교과목명']}\n"
                f"📌 주야: {row['주야']}\n"
                f"📌 학점: {row['학점']}\n"
                f"📌 담당교원: {row['담당교원']}\n"
                f"📌 강의실: {row['강의실']}\n"
                f"📌 강의시간: {row['강의시간']}"
            )
            messages.append(msg)

        dispatcher.utter_message(text="\n---\n".join(messages))
        return []


# 학사일정 조회
class ActionAcademicSchedule(Action):
    def name(self) -> str:
        return "action_academic_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]) -> List[Dict[str, Any]]:

        user_text = tracker.latest_message.get("text", "").strip()
        match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", user_text)
        if not match:
            dispatcher.utter_message(text="날짜를 '6월 30일' 형식으로 입력해 주세요.")
            return []

        month = int(match.group(1))
        day = int(match.group(2))
        date_str = f"2025-{month:02d}-{day:02d}"

        try:
            with open(ACADEMIC_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            dispatcher.utter_message(text="학사 일정을 불러오는 데 문제가 발생했습니다.")
            return []

        schedule = next((item["일정"] for item in data if item["날짜"] == date_str), None)

        if schedule:
            dispatcher.utter_message(text=f"📅 {month}월 {day}일 학사일정:\n{schedule}")
        else:
            dispatcher.utter_message(text=f"{month}월 {day}일에는 특별한 학사일정이 없습니다.")

        return []

