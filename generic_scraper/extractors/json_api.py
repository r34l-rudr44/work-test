import json
import requests
from urllib.parse import urljoin

from ..schema import Record
from .base import BaseExtractor


class JsonApiExtractor(BaseExtractor):
    def extract(self) -> list[Record]:
        api = self.config.get("api", {})
        url = api.get("url", "")
        data_path = api.get("data_path", "data")
        mapping = self.config.get("field_mapping", {})
        name_field = self.config.get("name_field", "")
        url_field = self.config.get("url_field", "")
        transforms = self.config.get("transforms", {})

        if not url:
            return []

        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()

        for seg in data_path.split("."):
            data = data.get(seg, [])
        if not isinstance(data, list):
            data = [data]

        records = []
        for item in data:
            if not isinstance(item, dict):
                continue
            raw = {}
            for out_key, json_key in mapping.items():
                val = self._get_nested(item, json_key)
                t = transforms.get(out_key, "raw")
                val = self._apply_transform(val, t)
                raw[out_key] = val
            name_val = raw.get(name_field or (list(mapping.keys())[0] if mapping else ""), "")
            if isinstance(name_val, list):
                name_val = " ".join(str(x) for x in name_val if x)
            name_val = str(name_val).strip()
            url_val = ""
            if url_field and url_field in raw:
                p = raw[url_field]
                url_val = urljoin(self.base_url + "/", str(p)) if p else ""
            email_val = str(raw.get("email", "")).strip()
            records.append(Record(source=self.source_id, name=name_val, url=url_val, email=email_val, raw=raw))
        return records

    def _get_nested(self, d: dict, path: str):
        for k in path.split("."):
            d = d.get(k) if isinstance(d, dict) else None
        return d

    def _apply_transform(self, val, t: str):
        if t == "raw":
            return val
        if t == "list_join":
            if isinstance(val, list):
                return "; ".join(str(x).strip() for x in val if x)
            return str(val) if val else ""
        if t == "andrew_email":
            if val:
                return f"{val}@andrew.cmu.edu"
            return ""
        return val
