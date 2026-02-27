import re
import requests
from urllib.parse import urljoin, urlparse

import bs4

from ..schema import Record
from .base import BaseExtractor


class HtmlListingExtractor(BaseExtractor):
    def extract(self) -> list[Record]:
        listing = self.config.get("listing", {})
        detail_cfg = self.config.get("detail", {})

        listing_url = listing.get("url", "")
        if not listing_url:
            return []

        base = f"{urlparse(listing_url).scheme}://{urlparse(listing_url).netloc}"
        resp = requests.get(listing_url, headers={"User-Agent": "Mozilla/5.0"})
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = bs4.BeautifulSoup(resp.content, "html.parser")

        links = self._get_links(soup, listing, base, listing_url)
        records = []
        for item_id, item_url in links.items():
            rec = self._scrape_detail(item_url, item_id, detail_cfg, base)
            records.append(rec)
        return records

    def _get_links(self, soup: bs4.BeautifulSoup, listing: dict, base: str, listing_url: str) -> dict[str, str]:
        sel = listing.get("link_selector", "a[href]")
        link_attr = listing.get("link_attr", "href")
        flt = listing.get("link_filter", {})
        id_from_path = listing.get("id_from_path", -1)

        items: dict[str, str] = {}
        for a in soup.select(sel) if sel else soup.find_all("a"):
            href = a.get(link_attr) or ""
            href = str(href).strip()
            if not href:
                continue
            if flt.get("href_contains") and flt["href_contains"] not in href:
                continue
            if "path_segments" in flt:
                parts = href.replace("\\", "/").split("/")
                if len(parts) != flt["path_segments"]:
                    continue
            full_url = urljoin(base + "/", href.lstrip("./"))
            if id_from_path >= 0:
                parts = full_url.rstrip("/").split("/")
                item_id = parts[id_from_path] if id_from_path < len(parts) else full_url
            else:
                item_id = full_url
            items[item_id] = full_url
        return items

    def _scrape_detail(self, url: str, item_id: str, detail_cfg: dict, base: str) -> Record:
        raw: dict = {}
        url_val = url
        name_val = item_id
        email_val = ""

        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = bs4.BeautifulSoup(resp.content, "html.parser")
        except Exception:
            return Record(source=self.source_id, name=name_val, url=url_val, email=email_val, raw=raw)

        raw["member_id"] = item_id
        raw["url"] = url
        extract_rules = detail_cfg.get("extract", [])
        for rule in extract_rules:
            field = rule.get("field", "")
            if not field:
                continue
            if rule.get("from_id"):
                raw[field] = item_id
                if field == "name":
                    name_val = item_id
                continue
            if rule.get("from_url"):
                raw[field] = url
                continue
            if rule.get("selector"):
                val = self._extract_by_rule(soup, rule, base)
                if field == "name":
                    name_val = val or name_val
                elif field == "email":
                    email_val = val or email_val
                raw[field] = val
            elif rule.get("tag"):
                val = self._extract_generic(soup, rule)
                if field == "name":
                    name_val = val or name_val
                elif field == "email":
                    email_val = val or email_val
                raw[field] = val

        transforms = detail_cfg.get("transforms", {})
        for fname, tname in transforms.items():
            if fname in raw and tname == "mailto_extract":
                raw[fname] = self._mailto_extract(raw[fname])
                if fname == "email" or fname == "mailto_raw":
                    email_val = raw[fname] or email_val

        return Record(source=self.source_id, name=name_val, url=url_val, email=email_val, raw=raw)

    def _extract_by_rule(self, soup: bs4.BeautifulSoup, rule: dict, base: str) -> str:
        sel = rule.get("selector", "")
        attr = rule.get("attribute")
        as_text = rule.get("text", False)
        first_only = rule.get("first", True)
        els = soup.select(sel) if sel else []
        if not els:
            return ""
        if first_only and els:
            els = [els[0]]
        vals = []
        for el in els:
            if as_text:
                vals.append(el.get_text(strip=True))
            elif attr:
                v = el.get(attr) or ""
                if attr == "href" and v and not str(v).startswith("http") and base:
                    v = urljoin(base + "/", str(v))
                vals.append(str(v) if v else "")
            else:
                vals.append(el.get_text(strip=True))
        return "; ".join(v for v in vals if v)

    def _extract_generic(self, soup: bs4.BeautifulSoup, rule: dict) -> str:
        tag = rule.get("tag", "")
        if tag == "mailto":
            links = soup.find_all("a", href=True)
            for a in links:
                h = a.get("href", "")
                if "mailto:" in str(h):
                    return str(h).replace("mailto:", "").strip()
            return ""
        if tag == "page_text":
            stop = rule.get("stop_at") or []
            text = soup.get_text(separator="\n", strip=True)
            for marker in stop:
                if marker in text:
                    text = text.split(marker)[0]
            return text[: rule.get("max_chars", 10000)]
        return ""

    def _mailto_extract(self, val: str) -> str:
        if not val:
            return ""
        if isinstance(val, str) and "mailto:" in val:
            return val.replace("mailto:", "").strip()
        return str(val)
