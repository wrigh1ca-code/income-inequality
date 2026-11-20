#!/usr/bin/env python3
"""Refresh the Federal Reserve wealth data embedded in index.html.

Pulls from FRED (St. Louis Fed):
  - Distributional Financial Accounts: bottom-50% net worth and household count,
    and wealth shares of the top 1%, next 9%, next 40% and bottom 50%
  - CPI-U (not seasonally adjusted) to express bottom-50% wealth in real dollars

Uses the FRED API when FRED_API_KEY is set, otherwise FRED's public CSV download.
Every series is sanity-checked; if anything looks wrong the script exits with an
error and changes nothing, so a bad download can never break the site.

Usage: python scripts/update_data.py            # update in place
       python scripts/update_data.py --dry-run  # report only
"""
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
DATA_DIR = os.path.join(ROOT, "data")

SHARES = {"top1": "WFRBST01134", "next9": "WFRBSN09161", "next40": "WFRBSN40188", "bottom50": "WFRBSB50215"}
B50_NETWORTH = "WFRBLB50107"   # millions of dollars
B50_HOUSEHOLDS = "WFRBLB50300"  # number of households
CPI = "CPIAUCNS"


def fetch(series_id):
    key = os.environ.get("FRED_API_KEY", "").strip()
    if key:
        url = ("https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={series_id}&api_key={key}&file_type=json")
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "income-inequality-site-updater/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8")
            break
        except Exception as e:  # network hiccup: back off and retry
            last = e
            time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"could not download {series_id}: {last}")
    out = []
    if key:
        for o in json.loads(body)["observations"]:
            if o["value"] not in (".", ""):
                out.append((dt.date.fromisoformat(o["date"]), float(o["value"])))
    else:
        rows = csv.reader(io.StringIO(body))
        next(rows)  # header
        for d, v in rows:
            if v not in (".", ""):
                out.append((dt.date.fromisoformat(d), float(v)))
    if not out:
        raise RuntimeError(f"{series_id}: no observations")
    return out


def quarter(d):
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


def check(cond, msg):
    if not cond:
        sys.exit(f"Sanity check failed: {msg}. No changes written.")


def main(dry_run=False):
    nw = dict(fetch(B50_NETWORTH))
    hh = dict(fetch(B50_HOUSEHOLDS))
    cpi_m = fetch(CPI)
    shares = {k: dict(fetch(v)) for k, v in SHARES.items()}

    # CPI annual averages; the latest complete year is the dollar base
    by_year = {}
    for d, v in cpi_m:
        by_year.setdefault(d.year, []).append(v)
    cpi_avg = {y: sum(v) / len(v) for y, v in by_year.items()}
    complete = [y for y, v in by_year.items() if len(v) == 12]
    check(complete, "no complete CPI year")
    base = max(complete)

    # Bottom-50% real net worth per household, Q3 of each year
    b50 = []
    for d in sorted(nw):
        if d.month == 7 and d in hh and d.year in cpi_avg:
            real = nw[d] * 1e6 / hh[d] * cpi_avg[base] / cpi_avg[d.year]
            b50.append([d.year, round(real)])
    check(len(b50) >= 30, f"only {len(b50)} years of bottom-50% data")
    check(b50[0][0] == 1989, f"bottom-50% series starts in {b50[0][0]}, expected 1989")
    check(all(0 < v < 500_000 for _, v in b50), "bottom-50% value out of range")

    # Wealth shares: Q3 1989 vs the latest quarter all four groups report
    common = set.intersection(*(set(s) for s in shares.values()))
    start_d = dt.date(1989, 7, 1)
    check(start_d in common, "Q3 1989 missing from share series")
    latest_d = max(common)

    def snap(d):
        row = {"q": quarter(d)}
        row.update({k: round(shares[k][d], 1) for k in SHARES})
        return row

    for d in (start_d, latest_d):
        tot = sum(shares[k][d] for k in SHARES)
        check(abs(tot - 100) < 1.0, f"shares in {quarter(d)} sum to {tot:.1f}")
    top1_max_d = max(shares["top1"], key=lambda d: shares["top1"][d])
    dfa = {"start": snap(start_d), "latest": snap(latest_d),
           "top1max": {"q": quarter(top1_max_d), "v": round(shares["top1"][top1_max_d], 1)}}

    html = open(INDEX, encoding="utf-8").read()
    m = re.search(r"^const DATA=(.*);$", html, re.M)
    check(m is not None, "could not find DATA in index.html")
    data = json.loads(m.group(1))
    changed = data.get("b50") != b50 or data.get("dfa") != dfa or data.get("meta", {}).get("b50base") != base

    print(f"Dollar base year: {base}")
    print(f"Bottom-50% per household: {b50[0][0]} ${b50[0][1]:,} -> {b50[-1][0]} ${b50[-1][1]:,}")
    print(f"Wealth shares {dfa['latest']['q']}: " + ", ".join(f"{k} {dfa['latest'][k]}%" for k in SHARES))
    print(f"Top 1% record: {dfa['top1max']['v']}% in {dfa['top1max']['q']}")
    if not changed:
        print("No change in Federal Reserve data.")
        return
    if dry_run:
        print("Dry run: data changed, nothing written.")
        return

    data["b50"] = b50
    data["dfa"] = dfa
    data.setdefault("meta", {})
    data["meta"]["b50base"] = base
    data["meta"]["updated"] = dt.date.today().strftime("%B %Y")
    html = html[:m.start()] + "const DATA=" + json.dumps(data, separators=(",", ":")) + ";" + html[m.end():]
    open(INDEX, "w", encoding="utf-8").write(html)

    with open(os.path.join(DATA_DIR, "bottom50_real_networth_per_household.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", f"net_worth_per_household_{base}_dollars"])
        w.writerows(b50)
    with open(os.path.join(DATA_DIR, "dfa_wealth_shares_quarterly.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter", *SHARES])
        for d in sorted(common):
            w.writerow([quarter(d), *(shares[k][d] for k in SHARES)])
    print("index.html and data/ updated.")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
