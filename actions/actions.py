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
from bs4 import BeautifulSoup
import requests
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker

# source: https://learning.rasa.com/conversational-ai-with-rasa/custom-actions/

opening_times_db = {
    'april-bis-oktober': 'Mo. - So.: 10:00 bis 18:00 Uhr',
    'november': 'Mo. - So.: 13:00 bis 16:00 Uhr',
    'dezember-bis-januar': 'bis 8. Januar: Mo. - So.: 11:00 bis 17:00 Uhr',
    'januar-bis-maerz': 'ab 9. Januar: Mo. - So.: 13:00 bis 16:00 Uhr',
    'weihnachten': 'An Heiligabend haben wir für Sie von 10:00 bis 13:00 Uhr geöffnet',
    'silvester': 'An Silvester haben wir für Sie von 10:00 bis 13:00 Uhr geöffnet',
}

class ActionGetOpeningTimes(Action):

    def name(self) -> Text:
        return "action_get_opening_times"
    
    def run(self, dispather: CollectingDispatcher, tracker: Tracker):
        #TODO: tracker gives chat history
        url = "https://www.kriminalmuseum.eu/besucherplaner/oeffnungszeiten/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        soup.find_all("div", class_="wpb_wrapper")[1].text.strip()

        #TODO: extract right opening times from soup with tracker information
        current_entity = next(tracker.get_latest_entity_values("holiday"), None)

        if not current_entity:
            # TODO: was wenn kein "holiday" erkannt wurde?
            msg = "Es tut mir leid, das habe ich nicht richtig verstanden. Wenn du etwas über die Öffnungszeiten wissen möchtest, dann frage einfach nach Öffnungszeiten"
            dispather.utter_message(text=msg)
        pass


class ActionGetPrices(Action):

    def name(self) -> Text:
        return "action_get_price"

    def run(self, dispather: CollectingDispatcher, tracker: Tracker):
        prices = self.scrape_prices()
        msg = self.prices_to_string(prices)
        dispather.utter_message(text=msg)


    def scrape_prices():
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
    
    def prices_to_string(prices):
        price_string = ""
        for price in prices:
            price_string += price[0] + ": " + price[1] + "\n"

