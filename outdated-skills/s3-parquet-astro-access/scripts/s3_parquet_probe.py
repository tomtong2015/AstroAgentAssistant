#!/usr/bin/env python3
"""Probe S3/Parquet astronomy datasets with safe column projection.

Examples:
  python s3_parquet_probe.py --uri 's3://bucket/path/*.parquet' --columns bprp0,mg0 --anon
  python s3_parquet_probe.py --uri 's3://bucket/path/*.parquet' \
    --endpoint-url https://s3.data.aip.de:9000 --columns bprp0,mg0 --out /tmp/probe
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def parse_columns(value: str | None) -> list[str] | None:
    if not value:
        return None
    cols = [x.strip() for x in value.split(",") if x.strip()]
    return cols or None


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe S3/Parquet access and cache a small preview.")
    parser.add_argument("--uri", required=True, help="Parquet URI, e.g. s3://bucket/path/*.parquet")
    parser.add_argument("--columns", help="Comma-separated columns to read")
    parser.add_argument("--endpoint-url", help="S3-compatible endpoint URL")
    parser.add_argument("--anon", action="store_true", help="Use anonymous S3 access")
    parser.add_argument("--out", default="s3_parquet_probe", help="Output directory")
    parser.add_argument("--head", type=int, default=10, help="Preview rows")
    args = parser.parse_args()

    import dask.dataframe as dd

    storage_options: dict = {}
    if args.anon:
        storage_options["anon"] = True
    if args.endpoint_url:
        storage_options.setdefault("client_kwargs", {})["endpoint_url"] = args.endpoint_url

    columns = parse_columns(args.columns)
    ddf = dd.read_parquet(args.uri, columns=columns, storage_options=storage_options or None)
    preview = ddf.head(args.head)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    preview.to_csv(out / "preview.csv", index=False)
    try:
        preview.to_parquet(out / "preview.parquet", index=False)
    except Exception:
        pass
    provenance = {
        "access_method": "s3-parquet-dask",
        "source_uri": args.uri,
        "endpoint_url": args.endpoint_url,
        "anonymous": bool(args.anon),
        "columns": columns,
        "preview_rows": int(len(preview)),
        "created_utc": dt.datetime.utcnow().isoformat() + "Z",
    }
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
