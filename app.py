#! /usr/bin/python3.8
import requests
import re

from bs4 import BeautifulSoup
from flask import Flask, render_template, send_from_directory


def get_links():

    pagelist = {
        "Hackaday": ("hackaday.com", r"\/\d{4}\/\d{2}\/\d{2}\/.+?\/", r"(\w+-)+\w+"),
        "PC Gamer": ("pcgamer.com", r"pcgamer\.com\/(\w+-)+\w+\/", r"(\w+-)+\w+"),
        "Eurogamer": ("eurogamer.net", r"\/articles\/(\d{2,}-){3}([a-zA-Z]+-)+\w+", r"(\w+-)+\w+"),
        "Kotaku": ("kotaku.com", r"kotaku\.com\/(\w+-)+(\w+|\d+)", r"(\w+-)+\w+"),
        "Anime News Network": (
            "animenewsnetwork.com",
            r"\/(\w+-)?(\w+\/)\d{4}-\d{2}-\d{2}\/(\w+-)+(\w+|\d+)\/\.\d+", r"\/([a-zA-Z]+-)+\w+\/\."
        )
    }

    pages = []
    for name, details in pagelist.items():
        site, link_pattern, title_pattern = details[0], details[1], details[2]
        page = requests.get("http://" + site)

        if page.status_code == 200:
            soup = BeautifulSoup(page.text, features="html.parser")
            tag_list = soup.find_all("a", href=True)

            link_regex = re.compile(link_pattern)

            links = []
            for tag in tag_list:
                link = link_regex.search(str(tag))
                if link is not None:
                    link = link.group()
                    if site not in link:
                        link = "http://" + site + link
                    else:
                        link = "http://" + link
                    links.append(link)
            links = list(set(links))

            final_links = []
            titles = []
            i = 0
            while len(titles) < 10 and i < len(links):
                if title := re.search(title_pattern, links[i]):
                    title = re.sub("/", " ", title.group())
                    title = re.sub("-", " ", title)
                    title = re.sub(r"(\d{2,4} ){3}", "", title)
                    title = re.sub(r"\d{10}", "", title)
                    title = title.strip(".")
                    title = title.capitalize()

                    titles.append(title)
                    final_links.append(links[i])
                i += 1

            pages.append({"page": name, "links": final_links, "titles": titles})

    return pages


app = Flask(__name__)

@app.route("/")
def index():
    all_links = get_links()
    return render_template("index.html", pages=all_links, no_of_articles=len(all_links[0]["links"]))


@app.route("/favicon.ico")
def favicon():
    return send_from_directory("./static/images/", "favicon.ico", mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    index()