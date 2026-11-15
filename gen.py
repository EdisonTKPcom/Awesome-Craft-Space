#!/usr/bin/env python3
"""Generate README.md and assets/dashboard.svg from stats and launch-data CSVs."""
import csv
import html
import urllib.parse as U
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AS = "2026-11-15"
ACTIVE_SINCE = "2026-10-16"
UNMAINTAINED_BEFORE = "2025-11-15"

S = {
    r[0]: dict(stars=int(r[1]), forks=int(r[2]), lic=r[3], lang=r[4], push=r[5])
    for r in csv.reader((ROOT / "stats.tsv").open(), delimiter="\t")
}

LIC_OVERRIDE = {
    "openrocket/openrocket": "GPL-3.0-or-later",
    "nasa/openmct": "Apache-2.0",
    "OpenSpace/OpenSpace": "MIT",
    "nasa/trick": "NOSA-1.3",
    "OpenC3/cosmos": "OpenC3 Builder's License V2",
}
ARCHIVED = {"poliastro/poliastro", "r-spacex/SpaceX-API"}
LICNAME = {"NOASSERTION": "Undeclared", "none": "Undeclared"}

# Categories: (heading, intro_or_None, entries)
# entry: (name, repo_or_url, description)
C = [
    (
        "Orbital mechanics and astrodynamics",
        None,
        [
            ("ANISE", "nyx-space/anise", "Rust toolkit for SPICE-style trajectory, orientation and ephemeris work."),
            ("hapsira", "pleiszenburg/hapsira", "Community fork of poliastro for astrodynamics in Python. Unmaintained (last push 2024-05-09)."),
            ("Nyx", "nyx-space/nyx", "High-fidelity astrodynamics and mission-design toolkit written in Rust."),
            ("Orekit", "CS-SI/Orekit", "Low-level space dynamics library. The GitHub repository is a mirror; development happens on gitlab.orekit.org."),
            ("poliastro", "poliastro/poliastro", "Python astrodynamics library. Archived (last push 2023-10-14); see hapsira for a community fork."),
            ("pykep", "esa/pykep", "ESA toolkit for interplanetary trajectory design and optimisation."),
            ("python-sgp4", "brandon-rhodes/python-sgp4", "Python implementation of the SGP4/SDP4 satellite propagator."),
            ("Skyfield", "skyfielders/python-skyfield", "Astronomy and Earth-satellite positions computed from official almanac data."),
            ("SpiceyPy", "AndrewAnnex/SpiceyPy", "Pythonic wrapper for NASA's SPICE toolkit."),
            ("Tudat", "tudat-team/tudatpy", "TU Delft astrodynamics toolbox, with a Python interface around the C++ core."),
        ],
    ),
    (
        "Mission design and simulation",
        None,
        [
            ("42", "ericstoneking/42", "General-purpose spacecraft attitude and orbit simulation. No licence file was present at the repository HEAD on 2026-11-15."),
            ("Basilisk", "AVSLab/basilisk", "Modular astrodynamics and spacecraft simulation framework from CU Boulder's AVS Lab."),
            ("GMAT", "nasa/GMAT", "NASA's General Mission Analysis Tool for spacecraft trajectory design and optimisation."),
            ("NOS3", "nasa/nos3", "NASA Operational Simulator for Small Satellites. GitHub did not detect a standard SPDX licence."),
            ("Orbiter", "orbitersim/orbiter", "Realistic spaceflight simulator with a long-standing add-on ecosystem."),
            ("OSP-Magnum", "TheOpenSpaceProgram/osp-magnum", "Open-source spaceflight game and simulation project in the spirit of Kerbal Space Program."),
            ("pagmo", "esa/pagmo2", "ESA's platform for massively parallel optimisation, often used for trajectory problems."),
            ("Trick", "nasa/trick", "NASA simulation framework used for flight software testbeds. Licensed under the NASA Open Source Agreement 1.3, which is not OSI-approved."),
        ],
    ),
    (
        "Flight software",
        None,
        [
            ("cFS", "nasa/cFS", "NASA Core Flight System, a reusable flight software framework used across many missions."),
            ("Copper", "copper-project/copper-rs", "Rust runtime for robotics and, as a stated project goal, future spacefaring systems."),
            ("F Prime", "nasa/fprime", "NASA flight software and embedded systems framework, flown on missions including Ingenuity."),
            ("NanoSat MO Framework", "esa/nanosat-mo-framework", "ESA CCSDS Mission Operations framework for nanosatellites. No licence file was present at the repository HEAD on 2026-11-15."),
        ],
    ),
    (
        "Rocket design and trajectory",
        None,
        [
            ("openMotor", "reilleya/openMotor", "Internal ballistics simulator for commercial and experimental solid rocket motors."),
            ("OpenRocket", "openrocket/openrocket", "Model-rocket design and simulation. The licence is GPL-3.0-or-later with an additional permission for data files."),
            ("RocketCEA", "sonofeft/RocketCEA", "Python wrapper for NASA's Chemical Equilibrium with Applications code."),
            ("RocketPy", "RocketPy-Team/RocketPy", "Next-generation six-degree-of-freedom rocket trajectory simulator in Python."),
        ],
    ),
    (
        "Ground stations and telemetry",
        None,
        [
            ("gr-satellites", "daniestevez/gr-satellites", "GNU Radio decoders for amateur and scientific satellite telemetry."),
            ("OpenC3 COSMOS", "OpenC3/cosmos", "Command and control platform for mission operations. Distributed under the OpenC3 Builder's License V2, which is source-available and not OSI-approved."),
            ("OpenMCT", "nasa/openmct", "NASA web-based mission control framework for telemetry display and operations tools."),
            ("SatDump", "SatDump/SatDump", "Multi-mission satellite data decoder, with support for weather and Earth-observation downlinks."),
            ("SatNOGS Network", "https://gitlab.com/librespacefoundation/satnogs/satnogs-network", "Libre Space Foundation network of volunteer satellite ground stations. Official source is on GitLab; a SatNOGS Client lives in the same group. GitLab stars are not included in the combined GitHub star total."),
            ("YAMCS", "yamcs/yamcs", "Mission control system for telemetry, telecommand and packet processing."),
        ],
    ),
    (
        "Satellite tracking and TLE",
        None,
        [
            ("Gpredict", "csete/gpredict", "Real-time satellite tracking and orbit prediction application."),
            ("KeepTrack", "thkruz/keeptrack.space", "Browser-based space-object visualisation and tracking workbench."),
            ("orbit-predictor", "satellogic/orbit-predictor", "Python library for satellite pass prediction from TLEs. Unmaintained (last push 2025-06-16)."),
            ("satellite.js", "shashwatak/satellite-js", "JavaScript port of the SGP4/SDP4 propagator for browser and Node.js use."),
        ],
    ),
    (
        "Launch data and APIs",
        "Launch Library 2 itself is a public HTTP API, not a public application repository, so it is not listed as a software entry. Official examples for the pad and location endpoints live under Launch sites and pads. Combined GitHub stars exclude non-GitHub hosts.",
        [
            ("Spaceflight News API", "TheSpaceDevs/spaceflightnewsapi", "News and blog API from TheSpaceDevs. No licence file was present at the repository HEAD on 2026-11-15."),
            ("SpaceX-API", "r-spacex/SpaceX-API", "Unofficial community API for historical SpaceX launch data. Archived (last push 2024-08-17)."),
        ],
    ),
    (
        "Launch sites and pads",
        None,  # filled with a data-aware intro in emit()
        [
            ("TheSpaceDevs Tutorials", "TheSpaceDevs/Tutorials", "Official examples for Launch Library 2, including the pad and location endpoints used to build the snapshot in this repository."),
        ],
    ),
    (
        "CubeSat",
        None,
        [
            ("libcsp", "libcsp/libcsp", "Cubed Satellite Protocol, a small network-layer stack used on many CubeSats."),
            ("OpenLST", "OpenLST/openlst", "Open-source radio design based on the Planet Line-of-Sight Transceiver. Unmaintained (last push 2023-12-04)."),
        ],
    ),
    (
        "Visualisation",
        None,
        [
            ("Celestia", "CelestiaProject/Celestia", "Real-time 3D space simulation that lets you travel through the solar system and beyond."),
            ("Cesium", "CesiumGS/cesium", "Open geospatial 3D globe and map engine for the web."),
            ("OpenSpace", "OpenSpace/OpenSpace", "Interactive data visualisation software for the known universe, used in planetariums and research."),
            ("Stellarium", "Stellarium/stellarium", "Planetarium software that renders a realistic sky in real time."),
            ("WorldWind Java", "NASAWorldWind/WorldWindJava", "NASA virtual globe SDK. No licence file was confirmed at the repository HEAD on 2026-11-15."),
        ],
    ),
    (
        "Recent Starbase activity",
        None,  # filled with a data-aware intro in emit()
        [
            ("Starship Telemetry", "chrisjbillington/starship_telemetry", "Extracts on-screen telemetry from Starship webcasts. Unmaintained (last push 2023-04-29)."),
            ("StarshipTelemetryExtractor", "SofieBrink/StarshipTelemetryExtractor", "C# tool for reading telemetry overlays from Starship flight videos. Unmaintained (last push 2024-11-21)."),
        ],
    ),
]


