from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime
import json
import os


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
        except Exception as e:
            dispatcher.utter_message(text="메뉴 데이터를 불러오는 데 문제가 발생했어요.")
            return []

        text = tracker.latest_message.get("text", "").lower()

        today_idx = datetime.datetime.today().weekday()
        weekday_map = {
            0: "월요일", 1: "화요일", 2: "수요일",
            3: "목요일", 4: "금요일"
        }

        day = None
        for d in weekday_map.values():
            if d in text:
                day = d
                break

        if not day and today_idx < 5:
            day = weekday_map[today_idx]
        elif not day:
            dispatcher.utter_message(text="주말에는 기숙사식당이 운영되지 않아요!")
            return []

        if "저녁" in text:
            meal_time = "저녁"
        else:
            meal_time = "점심"

        if "솔마루" in text:
            restaurant = "솔마루식당"
            menu_sections = menu_data.get(restaurant, {})
            message = f"{restaurant}에서는 다음 코너 메뉴를 제공합니다:\n"
            for section, items in menu_sections.items():
                message += f"- {section}: {items}\n"
            dispatcher.utter_message(text=message)
            return []

        else:
            restaurant = "기숙사식당"
            try:
                today_menu = menu_data[restaurant][day][meal_time]
                dispatcher.utter_message(
                    text=f"{restaurant}의 {day} {meal_time} 메뉴는 {today_menu}입니다.")
            except KeyError:
                dispatcher.utter_message(
                    text=f"{restaurant}의 {day} {meal_time} 메뉴 정보가 없어요.")
            return []




class ActionProvideNotice(Action):
    def name(self) -> Text:
        return "action_provide_notice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 사용자가 입력한 문장
        user_text = tracker.latest_message.get('text', '').lower()

        # 공지사항 파일 경로
        path = os.path.join("data", "notice.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)["notices"]
        except:
            dispatcher.utter_message("공지사항 데이터를 불러올 수 없습니다.")
            return []

        filtered = []

        # 날짜 필터링 (오늘, 날짜 포함 여부)
        today = datetime.date.today().isoformat()
        if "오늘" in user_text:
            filtered = [n for n in data if n["date"] == today]
        else:
            for n in data:
                if any(date in user_text for date in [n["date"], n["date"].replace("-", ".")]):
                    filtered.append(n)

        # 키워드 또는 카테고리 필터링
        keywords = ["장학", "수강", "행사", "채용", "복학", "졸업", "등록"]
        for k in keywords:
            if k in user_text:
                filtered += [n for n in data if k in n["title"].lower() or k in n["category"].lower()]

        # 중복 제거
        filtered = list({n['title']:n for n in filtered}.values())

        # 기본: 전체 상위 3개
        if not filtered:
            filtered = data[:3]

        # 응답 구성
        msg = "📢 공지사항:\n"
        for n in filtered[:5]:
            msg += f"- {n['title']} ({n['date']})\n  👉 {n['url']}\n"

        dispatcher.utter_message(msg.strip())
        return []
