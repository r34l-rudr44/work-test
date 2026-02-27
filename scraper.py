import csv
import json
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

import bs4


DATA_DIR = Path(__file__).parent
OUTPUT_FILE = DATA_DIR / "v1_master.csv"

OXFORD_URL = "https://oatml.cs.ox.ac.uk/members.html"
CMU_INDEX_URL = "https://ml.cmu.edu/peopleindexes/phd-students-index.v1.json"
IITM_URL = "https://cse.iitm.ac.in/outerfaculty.php"
IITM_BASE = "https://cse.iitm.ac.in/"


def _raw_val(val):
    if val is None:
        return ""
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def scrape_oxford():
    req = requests.get(OXFORD_URL, headers={"User-Agent": "Mozilla/5.0"})
    req.encoding = req.apparent_encoding or "utf-8"
    soup = bs4.BeautifulSoup(req.content, "html.parser")
    links = soup.find_all("a")
    name_links = {}
    base_url = f"{urlparse(OXFORD_URL).scheme}://{urlparse(OXFORD_URL).netloc}"
    for link in links:
        if link.attrs.get("href") and "members" in str(link.attrs.get("href")):
            if len(str(link.attrs.get("href")).split("/")) == 4:
                href = str(link.attrs.get("href"))
                name = href.split("/")[2]
                member_url = urljoin(base_url + "/", href.lstrip("./"))
                name_links[name] = member_url

    rows = []
    for member_id, member_url in name_links.items():
        try:
            page = requests.get(member_url, headers={"User-Agent": "Mozilla/5.0"})
            page.encoding = page.apparent_encoding or "utf-8"
            soup = bs4.BeautifulSoup(page.content, "html.parser")
            text = soup.get_text(separator="\n", strip=True)

            mailto_raw = []
            for a in soup.find_all("a", href=True):
                h = a.get("href", "")
                if "mailto" in str(h):
                    mailto_raw.append(str(h))

            all_links_raw = []
            for a in soup.find_all("a", href=True):
                all_links_raw.append(str(a.get("href", "")))

            desc_raw = text
            if "Publications while at OATML" in text:
                desc_raw = text.split("Publications while at OATML")[0]
            elif "---" in text:
                desc_raw = re.split(r"\n\s*---\s*\n", text, maxsplit=1)[0]

            row = {
                "source": "oxford",
                "name": member_id,
                "oxford_member_id": member_id,
                "oxford_url": member_url,
                "oxford_email_raw": "; ".join(mailto_raw) if mailto_raw else "",
                "oxford_page_text_raw": desc_raw[:10000],
                "oxford_all_mailto_raw": json.dumps(mailto_raw),
                "oxford_all_links_raw": json.dumps(all_links_raw[:200]),
                "cmu_id": "",
                "cmu_n": "",
                "cmu_sn": "",
                "cmu_institution": "",
                "cmu_degree": "",
                "cmu_advisor": "",
                "cmu_rsrc": "",
                "cmu_href": "",
                "cmu_img": "",
                "cmu_dept": "",
                "cmu_soc": "",
                "cmu_joint_degree": "",
                "iitm_data_name": "",
                "iitm_data_mail": "",
                "iitm_data_phone": "",
                "iitm_data_resrch": "",
                "iitm_data_profile_link": "",
                "iitm_data_personallink": "",
                "iitm_data_designation": "",
                "iitm_data_image": "",
                "iitm_data_labno": "",
                "iitm_data_office": "",
                "iitm_data_bio": "",
                "iitm_data_specializations": "",
                "iitm_data_researchareas": "",
            }
            rows.append(row)
        except Exception:
            row = {
                "source": "oxford",
                "name": member_id,
                "oxford_member_id": member_id,
                "oxford_url": member_url,
                "oxford_email_raw": "",
                "oxford_page_text_raw": "",
                "oxford_all_mailto_raw": "",
                "oxford_all_links_raw": "",
                "cmu_id": "",
                "cmu_n": "",
                "cmu_sn": "",
                "cmu_institution": "",
                "cmu_degree": "",
                "cmu_advisor": "",
                "cmu_rsrc": "",
                "cmu_href": "",
                "cmu_img": "",
                "cmu_dept": "",
                "cmu_soc": "",
                "cmu_joint_degree": "",
                "iitm_data_name": "",
                "iitm_data_mail": "",
                "iitm_data_phone": "",
                "iitm_data_resrch": "",
                "iitm_data_profile_link": "",
                "iitm_data_personallink": "",
                "iitm_data_designation": "",
                "iitm_data_image": "",
                "iitm_data_labno": "",
                "iitm_data_office": "",
                "iitm_data_bio": "",
                "iitm_data_specializations": "",
                "iitm_data_researchareas": "",
            }
            rows.append(row)

    return rows