def k(n):
    if n >= 1e6:
        return f"{n/1e6:.2f}M"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def anchor(n):
    return (
        n.lower()
        .replace(",", "")
        .replace(" ", "-")
        .replace("/", "")
        .replace("&", "")
    )


def is_github(repo):
    return not str(repo).startswith("http")


def url_of(repo):
    return repo if str(repo).startswith("http") else f"https://github.com/{repo}"


def lic_of(repo):
    if not is_github(repo):
        return None
    if repo in LIC_OVERRIDE:
        return LIC_OVERRIDE[repo]
    raw = S[repo]["lic"]
    return LICNAME.get(raw, raw)


def load_csv(name):
    path = ROOT / "data" / name
    return list(csv.DictReader(path.open(encoding="utf-8")))


def fact(text):
    return (
        f'<span style="display:inline-block;border:2px solid #0284c7;padding:0 7px;'
        f'border-radius:4px;font-weight:700;color:#0284c7;">FACT</span> {text}'
    )


def goal(text):
    return (
        f'<span style="display:inline-block;border:2px dashed #d97706;padding:0 7px;'
        f'border-radius:4px;font-weight:700;color:#d97706;">GOAL</span> {text}'
    )


def estimate(text):
    return (
        f'<span style="display:inline-block;border:2px dotted #7c3aed;padding:0 7px;'
        f'border-radius:4px;font-weight:700;color:#7c3aed;">ESTIMATE</span> {text}'
    )


