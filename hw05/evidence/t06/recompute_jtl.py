"""Recompute the windows and figures used in HW05's T06 review (Python 3.10+)."""
import csv
import json
import math
import re
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import linear_regression

HW = Path(__file__).resolve().parents[2]
RESULTS = HW / "results"
TZ = timezone(timedelta(hours=7))


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as file:
        yield from csv.DictReader(file)


def read_jtl(case):
    path = RESULTS / f"23120410_{case}_20261119.jtl"
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [dict(start=int(row["timeStamp"]), end=int(row["timeStamp"]) + int(row["elapsed"]),
                     elapsed=int(row["elapsed"]), label=row["label"], vu=int(row["allThreads"]),
                     thread=row["threadName"], success=row["success"] == "true", code=row["responseCode"],
                     failure=row["failureMessage"], connect=int(row["Connect"]), latency=int(row["Latency"]),
                     line=reader.line_num) for row in reader]


def percentile(values, interpolate=False):
    ordered = sorted(values)
    rank = 0.95 * (len(ordered) + int(interpolate))
    if not interpolate:
        return ordered[math.ceil(rank) - 1]
    if rank >= len(ordered):
        return ordered[-1]
    lower = math.floor(rank)
    return ordered[lower - 1] + (rank - lower) * (ordered[lower] - ordered[lower - 1])


def summarize(group, duration):
    values = [row["elapsed"] for row in group]
    errors = sum(not row["success"] for row in group)
    return dict(n=len(group), rps=len(group) / duration, nearest=percentile(values),
                interpolated=percentile(values, True), errors=errors, error_pct=100 * errors / len(group),
                vu=[min(row["vu"] for row in group), max(row["vu"] for row in group)])


def from_epoch(epoch_ms):
    return datetime.fromtimestamp(epoch_ms / 1000, TZ).isoformat(timespec="milliseconds")


def absolute_window(rows, start, end, clock):
    group = [row for row in rows if start <= row[clock] < end]
    result = summarize(group, (end - start) / 1000)
    result["by_label"] = {
        label: {"n": len(values), "p95": percentile(values, True)}
        for label in sorted({row["label"] for row in group})
        if (values := [row["elapsed"] for row in group if row["label"] == label])
    }
    checkout = [row for row in group if row["label"] == "05 Checkout"]
    if checkout:
        result["checkout_p95"] = percentile([row["elapsed"] for row in checkout])
        result["checkout_max"] = max(checkout, key=lambda row: row["elapsed"])
    return result


def window(rows, t0, bounds, clock="end"):
    begin, end = bounds
    return absolute_window(rows, t0 + begin * 1000, t0 + end * 1000, clock)


def inspect_case(case, bounds, short_bounds):
    rows = read_jtl(case)
    begin = min(row["start"] for row in rows)
    end = max(row["end"] for row in rows)
    duration = (end - begin) / 1000
    labels = {}
    for label in sorted({row["label"] for row in rows}):
        group = [row for row in rows if row["label"] == label]
        span = (max(row["end"] for row in group) - min(row["start"] for row in group)) / 1000
        labels[label] = dict(summarize(group, duration), within_label_rps=len(group) / span)
    slow = [row for row in rows if row["elapsed"] >= 100]
    result = dict(first=from_epoch(begin), last=from_epoch(end), duration_s=duration, labels=labels,
                  total=summarize(rows, duration), status_codes=dict(Counter(row["code"] for row in rows)),
                  nonempty_failure_messages=sum(bool(row["failure"]) for row in rows),
                  windows={f"{a}-{b}": window(rows, begin, (a, b)) for a, b in bounds + short_bounds})
    if slow:
        result["slow"] = dict(n=len(slow), start_offsets_s=[(row["start"] - begin) / 1000 for row in
                                                         (min(slow, key=lambda row: row["start"]),
                                                          max(slow, key=lambda row: row["start"]))],
                              max=max(slow, key=lambda row: row["elapsed"]),
                              connects=sorted({row["connect"] for row in slow}),
                              latency_eq_elapsed=sum(row["latency"] == row["elapsed"] for row in slow))
    if case == "Spike":
        burst = [row for row in rows if row["thread"].startswith("Spike Burst")]
        first_burst = min(burst, key=lambda row: row["start"])
        last_burst = max(burst, key=lambda row: row["end"])
        result["burst"] = dict(first=first_burst, last=last_burst,
                               start_s=(first_burst["start"] - begin) / 1000,
                               end_s=(last_burst["end"] - begin) / 1000,
                               recovery_window_end_s_after_last_sample=85 - (last_burst["end"] - begin) / 1000)
        high_seconds = (window(rows, begin, (start, start + 1)) for start in range(60, 80))
        result["peak_one_second"] = max((stats for stats in high_seconds if stats["n"] >= 100),
                                        key=lambda stats: stats["nearest"])
    return result


