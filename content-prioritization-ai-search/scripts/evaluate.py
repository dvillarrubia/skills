#!/usr/bin/env python3
"""Content Prioritization in an AI Search Era (Aleyda Solis): calculation helper, v1.4 (October 2026).

Applies the skill's documented settings to an inventory or a Search Console export:
type defaults, sort score, click maths, flags, draft actions, the review gate and
portfolio findings. It never derives a score from a metric, never fetches pages and
never changes a site. Its actions are drafts for an expert to review.

Usage: python scripts/evaluate.py INPUT.(xlsx|csv|json) --out-dir DIR [--setting key=value ...]
"""
import argparse, csv, json, math, re, sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

VERSION = "1.4"
ROOT = Path(__file__).resolve().parent.parent
TYPES = json.loads((ROOT / "data" / "content-types.json").read_text(encoding="utf-8"))
BYID = {t["id"]: t for t in TYPES}
DIMS = ["CR", "CP", "BM", "BV", "PA", "EF"]
LV = {"L": 1, "M": 2, "H": 3}
ROLE_FIRST_PARTY = {"P1", "P2", "P3"}
CURRENT_FACTS = {"P1", "P2", "P3", "P6", "P13"}
PUBLISHER_MODELS = {"publisher", "media", "affiliate", "reference"}
NOTICE = ("This output supports an expert assessment; it doesn't replace it. Check classifications, scores "
          "and recommendations against your knowledge of the site, audience and data before acting.")
SORT_NOTE = ("Priority and the sort score are skill settings, not a framework rule. Priority follows the companion evaluator's rule: "
             "High when business value and proprietary advantage are High and click resilience or citation potential is High; "
             "Medium when business value is at least Medium and the sort score is 2.0 or above; Low otherwise. The sort score is the mean "
             "of click resilience, citation potential, brand mention, business value and proprietary advantage (Low=1, Medium=2, High=3); "
             "effort is shown beside it, not inside it. Results built mostly from defaults are provisional, and none of this predicts "
             "rankings, citations or traffic. The 100-click floor, the material-traffic share, the -35% click flag and the 6- and "
             "12-month freshness windows are skill settings too.")

def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s or "").strip().lower()).strip("_")

ALIASES = {
    "page": ["page", "page_name", "name", "title", "page_group", "asset"],
    "url": ["url", "address", "link", "path", "url_pattern", "top_pages", "page_url", "landing_page"],
    "content_type": ["content_type", "type", "format", "content_format", "page_type", "template", "type_id"],
    "classification": ["classification", "classification_status"],
    "status": ["status", "state", "stage"],
    "pages": ["pages", "url_count", "urls", "count", "page_count"],
    "topic": ["topic", "category", "product_line", "cluster", "section"],
    "clicks": ["clicks", "organic_clicks", "gsc_clicks", "clicks_current", "gsc_clicks_current", "current_clicks"],
    "clicks_previous": ["clicks_previous", "previous_clicks", "prior_clicks", "gsc_clicks_previous", "clicks_prev"],
    "clicks_change_pct": ["clicks_change_pct", "click_change", "clicks_change", "yoy", "clicks_yoy", "change_pct", "reported_click_change"],
    "impressions": ["impressions", "impressions_current", "current_impressions"],
    "impressions_previous": ["impressions_previous", "previous_impressions", "prior_impressions"],
    "impressions_change_pct": ["impressions_change_pct", "impr_change", "impressions_change"],
    "sessions": ["sessions", "analytics_sessions", "organic_sessions"],
    "conversions": ["conversions", "conv", "leads", "transactions", "goal_completions"],
    "revenue": ["revenue"],
    "currency": ["currency"],
    "tracking_verified": ["tracking_verified", "tracking_status", "tracking"],
    "ai_cited_groups": ["ai_cited_groups", "ai_citations", "cited_prompt_groups", "prompt_groups", "citation_count"],
    "ai_tracked_groups": ["ai_tracked_groups", "tracked_prompt_groups", "tracked_groups"],
    "ai_scope": ["ai_scope", "ai_platforms", "ai_platform", "platforms"],
    "ai_cited": ["ai_cited", "cited_by_ai", "cited"],
    "gsc_ai_impressions": ["gsc_ai_impressions", "ai_impressions"],
    "first_party_data": ["first_party_data", "distinctive_value", "first_party", "proprietary_data", "own_data", "unique_data"],
    "last_verified": ["last_verified", "last_updated", "updated", "last_modified", "modified", "date_updated"],
    "referring_domains": ["referring_domains", "backlinks", "ref_domains", "rd"],
    "required": ["required", "required_role"],
    "value_reviewed": ["value_reviewed"],
    "same_intent_confirmed": ["same_intent_confirmed", "same_intent"],
    "verified_issue": ["verified_issue", "issue"],
    "consolidate_into": ["consolidate_into", "canonical", "merge_into", "redirect_to", "target_url"],
    "owner": ["owner", "team", "department"],
    "notes": ["notes", "note", "comments"],
    "score_notes": ["score_notes", "assessment_notes", "rationale"],
    **{d.lower(): [d.lower()] for d in DIMS},
}
for k, v in {"click_resilience": "cr", "citation_potential": "cp", "brand_mention": "bm", "brand_mention_potential": "bm",
             "business_value": "bv", "proprietary_advantage": "pa", "effort": "ef", "expected_effort": "ef"}.items():
    ALIASES[v].append(k)

