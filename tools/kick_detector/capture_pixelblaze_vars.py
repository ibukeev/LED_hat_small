#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any


def flatten_vars(data: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, list):
            if key == "frequencyData":
                for idx, item in enumerate(value):
                    row[f"frequencyData_{idx:02d}"] = item
            else:
                row[key] = json.dumps(value, separators=(",", ":"))
        else:
            row[key] = value
    return row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture exported Pixelblaze vars over time and write them to CSV/JSONL."
    )
    parser.add_argument("host", help="Pixelblaze hostname or IP address")
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Capture duration in seconds (default: 30)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Polling interval in seconds (default: 0.05, about 20 Hz)",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=Path("tools/kick_detector/output/pixelblaze-capture"),
        help="Output file prefix without extension",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from pixelblaze import Pixelblaze
    except Exception as exc:
        print(
            "Missing dependency: pixelblaze-client.\n"
            "Install with:\n"
            "  . .venv/bin/activate && python -m pip install pixelblaze-client\n"
            f"Import error: {exc}",
            file=sys.stderr,
        )
        return 2

    pb = Pixelblaze(args.host)

    jsonl_path = args.output_prefix.with_suffix(".jsonl")
    csv_path = args.output_prefix.with_suffix(".csv")
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    start = time.time()
    deadline = start + args.duration

    print(f"Connecting to Pixelblaze at {args.host}")
    print(f"Capturing for {args.duration:.2f}s at ~{1.0 / args.interval:.1f} Hz")

    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        while True:
            now = time.time()
            if now >= deadline:
                break

            vars_data = pb.getActiveVariables()
            row = flatten_vars(vars_data)
            row["ts_epoch"] = now
            row["ts_rel"] = now - start
            rows.append(row)
            jsonl_file.write(json.dumps(row, separators=(",", ":")) + "\n")

            time.sleep(args.interval)

    if rows:
        fieldnames: list[str] = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    fieldnames.append(key)

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f"Wrote {len(rows)} samples to:")
    print(f"  {jsonl_path}")
    print(f"  {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
