import json
import urllib.parse
import pprint

import requests

loc_db = None
keys = None

def load_keys():
    global keys
    f = open('keys.json', 'r', encoding="utf-8")
    keys = json.load(f)
    f.close()

def load_loc_db():
    global loc_db
    f = open('loc_db.json', 'r', encoding="utf-8")
    loc_db = json.load(f)
    f.close()


def save_loc_db():
    if loc_db:
        with open('loc_db.json', 'w', encoding='utf-8') as outfile:
            json.dump(loc_db, outfile, ensure_ascii=False)


def getCoords(place, offlineOnly=False):
    if place in loc_db:
        return loc_db[place]
    else:
        if not offlineOnly:
            coords = fetch_online_baidu(place)
            loc_db[place] = coords
            save_loc_db()
            return coords
        else:
            raise Exception("no offline data")


def fetch_online_mapbox(place):
    print("fetching online mapbox", place)
    enc_place = urllib.parse.quote(place)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{enc_place}.json?access_token=${keys['mapbox_token']}"
    # print(url)
    r = requests.get(url)
    if r.ok:
        js = r.json()
        # pprint.pprint(js)
        feature = js["features"][0]
        # print(feature)
        return {"lat": feature["center"][0], "lng": feature["center"][1]}

    else:
        raise Exception(r.status_code, r.content)


def fetch_online_google(place):
    print("fetching online google", place)
    enc_place = urllib.parse.quote(place)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={enc_place}&key={keys['google_key']}"
    # print(url)
    r = requests.get(url)
    if r.ok:
        js = r.json()
        # pprint.pprint(js)
        feature = js["results"][0]
        # print(feature)
        return feature["geometry"]["location"]

    else:
        raise Exception(r.status_code, r.content)


def fetch_online_baidu(place):
    print("fetching online baidu", place)
    enc_place = urllib.parse.quote(place)
    url = f"https://api.map.baidu.com/geocoding/v3/?address={enc_place}&output=json&ak={keys['baidu_key']}"
    # print(url)
    r = requests.get(url)
    if r.ok:
        js = r.json()
        # pprint.pprint(js)
        # print(feature)
        return js["result"]["location"]

    else:
        raise Exception(r.status_code, r.content)


load_keys()