def scrape_cmu():
    r = requests.get(CMU_INDEX_URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    data = json.loads(r.text)
    students = data.get("data", [])

    rows = []
    for s in students:
        name = s.get("n") or s.get("sn") or ""
        if isinstance(name, list):
            name = _raw_val(name)
        else:
            name = str(name)

        row = {
            "source": "cmu",
            "name": name,
            "oxford_member_id": "",
            "oxford_url": "",
            "oxford_email_raw": "",
            "oxford_page_text_raw": "",
            "oxford_all_mailto_raw": "",
            "oxford_all_links_raw": "",
            "cmu_id": _raw_val(s.get("id")),
            "cmu_n": _raw_val(s.get("n")),
            "cmu_sn": _raw_val(s.get("sn")),
            "cmu_institution": _raw_val(s.get("institution")),
            "cmu_degree": _raw_val(s.get("degree")),
            "cmu_advisor": _raw_val(s.get("advisor")),
            "cmu_rsrc": _raw_val(s.get("rsrc")),
            "cmu_href": _raw_val(s.get("href")),
            "cmu_img": _raw_val(s.get("img")),
            "cmu_dept": _raw_val(s.get("dept")),
            "cmu_soc": _raw_val(s.get("soc")),
            "cmu_joint_degree": _raw_val(s.get("joint-degree")),
            "iitm_data_name": "",
            "iitm_data_mail": "",
            "iitm_data_phone": "",
            "iitm_data_resrch": "",
            "iitm_data_profile_link": "",
            "iitm_data_personallink": "",
            "iitm_data_designation": "",
            "iitm_data_image": "",
            "iitm_data_labno": "",
            "iitm_data_office": "",
            "iitm_data_bio": "",
            "iitm_data_specializations": "",
            "iitm_data_researchareas": "",
        }
        rows.append(row)

    return rows


def scrape_iitm():
    r = requests.get(IITM_URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    elements = soup.find_all(attrs={"data-mail": True})

    rows = []
    for el in elements:
        name = el.get("data-name", "").strip()
        profile_rel = el.get("data-profile-link", "")
        if profile_rel and not str(profile_rel).startswith("http"):
            profile_rel = urljoin(IITM_BASE, str(profile_rel))
        personal = el.get("data-personallink", "").strip()
        if personal and not personal.startswith("http"):
            personal = urljoin(IITM_BASE, personal)

        row = {
            "source": "iitm",
            "name": name,
            "oxford_member_id": "",
            "oxford_url": "",
            "oxford_email_raw": "",
            "oxford_page_text_raw": "",
            "oxford_all_mailto_raw": "",
            "oxford_all_links_raw": "",
            "cmu_id": "",
            "cmu_n": "",
            "cmu_sn": "",
            "cmu_institution": "",
            "cmu_degree": "",
            "cmu_advisor": "",
            "cmu_rsrc": "",
            "cmu_href": "",
            "cmu_img": "",
            "cmu_dept": "",
            "cmu_soc": "",
            "cmu_joint_degree": "",
            "iitm_data_name": el.get("data-name", ""),
            "iitm_data_mail": el.get("data-mail", ""),
            "iitm_data_phone": el.get("data-phone", ""),
            "iitm_data_resrch": el.get("data-resrch", ""),
            "iitm_data_profile_link": profile_rel,
            "iitm_data_personallink": personal,
            "iitm_data_designation": el.get("data-designation", ""),
            "iitm_data_image": el.get("data-image", ""),
            "iitm_data_labno": el.get("data-labno", ""),
            "iitm_data_office": el.get("data-office", ""),
            "iitm_data_bio": el.get("data-bio", ""),
            "iitm_data_specializations": el.get("data-specializations", ""),
            "iitm_data_researchareas": el.get("data-researchareas", ""),
        }
        rows.append(row)

    return rows


def main():
    all_rows = []
    all_rows.extend(scrape_oxford())
    all_rows.extend(scrape_cmu())
    all_rows.extend(scrape_iitm())

    columns = [
        "source",
        "name",
        "oxford_member_id",
        "oxford_url",
        "oxford_email_raw",
        "oxford_page_text_raw",
        "oxford_all_mailto_raw",
        "oxford_all_links_raw",
        "cmu_id",
        "cmu_n",
        "cmu_sn",
        "cmu_institution",
        "cmu_degree",
        "cmu_advisor",
        "cmu_rsrc",
        "cmu_href",
        "cmu_img",
        "cmu_dept",
        "cmu_soc",
        "cmu_joint_degree",
        "iitm_data_name",
        "iitm_data_mail",
        "iitm_data_phone",
        "iitm_data_resrch",
        "iitm_data_profile_link",
        "iitm_data_personallink",
        "iitm_data_designation",
        "iitm_data_image",
        "iitm_data_labno",
        "iitm_data_office",
        "iitm_data_bio",
        "iitm_data_specializations",
        "iitm_data_researchareas",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
