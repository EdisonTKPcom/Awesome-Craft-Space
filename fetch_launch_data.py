#!/usr/bin/env python3
"""Refresh launch-pad and Starbase snapshots from Launch Library 2.

Uses the public LL2 API at ll.thespacedevs.com. The anonymous free tier is
about 15 requests per hour; this script checks /api-throttle/ first, pages
pads with ordering=id (limit 100), then fetches dashboard/starship. That is
typically 4 or 5 requests.
"""
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
UA = "Awesome-Craft-Space-launch-data (https://github.com/EdisonTKPcom/Awesome-Craft-Space)"
BASE = "https://ll.thespacedevs.com/2.3.0"
MYT = ZoneInfo("Asia/Kuala_Lumpur")
PAD_LIMIT = 100
SLEEP = 1.0


def iso_date(now=None):
    now = now or datetime.now(MYT)
    return now.strftime("%Y-%m-%d")


def get(url, attempt=0):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if e.code in (429, 403) and attempt < 5:
            wait = min(120, 20 * (attempt + 1))
            print(f"rate limited ({e.code}) on {url}, sleeping {wait}s", flush=True)
            time.sleep(wait)
            return get(url, attempt + 1)
        if e.code in (500, 502, 503, 504) and attempt < 5:
            wait = min(60, 2 ** attempt)
            print(f"server error {e.code} on {url}, retry in {wait}s", flush=True)
            time.sleep(wait)
            return get(url, attempt + 1)
        raise SystemExit(f"HTTP {e.code} for {url}: {body[:300]}")


def check_throttle(need):
    status, data = get(f"{BASE}/api-throttle/")
    if status != 200:
        raise SystemExit(f"throttle check failed: {status} {data}")
    limit = int(data.get("your_request_limit") or 15)
    used = int(data.get("current_use") or 0)
    freq = int(data.get("limit_frequency_secs") or 3600)
    remaining = limit - used
    print(
        f"LL2 throttle remaining={remaining}/{limit} used={used} window={freq}s need={need}",
        flush=True,
    )
    if remaining < need:
        raise SystemExit(
            f"Launch Library 2 free-tier budget is too low ({remaining} remaining, need {need}). "
            f"Wait up to {freq} seconds and retry."
        )


def fetch_all_pads():
    pads = []
    offset = 0
    while True:
        q = urllib.parse.urlencode({"limit": PAD_LIMIT, "offset": offset, "ordering": "id"})
        url = f"{BASE}/pads/?{q}"
        print(f"GET {url}", flush=True)
        status, data = get(url)
        if status != 200:
            raise SystemExit(f"pads fetch failed: {status} {data}")
        batch = data.get("results") or []
        pads.extend(batch)
        print(f"  got {len(batch)} (running unique {len({p['id'] for p in pads})}, count={data.get('count')})", flush=True)
        nxt = data.get("next")
        if not nxt or not batch:
            break
        offset += PAD_LIMIT
        time.sleep(SLEEP)
    # Deduplicate by id in case a later API change repeats a page.
    by_id = {}
    for p in pads:
        by_id[p["id"]] = p
    ordered = [by_id[i] for i in sorted(by_id)]
    declared = data.get("count")
    if declared and declared != len(ordered):
        print(f"warning: API count={declared} but unique pads={len(ordered)}", flush=True)
    return ordered


def country_name(p):
    c = p.get("country")
    if isinstance(c, dict):
        return c.get("name") or c.get("alpha_2_code") or ""
    return ""


def loc_name(obj):
    loc = obj.get("location") or {}
    if isinstance(loc, dict):
        return loc.get("name") or ""
    return loc or ""


def is_starbase(location, pad=None, text=""):
    parts = [location or "", text or ""]
    if pad:
        parts.append(pad.get("name") or "")
        parts.append(loc_name(pad))
    blob = " ".join(parts).lower()
    return "starbase" in blob or "boca chica" in blob


def fmt_times(iso):
    if not iso:
        return "", ""
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    utc = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    myt = dt.astimezone(MYT).strftime("%Y-%m-%d %H:%M:%S MYT")
    return utc, myt


