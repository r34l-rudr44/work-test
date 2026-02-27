import csv
import re
import requests
import bs4
from pathlib import Path
from urllib.parse import urljoin, urlparse
from sklearn.feature_extraction.text import TfidfVectorizer


DATA_DIR = Path("basic info")
DATA_DIR.mkdir(exist_ok=True)


def get_research_interests(url: str) -> str:
    page = requests.get(url)
    page.encoding = page.apparent_encoding or "utf-8"
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    elements = soup.select("p")
    paras = [
        ele.get_text(strip=True)
        for ele in elements
        if "interest" in ele.get_text().lower() or "interested" in ele.get_text().lower()
    ]
    if not paras:
        return ""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=20, ngram_range=(1, 2))
    X = vectorizer.fit_transform(paras)
    features = vectorizer.get_feature_names_out()
    return "; ".join(features)


def get_affiliations(url: str) -> str:
    page = requests.get(url)
    page.encoding = page.apparent_encoding or "utf-8"
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    description = re.split(r"\s*---\s*|Publications while at OATML", text, maxsplit=1)[0]
    paras = re.split(r"\s{2,}", description.strip())
    bio_text = " ".join(paras[:2]) if paras else ""

    affiliations = []
    patterns = [
        r"(?:at|in)\s+(?:the\s+)?([\w\s]+?(?:University|Institute|College|Group|Department|Centre|Lab)(?:\s+of\s+[\w\s]+)?)",
        r"(?:,\s*)((?:National\s+)?(?:University|Institute|College)\s+(?:of\s+)?[\w\s]+?)(?:\s*,|\s*\.|$)",
        r"((?:OATML|Big Data|Turing)\s+(?:AI\s+)?(?:Group|Institute))",
        r"(Christ Church|St\s+\w+\'?s?\s+College)",
    ]
    seen = set()
    for pattern in patterns:
        for m in re.finditer(pattern, bio_text, re.IGNORECASE):
            aff = " ".join(m.group(1).split()).strip().rstrip(".,")
            aff = re.sub(r"^the\s+", "", aff, flags=re.I)
            if " in the " in aff:
                continue
            key = aff.lower()
            if 4 < len(aff) < 70 and key not in seen:
                seen.add(key)
                affiliations.append(aff)

    if affiliations:
        return "; ".join(affiliations)

    return paras[0][:500] if paras else ""


def get_data(url: str):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, "html.parser")
    links = soup.find_all("a")
    name_links = {}
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    for link in links:
        if link.attrs.get("href") and "members" in str(link.attrs.get("href")):
            if len(str(link.attrs.get("href")).split("/")) == 4:
                href = str(link.attrs.get("href"))
                name = href.split("/")[2]
                member_url = urljoin(base_url + "/", href.lstrip("./"))
                name_links[name] = member_url

    rows = []
    for name, link in name_links.items():
        email = get_mail(link)
        research_interest = get_research_interests(link)
        affiliations = get_affiliations(link)
        rows.append((name, email, research_interest, affiliations))

    output_file = DATA_DIR / "v5_oxford_basic.csv"
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "research_interests", "affiliations"])
        writer.writerows(rows)
    print(f"Saved to {output_file}")


def get_mail(url: str):
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    elements = soup.find_all("a")
    emails = [ele.attrs.get("href") for ele in elements if ele.attrs.get("href") and "mailto" in str(ele.attrs.get("href"))]
    return emails[0] if emails else ""


if __name__ == "__main__":
    get_data("https://oatml.cs.ox.ac.uk/members.html")
