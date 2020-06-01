#! /usr/bin/python3.8
import requests
import re

from bs4 import BeautifulSoup
from flask import Flask, render_template


def get_links():

    pagelist = {
        "Hackaday": ("hackaday.com", r"\/\d{4}\/\d{2}\/\d{2}\/.+?\/"),
        "PC Gamer": ("pcgamer.com", r"pcgamer\.com\/(\w+-)+\w+\/"),
        "Eurogamer": ("eurogamer.net", r"\/articles\/(\d{2,}-)*(\w+-)*\w+"),
        "Kotaku": ("kotaku.com", r"kotaku\.com\/(\w+-)+(\w+|\d+)"),
        "Anime News Network": (
            "animenewsnetwork.com",
            r"\/(\w+-)?(\w+\/)\d{4}-\d{2}-\d{2}\/(\w+-)+(\w+|\d+)\/\.\d+",
        ),
    }

    pages = []
    for name, details in pagelist.items():
        site, pattern = details[0], details[1]
        page = requests.get("http://" + site)
        soup = BeautifulSoup(page.text, features="html.parser")
        tag_list = soup.find_all("a", href=True)

        regex = re.compile(pattern)

        links = []
        for tag in tag_list:
            link = regex.search(str(tag))
            if link is not None:
                link = link.group()
                if site not in link:
                    link = "http://" + site + link
                else:
                    link = "http://" + link
                links.append(link)
        pages.append({"page": name, "links": list(set(links))[:10]})

    return pages


app = Flask(__name__)


@app.route("/")
def index():
    all_links = get_links()
    return render_template("index.html", pages=all_links)
