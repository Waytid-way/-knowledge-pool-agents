from __future__ import annotations

import argparse
from pathlib import Path

from llm_wiki.schema_export import check_schemas, export_schemas


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic Pydantic JSON Schemas")
    parser.add_argument("--output", type=Path, default=Path("schemas"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        drift = check_schemas(args.output)
        if drift:
            for item in drift:
                print(item)
            return 1
        return 0

    export_schemas(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
