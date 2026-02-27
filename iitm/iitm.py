import csv
import requests
from pathlib import Path
from urllib.parse import urljoin

import bs4


DATA_DIR = Path(__file__).parent
BASE_URL = "https://cse.iitm.ac.in/"
FACULTY_URL = "https://cse.iitm.ac.in/outerfaculty.php"


def _deobfuscate_email(text: str) -> str:
    if not text:
        return ""
    return text.replace("[at]", "@").replace("[dot]", ".")


def _make_absolute(url: str) -> str:
    if not url:
        return ""
    if url.startswith("http"):
        return url
    return urljoin(BASE_URL, url)


def get_data():
    r = requests.get(FACULTY_URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"

    soup = bs4.BeautifulSoup(r.content, "html.parser")
    elements = soup.find_all(attrs={"data-mail": True})

    rows = []
    for el in elements:
        name = el.get("data-name", "").strip()
        mail_raw = el.get("data-mail", "")
        email = _deobfuscate_email(mail_raw).strip()
        research_interest = el.get("data-resrch", "").strip()
        profile_rel = el.get("data-profile-link", "")
        faculty_profile = _make_absolute(profile_rel) if profile_rel else ""
        personal_website = el.get("data-personallink", "").strip()
        if personal_website and not personal_website.startswith("http"):
            personal_website = _make_absolute(personal_website)
        phone = el.get("data-phone", "").strip()

        rows.append(
            (
                name,
                email,
                research_interest,
                faculty_profile,
                personal_website,
                phone,
            )
        )

    output_file = DATA_DIR / "iitm_data.csv"
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "name",
                "email",
                "research_interest",
                "faculty_profile",
                "personal_website",
                "phone",
            ]
        )
        writer.writerows(rows)

    print(f"Saved to {output_file}")


if __name__ == "__main__":
    get_data()
