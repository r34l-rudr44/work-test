import argparse
from pathlib import Path

from .engine import run_targets, write_csv

DEFAULT_TARGETS = Path(__file__).parent / "targets"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "generic_master.csv"


def main():
    parser = argparse.ArgumentParser(description="Run config-driven scrapers")
    parser.add_argument(
        "configs",
        nargs="*",
        help="YAML config paths (default: all in targets/)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all configs in targets/",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    if args.all or not args.configs:
        configs = sorted(DEFAULT_TARGETS.glob("*.yaml"))
    else:
        configs = [Path(p) for p in args.configs]

    records = run_targets(configs)
    write_csv(records, args.output)
    print(f"Scraped {len(records)} records -> {args.output}")


if __name__ == "__main__":
    main()
