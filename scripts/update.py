"""Refresh the dataset from panelcompare.com.

Run daily by .github/workflows/update.yml, after the site's 22:05 UTC rebuild.

- data/            the latest copy of each published file, overwritten
- snapshots/       one copy of price-index.csv per index day, never rewritten
- history/         one row per service per day, appended for days not yet in it

With --backfill it also rebuilds history/ from the API's per-service history
(about 50 days on 2026-10-28). That reads one endpoint per service, so it is
for the first run, not for the schedule.

Standard library only, so the workflow needs no install step.
"""

import csv
import io
import json
import os
import sys
import time
import urllib.request

BASE = "https://panelcompare.com"
UA = "smm-panel-price-index/1.0 (+https://github.com/azorkai/smm-panel-price-index)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    ("/data/price-index.csv", "data/price-index.csv"),
    ("/data/price-index.json", "data/price-index.json"),
    ("/data/panel-facts.csv", "data/panel-facts.csv"),
    ("/data/panel-facts.json", "data/panel-facts.json"),
]

HISTORY = "history/price-index-history.csv"
HISTORY_COLUMNS = [
    "day",
    "platform_slug",
    "service_slug",
    "service",
    "min_price_per_1000",
    "median_price_per_1000",
    "max_price_per_1000",
    "quotable_min_price_per_1000",
    "quotable_max_price_per_1000",
    "panels_sampled",
]


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as res:
        if res.status != 200:
            raise RuntimeError(f"{path}: HTTP {res.status}")
        return res.read()


def write(rel, body):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(body)


def read_history():
    path = os.path.join(ROOT, HISTORY)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_history(rows):
    rows.sort(key=lambda r: (r["day"], r["platform_slug"], r["service_slug"]))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=HISTORY_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    write(HISTORY, buf.getvalue().encode("utf-8"))


def blank(v):
    # The API's floats carry binary noise (7.393750000000001); six decimals is
    # finer than any price the site prints.
    if v is None:
        return ""
    return round(v, 6) if isinstance(v, float) else v


def backfill():
    services = []
    offset = 0
    while True:
        page = json.loads(get(f"/api/v1/services?limit=200&offset={offset}"))
        services += page["data"]
        nxt = page["_meta"]["pagination"]["next"]
        if not nxt:
            break
        offset += 200
    rows = []
    for s in services:
        p, sv = s["platform"]["slug"], s["slug"]
        detail = json.loads(get(f"/api/v1/services/{p}/{sv}?limit=1"))["data"]
        for h in detail.get("priceIndexHistory") or []:
            rows.append(
                {
                    "day": h["day"],
                    "platform_slug": p,
                    "service_slug": sv,
                    "service": s["name"],
                    "min_price_per_1000": blank(h.get("minPricePer1000")),
                    "median_price_per_1000": blank(h.get("medianPricePer1000")),
                    "max_price_per_1000": blank(h.get("maxPricePer1000")),
                    "quotable_min_price_per_1000": blank(h.get("quotableMinPricePer1000")),
                    "quotable_max_price_per_1000": blank(h.get("quotableMaxPricePer1000")),
                    "panels_sampled": blank(h.get("panelsSampled")),
                }
            )
        time.sleep(0.5)
    write_history(rows)
    print(f"backfill: {len(rows)} rows from {len(services)} services")


def main():
    if "--backfill" in sys.argv:
        backfill()

    bodies = {}
    for src, dest in FILES:
        bodies[dest] = get(src)
        write(dest, bodies[dest])

    index = list(csv.DictReader(io.StringIO(bodies["data/price-index.csv"].decode("utf-8"))))
    if not index or "day" not in index[0]:
        raise RuntimeError("price-index.csv has no rows or no day column")
    day = max(r["day"] for r in index)

    snapshot = f"snapshots/price-index/{day}.csv"
    if not os.path.exists(os.path.join(ROOT, snapshot)):
        write(snapshot, bodies["data/price-index.csv"])

    history = read_history()
    # The site recomputes the current day several times a day, so a day already
    # in the file is replaced by the newer reading rather than kept twice.
    history = [r for r in history if r["day"] != day]
    for r in index:
        if r["day"] != day:
            continue
        history.append({k: r.get(k, "") for k in HISTORY_COLUMNS})
    write_history(history)
    print(f"index day {day}: {sum(1 for r in index if r['day'] == day)} services")


if __name__ == "__main__":
    main()
