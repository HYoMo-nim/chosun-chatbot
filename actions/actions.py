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
