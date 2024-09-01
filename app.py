from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

from flask import Flask, render_template, send_from_directory
from waitress import serve

import requests
import urllib


def request_page(name, details):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
    }
    return name, requests.get(
        f"http://{details['root']}{details['path']}", headers=headers
    )


def get_links():
    pagelist = {
        "Hackaday": {
            "root": "hackaday.com",
            "path": "/",
            "tag": "h2",
            "class_": "",
            "use_root": False,
        },
        "PC Gamer": {
            "root": "pcgamer.com",
            "path": "/",
            "tag": "a",
            "class_": "article-link",
            "use_root": False,
        },
        "Eurogamer": {
            "root": "eurogamer.net",
            "path": "/archive",
            "tag": "a",
            "class_": "link",
            "use_root": False,
        },
        "Kotaku": {
            "root": "kotaku.com",
            "path": "/latest",
            "tag": "h2",
            "class_": "",
            "use_root": False,
        },
        "Anime News Network": {
            "root": "animenewsnetwork.com",
            "path": "/news",
            "tag": "h3",
            "class_": "",
            "use_root": True,
        },
        "Formula 1": {
            "root": "www.formula1.com",
            "path": "/en/latest/all.html",
            "tag": "li",
            "class_": "group",
            "use_root": False,
        },
        "In the Pipeline": {
            "root": "www.science.org",
            "path": "/blogs/pipeline",
            "tag": "div",
            "class_": "card-header",
            "use_root": True,
        },
        "FIA Decision Documents": {
            "root": "www.fia.com",
            "path": "/documents",
            "tag": "li",
            "class_": "document-row",
            "use_root": True,
        },
        "Hacker News": {
            "root": "news.ycombinator.com",
            "path": "/news",
            "tag": "span",
            "class_": "titleline",
            "use_root": False,
        },
        "Motorsport": {
            "root": "motorsport.com",
            "path": "/f1/news",
            "tag": "a",
            "class_": "ms-item",
            "use_root": True,
        },
        "Space News": {
            "root": "spacenews.com",
            "path": "/section/news-archive",
            "tag": "h2",
            "class_": "entry-title",
            "use_root": False,
        },
        "Phys Org": {
            "root": "phys.org",
            "path": "/latest-news",
            "tag": "a",
            "class_": "news-link",
            "use_root": False,
        },
        "NASA Blog": {
            "root": "blogs.nasa.gov",
            "path": "/",
            "tag": "h2",
            "class_": "entry-title",
            "use_root": False,
        },
    }

    executor = ThreadPoolExecutor(max_workers=10)

    responses = executor.map(request_page, pagelist.keys(), pagelist.values())

    pages = []

    for response in responses:
        name, page = response
        details = pagelist[name]

        if page.status_code == 200:
            print(name)
            soup = BeautifulSoup(page.text, features="html.parser")
            if details["class_"]:
                tag_list = soup.find_all(details["tag"], class_=details["class_"])
            else:
                tag_list = soup.find_all(details["tag"])

            links = []
            titles = []
            print(name)
            for tag in tag_list:
                if tag.name == "a":
                    link = tag["href"]
                    title = tag.text
                elif tag.find("a"):
                    link = tag.a["href"]
                    title = tag.text
                else:
                    try:
                        link = tag.parent["href"]
                        title = tag.text
                    except KeyError:
                        continue

                protocols = ["http://", "http//", "https://", "https//"]
                for protocol in protocols:
                    if link.startswith(protocol):
                        link = link[len(protocol) :]

                link = urllib.parse.quote(link)
                if details["use_root"]:
                    link = f"https://{details['root']}{link}"
                else:
                    link = f"https://{link}"

                links.append(link)
                titles.append(title)

            pages.append(
                {
                    "page": name,
                    "url": f"https://{details['root']}",
                    "links": links[:10],
                    "titles": titles[:10],
                }
            )

    return pages


app = Flask(__name__)


@app.route("/")
def index():
    all_links = get_links()
    return render_template(
        "index.html", pages=all_links, no_of_articles=len(all_links[0]["links"])
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "./static/images/", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


serve(app, port=8080)

if __name__ == "__main__":
    serve(app, port=8080)
