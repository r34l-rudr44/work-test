"""Run config-driven scrapers and write unified CSV."""
import csv
from pathlib import Path

from .schema import Record, collect_all_columns
from .extractors import get_extractor


def run_targets(config_paths: list[Path]) -> list[Record]:
    """Load each config, run its extractor, return combined records."""
    records: list[Record] = []
    for path in config_paths:
        cfg = _load_config(path)
        if not cfg:
            continue
        source_type = cfg.get("source_type", "")
        extractor_cls = get_extractor(source_type)
        extractor = extractor_cls(cfg)
        records.extend(extractor.extract())
    return records


def write_csv(records: list[Record], out_path: Path) -> None:
    """Write records to CSV with dynamic columns."""
    columns = collect_all_columns(records)
    rows = [r.to_flat_dict(columns) for r in records]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _load_config(path: Path) -> dict | None:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