def map_headers(headers):
    """Exact aliases first, then Search Console period wording ('Last 3 months Clicks', 'Previous 3 months Clicks')."""
    mapping, used = {}, set()
    nh = [norm(h) for h in headers]
    for i, h in enumerate(nh):
        for field, al in ALIASES.items():
            if h in al and field not in used:
                mapping[i] = field; used.add(field); break
    for i, h in enumerate(nh):
        if i in mapping: continue
        for metric in ("clicks", "impressions"):
            if metric in h and "ctr" not in h:
                prev = any(w in h for w in ("previous", "prior", "compare", "before", "last_year"))
                field = metric + ("_previous" if prev else "")
                if field not in used:
                    mapping[i] = field; used.add(field)
                break
    return mapping

def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())

def num(v):
    if blank(v) or isinstance(v, bool): return None
    if isinstance(v, (int, float)): return float(v) if math.isfinite(v) else None
    s = str(v).strip().replace(",", "").replace("€", "").replace("$", "").replace("£", "")
    try: return float(s)
    except ValueError: return None

def pct(v, unit, excel_pct=False):
    """Return a fraction (-0.22 for -22%). Values with % and Excel percentage cells are explicit."""
    if blank(v): return None
    if isinstance(v, str) and v.strip().endswith("%"):
        n = num(v.strip()[:-1]); return None if n is None else n / 100
    n = num(v)
    if n is None: return None
    return n if (excel_pct or unit == "fraction") else n / 100

def yn(v):
    if blank(v): return None
    s = str(v).strip().lower()
    if s in ("y", "yes", "true", "1", "verified"): return True
    if s in ("n", "no", "false", "0", "unverified", "unusable"): return False
    return None

def to_date(v):
    if blank(v): return None
    if isinstance(v, datetime): return v.date()
    if isinstance(v, date): return v
    if isinstance(v, (int, float)) and 20000 < v < 80000:
        return date.fromordinal(date(1899, 12, 30).toordinal() + int(v))
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try: return datetime.strptime(str(v).strip()[:10], fmt).date()
        except ValueError: pass
    return None

def resolve_type(v):
    if blank(v): return None
    s = str(v).strip()
    m = re.match(r"^\s*([PpDd])\s*-?\s*(\d{1,2})\s*$", s)
    if m:
        tid = m.group(1).upper() + str(int(m.group(2)))
        return tid if tid in BYID else None
    if s.upper() == "X": return "X"
    n = norm(s)
    for t in TYPES:
        if n in (norm(t["name"]), norm(t["short_name"]), norm(t["id"])): return t["id"]
    for t in TYPES:
        if norm(t["short_name"]) in n: return t["id"]
    if n in ("hub", "index", "router", "other"): return "X"
    return None

def parse_score(v):
    """'H', 'M page', 'L measured', 'H set' -> (level, basis). A level alone is User set."""
    if blank(v): return None
    s = str(v).strip()
    lvl = s[0].upper()
    if lvl not in "HMLU": return None
    rest = s[1:].lower()
    return lvl, ("Page assessment" if "page" in rest else "Measured" if "measur" in rest else "User set")

def is_group(pages, url):
    return pages > 1 or "*" in str(url or "") or "[" in str(url or "")

def is_homepage(url):
    if blank(url): return False
    s = str(url).strip()
    p = urlsplit(s if "://" in s else "https://x" + (s if s.startswith("/") else "/" + s))
    return p.path in ("", "/") and not p.query

def menu(tid):
    opts = BYID[tid].get("rework_options", []) if tid in BYID else []
    return "; ".join(opts) if opts else "no rework option for this type"

