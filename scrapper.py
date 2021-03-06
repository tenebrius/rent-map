import os.path
import time
from pprint import pprint

from bs4 import BeautifulSoup
from urllib.request import urlopen

import json
import urllib.parse
import pprint

import requests

db = None
db_path ='scrapper_db.json'

def load_db():
    global db
    if os.path.exists(db_path):
        f = open(db_path, 'r', encoding="utf-8")
        db = json.load(f)
        f.close()
    else:
        db=[]


def save_db():
    global db
    if db:
        with open(db_path, 'w', encoding='utf-8') as outfile:
            json.dump(db, outfile, ensure_ascii=False)


def download_all(start, end):
    load_db()
    global db
    total_items = 0
    for x in range(start, end):
        url = f"https://sz.lianjia.com/zufang/pg{x}/"
        print("downloading page", url)
        items = download_page(url)
        total_items = total_items + len(items)
        db = db + items
        save_db()
        print(f"downloaded {total_items}")
        time.sleep(3)


def download_page(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    items = []

    for block in soup.findAll("div", {"class": "content__list--item"}):
        item = []
        # content__list - -item - price
        price = block.find("span", {"class": "content__list--item-price"}).find("em").get_text()
        title = block.find("a", {"class": "twoline"})
        if title:
            type = title.get_text().replace("\n", "").strip()[0:2]
            if type == '合租':
                continue
            item.append(price)
            for piece in block.find("p", {"class": "content__list--item--des"}):
                text = piece.getText().replace("/", "").replace("-", "").strip()
                if "仅剩" in text:
                    continue
                else:
                    if len(text) > 0:
                        item.append(text)
            items.append(item)
    return items


def clean_lanjia_scrap ():
    f = open('lanjia_scrap.json', 'r', encoding="utf-8")
    data = json.load(f)

    nItems = []
    for item in data:
        nItem = [p for p in item if p != "精选"]
        nItems.append(nItem)

    prices = []
    locs = []
    areas = []
    items = []
    for item in nItems:
        price = int(item.pop(0))
        prices.append(price)

        loc = item.pop(0) + "-" + item.pop(0)
        # locs1.append(item.pop(0))
        # locs2.append(item.pop(0))
        if len(item) == 5:
            loc = loc + "-" + str(item.pop(0))
        locs.append(loc)
        area = int(float(item.pop(0).replace("㎡", "")))
        areas.append(area)
        items.append([str(area), loc, str(price)])

    with open("lanjia.json", 'w', encoding='utf-8') as outfile:
        json.dump(items, outfile, ensure_ascii=False)

if __name__ == '__main__':
    # load_db()
    # download_all(1000, 1500)
    clean_lanjia_scrap()