"""Summarize a JMeter CSV JTL containing HTTP samples with start timestamps."""

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Sample:
    start: int
    elapsed: int
    label: str
    success: bool
    code: str
    threads: int | None


def p95(values):
    ordered = sorted(values)
    rank = min(len(ordered), max(1, 0.95 * (len(ordered) + 1)))
    before, after = math.floor(rank), math.ceil(rank)
    return ordered[before - 1] + (rank - before) * (ordered[after - 1] - ordered[before - 1])


def read_jtl(path):
    required = {"timeStamp", "elapsed", "label", "success", "responseCode"}
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing JTL columns: {', '.join(sorted(missing))}")
        samples = []
        for row in reader:
            try:
                start, elapsed = int(row["timeStamp"]), int(row["elapsed"])
                label, success, code = row["label"], row["success"].lower(), row["responseCode"]
                threads = int(row["allThreads"]) if row.get("allThreads") else None
                if start < 0 or elapsed < 0 or not label or not code or success not in ("true", "false"):
                    raise ValueError
            except (AttributeError, TypeError, ValueError):
                raise ValueError(f"Malformed sample at JTL line {reader.line_num}") from None
            samples.append(Sample(start, elapsed, label, success == "true", code, threads))
    if not samples:
        raise ValueError("Zero HTTP samples. Check JMeter logs before interpreting the run.")
    return samples


def metrics(samples, duration=None):
    if duration is None and samples:
        duration = (max(s.start + s.elapsed for s in samples) - min(s.start for s in samples)) / 1000
    count = len(samples)
    failed = Counter(s.code for s in samples if not s.success)
    errors = sum(failed.values())
    threads = [s.threads for s in samples if s.threads is not None]
    return {
        "samples": count,
        "duration_s": duration,
        "rps": count / duration if duration else None,
        "p95_ms": p95(s.elapsed for s in samples) if count else None,
        "error_pct": 100 * errors / count if count else None,
        "errors": errors,
        "failed_codes": dict(sorted(failed.items())),
        "threads": [min(threads), max(threads)] if threads else None,
    }


def summarize(samples, bounds=None):
    duration = None if bounds is None else bounds[1] - bounds[0]
    groups = defaultdict(list)
    for sample in samples:
        groups[sample.label].append(sample)
    return {
        "window_s": bounds,
        "total": metrics(samples, duration),
        "by_label": {label: metrics(group, duration) for label, group in sorted(groups.items())},
    }


def parse_window(spec):
    try:
        name, start, end = spec.split(":")
        start, end = float(start), float(end)
        if not name.strip() or name == "full" or not (0 <= start < end < math.inf):
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("Expected NAME:START:END with 0 <= START < END, in seconds") from None
    return name, (start, end)


def print_report(report):
    print(f"Profile: {report['profile']} | Origin: {report['origin_ms']} ms ({report['origin_kind']})")
    for name, scope in report["scopes"].items():
        print(f"\n{name}" + (f" [s]: {scope['window_s']}" if name != "full" else ""))
        print("Label                          Samples       RPS     p95 ms     Error %    Errors")
        records = [("ALL", scope["total"]), *scope["by_label"].items()]
        for label, record in records:
            rps, tail, rate = (
                "-" if record[field] is None else f"{record[field]:.2f}"
                for field in ("rps", "p95_ms", "error_pct")
            )
            print(f"{label:<30} {record['samples']:>7} {rps:>9} {tail:>10} {rate:>11} {record['errors']:>9}")
        total = scope["total"]
        if total["threads"] is not None:
            print(f"Observed VU (allThreads): {total['threads']}")
        if total["failed_codes"]:
            print(f"Failed samples by responseCode: {total['failed_codes']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jtl", type=Path, required=True)
    parser.add_argument("--profile", required=True, help="Identity of workload, data and runner")
    parser.add_argument("--origin-ms", type=int, help="First Thread Group start as epoch ms")
    parser.add_argument("--window", action="append", type=parse_window, default=[], metavar="NAME:START:END")
    parser.add_argument("--json-out", type=Path, help="New JSON file for baseline comparison")
    args = parser.parse_args()
    try:
        samples = read_jtl(args.jtl)
        windows = dict(args.window)
        if len(windows) != len(args.window):
            raise ValueError("Window names must be unique")
        origin = min(s.start for s in samples) if args.origin_ms is None else args.origin_ms
        report = {
            "profile": args.profile,
            "origin_ms": origin,
            "origin_kind": "first-sample" if args.origin_ms is None else "thread-group",
            "scopes": {"full": summarize(samples)},
        }
        for name, (start, end) in windows.items():
            selected = [s for s in samples if start * 1000 <= s.start - origin < end * 1000]
            report["scopes"][name] = summarize(selected, (start, end))
        if args.json_out:
            with args.json_out.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(report, stream, indent=2)
                stream.write("\n")
        print_report(report)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Analysis failed: {error}\n")


if __name__ == "__main__":
    main()