# ---------------- reading ----------------
def read_rows(path):
    p = Path(path)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        recs = data.get("records", []) if isinstance(data, dict) else data
        headers = list(dict.fromkeys(k for r in recs for k in r))
        return headers, [[r.get(h) for h in headers] for r in recs], [{} for _ in recs], (data.get("settings", {}) if isinstance(data, dict) else {})
    if p.suffix.lower() == ".csv":
        with open(p, newline="", encoding="utf-8-sig") as f:
            rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
        if not rows: sys.exit("The CSV is empty.")
        return rows[0], rows[1:], [{} for _ in rows[1:]], {}
    if p.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("Reading .xlsx needs openpyxl (pip install openpyxl), or save the sheet as CSV.")
        wb = openpyxl.load_workbook(p, data_only=True)
        name = next((n for n in wb.sheetnames if norm(n) in ("inventory", "pages", "content_inventory")), wb.sheetnames[0])
        grid = list(wb[name].iter_rows())
        if not grid: sys.exit("The sheet is empty.")
        headers = [c.value for c in grid[0]]
        body, fmts = [], []
        for r in grid[1:]:
            vals = [c.value for c in r]
            if all(blank(v) for v in vals): continue
            body.append(vals); fmts.append({i: ("%" in (c.number_format or "")) for i, c in enumerate(r)})
        settings = {}
        sname = next((n for n in wb.sheetnames if norm(n) == "settings"), None)
        if sname:
            for r in wb[sname].iter_rows(min_row=2, values_only=True):
                if r and not blank(r[0]) and len(r) > 1 and not blank(r[1]): settings[str(r[0]).strip()] = r[1]
        return headers, body, fmts, settings
    sys.exit("Use an .xlsx, .csv or .json file.")

DEFAULT_SETTINGS = {"change_unit": "points", "min_comparison_clicks": 100, "decline_threshold": -35, "material_share": 0.5,
                    "review_months": 12, "review_months_current_facts": 6, "inventory_complete": "N",
                    "same_period_last_year": "", "site_model": "", "objective": "", "as_of": "", "not_relevant": ""}

def settings_from(raw, overrides):
    s = dict(DEFAULT_SETTINGS)
    for k, v in {**(raw or {}), **overrides}.items(): s[norm(k)] = v
    s["min_comparison_clicks"] = num(s["min_comparison_clicks"]) or 100
    thr = num(str(s["decline_threshold"]).replace("%", ""))
    s["decline_threshold"] = (thr / 100 if thr is not None and abs(thr) >= 1 else thr) if thr is not None and thr < 0 else -0.35
    s["review_months"] = num(s["review_months"]) or 12
    s["review_months_current_facts"] = num(s["review_months_current_facts"]) or 6
    s["as_of"] = to_date(s.get("as_of")) or date.today()
    s["change_unit"] = "fraction" if str(s["change_unit"]).lower().startswith("frac") else "points"
    s["publisher"] = norm(s.get("site_model")) in PUBLISHER_MODELS
    ms = num(str(s.get("material_share")).replace("%", ""))  # a percentage: 0.5 means 0.5% of the supplied rows' clicks
    s["material_share"] = ms / 100 if ms is not None and ms >= 0 else 0.005
    return s

# ---------------- rows ----------------
def evaluate(path, overrides):
    headers, body, fmts, raw_settings = read_rows(path)
    S = settings_from(raw_settings, overrides)
    mapping = map_headers(headers)
    rows = []
    for vals, fmt in zip(body, fmts):
        r = {"_raw": list(vals)}
        for i, f in mapping.items():
            if i < len(vals): r[f] = vals[i]
            if f.endswith("change_pct") and fmt.get(i): r["_excel_pct_" + f] = True
        if blank(r.get("page")) and blank(r.get("url")): continue
        rows.append(r)
    by_url = {str(r.get("url")).strip().lower(): r for r in rows if not blank(r.get("url"))}
    live_raw = [r for r in rows if not re.search(r"plan|idea|backlog|todo|brief|n/a|^na$|not relevant|excluded", str(r.get("status") or "live").strip().lower())]
    total_clicks = sum(max(num(r.get("clicks")) or 0, num(r.get("clicks_previous")) or 0) for r in live_raw)
    S["total_clicks"] = total_clicks
    S["material_clicks"] = max(S["min_comparison_clicks"], S["material_share"] * total_clicks)
    S["total_conversions"] = sum(num(r.get("conversions")) or 0 for r in live_raw)
    S["total_revenue"] = sum(num(r.get("revenue")) or 0 for r in live_raw)
    out = [evaluate_row(r, S, by_url) for r in rows]
    return S, headers, mapping, out, portfolio(out, S)

