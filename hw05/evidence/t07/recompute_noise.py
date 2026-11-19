"""Recompute T07A's per-label p95 noise from T04 and T05 JTL files."""

import csv
import json
from pathlib import Path
from runpy import run_path
from statistics import median

HW05 = Path(__file__).resolve().parents[2]
T04_ARCHIVE = HW05.parents[1] / ".runtime" / "T04"
percentile = run_path(str(HW05 / "evidence" / "t06" / "recompute_jtl.py"))["percentile"]

T04_RUNS = {
    "Load": ("Load-original-20261119-005503", None),
    "Stress": ("Stress-original-20261119-012349", "Stress-rerun-20261119-013048", None),
}


def read_jtl(path):
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(rows):
    if not rows or any(row["success"] != "true" for row in rows):
        raise ValueError("Expected a nonempty window of successful samples.")
    elapsed_by_label = {}
    for row in rows:
        elapsed_by_label.setdefault(row["label"], []).append(int(row["elapsed"]))
    return {
        label: percentile(elapsed, interpolate=True)
        for label, elapsed in sorted(elapsed_by_label.items())
    }


def print_noise(summaries):
    for label in summaries[0]:
        values = [summary[label] for summary in summaries]
        span = max(values) - min(values)
        samples = " / ".join(f"{value:.2f}" for value in values)
        percent = 100 * span / median(values)
        print(f"{label}: {samples} ms; span {span:.2f} ms ({percent:.2f}%)")


def window(rows, t0, start, end):
    return [
        row for row in rows
        if t0 + 1000 * start <= int(row["timeStamp"]) < t0 + 1000 * end
    ]


def compare_t04(scenario, runs):
    full = []
    plateau = []
    stem = f"23120410_{scenario}_20261119"
    for archive_name in runs:
        if archive_name:
            folder = T04_ARCHIVE / archive_name
            evidence = folder / "evidence"
        else:
            folder = HW05
            evidence = folder / "evidence" / "t04"
        results = folder / "results"
        rows = read_jtl(results / f"{stem}.jtl")
        summary = summarize(rows)
        dashboard = read_json(results / stem / "statistics.json")
        if len(rows) != dashboard["Total"]["sampleCount"] or any(
            abs(value - dashboard[label]["pct2ResTime"]) >= 1e-8
            for label, value in summary.items()
        ):
            raise ValueError(f"JTL and dashboard differ: {results / stem}")
        print(f"{scenario} {archive_name or 'submitted'}: {len(rows)} samples")
        full.append(summary)

        if scenario == "Stress":
            t0 = read_json(evidence / "stress-verification.json")["run"]["t0_epoch_ms"]
            stable = window(rows, t0, 94, 108)
            if {row["allThreads"] for row in stable} != {"144"}:
                raise ValueError(f"Expected 144 VU in the plateau: {results / stem}")
            plateau.append(summarize(stable))

    print(f"T04 {scenario}, full runs")
    print_noise(full)
    if plateau:
        print("T04 Stress, 144 VU in [94,108) s")
        print_noise(plateau)


def main():
    for scenario, runs in T04_RUNS.items():
        compare_t04(scenario, runs)
    record = read_json(HW05 / "evidence" / "t05" / "endurance-verification.json")
    t0 = record["run"]["t0_epoch_ms"]
    rows = read_jtl(HW05 / "results" / "23120410_Endurance_20261119.jtl")
    print("T05 Endurance, five consecutive 180 s windows after ramp-up")
    print_noise([
        summarize(window(rows, t0, start, start + 180))
        for start in range(20, 920, 180)
    ])


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        raise SystemExit(
            f"Missing input: {error.filename}\n"
            f"The three archived T04 runs are needed at {T04_ARCHIVE}."
        ) from None