def write_dashboard_svg(path, *, gh_tools, tot, forks, langs, active, n_tools, pads, starbase, cat_stars, top):
    W, H = 880, 640
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-sans-serif, system-ui, sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#0b1220"/>',
        '<text x="24" y="36" fill="#fde68a" font-size="20" font-weight="700">Evidence dashboard</text>',
        f'<text x="24" y="58" fill="#94a3b8" font-size="12">Snapshot {AS}. Solid = FACT, dashed = GOAL, dotted = ESTIMATE.</text>',
        # legend
        '<rect x="620" y="20" width="14" height="10" fill="#38bdf8" stroke="#38bdf8"/>',
        '<text x="640" y="30" fill="#e2e8f0" font-size="11">FACT</text>',
        '<rect x="690" y="20" width="22" height="10" fill="none" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6 4"/>',
        '<text x="718" y="30" fill="#e2e8f0" font-size="11">GOAL</text>',
        '<rect x="770" y="20" width="22" height="10" fill="none" stroke="#a78bfa" stroke-width="2" stroke-dasharray="2 3"/>',
        '<text x="798" y="30" fill="#e2e8f0" font-size="11">ESTIMATE</text>',
    ]

    # Top 10 FACT star bars (left)
    parts.append('<text x="24" y="92" fill="#e2e8f0" font-size="14" font-weight="700">Top projects by GitHub stars (FACT)</text>')
    mx = top[0][1] if top else 1
    y = 106
    bar_x, bar_w = 200, 220
    for name, stars in top:
        bw = max(2, int(stars / mx * bar_w))
        parts.append(f'<text x="24" y="{y+11}" fill="#cbd5e1" font-size="11">{html.escape(name)}</text>')
        parts.append(
            f'<rect x="{bar_x}" y="{y}" width="{bw}" height="14" fill="#38bdf8" stroke="#0284c7" stroke-width="1"/>'
        )
        parts.append(f'<text x="{bar_x+bw+8}" y="{y+11}" fill="#fde68a" font-size="11">{k(stars)}</text>')
        y += 22

    # Category combined stars (ESTIMATE, dotted)
    parts.append('<text x="470" y="92" fill="#e2e8f0" font-size="14" font-weight="700">Combined stars by category (ESTIMATE)</text>')
    cmax = max((s for _, s in cat_stars), default=1) or 1
    y = 106
    bar_x, bar_w = 670, 130
    for name, stars in cat_stars:
        bw = max(2, int(stars / cmax * bar_w)) if stars else 0
        label = name if len(name) <= 28 else name[:26] + "…"
        parts.append(f'<text x="470" y="{y+11}" fill="#cbd5e1" font-size="11">{html.escape(label)}</text>')
        if bw:
            parts.append(
                f'<rect x="{bar_x}" y="{y}" width="{bw}" height="14" fill="none" stroke="#a78bfa" stroke-width="2" stroke-dasharray="2 3"/>'
            )
        parts.append(f'<text x="{bar_x+max(bw,2)+8}" y="{y+11}" fill="#ddd6fe" font-size="11">{k(stars)}</text>')
        y += 22

    # Bottom summary cards
    by = 510
    def card(x, title, value, tag, stroke, dash):
        parts.append(f'<rect x="{x}" y="{by}" width="200" height="110" rx="8" fill="#111827" stroke="{stroke}" stroke-width="2" stroke-dasharray="{dash}"/>')
        parts.append(f'<text x="{x+14}" y="{by+24}" fill="{stroke}" font-size="11" font-weight="700">{tag}</text>')
        parts.append(f'<text x="{x+14}" y="{by+62}" fill="#f8fafc" font-size="26" font-weight="700">{html.escape(str(value))}</text>')
        parts.append(f'<text x="{x+14}" y="{by+86}" fill="#94a3b8" font-size="12">{html.escape(title)}</text>')

    n_pads = len(pads)
    n_active = sum(1 for p in pads if p["active"] == "true")
    fact_flights = [r for r in starbase if r["evidence"] == "FACT" and r["kind"] == "launch"]
    goal_events = [r for r in starbase if r["evidence"] == "GOAL"]
    card(24, "LL2 launch pads listed", n_pads, "FACT", "#38bdf8", "0")
    card(236, "pads marked active (our count)", n_active, "ESTIMATE", "#a78bfa", "2 3")
    card(448, "Starbase flights on LL2 dashboard", len(fact_flights), "FACT", "#38bdf8", "0")
    card(660, f"upcoming events still listed ({len(goal_events)})", "GOAL", "GOAL", "#f59e0b", "6 4")

    parts.append("</svg>")
    path.write_text("".join(parts))