def evaluate_row(r, S, by_url):
    res = {"page": r.get("page") or r.get("url"), "url": r.get("url"), "notes": [], "issues": [], "_raw": r["_raw"]}
    st = str(r.get("status") or "Live").strip().lower()
    status = "N/A" if st in ("n/a", "na", "not relevant", "excluded") else ("Planned" if re.search(r"plan|idea|backlog|todo|brief", st) else "Live")
    tid = resolve_type(r.get("content_type"))
    cls = str(r.get("classification") or "").strip().title()
    if tid is None:
        cls = "Unclassified"
        if not blank(r.get("content_type")): res["issues"].append(f"Content type '{r.get('content_type')}' not recognized")
    elif cls not in ("Confirmed", "Inferred"):
        cls = "Supplied (not yet checked)"
    t = BYID.get(tid, {})
    group = t.get("group", "Prioritize" if tid == "X" else "")
    pages = num(r.get("pages")); pages = int(pages) if pages and pages >= 1 else 1
    res.update(status=status, type_id=tid, type=t.get("short_name", "Hub or other (X)" if tid == "X" else "Unclassified"),
               group=group, classification=cls, pages=pages, topic=r.get("topic"), owner=r.get("owner"))
    live = status == "Live"
    # ---- performance (reported, never turned into scores)
    cur, prev = num(r.get("clicks")), num(r.get("clicks_previous"))
    rep = pct(r.get("clicks_change_pct"), S["change_unit"], r.get("_excel_pct_clicks_change_pct"))
    change, prev_est = None, False
    if cur is not None and prev is not None:
        if prev > 0: change = (cur - prev) / prev
        else: res["issues"].append("Zero clicks in the earlier period: percentage change undefined")
        if rep is not None and change is not None and abs(rep - change) > 0.01:
            res["issues"].append("Reported click change conflicts with the counts; counts used")
    elif cur is not None and rep is not None and rep > -1:
        change, prev, prev_est = rep, cur / (1 + rep), True
    ic, ip = num(r.get("impressions")), num(r.get("impressions_previous"))
    ichg = (ic - ip) / ip if (ic is not None and ip) else pct(r.get("impressions_change_pct"), S["change_unit"], r.get("_excel_pct_impressions_change_pct"))
    conv, rev = num(r.get("conversions")), num(r.get("revenue"))
    tracking = yn(r.get("tracking_verified"))
    fp, required = yn(r.get("first_party_data")), yn(r.get("required"))
    value_reviewed, same_intent = yn(r.get("value_reviewed")), yn(r.get("same_intent_confirmed"))
    rd = num(r.get("referring_domains"))
    cited, tracked = num(r.get("ai_cited_groups")), num(r.get("ai_tracked_groups"))
    coverage = cited / tracked if (cited is not None and tracked and not blank(r.get("ai_scope"))) else None
    if cited is not None and coverage is None:
        res["notes"].append(f"AI citations reported ({cited:g} groups) without a tracked-groups denominator and scope: shown, not used as a rate")
    ai_flag = yn(r.get("ai_cited"))
    if ai_flag is not None and coverage is None:
        res["notes"].append(f"ai_cited = {'Y' if ai_flag else 'N'} reported as a flag only: no denominator or scope, so not a rate and not a score input")
    res.update(clicks=cur, clicks_previous=None if prev is None else round(prev), clicks_previous_estimated=prev_est,
               clicks_change=change, impressions_change=ichg, conversions=conv, revenue=rev, currency=r.get("currency"),
               tracking_verified=tracking, first_party_data=fp, required=required, value_reviewed=value_reviewed,
               same_intent_confirmed=same_intent, referring_domains=rd, ai_cited_groups=cited, ai_tracked_groups=tracked,
               ai_coverage=coverage, ai_scope=r.get("ai_scope"), gsc_ai_impressions=num(r.get("gsc_ai_impressions")),
               consolidate_into=r.get("consolidate_into"))
    if live and conv is not None and tracking is not True:
        res["notes"].append("Conversions reported but tracking not verified")
    # ---- scores: framework defaults, page assessments or user-set levels only
    scores = {}
    for d in DIMS:
        ps = parse_score(r.get(d.lower()))
        if ps: scores[d] = {"level": ps[0], "basis": ps[1]}
        elif t: scores[d] = {"level": t["defaults"][d], "basis": "Framework default"}
        else: scores[d] = {"level": "U", "basis": "Unknown"}
    if fp is not None:
        if tid in ROLE_FIRST_PARTY:
            res["notes"].append("first_party_data is a clue only; for brand, transaction and official pages judge completeness and currency instead")
        elif fp is False and t:
            res["notes"].append("first_party_data = N is a clue, not a score: confirm distinctive value on the page")
    res["scores"] = scores
    v5 = [LV.get(scores[d]["level"]) for d in DIMS[:5]]
    sort = None if None in v5 else sum(v5) / 5
    res["sort_score"] = None if sort is None else round(sort, 2)
    g = lambda d: scores[d]["level"]
    if status == "N/A": band = "Excluded"
    elif sort is None: band = "Unranked"
    elif g("BV") == "H" and g("PA") == "H" and (g("CR") == "H" or g("CP") == "H"): band = "High"
    elif LV[g("BV")] >= 2 and sort >= 2.0: band = "Medium"
    else: band = "Low"
    res["sort"] = band
    res["provisional"] = cls != "Confirmed" or sum(scores[d]["basis"] == "Framework default" for d in DIMS[:5]) >= 3 or sort is None
    # ---- flags
    low_volume = prev is not None and prev < S["min_comparison_clicks"]
    if low_volume and change is not None:
        res["notes"].append(f"Only {round(prev)} clicks in the earlier period: read the change with caution")
    decline = live and change is not None and change < S["decline_threshold"] and not low_volume
    diag = ""
    if decline and ichg is not None:
        diag = (" Impressions fell about as much: check rankings and demand first." if ichg < 0 and abs(ichg - change) <= 0.10
                else " Impressions held or fell much less: check SERP features, query mix and position.")
    invest = "Investigate click loss." + diag
    last = to_date(r.get("last_verified"))
    cycle = S["review_months_current_facts"] if tid in CURRENT_FACTS else S["review_months"]
    fresh_due = live and last is not None and (S["as_of"] - last).days > cycle * 30.44
    if live and last is None and tid in CURRENT_FACTS: res["notes"].append("No last-verified date for a current-facts page")
    material = any(x is not None and x >= S["material_clicks"] for x in (cur, prev))
    value_pos = tracking is True and ((conv or 0) > 0 or (rev or 0) > 0)
    issue = not blank(r.get("verified_issue"))
    grp = is_group(pages, r.get("url"))
    acts, review = [], None
    # ---- draft actions
    if status == "N/A":
        acts = ["Excluded from this assessment"]
    elif tid is None:
        acts = ["Classify: read the page and set its type"]
        if decline: acts.append(invest)
    elif group == "Deprioritize":
        opts = menu(tid)
        likely = t["likely_direction"]
        ctx = value_context(conv, rev, r.get("currency"), S)
        if status == "Planned":
            if required is True:
                acts.append("Don't create as briefed: this need carries a required role, so create the official or task page that carries the duty, not this format")
            else:
                acts.append(f"Don't create as briefed. Redesign it as: {opts}. Drop it only if that does not fit")
        else:
            review = gate(r, res, S, by_url, t, grp, material)
            if issue: acts.append("Correct verified issue")
            if required is True:
                acts.append("Keep: required role. Do not retire, prune, noindex, or merge this page away")
            elif grp:
                acts.append(f"Review the template before changing these URLs ({pages} URLs). Likely direction: {likely}. "
                            "Check the URLs that still have traffic, links or conversions first, and don't approve the group as a batch")
                if S["publisher"]: acts.append("Review against the editorial remit before changing this. Deprioritization defaults fit publishers, affiliates, and reference sites less well")
                if value_pos: acts.append(f"The group has measured value ({ctx}): keep or rework the URLs that earn it ({opts}). It doesn't freeze the rest of the template")
            elif S["publisher"]:
                acts.append("Review against the editorial remit before changing this. Deprioritization defaults fit publishers, affiliates, and reference sites less well")
                if value_pos: acts.append(f"It has verified value ({ctx}): rework it ({opts}) only if the page is truly generic")
            elif value_pos:
                acts.append(f"Rework to keep the measured value ({ctx}). Options: {opts}")
            elif material:
                acts.append(f"Review before changing: this page has material traffic ({int(max(cur or 0, prev or 0)):,} clicks in a period). Likely direction: {likely}; removal needs an explicit reason. Rework options: {opts}")
            elif cls != "Confirmed":
                acts.append(f"Verify the type by reading the page before deciding. If it is confirmed, the likely direction is: {likely}")
            elif review["status"] == "Candidate for owner review":
                acts.append(f"{t['summary_label']} (candidate for owner review): {likely}. Rework options: {opts}")
            else:
                acts.append(f"{t['summary_label']} (review required before deciding: see what's missing): {likely}. Rework options: {opts}")
            if decline: acts.append(invest)
            if fresh_due: acts.append("Review freshness")
            if cls == "Inferred" and not acts[0].startswith("Verify"): acts.append("Verify the type by reading the page")
    else:
        if issue: acts.append("Correct verified issue")
        if required is True and live: acts.append("Keep (required role)")
        if status == "Planned": acts.append("Create")
        if decline: acts.append(invest)
        if fresh_due: acts.append("Review freshness: confirm the facts are current")
        if live and fp is False and tid not in ROLE_FIRST_PARTY and tid != "X": acts.append("Confirm distinctive value on the page")
        if live and coverage == 0 and t.get("defaults", {}).get("CP") in ("M", "H"):
            acts.append("Consider making it citable (suggestion; the score does not change)")
        if live and not acts: acts.append("Maintain and measure")
        if live and tid == "X": res["notes"].append("Hub or other page: judge its routing; no type defaults apply")
        if cls == "Inferred":
            if acts and acts[0] == "Maintain and measure": acts.insert(0, "Verify the type by reading the page")
            else: acts.append("Verify the type by reading the page")
        if live and consolidate_wanted(r):
            review = gate(r, res, S, by_url, t, grp, material)
    res["primary_action"], res["secondary_actions"] = acts[0], acts[1:]
    res["review"], res["fresh_due"], res["decline"] = review, fresh_due, decline
    return res

