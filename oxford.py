import csv
import requests
import bs4
import os
from pathlib import Path


DATA_DIR = Path("basic info")
DATA_DIR.mkdir(exist_ok=True)

def get_data(url: str):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, "html.parser")
    links = soup.find_all("a")
    name_links = {}
    for link in links:
        if link.attrs.get("href") and "members" in str(link.attrs.get("href")):
            # name_links[str(link.attrs.get("href")).split("/")[-1]] = link.attrs.get("href")
            name_links[str(link.attrs.get("href")).split("/")[2]] = "/".join([url,  str(link.attrs.get("href"))[1:]])
        
    output_file = DATA_DIR / "oxford_basic.csv"
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "url"])
        for name, link_url in name_links.items():
            writer.writerow([name, link_url])
    print(f"Saved to {output_file}")

if __name__ == '__main__':
    get_data("https://oatml.cs.ox.ac.uk/members.html")