"""Compare three valid candidate JTL summaries with a compatible p95 baseline."""

import argparse
import json
import math
from pathlib import Path
from statistics import median
from sys import stderr


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_inputs(baseline, runs):
    minimum = baseline.get("min_samples_per_label", 100)
    if type(minimum) is not int or minimum < 100:
        raise ValueError("T07A requires at least 100 samples per label in each compared scope.")
    if not baseline["profile"] or not baseline["scopes"]:
        raise ValueError("Baseline requires a profile ID and at least one scope.")
    for name, scope in baseline["scopes"].items():
        if not scope["p95_ms"] or any(not math.isfinite(p) or p < 0 for p in scope["p95_ms"].values()):
            raise ValueError(f"Invalid baseline p95 in scope {name}.")
    reasons = []
    if len(runs) != 3:
        reasons.append(f"Need 3 independent runs, got {len(runs)}.")
    for index, run in enumerate(runs, 1):
        if run["profile"] != baseline["profile"]:
            reasons.append(f"Run {index}: profile mismatch ({run['profile']} vs {baseline['profile']}).")
            continue
        if run["scopes"]["full"]["total"]["errors"]:
            reasons.append(f"Run {index}: failed samples present. Review functionality or fixture before p95.")
        for name, expected in baseline["scopes"].items():
            actual = run["scopes"].get(name)
            if actual is None or actual["window_s"] != expected["window_s"] or (
                actual["window_s"] is not None and run["origin_kind"] != expected["origin_kind"]
            ):
                reasons.append(f"Run {index}: absent or incompatible scope {name}.")
                continue
            if set(actual["by_label"]) != set(expected["p95_ms"]):
                reasons.append(f"Run {index}: label set differs in {name}.")
                continue
            if any(record["samples"] < minimum for record in actual["by_label"].values()):
                reasons.append(f"Run {index}: fewer than {minimum} samples for a label in {name}.")
            baseline_rps = expected.get("rps")
            if baseline_rps is not None and (actual["total"]["rps"] or 0) < 0.9 * baseline_rps:
                reasons.append(f"Run {index}: RPS below 90% of baseline in {name}.")
    return reasons


def compare(baseline, runs):
    reasons = check_inputs(baseline, runs)
    if reasons:
        print("WARN: Inconclusive p95 comparison.")
        for reason in reasons:
            print(f"- {reason}")
        return 2

    worst = 0
    print("Scope / label | baseline ms | run p95 ms | median ms | limit ms | verdict")
    for name, scope in baseline["scopes"].items():
        for label, reference in scope["p95_ms"].items():
            values = [run["scopes"][name]["by_label"][label]["p95_ms"] for run in runs]
            limit = reference + max(4, 0.25 * reference)
            center = median(values)
            outcome = "FAIL" if center > limit else "WARN" if max(values) > limit else "PASS"
            worst = max(worst, ("PASS", "WARN", "FAIL").index(outcome))
            print(f"{name} / {label} | {reference:.2f} | {values} | {center:.2f} | {limit:.2f} | {outcome}")
    print(f"Overall: {('PASS', 'WARN', 'FAIL')[worst]}")
    return (0, 2, 1)[worst]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--runs", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    try:
        if len({path.resolve() for path in args.runs}) != len(args.runs):
            raise ValueError("Supply distinct run files. Do not repeat one run to form a median.")
        return compare(load(args.baseline), [load(path) for path in args.runs])
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(f"Invalid comparison inputs: {error}", file=stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