def value_context(conv, rev, currency, S):
    parts = []
    if conv: parts.append(f"{conv:,.0f} conversions" + (f", {conv / S['total_conversions']:.1%} of all conversions in the supplied rows" if S.get("total_conversions") else ""))
    if rev: parts.append(f"{rev:,.0f} {currency or ''}".strip() + " revenue" + (f", {rev / S['total_revenue']:.1%} of all revenue in the supplied rows" if S.get("total_revenue") else ""))
    return "; ".join(parts) if parts else "no measured value"

def consolidate_wanted(r):
    return not blank(r.get("consolidate_into"))

def gate(r, res, S, by_url, t, grp, material):
    """Returns Review required, Blocked: required role, or Candidate for owner review. Never an approval."""
    missing, notes = [], []
    direction = t.get("summary_label", "Consolidate")
    if res["required"] is True:
        return {"direction": direction, "status": "Blocked: required role", "missing": ["page has a required role"],
                "notes": ["Keep the page; improve it instead"]}
    if res["classification"] != "Confirmed": missing.append("confirm the type by reading the page")
    if grp: missing.append(f"a group or pattern ({res['pages']} URLs) is never a candidate: review each URL")
    if res["required"] is None: missing.append("an explicit 'no' on legal, regulatory, support or accessibility roles (required = N)")
    if S["publisher"]: missing.append("review against the editorial remit (publisher, affiliate or reference site)")
    if res["clicks"] is None: missing.append("click data")
    elif material: missing.append(f"material traffic ({int(S['material_clicks']):,}+ clicks in a period) needs an explicit reason to change")
    if res["tracking_verified"] is not True: missing.append("verified conversion and revenue tracking")
    elif (res["conversions"] or 0) > 0 or (res["revenue"] or 0) > 0:
        missing.append("measured conversions or revenue: rework to keep that value instead")
    elif res["conversions"] is None or res["revenue"] is None:
        missing.append("conversions and revenue figures")
    if res["value_reviewed"] is not True: missing.append("value_reviewed = Y (assisted, support and audience value considered)")
    if res["referring_domains"] is None: missing.append("referring domains")
    elif res["referring_domains"] > 0: notes.append(f"{int(res['referring_domains'])} referring domains: needs a same-need destination or a deliberate 404/410")
    needs_dest = re.search(r"consolidat|prune", direction, re.I) or not blank(r.get("consolidate_into"))
    if needs_dest:
        tgt = r.get("consolidate_into")
        if blank(tgt):
            if re.search(r"consolidat", direction, re.I): missing.append("a destination that serves the same need, or a decision to retire with 404/410")
        else:
            if is_homepage(tgt): missing.append(f"{tgt} is a homepage, not an equivalent destination")
            trow = by_url.get(str(tgt).strip().lower())
            if trow is not None:
                tt = resolve_type(trow.get("content_type"))
                if tt in BYID and BYID[tt]["group"] == "Deprioritize": missing.append(f"destination {tgt} is itself a deprioritized type")
            if res["same_intent_confirmed"] is not True:
                missing.append("same_intent_confirmed = Y (the destination serves the same need; appearing in the inventory is not proof)")
    notes.append("A 404 or 410 is legitimate when no equivalent page exists; never redirect to an unrelated URL")
    status = "Review required" if missing else "Candidate for owner review"
    return {"direction": direction, "status": status, "missing": missing, "notes": notes}