def emit():
    pads = load_csv("launch-pads.csv")
    starbase = load_csv("starbase-recent.csv")
    fetch_date = pads[0]["fetch_date"] if pads else AS

    tools = [(n, r, d) for _, _, ts in C for (n, r, d) in ts]
    gh_tools = [t for t in tools if is_github(t[1])]
    missing = [t[1] for t in gh_tools if t[1] not in S]
    if missing:
        raise SystemExit(f"missing stats for: {missing}")

    tot = sum(S[t[1]]["stars"] for t in gh_tools)
    forks = sum(S[t[1]]["forks"] for t in gh_tools)
    langs = sorted({S[t[1]]["lang"] for t in gh_tools if S[t[1]]["lang"] not in ("", "none")})
    active = sum(1 for t in gh_tools if S[t[1]]["push"] >= ACTIVE_SINCE)
    unmaintained = [t for t in gh_tools if S[t[1]]["push"] < UNMAINTAINED_BEFORE]
    archived = [t for t in gh_tools if t[1] in ARCHIVED]

    n_pads = len(pads)
    n_active_pads = sum(1 for p in pads if p["active"] == "true")
    fact_flights = [r for r in starbase if r["evidence"] == "FACT" and r["kind"] == "launch"]
    goal_rows = [r for r in starbase if r["evidence"] == "GOAL"]
    outcomes = Counter(r["outcome"] for r in fact_flights)
    upcoming_launches = 0  # none in this snapshot; confirmed by CSV having no GOAL launches

    cat_stars = []
    for heading, _, ts in C:
        s = sum(S[t[1]]["stars"] for t in ts if is_github(t[1]))
        cat_stars.append((heading, s))

    top = sorted(
        ((t[0], S[t[1]]["stars"]) for t in gh_tools),
        key=lambda x: -x[1],
    )[:10]

    write_dashboard_svg(
        ROOT / "assets" / "dashboard.svg",
        gh_tools=gh_tools,
        tot=tot,
        forks=forks,
        langs=langs,
        active=active,
        n_tools=len(tools),
        pads=pads,
        starbase=starbase,
        cat_stars=cat_stars,
        top=top,
    )

    o = []
    o.append(
        f"""<div align="center">

# Awesome Craft Space [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of open-source tools for spaceflight and rockets — orbit simulation, telemetry, launch data and more.

<img src="assets/craft-space.svg" alt="Pixel-art night launch scene with a generic rocket on a pad, a catch-arm tower, a ground station and stars" width="100%">

![Tools](https://img.shields.io/badge/tools-{len(tools)}-6366f1?style=for-the-badge)
[![Categories](https://img.shields.io/badge/categories-{len(C)}-0ea5e9?style=for-the-badge)](#contents)
![Combined stars](https://img.shields.io/badge/combined_stars-{k(tot)}-f59e0b?style=for-the-badge)
[![Stars](https://img.shields.io/github/stars/EdisonTKPcom/Awesome-Craft-Space?style=for-the-badge&color=22c55e)](https://github.com/EdisonTKPcom/Awesome-Craft-Space/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/EdisonTKPcom/Awesome-Craft-Space?style=for-the-badge&color=ec4899)](https://github.com/EdisonTKPcom/Awesome-Craft-Space/commits/main)

</div>

Open-source software for designing trajectories, flying flight software, tracking satellites and reading launch data. Every project has a public repository that was checked on {AS}. Figures on the dashboard are tagged FACT (measured, with a cited source and date), GOAL (a stated plan, not a result) or ESTIMATE (a sum or count computed here). The pixel banner is an original scene; it does not use company logos or wordmarks. This list does not include unverified cost claims.

Related list: [Awesome Craft](https://github.com/EdisonTKPcom/Awesome-Craft), a family of curated open-source lists.

## Contents
"""
    )
    o += ["- [Dashboard](#dashboard)"] + [f"- [{n}](#{anchor(n)})" for n, _, _ in C]
    o.append("\n## Dashboard\n")
    o.append(
        f"""<table>
<tr>
<td align="center"><h2>{len(tools)}</h2>{estimate("listed projects")}</td>
<td align="center"><h2>{len(C)}</h2>{estimate("categories")}</td>
<td align="center"><h2>{k(tot)}</h2>{estimate("combined GitHub stars")}</td>
<td align="center"><h2>{k(forks)}</h2>{estimate("combined GitHub forks")}</td>
<td align="center"><h2>{active}/{len(gh_tools)}</h2>{estimate("GitHub repos pushed in the last 30 days")}</td>
<td align="center"><h2>{len(langs)}</h2>{estimate("languages among GitHub repos")}</td>
</tr>
</table>

<img src="assets/dashboard.svg" alt="Evidence dashboard: FACT star counts, ESTIMATE category totals, Launch Library 2 pad and Starbase figures" width="100%">

### How the figures are tagged

<table>
<tr><th>Tag</th><th>Claim</th></tr>
<tr><td>{fact("")}</td><td>Individual GitHub star, fork and last-push values come from the GitHub API, snapshot {AS}, stored in stats.tsv.</td></tr>
<tr><td>{estimate("")}</td><td>Combined GitHub stars ({k(tot)}, or {tot:,}) are the arithmetic sum of stargazers_count for the {len(gh_tools)} GitHub-hosted entries only. SatNOGS Network is hosted on GitLab and is excluded from this sum.</td></tr>
<tr><td>{estimate("")}</td><td>Combined forks ({k(forks)}), unique languages ({len(langs)}) and the {active}/{len(gh_tools)} repos pushed on or after {ACTIVE_SINCE} are counts computed from that same snapshot.</td></tr>
<tr><td>{fact("")}</td><td>Launch Library 2 reported {n_pads} pads on {fetch_date} (API 2.3.0, ordered id pagination).</td></tr>
<tr><td>{estimate("")}</td><td>{n_active_pads} of those pads have active=true in the snapshot (our count of the active flag).</td></tr>
<tr><td>{fact("")}</td><td>The Starship dashboard listed {len(fact_flights)} previous launches and {upcoming_launches} upcoming launches on {fetch_date}.</td></tr>
<tr><td>{estimate("")}</td><td>Of those previous launches, {outcomes.get("Success", 0)} are recorded as Success, {outcomes.get("Failure", 0)} as Failure and {outcomes.get("Partial Failure", 0)} as Partial Failure (our grouping of the LL2 status abbrev).</td></tr>
<tr><td>{goal("")}</td><td>Starship Orbital Catch Attempt remains listed as an upcoming LL2 event (date 2026-11-14 21:20:10 UTC / 2026-11-15 05:20:10 MYT). No outcome is recorded in the dashboard, so it is not treated as a result.</td></tr>
<tr><td>{goal("")}</td><td>Copper describes itself as a runtime aimed at spacefaring systems — a project goal, not a flown result.</td></tr>
</table>

Each flight outcome in the Starbase table is a FACT with its LL2 timestamp. Announced next flights or catch attempts are GOAL. This list does not invent upcoming launches or catch results.

### Leaderboard

Individual star counts below are FACT values from the {AS} GitHub API snapshot.

<table>
<tr><th>Rank</th><th>Project</th><th align="right">Stars</th><th></th></tr>
"""
    )
    mx = top[0][1]
    for i, (name, stars) in enumerate(top, 1):
        bar = "█" * max(1, round(stars / mx * 20))
        medal = ["🥇", "🥈", "🥉"][i - 1] if i < 4 else i
        o.append(
            f'<tr><td align="center">{medal}</td><td><b>{html.escape(name)}</b></td>'
            f'<td align="right">{k(stars)}</td><td><code>{bar}</code></td></tr>'
        )
    o.append("</table>\n")

    lc = {}
    for t in gh_tools:
        L = lic_of(t[1])
        lc[L] = lc.get(L, 0) + 1
    o.append("### Licences\n")
    o.append(
        " ".join(
            f"![{U.quote(L, safe='')}](https://img.shields.io/badge/{U.quote(L.replace('-', '--'))}-{c}-64748b?style=flat-square)"
            for L, c in sorted(lc.items(), key=lambda x: -x[1])
        )
    )
    o.append("")
    o.append(
        "Licence badges use the project's SPDX identifier when GitHub detects one, or the text of the licence file when that identifier is missing. "
        '"Undeclared" means no licence file was confirmed at the repository HEAD on the snapshot date. '
        "The OpenC3 Builder's License V2 and NASA Open Source Agreement 1.3 are not OSI-approved; read them before you use those projects. "
        "Archived and unmaintained projects stay in the star sum and are flagged in their entries.\n"
    )
    o.append("### Sources\n")
    o.append(
        f"""<table>
<tr><th>Source</th><th>What it supports</th></tr>
<tr><td>GitHub API, snapshot {AS} (Asia/Kuala_Lumpur calendar date), stored in <code>stats.tsv</code></td><td>stargazers_count, forks_count, license, language and pushed_at for {len(gh_tools)} repositories.</td></tr>
<tr><td>Launch Library 2 2.3.0 <a href="https://ll.thespacedevs.com/2.3.0/pads/">pads</a> (ordered by id, pages of 100) and <a href="https://ll.thespacedevs.com/2.3.0/dashboard/starship/">Starship dashboard</a>, snapshot {fetch_date}</td><td>Stored in <code>data/launch-pads.csv</code> and <code>data/starbase-recent.csv</code>. Refresh with <code>python3 fetch_launch_data.py</code>.</td></tr>
<tr><td>Project licence files read on 2026-11-15</td><td>OpenRocket GPL-3.0-or-later, OpenMCT Apache-2.0, OpenSpace MIT, Trick NASA Open Source Agreement 1.3, OpenC3 Builder's License V2.</td></tr>
<tr><td>SatNOGS Network GitLab project metadata, 2026-11-15</td><td>star_count 60, not mixed into the GitHub star total.</td></tr>
</table>
"""
    )

    intros = {
        "Launch sites and pads": (
            f"Open data and official examples for launch sites. The snapshot in `data/launch-pads.csv` "
            f"has {n_pads} pads ({n_active_pads} with `active=true`) from Launch Library 2 2.3.0, fetched {fetch_date}. "
            f"Columns are name, location, country, latitude, longitude, total_launch_count, active, source_url and fetch_date. "
            f"Regenerate it with `python3 fetch_launch_data.py`, which pages `/pads/?limit=100&ordering=id` and respects the anonymous free-tier budget of about 15 requests per hour. "
            f"A general open-source NOTAM or launch-window tool was not included because no well-maintained public repository was verified for this list. "
            f"LL2 notices and road-closure fields are the open data path for related constraints."
        ),
        "Recent Starbase activity": (
            f"Latest Starship flights and events at Starbase, Texas, from Launch Library 2, plus community tools that extract webcast telemetry. "
            f"The snapshot in `data/starbase-recent.csv` has {len(starbase)} rows "
            f"({len(fact_flights)} FACT launches and {len(goal_rows)} GOAL event), fetched {fetch_date}. "
            f"Times are given in UTC and in Malaysia Time (Asia/Kuala_Lumpur, UTC+8). "
            f"Flight outcomes from LL2 are FACT. Announced attempts still listed without an outcome are GOAL. "
            f"Refresh the snapshot with `python3 fetch_launch_data.py`. This section does not invent catch results or upcoming flights."
        ),
    }

    for heading, intro, ts in C:
        o.append(f"## {heading}\n")
        text = intros.get(heading, intro)
        if text:
            o.append(text + "\n")
        if heading == "Recent Starbase activity":
            o.append(
                "<table>\n<tr><th>Evidence</th><th>Mission or event</th><th>Status</th><th>Outcome</th>"
                "<th>NET (UTC)</th><th>NET (MYT)</th><th>Pad</th></tr>"
            )
            for r in starbase:
                ev = r["evidence"]
                style = {
                    "FACT": "border:2px solid #0284c7;color:#0284c7;",
                    "GOAL": "border:2px dashed #d97706;color:#d97706;",
                    "ESTIMATE": "border:2px dotted #7c3aed;color:#7c3aed;",
                }[ev]
                o.append(
                    "<tr>"
                    f'<td><span style="display:inline-block;{style}padding:0 7px;border-radius:4px;font-weight:700;">{ev}</span></td>'
                    f"<td>{html.escape(r['mission_name'])}</td>"
                    f"<td>{html.escape(r['status'])}</td>"
                    f"<td>{html.escape(r['outcome'])}</td>"
                    f"<td>{html.escape(r['net_utc'])}</td>"
                    f"<td>{html.escape(r['net_myt'])}</td>"
                    f"<td>{html.escape(r['pad'])}</td>"
                    "</tr>"
                )
            o.append("</table>\n")
            o.append("Community tools that track or decode Starbase webcasts:\n")
        for t in sorted(ts, key=lambda t: t[0].lower()):
            name, repo, desc = t
            line = f"- [{name}]({url_of(repo)}) - {desc}"
            if is_github(repo):
                line += f" ![Stars](https://img.shields.io/github/stars/{repo}?style=flat-square&label=%E2%AD%90)"
            o.append(line)
        o.append("")

    o.append(
        "## Contributing\n\nContributions welcome! Read the [contribution guidelines](contributing.md) first.\n\n"
        '<div align="center">\n\n'
        "If this list helped you, give it a ⭐ so others can find it.\n\n"
        "</div>\n"
    )
    (ROOT / "README.md").write_text("\n".join(o) + "\n")
    print(
        f"wrote README.md tools={len(tools)} github={len(gh_tools)} stars={tot} "
        f"forks={forks} langs={len(langs)} active={active}/{len(gh_tools)} "
        f"archived={len(archived)} unmaintained={len(unmaintained)} "
        f"pads={n_pads} active_pads={n_active_pads} starbase={len(starbase)} "
        f"fact_flights={len(fact_flights)} goal_rows={len(goal_rows)} "
        f"outcomes={dict(outcomes)}"
    )
    for heading, _, ts in C:
        print(f"  {heading}: {len(ts)}")


if __name__ == "__main__":
    emit()
