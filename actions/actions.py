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
# %%
from typing import Text, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import requests
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker

# source: https://learning.rasa.com/conversational-ai-with-rasa/custom-actions/

OPENING_TIMES ="""
\n\nDie Hauptausstellung:\nApril – Oktober 2023:\nMo. – So.: 10:00 – 18:00 Uhr\nNovember 2023:\nMo. – So. 13:00 – 16:00 Uhr\nDezember 2023 – 8. Januar 2024:\xa0\nMo. – So. 11:00 – 17:00 Uhr\n9. Januar\xa0 –\xa0 März 2024:\nMo. – So.: 13:00 – 16:00 Uhr\n\xa0\nSonderöffnungszeiten:\n24.12.2023 (Heilig Abend):\xa0 \xa010:00 – 13:00 Uhr\n31.12.2023 (Silvester):\xa0 \xa010:00 – 13:00 Uhr\n\n\n\n\nDer letzte Einlass ist immer 45 Minuten vor Schließung.\nWir freuen uns auf Ihren Besuch!
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

time_mapping = [
    "morgen",
    "heute",
]

def crawl_opening_times(url: str = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/") -> str:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    extract_str = soup.find_all("div", class_="wpb_wrapper")[1].text.strip()
    return extract_str

def get_holiday_times(text: str, holiday: str) -> str:
    text = text.replace("\xa0", "")
    split = text.split("\n")
    for entry in split:
        if holiday is "24.12":
            if "24.12." in entry:
                return entry
        if holiday is "31.12":
            if "31.12." in entry:
                return entry
    return ""

def split_date_and_time(text: str) -> Tuple[str, str]:
    split = text.split(": ")
    return split[0].strip(), split[1].strip()

class ActionGetOpeningTimes(Action):

    def name(self) -> Text:
        return "action_get_opening_times"
    
    def _msg_builder(self, months: str, times: str):
        return f"\nWeitere Öffnungszeiten: {OPENING_TIMES}\nGEFUNDENE ÖFFNUNGSZEITEN:\nVon {months.strip(':')} haben wir von {times} geöffnet.\nWeitere Öffnungszeiten können vorherigen Nachrichten entnommen werden."
    
    def _set_default(self, 
                     day: int, 
                     month: int, 
                     url: str = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/") -> str:
        return f"Zu Heute, dem {day}.{month} wurden keine Öffnungszeiten gefunden. Sie können diese unter {url} einsehen. \nAlternativ hier ein Ausschnitt: {OPENING_TIMES}"
    
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
            print(f"\n\nERROR IN FETCHING ENTITY: {e}\n\n")
            return None
        
    # def _generate_holiday_msg(self, holiday: str) -> str:
    #     if holiday.lower() == "silvester":
    #         return f"Am 31.12.2023 haben wir von 10:00 – 13:00 Uhr geöffnet\n\n\nAndere Öffnungszeiten: {OPENING_TIMES}"
    #     elif holiday.lower() == "weihnachten" or holiday.lower() == "heilig abend":
    #         return f"Am 24.12.2023 haben wir von 10:00 – 13:00 Uhr geöffnet\n\n\nAndere Öffnungszeiten: {OPENING_TIMES}"
        
    # def is_holiday(self, text: str) -> bool:
    #     if text.lower() == "silvester" or text.lower() == "weihnachten" or text.lower() == "heilig abend":
    #         return True
    #     return False
    
    def is_time(self, text: str) -> bool:
        if text.lower() in time_mapping:
            return True
        return False
    
    def _calculate_time(self, days: int = 0) -> Tuple[int,int]:
        new_time = datetime.now() + timedelta(days=days)
        return new_time.month, new_time.day

    def run(self, 
            dispather: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]):

        extract_str = crawl_opening_times()

        current_ent = self._get_entity_values(tracker)

        crt_month = datetime.now().month
        crt_day = datetime.now().day

        if current_ent is not None:
            if self.is_time(current_ent):
                if current_ent.lower() == time_mapping[0]:
                    crt_month, crt_day = self._calculate_time(1)
                    print(f'calculated month: {crt_month}\ncalculated day: {crt_day}')

        try: 
            months_times, time_times = self._get_matches2(
                                                        text=extract_str, 
                                                        month=crt_month, 
                                                        day=crt_day
                                                        )
        except Exception as e:
            msg = self._set_default(crt_day, crt_month)
            print(f"\n\nERROR: {e}\n\n")
            dispather.utter_message(text=msg)
            return []
        
        msg = self._msg_builder(months=months_times, times=time_times)
        
        dispather.utter_message(text=msg)
        return []

class ActionGetChristmasOpeningTimes(Action):
    def name(self) -> Text:
        return "action_get_christmas_opening_times"
    
    def _msg_builder(self, text: str) -> str:
        date , time = split_date_and_time(text)
        return f"Am {date} haben wir von {time} geöffnet.\nAndere Öffnungszeiten: {OPENING_TIMES}"
    
    def run(self, dispather: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        crawled_opening_times = crawl_opening_times()
        extr_times = get_holiday_times(crawled_opening_times, "24.12")
        msg = self._msg_builder(extr_times)
        dispather.utter_message(text=msg)
        return []
    
class ActionGetNewYearsOpeningTimes(Action):
    def name(self) -> Text:
        return "action_get_new_years_opening_times"
    
    def _msg_builder(self, text: str) -> str:
        date , time = split_date_and_time(text)
        return f"Am {date} haben wir von {time} geöffnet.\nAndere Öffnungszeiten: {OPENING_TIMES}"
    
    def run(self, dispather: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        crawled_opening_times = crawl_opening_times()
        extr_times = get_holiday_times(crawled_opening_times, "31.12")
        msg = self._msg_builder(extr_times)
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
            price_string += price[0].replace("\n", " ").replace(":", "") + "  |  " + price[1] + "\n"
        return price_string