# ---------------- portfolio ----------------
def cohort(rows):
    m = [r for r in rows if r["clicks"] is not None and r["clicks_previous"] not in (None, 0)]
    cur = sum(r["clicks"] for r in m); prev = sum(r["clicks_previous"] for r in m)
    return ((cur / prev - 1) if prev else None), len(m)

def share(a, b):
    return None if not b else a / b

def portfolio(rows, S):
    live = [r for r in rows if r["status"] == "Live"]
    pri = [r for r in live if r["group"] == "Prioritize"]
    dep = [r for r in live if r["group"] == "Deprioritize"]
    complete = yn(S.get("inventory_complete")) is True
    scope = "the full inventory" if complete else "the supplied rows (a sample; not proof of sitewide shares or gaps)"
    F = []
    planned_dep = [r for r in rows if r["status"] == "Planned" and r["group"] == "Deprioritize"]
    if planned_dep: F.append(("Planned work in deprioritized types: redesign these briefs using the rework options, or drop them", [r["page"] for r in planned_dep]))
    req = [r for r in live if r["required"] is True]
    if req: F.append(("Pages with a required role: keep them and improve them; they are not removal candidates", [r["page"] for r in req]))
    valued = [r for r in dep if r["tracking_verified"] is True and ((r["conversions"] or 0) > 0 or (r["revenue"] or 0) > 0)]
    if valued: F.append(("Deprioritized-type pages with verified conversions or revenue: rework them to keep that value rather than removing them", [r["page"] for r in valued]))
    urls = sum(r["pages"] for r in live if r["group"]); durls = sum(r["pages"] for r in dep)
    clicks = sum(r["clicks"] or 0 for r in live if r["group"]); dclicks = sum(r["clicks"] or 0 for r in dep)
    us, cs = share(durls, urls), share(dclicks, clicks)
    if us is not None and us >= 0.4:
        big = max(dep, key=lambda r: r["pages"])
        extra = f"; {big['page']} alone is {big['pages'] / durls:.0%} of them" if durls and big["pages"] / durls > 0.5 else ""
        cl = "click share unknown" if cs is None else f"{cs:.0%} of clicks"
        F.append((f"{us:.0%} of live URLs ({cl}) are in deprioritized types, in {scope}{extra}. A prompt to review those templates, not a reason to prune them", []))
    pc, _ = cohort(pri); dc, _ = cohort(dep); ac, an = cohort(live)
    if pc is not None and dc is not None and abs(pc - dc) < 0.10 and ac is not None and ac < -0.15:
        F.append((f"Clicks fell across the site ({ac:+.0%}), similarly for prioritized ({pc:+.0%}) and deprioritized ({dc:+.0%}) types. This is consistent with a sitewide cause (update, demand, tracking or migration) and must be checked before attributing it to content format", []))
    elif pc is not None and dc is not None and dc - pc <= -0.15:
        F.append((f"Deprioritized types lost clicks faster ({dc:+.0%}) than prioritized ones ({pc:+.0%}). Check query-level and SERP data before attributing this to AI answers or anything else", []))
    spl = norm(S.get("same_period_last_year"))
    if spl in ("n", "no", "false"):
        F.append(("The comparison isn't year over year: seasonal swings can look like gains or losses", []))
    elif spl not in ("y", "yes", "true") and any(r["clicks_change"] is not None for r in rows):
        F.append(("Confirm the comparison periods are the same period a year apart; otherwise seasonality can distort changes", []))
    fresh = [r for r in live if r["fresh_due"] and r["type_id"] in CURRENT_FACTS]
    if fresh: F.append(("Current-fact pages due a freshness check: confirm their facts are still correct", [r["page"] for r in fresh]))
    nodv = [r for r in pri if r["first_party_data"] is False and r["type_id"] not in ROLE_FIRST_PARTY and r["type_id"] != "X"]
    if nodv: F.append(("Prioritized-type pages flagged without distinctive value: confirm on the page", [r["page"] for r in nodv]))
    unc = [r for r in rows if r["type_id"] is None]
    if unc: F.append(("Unclassified rows: read and classify these before relying on the results", [r["page"] for r in unc]))
    notrel = {x.strip().upper() for x in str(S.get("not_relevant") or "").split(",") if x.strip()}
    cov = []
    for t in TYPES:
        if t["group"] != "Prioritize": continue
        R = [r for r in rows if r["type_id"] == t["id"] and r["status"] != "N/A"]
        L = [r for r in R if r["status"] == "Live"]
        if t["id"] in notrel: st = "Not relevant"
        elif not R: st = "Gap (if relevant to this business)" if complete else "Not observed in the supplied rows"
        elif not L: st = "Planned only"
        elif any(r["decline"] or r["fresh_due"] or r["first_party_data"] is False and t["id"] not in ROLE_FIRST_PARTY for r in L): st = "Needs work"
        elif any(r["provisional"] for r in L): st = "Present but still on type defaults"
        else: st = "Present and assessed"
        cov.append({"type_id": t["id"], "type": t["short_name"], "status": st, "live_rows": len(L), "planned_rows": len(R) - len(L)})
    n5 = sum(1 for r in rows for d in DIMS[:5] if r["scores"][d]["basis"] == "Framework default")
    cands = [{"page": r["page"], "url": r["url"], **r["review"], "clicks": r["clicks"], "conversions": r["conversions"],
              "revenue": r["revenue"], "referring_domains": r["referring_domains"]} for r in rows if r.get("review")]
    return {"notice": NOTICE, "sort_note": SORT_NOTE, "scope": scope, "findings": F, "coverage": cov,
            "click_change": {"all": ac, "prioritized": pc, "deprioritized": dc, "rows_with_counts": an},
            "share_scores_on_defaults": n5 / (5 * len(rows)) if rows else None,
            "review_rows": cands,
            "review_note": "Nothing here is approved. A group is never a candidate. Every item is a proposal for the owner's review."}

