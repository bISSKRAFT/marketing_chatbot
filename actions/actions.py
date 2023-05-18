# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Text
from datetime import datetime
from bs4 import BeautifulSoup
import re
import requests
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker

# source: https://learning.rasa.com/conversational-ai-with-rasa/custom-actions/

"""
'Die HAUPTAUSSTELLUNG\nApril – Oktober 2023:\nMo. – So.: 10:00 – 18:00 Uhr\nNovember 2023:\nMo. – So. 13:00 – 16:00 Uhr\nDezember 2023 – 8. Januar 2024:\xa0\nMo. – So. 11:00 – 17:00 Uhr\n9. Januar\xa0 –\xa0 März 2024:\nMo. – So.: 13:00 – 16:00 Uhr\n\xa0\nSonderöffnungszeiten:\n24.12.2023 (Heilig Abend): 10:00 – 13:00 Uhr\n31.12.2023 (Silvester):\xa0 \xa0 \xa0 \xa010:00 – 13:00 Uhr\n\xa0\nDer letzte Einlass ist immer 45 Minuten vor Schließung.\n\xa0\nDie Cafeteria mit neuer Sonderausstellung in der Johanniterscheune\n…wird zu den selben Zeiten ab dem 30. April wieder geöffnet sein.\n\n\xa0\n\xa0\nDer letzte Einlass ist immer 45 Minuten vor Schließung.\nWir freuen uns auf Ihren Besuch!\n\n\n\nFührung Buchen'
"""

class ActionGetOpeningTimes(Action):

    def name(self) -> Text:
        return "action_get_opening_times"
    
    def _set_default(day: int, month: int, url: str) -> str:
        return f"Zu Heute, dem {day}.{month} wurden keine Öffnungszeiten gefunden. Sie könenne diese unter {url} finden."
    
    def _get_matches(self, pattern: str, text: str, month: int , day: int):
        matches = re.finditer(pattern, text, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            
            if matchNum > 2:
                return None, None
            if month == 1 and day < 9:
                if matchNum == 1:
                    return match.group(2), match.group(3)
            if month == 1 and day >= 9:
                if matchNum == 2:
                    return match.group(2), match.group(3)
            return match.group(2), match.group(3)
            
    
    def run(self, dispather: CollectingDispatcher, tracker: Tracker):
        #TODO: tracker gives chat history
        url = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        soup.find_all("div", class_="wpb_wrapper")[1].text.strip()

        #TODO: extract right opening times from soup with tracker information
        current_entity = next(tracker.get_latest_entity_values("holiday"), None)
        crt_month = datetime.now().month
        crt_day = datetime.now().day

        if current_entity:
            #TODO: extract opening times for holiday
            pass

        if crt_month in range(4,11):
            pattern = r"(April..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, soup, crt_month, crt_day)
            if start == None or end == None:
                 msg = self._set_default(crt_day, crt_month, url)
            msg = f"Von April bis Oktober haben wir von {start} bis {end} geöffnet."
        elif crt_month == 11:
            pattern = r"(November..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, soup, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im November haben wir von {start} bis {end} geöffnet."
        elif crt_month == 12:
            pattern = r"(Dezember..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, soup, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im Dezember haben wir von {start} bis {end} geöffnet."
        elif crt_month == 1 and crt_day <= 8:
            pattern = r"(Januar..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, soup, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im Januar haben wir bis zum 8. von {start} bis {end} geöffnet."
        elif crt_month in range(1,4):
            #TODO: january - march
            pattern = r"(Januar..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, soup, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im Januar haben wir ab dem 9. von {start} bis {end} geöffnet."
        dispather.utter_message(text=msg)
        return []
