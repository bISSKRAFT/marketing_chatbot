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

OPENING_TIMES ="""
Die HAUPTAUSSTELLUNG\nApril – Oktober 2023:\nMo. – So.: 10:00 – 18:00 Uhr\nNovember 2023:\nMo. – So. 13:00 – 16:00 Uhr\nDezember 2023 – 8. Januar 2024:\xa0\nMo. – So. 11:00 – 17:00 Uhr\n9. Januar\xa0 –\xa0 März 2024:\nMo. – So.: 13:00 – 16:00 Uhr\n\xa0\nSonderöffnungszeiten:\n24.12.2023 (Heilig Abend): 10:00 – 13:00 Uhr\n31.12.2023 (Silvester):\xa0 \xa0 \xa0 \xa010:00 – 13:00 Uhr\n\xa0\nDer letzte Einlass ist immer 45 Minuten vor Schließung.\n\xa0\nDie Cafeteria mit neuer Sonderausstellung in der Johanniterscheune\n…wird zu den selben Zeiten ab dem 30. April wieder geöffnet sein.\n\n\xa0\n\xa0\nDer letzte Einlass ist immer 45 Minuten vor Schließung.\nWir freuen uns auf Ihren Besuch!
"""
mapping = {
    1: "januar",
    2: "märz",
    3: "märz",
    4: "april",
    5: "april",
    6: "april",
    7: "april",
    8: "april",
    9: "april",
    10: "oktober",
    11: "november",
    12: "dezember"
}

class ActionGetOpeningTimes(Action):

    def name(self) -> Text:
        return "action_get_opening_times"
    
    def _crawl_opening_times(self, url: str) -> str:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        extract_str = soup.find_all("div", class_="wpb_wrapper")[1].text.strip()
        return extract_str
    
    def _msg_builder(self, months: str, times: str):
        return f"Von {months} haben wir von {times} geöffnet.\n\n\nAndere Öffnungszeiten: {OPENING_TIMES}"
    
    def _set_default(self, 
                     day: int, 
                     month: int, 
                     url: str = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/") -> str:
        return f"Zu Heute, dem {day}.{month} wurden keine Öffnungszeiten gefunden. Sie könenne diese unter {url} einsehen."
    
    def _get_matches2(self, text: str, month: int, day: int):
        splits = text.split("\n")
        month_str = mapping[month]
        #print(splits)
        for idx, split in enumerate(splits):
            print("in for")
            time_split = split.split("–")
            if month == 11:
                if len(time_split) == 1:
                    if month_str in time_split[0].lower():
                            return split, splits[idx+1]
            if len(time_split) != 2:
                print("in continue")
                continue
            if month == 1 and day >= 9:
                print("in jan if")
                if month_str in time_split[0].lower():
                    return split, splits[idx+1]
                continue
            if month_str in time_split[0].lower():
                print("in month if 0")
                return split, splits[idx+1]
            if month_str in time_split[1].lower():
                print("in month if 1")
                return split, splits[idx+1]

    def _get_entity_values(self, tracker: Tracker) -> str:
        try:
            return tracker.latest_message["entities"][0]["value"]
        except Exception as e:
            print(f"\n\nERROR: {e}\n\n")
            return None
        
    def _generate_holiday_msg(self, holiday: str) -> str:
        if holiday.lower() == "silvester":
            return f"Am 31.12.2023 haben wir von 10:00 – 13:00 Uhr geöffnet\n\n\nAndere Öffnungszeiten: {OPENING_TIMES}"
        elif holiday.lower() == "weihnachten" or holiday.lower() == "heilig abend":
            return "Am 24.12.2023 haben wir von 10:00 – 13:00 Uhr geöffnet\n\n\nAndere Öffnungszeiten: {OPENING_TIMES}"
        
    def is_holiday(self, holiday: str) -> bool:
        if holiday.lower() == "silvester" or holiday.lower() == "weihnachten" or holiday.lower() == "heilig abend":
            return True
        return False


    def run(self, 
            dispather: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]):

        #TODO: tracker gives chat history
        url = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/"
        extract_str = self._crawl_opening_times(url)

        #TODO: extract right opening times from soup with tracker information
        #current_entity = tracker.latest_message["entities"][0]["entity"]
        current_ent = self._get_entity_values(tracker)
        if self.is_holiday(current_ent):
            msg = self._generate_holiday_msg(current_ent)
            dispather.utter_message(text=msg)
            return []
        crt_month = datetime.now().month
        crt_day = datetime.now().day

        try: 
            months_times, time_times = self._get_matches2(
                                                        text=extract_str, 
                                                        month=crt_month, 
                                                        day=crt_day)
        except Exception as e:
            msg = self._set_default(crt_day, crt_month)
            print(f"\n\nERROR: {e}\n\n")
            dispather.utter_message(text=msg)
            return []
        
        msg = self._msg_builder(months=months_times, times=time_times)
        
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