# ---------------- output ----------------
def fmt_pct(x): return "n/a" if x is None else f"{x * 100:+.1f}%"

def write_outputs(S, headers, mapping, rows, P, out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    js = {"version": VERSION, "notice": NOTICE, "sort_note": SORT_NOTE,
          "settings": {k: (str(v) if isinstance(v, date) else v) for k, v in S.items()},
          "rows": [{k: v for k, v in x.items() if k != "_raw"} for x in rows], "portfolio": P}
    (out / "results.json").write_text(json.dumps(js, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    rcols = ["result_type_id", "result_type", "result_group", "result_classification"] + [f"result_{d}" for d in DIMS] + \
            ["result_sort_score", "result_sort", "result_provisional", "result_clicks_change_pct", "result_primary_action",
             "result_secondary_actions", "result_review_status", "result_review_missing", "result_notes"]
    def rvals(x):
        rv = x.get("review")
        return [x["type_id"] or "", x["type"], x["group"], x["classification"]] + \
               [f"{x['scores'][d]['level']} ({x['scores'][d]['basis'].lower()})" for d in DIMS] + \
               [x["sort_score"], x["sort"], "Yes" if x["provisional"] else "No",
                None if x["clicks_change"] is None else round(x["clicks_change"] * 100, 1),
                x["primary_action"], " | ".join(x["secondary_actions"]),
                rv["status"] if rv else "", "; ".join(rv["missing"]) if rv else "",
                " | ".join(x["notes"] + x["issues"] + (rv["notes"] if rv else []))]
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        with open(out / "scored-inventory.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow([NOTICE]); w.writerow(list(headers) + rcols)
            for x in rows: w.writerow(list(x["_raw"]) + rvals(x))
        return out / "scored-inventory.csv"
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Inventory"
    ws.append([h if h is not None else "" for h in headers] + rcols)
    for x in rows: ws.append([v if not isinstance(v, (list, dict)) else json.dumps(v) for v in x["_raw"]] + rvals(x))
    grey = PatternFill("solid", fgColor="E8EAF1"); blue = PatternFill("solid", fgColor="DCE6FA")
    for c in ws[1]: c.font = Font(bold=True); c.fill = blue if str(c.value).startswith("result_") else grey
    ws.freeze_panes = "B2"
    f = wb.create_sheet("Findings")
    f.append(["Content Prioritization in an AI Search Era · assessment helper v" + VERSION]); f["A1"].font = Font(bold=True)
    f.append([NOTICE]); f.append([SORT_NOTE])
    f.append([f"Scope: {P['scope']}." + ("" if P["share_scores_on_defaults"] is None else f" Scores on framework defaults: {P['share_scores_on_defaults']:.0%}.")])
    cc = P["click_change"]
    f.append([f"Click change, rows with both periods ({cc['rows_with_counts']}): all {fmt_pct(cc['all'])}, prioritized {fmt_pct(cc['prioritized'])}, deprioritized {fmt_pct(cc['deprioritized'])}"])
    f.append([]); f.append(["Findings to verify"]); f.cell(f.max_row, 1).font = Font(bold=True)
    for text, items in P["findings"]: f.append([text, ", ".join(map(str, items))])
    f.append([]); f.append(["Coverage of prioritized types", "Status", "Live rows", "Planned rows"])
    for c in f[f.max_row]: c.font = Font(bold=True)
    for c in P["coverage"]: f.append([f"{c['type_id']} {c['type']}", c["status"], c["live_rows"], c["planned_rows"]])
    f.column_dimensions["A"].width = 120; f.column_dimensions["B"].width = 40
    rv = wb.create_sheet("Review")
    rv.append([P["review_note"]]); rv["A1"].font = Font(bold=True)
    rv.append(["Page", "URL", "Suggested direction", "Status", "Still needed", "Notes", "Clicks", "Conversions", "Revenue", "Referring domains"])
    for c in rv[2]: c.font = Font(bold=True); c.fill = grey
    for c in P["review_rows"]:
        rv.append([c["page"], c["url"], c["direction"], c["status"], "; ".join(c["missing"]), "; ".join(c["notes"]), c["clicks"], c["conversions"], c["revenue"], c["referring_domains"]])
    tot = lambda k: sum(c[k] or 0 for c in P["review_rows"])
    rv.append([]); rv.append(["Whole batch listed here", "", "", "", "", "", tot("clicks"), tot("conversions"), tot("revenue"), tot("referring_domains")])
    st = wb.create_sheet("Settings used")
    st.append(["These are skill settings, not framework rules."])
    for k, v in js["settings"].items(): st.append([k, str(v)])
    for wsx in (ws, rv):
        for col in wsx.columns: wsx.column_dimensions[col[0].column_letter].width = 22
    wb.save(out / "scored-inventory.xlsx")
    return out / "scored-inventory.xlsx"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input"); ap.add_argument("--out-dir", required=True)
    ap.add_argument("--setting", action="append", default=[], help="key=value, e.g. --setting site_model=publisher")
    a = ap.parse_args()
    ov = dict(s.split("=", 1) for s in a.setting if "=" in s)
    print(NOTICE)
    S, headers, mapping, rows, P = evaluate(a.input, ov)
    path = write_outputs(S, headers, mapping, rows, P, a.out_dir)
    print(SORT_NOTE)
    if not rows: print("No rows with a page or url were found. Fill the Inventory sheet (or the first sheet) and run again.")
    print(f"{len(rows)} rows evaluated. Mapped columns: " + ", ".join(sorted(set(mapping.values()))))
    unmapped = [h for i, h in enumerate(headers) if i not in mapping and not blank(h)]
    if unmapped: print("Not used: " + ", ".join(map(str, unmapped)))
    for text, items in P["findings"]: print("- " + text + (f": {', '.join(map(str, items[:5]))}" if items else ""))
    print(f"Results: {path} and {Path(a.out_dir) / 'results.json'}")

if __name__ == "__main__":
    main()
