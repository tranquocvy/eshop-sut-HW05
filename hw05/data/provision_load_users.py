"""Create synthetic FR-01 users on the local EShop test backend."""

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener


ENDPOINT = "http://127.0.0.1:3000/api/register"
FIXTURES = Path(__file__).with_name("load-credentials.csv")


def register(opener, fixture, row_number):
    payload = json.dumps({key: fixture[key] for key in ("name", "email", "password")})
    request = Request(
        ENDPOINT,
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with opener.open(request, timeout=5) as response:
            result = json.load(response)
            user_id = result.get("id")
            if (
                response.status != 200
                or result.get("message") != "User registered successfully"
                or type(user_id) is not int
                or user_id < 1
            ):
                raise SystemExit(f"Row {row_number}: registration response failed the checks.")
    except HTTPError as error:
        raise SystemExit(f"Row {row_number}: registration returned HTTP {error.code}.") from None
    except (URLError, ValueError):
        raise SystemExit(f"Row {row_number}: local backend is unavailable or returned invalid JSON.") from None
    return user_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional CSV with registered IDs outside the repository")
    parser.add_argument("--accounts", required=True, type=int, help="Number of one-use account rows for the run")
    args = parser.parse_args()
    output = args.output.resolve() if args.output is not None else None
    if output is not None and (output.is_relative_to(Path(__file__).resolve().parents[2]) or output.exists()):
        parser.error("--output must be a new file outside the repository")

    with FIXTURES.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["name", "email", "password"]:
            raise SystemExit("Expected the fixture columns name,email,password.")
        fixtures = list(reader)
    if not 1 <= args.accounts <= len(fixtures):
        parser.error(f"--accounts must be between 1 and the fixture count ({len(fixtures)})")

    emails = set()
    selected = fixtures[:args.accounts]
    for row_number, fixture in enumerate(selected, 1):
        email = fixture["email"] or ""
        password = fixture["password"] or ""
        if (
            not (fixture["name"] or "").strip()
            or not re.fullmatch(r"[a-z0-9][a-z0-9._+-]*@hw05\.example\.test", email)
            or email in emails
            or len(password) < 8
            or not all(re.search(pattern, password) for pattern in ("[A-Z]", "[a-z]", "[0-9]", "[@$!%*?&]"))
        ):
            raise SystemExit(f"Row {row_number}: invalid or duplicate synthetic account.")
        emails.add(email)

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
    opener = build_opener(ProxyHandler({}))
    credentials = []
    for index, fixture in enumerate(selected, 1):
        user_id = register(opener, fixture, index)
        credentials.append((user_id, fixture["email"], fixture["password"]))
    if len({row[0] for row in credentials}) != len(credentials):
        raise SystemExit("Registration returned duplicate account IDs.")
    if output is not None:
        with output.open("x", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow(("expected_user_id", "email", "password"))
            writer.writerows(credentials)
    print(f"Registered {len(credentials)} synthetic users.")


if __name__ == "__main__":
    main()
