# -*-coding:Utf-8 -*

import requests
import re
import random
import os

from flask import Flask, render_template, request, session, url_for, jsonify

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

global_stop_words = app.config['STOP_WORDS']
special_chars = app.config['SPECIAL_CHARS']
context_stop_words = ["grandpy", "grand-py",
    "bonjour", "salut", "hello", "bye", "sil", "plait", "plaît", 
    "estce", "connais", "adresse", "saistu", "sais", "trouve"]
all_stop_words = global_stop_words + special_chars + context_stop_words

map_url = app.config['MAP_URL']
map_querystring = app.config['MAP_QUERYSTRING']
wiki_url = app.config['WIKI_URL']
wiki_querystring = app.config['WIKI_QUERYSTRING']


class DataMgt:
    # Class defined to manage and store necessary information

    def __init__(self, question_text):
        self.question_text = question_text
        self.place_address = ""
        self.place_coord = ""
        self.wiki_page_title = ""
        self.wiki_snippet = ""

    @property
    def answer(self):
        answer = ""

        # Remove special characters
        # Parse all chars to remove special chars, then join remaining ones
        #   to build and updated string
        for char in self.question_text:
            if char in special_chars:
                self.question_text = self.question_text.replace(char, ' ')

        # Remove all stop words (and remove potential spaces at the end of the string)
        #  Parse words to remove stop words and buld the string back
        answer = ' '.join([word for word in self.question_text.split(" ")
            if word.lower() not in all_stop_words]).strip()
        
        return answer

    def find_location(self):
        # Retreive information from Google Maps API
        map_querystring["input"] = self.answer
        map_req = requests.get(map_url, params=map_querystring)
        self.map_status = "KO"
        if len(map_req.json()["candidates"]) > 0:
            # If the place has been found, store the wanted informations
            self.place_address = map_req.json()["candidates"][0]["formatted_address"]
            self.place_coord = map_req.json()["candidates"][0]["geometry"]
            self.map_status = "OK"

    def extract_wiki(self):

        # Remove figures and unwanted words from parsed user's question
        # Then, new criterai will be related to address found with only key words
        search_criteria = ""
        search_criteria = ' '.join([word for word 
            in self.place_address.replace(",", "").split(" ") 
            if not (re.match("^([0-9]+)$", word) or word =="France")])

        # Search wiki info related to place's address
        wiki_querystring["srsearch"] = search_criteria
        wiki_req = requests.get(wiki_url, params=wiki_querystring)

        # Information is stored only if at least 1 page was found
        # (Very few chances that no values are returned - no case found during tests)
        # Among the results, one is randomly choosen
        if wiki_req.json()["query"]["searchinfo"]["totalhits"] > 0:
            page_nb = random.randint(0, len(wiki_req.json()["query"]["search"]) - 1)
            self.wiki_page_title = wiki_req.json()["query"]["search"][page_nb]["title"]
            self.wiki_snippet = wiki_req.json()["query"]["search"][page_nb]["snippet"]


appData = DataMgt("")

@app.route('/_question')
def answer_question():
    # Fake route to manage AJAX exchanges
    # This will launch API requests to gather related information

    appData.question_text = request.args.get("msg")

    appData.find_location()

    # Look for wiki infomations only if an emplacement was found
    if appData.map_status == "OK":
        appData.extract_wiki()

    # Format data tha will be sent back to AJAX request
    result = {"map_status": appData.map_status, "address":appData.place_address,
        "coord":appData.place_coord, "wiki_page_title": appData.wiki_page_title,
        "wiki_snippet": appData.wiki_snippet}
    return jsonify(result)

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")