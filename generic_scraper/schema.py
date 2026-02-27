from dataclasses import dataclass, field
from typing import Any


@dataclass
class Record:
    source: str
    name: str
    url: str = ""
    email: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    def to_flat_dict(self, all_columns: list[str]) -> dict[str, str]:
        out: dict[str, str] = {c: "" for c in all_columns}
        out["source"] = self.source
        out["name"] = str(self.name) if self.name else ""
        out["url"] = str(self.url) if self.url else ""
        out["email"] = str(self.email) if self.email else ""
        prefix = f"{self.source}_"
        for col in all_columns:
            if col.startswith(prefix):
                key = col[len(prefix) :]
                out[col] = _serialize(self.raw.get(key, ""))
        return out


def _serialize(val: Any) -> str:
    import json
    if val is None:
        return ""
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def collect_all_columns(records: list[Record]) -> list[str]:
    core = ["source", "name", "url", "email"]
    seen: set[str] = set()
    for r in records:
        for k in r.raw:
            seen.add(f"{r.source}_{k}")
    extra = sorted(seen)
    return core + extra
