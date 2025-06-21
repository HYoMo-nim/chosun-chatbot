from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime
import json
import os
import re
import pandas as pd
from difflib import get_close_matches

# ---------- 식당 메뉴 ----------
class ActionProvideMenu(Action):
    def name(self) -> Text:
        return "action_provide_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        json_path = os.path.join("data", "menu.json")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                menu_data = json.load(f)
        except Exception:
            dispatcher.utter_message(text="메뉴 데이터를 불러오는 데 문제가 발생했어요.")
            return []

        text = tracker.latest_message.get("text", "").lower()

        today_idx = datetime.datetime.today().weekday()
        weekday_map = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일"}

        day = next((d for d in weekday_map.values() if d in text), None)
        if not day and today_idx < 5:
            day = weekday_map[today_idx]
        elif not day:
            dispatcher.utter_message(text="주말에는 기숙사식당이 운영되지 않아요!")
            return []

        meal_time = "저녁" if "저녁" in text else "점심"

        if "솔마루" in text:
            restaurant = "솔마루식당"
            menu_sections = menu_data.get(restaurant, {})
            message = f"{restaurant}에서는 다음 코너 메뉴를 제공합니다:\n"
            for section, items in menu_sections.items():
                message += f"- {section}: {items}\n"
            dispatcher.utter_message(text=message)
        else:
            restaurant = "기숙사식당"
            try:
                today_menu = menu_data[restaurant][day][meal_time]
                dispatcher.utter_message(text=f"{restaurant}의 {day} {meal_time} 메뉴는 {today_menu}입니다.")
            except KeyError:
                dispatcher.utter_message(text=f"{restaurant}의 {day} {meal_time} 메뉴 정보가 없어요.")

        return []

# ---------- 공지사항 ----------
class ActionProvideNotice(Action):
    def name(self) -> Text:
        return "action_provide_notice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_text = tracker.latest_message.get('text', '').lower()
        path = os.path.join("data", "notice.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)["notices"]
        except:
            dispatcher.utter_message("공지사항 데이터를 불러올 수 없습니다.")
            return []

        filtered = []
        today = datetime.date.today().isoformat()
        if "오늘" in user_text:
            filtered = [n for n in data if n["date"] == today]
        else:
            for n in data:
                if any(date in user_text for date in [n["date"], n["date"].replace("-", ".")]):
                    filtered.append(n)

        keywords = ["장학", "수강", "행사", "채용", "복학", "졸업", "등록"]
        for k in keywords:
            if k in user_text:
                filtered += [n for n in data if k in n["title"].lower() or k in n["category"].lower()]

        filtered = list({n['title']:n for n in filtered}.values())
        if not filtered:
            filtered = data[:3]

        msg = "📢 공지사항:\n"
        for n in filtered[:5]:
            msg += f"- {n['title']} ({n['date']})\n  👉 {n['url']}\n"

        dispatcher.utter_message(msg.strip())
        return []

# ---------- 교수 정보 ----------
class ActionProfessorInfo(Action):
    def name(self) -> Text:
        return "action_professor_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_text = tracker.latest_message.get("text", "").strip()
        df = pd.read_excel("data/professor_data.xlsx")

        for _, row in df.iterrows():
            if str(row["교수명"]) in user_text:
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

# ---------- 과목 정보 ----------
class ActionCourseByName(Action):
    def name(self) -> Text:
        return "action_course_by_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_text = tracker.latest_message.get("text", "").strip()
        df = pd.read_excel("data/lecture_data.xlsx")
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

# ---------- 학사일정 ----------
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

        date_str = f"2025-{int(match.group(1)):02d}-{int(match.group(2)):02d}"
        try:
            with open("data/academic_schedule.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            dispatcher.utter_message(text="학사 일정을 불러오는 데 문제가 발생했습니다.")
            return []

        schedule = next((item["일정"] for item in data if item["날짜"] == date_str), None)
        if schedule:
            dispatcher.utter_message(text=f"📅 {match.group(1)}월 {match.group(2)}일 학사일정:\n{schedule}")
        else:
            dispatcher.utter_message(text=f"{match.group(1)}월 {match.group(2)}일에는 특별한 학사일정이 없습니다.")
        return []

# ---------- 동아리 ----------
class ActionShowClubEvents(Action):
    def name(self) -> Text:
        return "action_show_club_events"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            filepath = os.path.join("data", "external", "club_events.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            events = data.get("events", [])
            if not events:
                dispatcher.utter_message(text="현재 등록된 행사 정보가 없습니다.")
                return []
            message = "현재 진행 중이거나 예정된 행사 목록입니다:\n\n"
            for idx, event in enumerate(events[:5], 1):
                message += f"{idx}. {event['title']} - {event['date']}\n"
            if len(events) > 5:
                message += f"\n... 외 {len(events) - 5}개의 행사가 더 있습니다. 특정 행사명을 말씀해 주세요."
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
            event_name = tracker.get_slot("event_name")
            if not event_name:
                dispatcher.utter_message(text="어떤 행사에 대해 알고 싶으신가요?")
                return []

            filepath = os.path.join("data", "external", "club_events.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            events = data.get("events", [])
            matches = get_close_matches(event_name, [e["title"] for e in events], n=1, cutoff=0.6)
            if not matches:
                dispatcher.utter_message(text=f"'{event_name}' 행사에 대한 정보를 찾을 수 없습니다.")
                return []

            matched_event = next((e for e in events if e["title"] == matches[0]), None)
            if not matched_event:
                dispatcher.utter_message(text=f"'{event_name}' 행사에 대한 정보를 찾을 수 없습니다.")
                return []

            message = f"'{matched_event['title']}' 행사 정보입니다:\n\n날짜: {matched_event['date']}\n"
            if matched_event.get('link'):
                message += f"자세한 정보: {matched_event['link']}\n"
            dispatcher.utter_message(text=message)
        except Exception as e:
            dispatcher.utter_message(text=f"행사 세부 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
        return []

# ---------- FAQ ----------
class ActionShowFaqList(Action):
    def name(self) -> Text:
        return "action_show_faq_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            filepath = os.path.join("data", "external", "faq.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            faqs = data.get("faqs", [])
            if not faqs:
                dispatcher.utter_message(text="현재 등록된 FAQ가 없습니다.")
                return []

            message = "자주 묻는 질문 목록입니다:\n\n"
            for idx, faq in enumerate(faqs[:5], 1):
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
            user_question = tracker.latest_message.get("text", "")
            filepath = os.path.join("data", "external", "faq.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            faqs = data.get("faqs", [])
            if not faqs:
                dispatcher.utter_message(text="현재 등록된 FAQ가 없습니다.")
                return []

            questions = [faq["question"] for faq in faqs]
            matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
            if not matches:
                dispatcher.utter_message(text="죄송합니다. 질문에 맞는 답변을 찾을 수 없습니다. 다른 방식으로 질문해 주세요.")
                return []

            matched_faq = next((faq for faq in faqs if faq["question"] == matches[0]), None)
            if not matched_faq:
                dispatcher.utter_message(text="죄송합니다. 질문에 맞는 답변을 찾을 수 없습니다.")
                return []

            message = f"Q: {matched_faq['question']}\n\nA: {matched_faq['answer']}"
            dispatcher.utter_message(text=message)
        except Exception as e:
            dispatcher.utter_message(text=f"FAQ 답변을 찾는 중 오류가 발생했습니다: {str(e)}")
        return []
