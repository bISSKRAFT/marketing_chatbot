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
            msg = "Wenn du etwas über die Öffnungszeiten wissen möchtest, dann frage mich einfach nach Öffnungszeiten"
            dispather.utter_message(text=msg)
        pass
