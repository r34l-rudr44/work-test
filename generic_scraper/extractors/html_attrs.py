from urllib.parse import urljoin

import requests
import bs4

from ..schema import Record
from .base import BaseExtractor


class HtmlAttrsExtractor(BaseExtractor):
    def extract(self) -> list[Record]:
        url = self.config.get("url", "")
        container = self.config.get("container_selector", "")
        attr_map = self.config.get("attribute_map", {})
        transforms = self.config.get("transforms", {})
        base = self.config.get("base_url") or self.base_url or ""

        if not url or not container:
            return []

        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = bs4.BeautifulSoup(resp.content, "html.parser")

        records = []
        for el in soup.select(container):
            if not el:
                continue
            raw = {}
            for out_key, attr_name in attr_map.items():
                val = el.get(attr_name, "") or ""
                val = str(val).strip()
                t = transforms.get(out_key, "")
                if t == "deobfuscate_email":
                    val = val.replace("[at]", "@").replace("[dot]", ".")
                elif t == "absolute_url" and val and not val.startswith("http"):
                    val = urljoin(base + "/", val)
                raw[out_key] = val
            name_val = str(raw.get("name", "")).strip()
            email_val = str(raw.get("email", "")).strip()
            url_val = str(raw.get("profile_url", raw.get("url", ""))).strip()
            records.append(Record(source=self.source_id, name=name_val, url=url_val, email=email_val, raw=raw))
        return records
