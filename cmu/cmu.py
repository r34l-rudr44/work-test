import csv
import json
import requests
from pathlib import Path


DATA_DIR = Path(__file__).parent
INDEX_URL = "https://ml.cmu.edu/peopleindexes/phd-students-index.v1.json"
CURRENT_AFFILIATION = "Carnegie Mellon University, Machine Learning Department"


def _to_str(val) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        return "; ".join(str(v).strip() for v in val if v)
    return str(val).strip()


def get_data():
    r = requests.get(INDEX_URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    data = json.loads(r.text)
    students = data.get("data", [])

    rows = []
    for s in students:
        name = _to_str(s.get("n", ""))
        andrew_id = s.get("id", "")

        inst = s.get("institution")
        degree = s.get("degree")
        prev_parts = []
        if inst:
            prev_parts.append(_to_str(inst))
        if degree:
            prev_parts.append(_to_str(degree))
        previous_affiliation = "; ".join(prev_parts) if prev_parts else ""

        advisor = _to_str(s.get("advisor", ""))
        rsrc = s.get("rsrc")
        if isinstance(rsrc, list):
            research_topics = "; ".join(str(x).strip() for x in rsrc if x)
        elif isinstance(rsrc, str):
            research_topics = rsrc.strip()
        else:
            research_topics = ""

        email = f"{andrew_id}@andrew.cmu.edu" if andrew_id else ""

        rows.append(
            (
                name,
                email,
                previous_affiliation,
                CURRENT_AFFILIATION,
                advisor,
                research_topics,
            )
        )

    output_file = DATA_DIR / "cmu_data.csv"
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "name",
                "email",
                "previous_affiliation",
                "current_affiliation",
                "advisor",
                "research_topics",
            ]
        )
        writer.writerows(rows)

    print(f"Saved to {output_file}")


if __name__ == "__main__":
    get_data()
