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

from typing import Text, Dict, Any, List
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
    
    def _crawl_opening_times(self, url: str) -> str:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        extract_str = soup.find_all("div", class_="wpb_wrapper")[1].text.strip()
        return extract_str
    
    def _msg_builder(self, start: str, end: str, day: int, month: int):
        if start == "" or end == "":
             return self._set_default(day, month)
        return f"Am {day}.{month} haben wir von {start} bis {end} geöffnet."
    
    def _set_default(self, 
                     day: int, 
                     month: int, 
                     url: str = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/") -> str:
        return f"Zu Heute, dem {day}.{month} wurden keine Öffnungszeiten gefunden. Sie könenne diese unter {url} einsehen."
    
    def _get_matches(self, regex: str, text: str, month: int , day: int):
        #print("text: ",text)

        pass

    def run(self, 
            dispather: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]):

        #TODO: tracker gives chat history
        url = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/"
        extract_str = self._crawl_opening_times(url)

        #TODO: extract right opening times from soup with tracker information
        current_entity = next(tracker.get_latest_entity_values("holiday"), None)
        crt_month = datetime.now().month
        crt_day = datetime.now().day

        if current_entity:
            #TODO: extract opening times for holiday
            pass
        if crt_month in range(4,11):
            regex = r"(April..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(regex=regex,
                                           text=extract_str,
                                           month=crt_month,
                                           day=crt_day)
            msg = self._msg_builder(start, end, crt_day, crt_month)
        #TODO: refactor
        elif crt_month == 11:
            pattern = r"(November..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, extract_str, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im November haben wir von {start} bis {end} geöffnet."
        elif crt_month == 12:
            pattern = r"(Dezember..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, extract_str, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im Dezember haben wir von {start} bis {end} geöffnet."
        elif crt_month == 1 and crt_day <= 8:
            pattern = r"(Januar..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, extract_str, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im Januar haben wir bis zum 8. von {start} bis {end} geöffnet."
        elif crt_month in range(1,4):
            pattern = r"(Januar..).*?(\d{2}:\d{2}) – (\d{2}:\d{2})"
            start, end = self._get_matches(pattern, extract_str, crt_month, crt_day)
            if start == None or end == None:
                    msg = self._set_default(crt_day, crt_month, url)
            msg = f"Im Januar haben wir ab dem 9. von {start} bis {end} geöffnet."
        dispather.utter_message(text=msg)
        return []

class ActionGetPrices(Action):
    def name(self) -> Text:
        return "action_get_price"

    def run(self, dispather: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        prices = self.scrape_prices()
        msg = self.prices_to_string(prices)
        dispather.utter_message(text=msg)


    def scrape_prices(self):
        url = "https://www.kriminalmuseum.eu/besucherplaner/preise/"
        html = requests.get(url).text

        data = []
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all("table")[0]
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) # Get rid of empty values

        return data
    
    def prices_to_string(self, prices):
        price_string = ""
        for price in prices:
            price_string += price[0] + price[1] + "\n" + "-----------------------" + "\n"
        return price_string
