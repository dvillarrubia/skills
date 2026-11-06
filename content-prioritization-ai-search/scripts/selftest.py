#!/usr/bin/env python3
"""Acceptance tests for the v1.4 decision rules. Fails unless every assertion holds.
Run from the skill folder after any edit: python scripts/selftest.py
These check the script's calculations and draft actions, not how Claude behaves inside an app."""
import csv, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILS = []

def check(cond, msg):
    if not cond: FAILS.append(msg)

def run(path, settings, tmp, name):
    out = Path(tmp) / name
    cmd = [sys.executable, str(ROOT / "scripts/evaluate.py"), str(path), "--out-dir", str(out), "--setting", "as_of=2026-10-25"]
    for s in settings: cmd += ["--setting", s]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        FAILS.append(f"{name}: script failed: {p.stderr.strip()[-300:]}"); return None, ""
    raw = (out / "results.json").read_text(encoding="utf-8")
    return json.loads(raw), raw + p.stdout

def row(res, page):
    for x in res["rows"]:
        if x["page"] == page: return x
    FAILS.append(f"row not found: {page}"); return None

def text(x): return " ".join([x["primary_action"], *x["secondary_actions"]])

def no_ready(blob, name):
    check(not re.search(r"\bready\b", blob, re.I), f"{name}: output contains the word 'Ready'")

