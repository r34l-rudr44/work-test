"""
Generic CSS-selector extractor for arbitrary HTML pages.
Use when the page has a repeating structure (e.g. list, table) extractable via selectors.
"""
from urllib.parse import urljoin

import requests
import bs4

from ..schema import Record
from .base import BaseExtractor


class CssSelectExtractor(BaseExtractor):
    """
    Config:
      url: ...
      item_selector: CSS selector for each repeated item (e.g. "tr", ".person-card")
      field_selectors: { output_field: css_selector } - evaluated within each item
      field_attributes: { output_field: "href" } - extract attribute instead of text
      link_fields: [ fields to resolve as absolute URLs ]
      base_url: for link resolution
    """

    def extract(self) -> list[Record]:
        url = self.config.get("url", "")
        item_sel = self.config.get("item_selector", "")
        field_sel = self.config.get("field_selectors", {})
        field_attr = self.config.get("field_attributes", {})
        link_fields = set(self.config.get("link_fields", []))
        base = self.config.get("base_url") or self.base_url or ""

        if not url or not item_sel:
            return []

        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = bs4.BeautifulSoup(resp.content, "html.parser")

        records = []
        for el in soup.select(item_sel):
            raw = {}
            for out_key, sel in field_sel.items():
                sub = el.select_one(sel) if sel else el
                if not sub:
                    raw[out_key] = ""
                    continue
                attr = field_attr.get(out_key)
                if attr:
                    val = sub.get(attr, "") or ""
                    if out_key in link_fields and val and not str(val).startswith("http") and base:
                        val = urljoin(base + "/", str(val))
                else:
                    val = sub.get_text(strip=True)
                raw[out_key] = str(val).strip() if val else ""
            name_val = str(raw.get("name", raw.get("title", ""))).strip()
            email_val = str(raw.get("email", "")).strip()
            url_val = str(raw.get("url", raw.get("profile_url", raw.get("link", "")))).strip()
            records.append(Record(source=self.source_id, name=name_val, url=url_val, email=email_val, raw=raw))
        return records
