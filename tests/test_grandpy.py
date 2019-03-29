# -*-coding:Utf-8 -*


import grandpy.grandpy as grandpy
import pytest

test_data = grandpy.DataMgt("Salut GrandPy ! Est-ce que tu connais l'adresse d'OpenClassrooms à Paris ?")

class mock_get_map():
    # Class to mock requests.get for Google Maps API
    #  A class is used to add a join() method, to return the result in the right format

    def __init__(self, url, params=None):
        pass

    def json(self):
        result = {
            "candidates": [
                {
                    "formatted_address": "7 Cité Paradis, 75010 Paris, France",
                    "geometry": {
                        "location": {
                            "lat": 48.8747265,
                            "lng": 2.3505517
                        },
                        "viewport": {
                            "northeast": {
                                "lat": 48.87616082989272,
                                "lng": 2.351921729892723
                            },
                            "southwest": {
                                "lat": 48.87346117010728,
                                "lng": 2.349222070107278
                            }
                        }
                    },
                    "name": "Openclassrooms"
                }
            ],
            "status": "OK"
        }

        return result

class mock_get_wiki():
    # Class to mock requests.get for Wikipedia API

    def __init__(self, url, params=None):
        pass

    def json(self):
        result = {
            "batchcomplete": "",
            "continue": {
                "sroffset": 10,
                "continue": "-||"
            },
            "query": {
                "searchinfo": {
                    "totalhits": 3176
                },
                "search": [
                    {
                        "ns": 0,
                        "title": "Cité Paradis",
                        "pageid": 5653202,
                        "size": 2777,
                        "wordcount": 232,
                        "snippet": "homonymes, voir <span class=\"searchmatch\">Paradis</span> (homonymie). La <span class=\"searchmatch\">cité</span> <span class=\"searchmatch\">Paradis</span> est une voie publique située dans le 10e arrondissement de <span class=\"searchmatch\">Paris</span>. La <span class=\"searchmatch\">cité</span> <span class=\"searchmatch\">Paradis</span> est une voie publique",
                        "timestamp": "2018-08-08T11:50:07Z"
                    }
                    ]
                }
            }
        return result

def mock_random(start, end):
    # Mock random.randint() 
    return 0

def test_parse():
    assert test_data.answer == "OpenClassrooms Paris"


def test_find_location(monkeypatch):

    monkeypatch.setattr('requests.get', mock_get_map)


    test_data.find_location()

    assert test_data.place_address == "7 Cité Paradis, 75010 Paris, France"
    assert test_data.place_coord == {
                    "location": {
                        "lat": 48.8747265,
                        "lng": 2.3505517
                    },
                    "viewport": {
                        "northeast": {
                            "lat": 48.87616082989272,
                            "lng": 2.351921729892723
                        },
                        "southwest": {
                            "lat": 48.87346117010728,
                            "lng": 2.349222070107278
                        }
                    }
                }
    assert test_data.map_status == "OK"


def test_extract_wiki(monkeypatch):

    # Mock requests.get + random to bybass the random result and ensure comparison is possible
    monkeypatch.setattr('requests.get', mock_get_wiki)
    monkeypatch.setattr('random.randint', mock_random)

    test_data.extract_wiki()

    assert test_data.wiki_page_title == "Cité Paradis"
    assert test_data.wiki_snippet == "homonymes, voir <span class=\"searchmatch\">Paradis</span> (homonymie). La <span class=\"searchmatch\">cité</span> <span class=\"searchmatch\">Paradis</span> est une voie publique située dans le 10e arrondissement de <span class=\"searchmatch\">Paris</span>. La <span class=\"searchmatch\">cité</span> <span class=\"searchmatch\">Paradis</span> est une voie publique"