def t04_comparison(case):
    record = json.loads((HW / f"evidence/t04/{case.lower()}-verification.json").read_text(encoding="utf-8"))
    rows = read_jtl(case)
    if case == "Stress":
        t0 = record["run"]["t0_epoch_ms"]
        return {"144_vu": window(rows, t0, (94, 108), "start"),
                "two_windows": [window(rows, t0, bounds, "start") for bounds in ((94, 101), (101, 108))]}
    recovery = record["spike_recovery"]
    baseline = recovery["baseline_steady_window"]
    peak = recovery["peak_steady_window"]
    last_thread_end = recovery["burst_last_thread_finish_epoch_ms"]
    ranges = {"baseline": (baseline["start_epoch_ms"], baseline["end_epoch_ms"]),
              "peak": (peak["start_epoch_ms"], peak["end_epoch_ms"]),
              "recovery_first": (last_thread_end + 5000, last_thread_end + 35000)}
    return {name: absolute_window(rows, *bounds, "start") for name, bounds in ranges.items()}


def t05_comparison():
    evidence = json.loads((HW / "evidence/t05/endurance-verification.json").read_text(encoding="utf-8"))
    t0 = evidence["run"]["t0_epoch_ms"]
    rows = read_jtl("Endurance")
    stable = [row for row in rows if t0 + 20_000 <= row["start"] < t0 + 920_000]
    resources = list(read_csv(RESULTS / "23120410_Endurance_20261119_resources.csv"))
    tail = [row for row in resources if t0 + 200_000 <= int(row["epoch_ms"]) < t0 + 920_000]
    slope = linear_regression([(int(row["epoch_ms"]) - t0) / 60_000 for row in tail],
                              [float(row["node_working_set_mib"]) for row in tail]).slope
    return dict(rps=len(stable) / 900, errors=sum(not row["success"] for row in stable),
                node_peak_mib=max(float(row["node_working_set_mib"]) for row in resources), tail_slope=slope,
                first_window=window(rows, t0, (20, 200), "start"),
                last_window=window(rows, t0, (740, 920), "start"))


def product_query_plans():
    schema = (HW.parent / "backend/database.js").read_text(encoding="utf-8")
    create = re.search(r"CREATE TABLE products \([^;]+?\)", schema).group()
    with sqlite3.connect(":memory:") as db:
        db.execute(create)
        search = db.execute("EXPLAIN QUERY PLAN SELECT * FROM products WHERE name LIKE ?", ("%Galaxy%",))
        detail = db.execute("EXPLAIN QUERY PLAN SELECT * FROM products WHERE id = ?", (1,))
        return {"sqlite_version": sqlite3.sqlite_version, "substring": list(search), "primary_key": list(detail)}


if __name__ == "__main__":
    stress = [(5, 25), (35, 55), (65, 85), (89, 90), (90, 91), (91, 92), (95, 115), (111, 112)]
    spike = [(5, 55), (59, 60), (60, 65), (65, 75), (75, 76), (80, 85), (85, 145)]
    print(json.dumps({"Stress": inspect_case("Stress", stress, [(s, s + 5) for s in range(95, 115, 5)]),
                      "Spike": inspect_case("Spike", spike, [(65, 70), (70, 75), (85, 90), (90, 95)]),
                      "T04": {case: t04_comparison(case) for case in ("Stress", "Spike")},
                      "Endurance": t05_comparison(), "sqlite_query_plans": product_query_plans()}, indent=2))
