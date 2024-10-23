import time
import requests
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import json
import csv

def html_gen(url, **kwargs):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"}
    if kwargs.get("page"):
        resp = requests.get(url + f"?page={str(kwargs.get('page'))}#concert-table", headers = headers)
    else:
        resp = requests.get(url, headers = headers)
    try:
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(resp.status_code)
        return False 
    html = HTMLParser(resp.text)
    return html

def url_parser(html):
    gigs = html.css("div.table-responsive tr a")
    for gig in gigs:
        if "/concerts/" in gig.css_first("a").attributes["href"]:
            yield urljoin("https://www.concertarchives.org/", gig.css_first("a").attributes["href"])

def concert_parser(html):
    items = {
        "name": text_gen(html, "h1.profile-display"),
        "lineup": text_gen(html, "div.concert-band-list"),
        "location": text_gen(html, "dl.dl-horizontal.details dd a").strip(" "),
        "date": text_gen(html, "dl.dl-horizontal.details dd").strip("\n"),
        "genres": text_gen(html, "div.col-md-9 p:not([style]) strong")
    }
    return items

def text_gen(html, selection):
    try:
        return html.css_first(selection).text()
    except AttributeError:
        return None
    
def export_to_json(data):
    with open("concert_acchive.json", "w") as f:
        json.dump(data)

def append_to_csv(gig):
    field_names = ["name", "lineup", "location", "date", "genres"]
    with open("concertArchive.csv", "a", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writerow(gig)

def main():
    data = []
    org_url = "https://www.concertarchives.org/locations/amsterdam-netherlands"
    for x in range(727, 816):
        print(f"Analyzing page:{x}") 
        html = html_gen(org_url, page = x)
        if html is False:
            break
        urls = url_parser(html)
        for url in urls:
            html = html_gen(url)
            append_to_csv(concert_parser(html))
        time.sleep(5)
    export_to_json(data)

if __name__ == "__main__":
    main()

