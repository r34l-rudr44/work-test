import csv
import requests
import bs4
import os
from pathlib import Path


DATA_DIR = Path("basic info")
DATA_DIR.mkdir(exist_ok=True)

class Details:
    name: str
    email: str

DATA = {}

def get_data(url: str):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, "html.parser")
    links = soup.find_all("a")
    name_links = {}
    for link in links:
        if link.attrs.get("href") and "members" in str(link.attrs.get("href")):
            # name_links[str(link.attrs.get("href")).split("/")[-1]] = link.attrs.get("href")
            if len(str(link.attrs.get("href")).split("/")) == 4:
                name_links[str(link.attrs.get("href")).split("/")[2]] = "/".join([url,  str(link.attrs.get("href"))[2:]])


    rows = []
    for name, link in name_links.items():
        email = get_mail(link)
        rows.append((name, email))

    output_file = DATA_DIR / "v2_oxford_basic.csv"
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email"])
        writer.writerows(rows)
    print(f"Saved to {output_file}")

def get_mail(url: str):
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    elements = soup.find_all("a")
    emails = [ele.attrs.get("href") for ele in elements if ele.attrs.get("href") and "mailto" in str(ele.attrs.get("href"))]
    return emails[0] if emails else ""

if __name__ == '__main__':
    get_data("https://oatml.cs.ox.ac.uk/members.html")