with tempfile.TemporaryDirectory() as tmp:
    ex = ROOT / "examples"
    # ---- ecommerce
    r, blob = run(ex / "test-ecommerce.csv", ["site_model=ecommerce", "same_period_last_year=Y"], tmp, "ecom")
    if r:
        no_ready(blob, "ecommerce")
        x = row(r, "How to choose a sleeping bag")
        if x:
            check(x["scores"]["BV"] == {"level": "L", "basis": "Framework default"}, "sleeping bag: BV must stay L / Framework default")
            check(x["primary_action"].startswith("Rework to keep"), f"sleeping bag: primary '{x['primary_action']}'")
            check("Evidence-led comparisons" in x["primary_action"] and "First-hand tests" in x["primary_action"], "sleeping bag: menu must list Evidence-led comparisons and First-hand tests")
            check(x["review"] and x["review"]["status"] == "Review required", "sleeping bag: status must be Review required")
        x = row(r, "Celebrity hiking outfits")
        if x:
            check(not x["primary_action"].startswith("Retire"), "celebrity: primary must not start with Retire")
            check(x["review"] and x["review"]["status"] == "Review required", "celebrity: status must be Review required")
        x = row(r, "Product FAQ pages")
        if x:
            check(x["primary_action"].startswith("Review the template"), f"product FAQ: primary '{x['primary_action']}'")
            check(x["review"]["status"] != "Candidate for owner review", "product FAQ: must not be a candidate")
        x = row(r, "'Is [tent] waterproof?' FAQ pages")
        if x:
            check(x["primary_action"].startswith("Don't create as briefed"), "planned FAQ: must start with Don't create as briefed")
            check("Transaction" in x["primary_action"] and "Official docs" in x["primary_action"], "planned FAQ: must mention Transaction and Official docs")
        x = row(r, "Best tents 2026")
        if x:
            check(x["primary_action"].startswith("Rework") and "Evidence-led comparisons" in x["primary_action"], f"best tents: primary '{x['primary_action']}'")
        x = row(r, "Outdoor glossary")
        if x: check(x["primary_action"].startswith("Review the template"), f"glossary: primary '{x['primary_action']}'")
    # ---- publisher
    r, blob = run(ex / "test-publisher.csv", ["site_model=publisher", "same_period_last_year=Y"], tmp, "pub")
    if r:
        no_ready(blob, "publisher")
        x = row(r, "'What is' explainers")
        if x:
            check(not x["primary_action"].startswith("Consolidate"), "explainers: primary must not start with Consolidate")
            check(x["primary_action"].startswith("Review the template"), f"explainers: primary '{x['primary_action']}'")
            check(any("editorial remit" in m for m in x["review"]["missing"]), "explainers: gate must mention the editorial remit")
        x = row(r, "Newsletter signup")
        if x: check(x["scores"]["BV"] == {"level": "H", "basis": "Framework default"}, "newsletter: BV must stay H / Framework default")
        x = row(r, "Hiking calorie calculator")
        if x: check(x["primary_action"].startswith("Review against the editorial remit"), f"calculator: primary '{x['primary_action']}'")
    # ---- regulated
    r, blob = run(ex / "test-regulated.csv", ["site_model=regulated", "same_period_last_year=N"], tmp, "reg")
    if r:
        no_ready(blob, "regulated")
        x = row(r, "Mortgage calculator")
        if x:
            check(x["primary_action"].startswith("Rework to keep") and "Personalized tools" in x["primary_action"] and "Retire" not in x["primary_action"], f"mortgage: primary '{x['primary_action']}'")
        x = row(r, "ATM locator pages")
        if x:
            check(x["primary_action"].startswith("Review the template"), f"ATM: primary '{x['primary_action']}'")
            check(x["review"]["status"] != "Candidate for owner review", "ATM: must not be a candidate")
        x = row(r, "Key facts and fee disclosures")
        if x: check(x["primary_action"].startswith("Keep (required role)"), f"fees: primary '{x['primary_action']}'")
        x = row(r, "Complaints procedure")
        if x: check(x["primary_action"].startswith("Keep") and not x.get("review"), f"complaints: primary '{x['primary_action']}', review {x.get('review')}")
    # ---- Search Console export
    r, blob = run(ex / "search-console-export.csv", [], tmp, "gsc")
    if r:
        no_ready(blob, "gsc")
        x = next((y for y in r["rows"] if "what-is-a-tarp" in str(y["url"])), None)
        check(x is not None and x["primary_action"].startswith("Classify"), "tarp: primary must start with Classify")
        check(x is not None and any("Impressions held" in a for a in x["secondary_actions"]), "tarp: a secondary action must say impressions held")
        check(x is not None and all(s["level"] == "U" for s in x["scores"].values()), "unclassified row must have U scores")
    # ---- synthetic
    hdr = ["page", "url", "content_type", "classification", "status", "pages", "clicks", "clicks_previous", "conversions", "revenue",
           "tracking_verified", "referring_domains", "required", "value_reviewed", "same_intent_confirmed", "consolidate_into"]
    base = {"page": "Celebrity boots gallery", "url": "https://example.com/blog/celebrity-boots", "content_type": "D5", "classification": "Confirmed",
            "status": "Live", "pages": "1", "clicks": "10", "clicks_previous": "20", "conversions": "0", "revenue": "0", "tracking_verified": "Y",
            "referring_domains": "0", "required": "N", "value_reviewed": "Y", "same_intent_confirmed": "", "consolidate_into": ""}
    cases = {
        "cand": [base],
        "traffic": [dict(base, clicks="8000")],
        "home": [dict(base, page="Glossary term", url="https://example.com/glossary/tarp", content_type="D1", consolidate_into="https://example.com/", same_intent_confirmed="Y")],
        "nointent": [dict(base, page="Glossary term", url="https://example.com/glossary/tarp", content_type="D1", consolidate_into="https://example.com/learn/tarps")],
        "planned": [dict(base, status="Planned", clicks="", clicks_previous="", conversions="", revenue=""), dict(base, page="Brief 2", status="Planned", content_type="P4", clicks="", clicks_previous="", conversions="", revenue="")],
        "noclicks": [dict(base, clicks="", clicks_previous="", pages="3", url="/x/*")],
    }
    res = {}
    for name, rows in cases.items():
        p = Path(tmp) / f"{name}.csv"
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(rows)
        res[name], blob = run(p, ["site_model=ecommerce"], tmp, name)
        if res[name]: no_ready(blob, name)
    if res["cand"]:
        x = res["cand"]["rows"][0]
        check(x["review"] and x["review"]["status"] == "Candidate for owner review", f"synthetic D5: status {x['review'] and x['review']['status']}, missing {x['review'] and x['review']['missing']}")
        check(x["scores"]["CR"] == {"level": "L", "basis": "Framework default"}, "synthetic D5: CR must stay L / Framework default")
    if res["traffic"]:
        x = res["traffic"]["rows"][0]
        check(x["review"]["status"] == "Review required", "8,000 clicks: must be Review required")
        check("material traffic" in x["primary_action"] and not x["primary_action"].startswith("Retire"), f"8,000 clicks: primary '{x['primary_action']}'")
    if res["home"]:
        x = res["home"]["rows"][0]
        check(x["review"]["status"] == "Review required" and any("homepage" in m for m in x["review"]["missing"]), "homepage destination must be Review required")
    if res["nointent"]:
        x = res["nointent"]["rows"][0]
        check(x["review"]["status"] == "Review required" and any("same_intent_confirmed" in m for m in x["review"]["missing"]), "destination without same_intent_confirmed must be Review required")
    check(res["planned"] is not None, "planned inventory without clicks must run")
    check(res["noclicks"] is not None, "live rows without clicks must run")
    # ---- v1.4: likely directions, value context, relative material traffic, evaluator-aligned priority
    r, blob = run(ex / "test-ecommerce.csv", ["site_model=ecommerce", "same_period_last_year=Y"], tmp, "ecom14")
    if r:
        x = row(r, "Outdoor glossary")
        if x:
            p = x["primary_action"]
            check("Likely direction: consolidate into the relevant product, service or topic hubs" in p, f"glossary: likely direction missing: '{p}'")
            check("Check the URLs that still have traffic, links or conversions first" in p, "glossary: must say to check the URLs with traffic, links or conversions first")
            check(x["review"]["status"] == "Review required", "glossary: must stay Review required")
            check(any("doesn't freeze the rest of the template" in a for a in x["secondary_actions"]), "glossary: 4 conversions must not freeze the other URLs")
        x = row(r, "How to choose a sleeping bag")
        if x: check("85 conversions" in x["primary_action"] and "of all conversions" in x["primary_action"], "sleeping bag: value must be shown in context")
        x = row(r, "Fit finder")
        if x: check(x["sort"] == "High", f"fit finder (P10 defaults): evaluator rule gives High, got {x['sort']}")
        x = row(r, "Trekking pole X2 care guide")
        if x: check(x["primary_action"] == "Maintain and measure", "care guide: should be Maintain and measure")
        check(r["settings"]["material_clicks"] > 100, "material traffic must be relative to the supplied rows (above the 100-click floor here)")
    r, blob = run(ex / "test-regulated.csv", ["site_model=regulated", "same_period_last_year=N"], tmp, "reg14")
    if r:
        x = row(r, "Scam and fraud alerts")
        if x: check(x["sort"] == "Medium", f"P5 defaults: evaluator rule gives Medium, got {x['sort']}")
    # relative material traffic: a 600-click page among 200,000 clicks is not material; the same page alone is
    big = [dict(base, page="Big page", url="https://example.com/big", content_type="P2", clicks="200000", clicks_previous="190000", required="", value_reviewed=""),
           dict(base, page="Small D5", url="https://example.com/small-d5", clicks="600", clicks_previous="650")]
    p = Path(tmp) / "relative.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(big)
    rr, blob = run(p, ["site_model=ecommerce"], tmp, "relative")
    if rr:
        no_ready(blob, "relative")
        x = row(rr, "Small D5")
        if x:
            check("material traffic" not in x["primary_action"], "600 clicks among 200,000 should not count as material traffic")
            check(x["review"]["status"] == "Candidate for owner review", f"small D5 among large site: expected candidate, got {x['review']['status']} {x['review']['missing']}")
    # inferred removal rows lead with verification, not a removal
    inf = [dict(base, classification="Inferred")]
    p = Path(tmp) / "inferred.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(inf)
    ri, blob = run(p, ["site_model=ecommerce"], tmp, "inferred")
    if ri:
        x = ri["rows"][0]
        check(x["primary_action"].startswith("Verify the type"), f"inferred D5: primary '{x['primary_action']}'")
        check(x["review"]["status"] == "Review required", "inferred D5: Review required")
    # ---- findings JSON content
    if res["cand"]:
        P = res["cand"]["portfolio"]
        check("not a framework rule" in P["sort_note"], "sort note must say 'not a framework rule'")
        check("doesn't replace it" in P["notice"], "findings must include the expert-review notice")

if FAILS:
    print(f"{len(FAILS)} check(s) failed:"); [print(" - " + f) for f in FAILS]; sys.exit(1)
print("All acceptance checks passed")