def write_pads(pads, fetch_date):
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / "launch-pads.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "location",
                "country",
                "latitude",
                "longitude",
                "total_launch_count",
                "active",
                "source_url",
                "fetch_date",
            ],
        )
        w.writeheader()
        for p in pads:
            w.writerow(
                {
                    "name": p.get("name") or "",
                    "location": loc_name(p),
                    "country": country_name(p),
                    "latitude": p.get("latitude") if p.get("latitude") is not None else "",
                    "longitude": p.get("longitude") if p.get("longitude") is not None else "",
                    "total_launch_count": p.get("total_launch_count")
                    if p.get("total_launch_count") is not None
                    else "",
                    "active": "true" if p.get("active") else "false",
                    "source_url": p.get("url") or f"{BASE}/pads/",
                    "fetch_date": fetch_date,
                }
            )
    active = sum(1 for p in pads if p.get("active"))
    print(f"wrote {path} rows={len(pads)} active={active}", flush=True)
    return path, len(pads), active


def write_starbase(dash, fetch_date):
    rows = []
    previous = (dash.get("previous") or {}).get("launches") or []
    upcoming = (dash.get("upcoming") or {}).get("launches") or []
    events = (dash.get("upcoming") or {}).get("events") or []

    def add_launch(L, evidence):
        pad = L.get("pad") or {}
        location = loc_name(pad)
        if not is_starbase(location, pad, L.get("name") or ""):
            return
        st = L.get("status") or {}
        utc, myt = fmt_times(L.get("net"))
        rows.append(
            {
                "kind": "launch",
                "mission_name": L.get("name") or "",
                "status": st.get("name") or "",
                "outcome": st.get("abbrev") or ("planned" if evidence == "GOAL" else ""),
                "net_utc": utc,
                "net_myt": myt,
                "pad": pad.get("name") or "",
                "location": location,
                "evidence": evidence,
                "source_url": L.get("url") or f"{BASE}/dashboard/starship/",
                "fetch_date": fetch_date,
                "_sort": L.get("net") or "",
            }
        )

    for L in previous:
        add_launch(L, "FACT")
    for L in upcoming:
        add_launch(L, "GOAL")
    for e in events:
        loc = e.get("location") or ""
        if isinstance(loc, dict):
            loc = loc.get("name") or ""
        blob = " ".join([loc, e.get("name") or "", e.get("description") or ""])
        if not is_starbase(loc, text=blob):
            continue
        typ = e.get("type") or {}
        typ_name = typ.get("name") if isinstance(typ, dict) else (typ or "Event")
        utc, myt = fmt_times(e.get("date"))
        rows.append(
            {
                "kind": "event",
                "mission_name": e.get("name") or "",
                "status": typ_name,
                "outcome": "not recorded in LL2 dashboard",
                "net_utc": utc,
                "net_myt": myt,
                "pad": "",
                "location": loc,
                "evidence": "GOAL",
                "source_url": e.get("url") or f"{BASE}/dashboard/starship/",
                "fetch_date": fetch_date,
                "_sort": e.get("date") or "",
            }
        )

    rows.sort(key=lambda r: r["_sort"], reverse=True)
    for r in rows:
        del r["_sort"]

    path = DATA / "starbase-recent.csv"
    fields = [
        "kind",
        "mission_name",
        "status",
        "outcome",
        "net_utc",
        "net_myt",
        "pad",
        "location",
        "evidence",
        "source_url",
        "fetch_date",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    fact = sum(1 for r in rows if r["evidence"] == "FACT")
    goal = sum(1 for r in rows if r["evidence"] == "GOAL")
    print(f"wrote {path} rows={len(rows)} FACT={fact} GOAL={goal}", flush=True)
    return path, len(rows), fact, goal


def main():
    fetch_date = iso_date()
    # 1 throttle + ~3 pad pages + 1 dashboard
    check_throttle(need=5)
    time.sleep(SLEEP)
    pads = fetch_all_pads()
    time.sleep(SLEEP)
    print(f"GET {BASE}/dashboard/starship/", flush=True)
    status, dash = get(f"{BASE}/dashboard/starship/")
    if status != 200 or not isinstance(dash, dict):
        raise SystemExit(f"starship dashboard fetch failed: {status} {dash}")
    write_pads(pads, fetch_date)
    write_starbase(dash, fetch_date)
    print(f"snapshot date={fetch_date} (Asia/Kuala_Lumpur calendar date)", flush=True)


if __name__ == "__main__":
    main()
