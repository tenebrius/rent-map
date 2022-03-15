import os.path
import time
from pprint import pprint

from bs4 import BeautifulSoup
from urllib.request import urlopen

import json
import urllib.parse
import pprint

import requests
from playwright.sync_api import sync_playwright

db = None
db_path ='scrapper_58_db.json'

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
        url = f"https://sz.zu.anjuke.com/fangyuan/p{x}/?kw=&k_comm_id=/"
        print("downloading page", url)
        items = download_page(url)
        total_items = total_items + len(items)
        db = db + items
        save_db()
        print(f"downloaded {total_items}")
        time.sleep(5)


def download_page(url):
    html = ""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
    if ("访问过于频繁" in html):
        raise Exception("locked out")
    # with open("58.html", 'w', encoding='utf-8') as outfile:
    #     outfile.write(html)
    # return
    # html = ""
    # with open("58.html", 'r', encoding='utf-8') as outfile:
    #     html = outfile.read()
    soup = BeautifulSoup(html, "html.parser")

    items = []
    for block in soup.findAll("div", {"class": "zu-itemmod"}):
        item = []
        room = block.find("p", {"class": "details-item"}).get_text().split("|")[1].replace("平米", "")
        locs = block.find("address", {"class": "details-item"}).get_text().split("\n")
        locs = [loc.strip(" ") for loc in locs]
        locs = [loc for loc in locs if len(loc)>0]
        locs = locs[1].replace(" ", "-").split("-")
        price = block.find("div", {"class": "zu-side"}).find("b").get_text()

        items.append([ room, "-".join(locs), price])
    return items


if __name__ == '__main__':
    # load_db()
    download_all(20, 100)
