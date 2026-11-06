# Inputs, definitions and how to run the script

## What users can bring
Only **page or url** is required. Every other column is optional and turns a default into evidence.
- **A URL or a few URLs:** read the pages and assess them; no script needed.
- **A Search Console Performance export** (Pages tab, .csv or .xlsx), ideally a comparison of the same period a year apart. The script recognizes the standard export headers: "Top pages", "Clicks", "Impressions", and in comparison exports "Last 3 months Clicks" and "Previous 3 months Clicks" (any period wording works).
- **A full inventory**, using `templates/content-inventory-template.xlsx` or the user's own columns.

## Columns (names are matched loosely; aliases in brackets)

| Column | Meaning |
|---|---|
| page [name, title, page_group] | Page or page-group name |
| url [address, top pages, path, url_pattern] | URL or pattern such as /blog/* |
| content_type [type, format, page_type, type_id] | Type name, short name or ID (P1–P13, D1–D8, X). Blank means unclassified: read and classify, then fill it in |
| classification [classification_status] | Confirmed (page or brief read) or Inferred (URL or title only) |
| status | Live, Planned or N/A (N/A excludes the row). Blank means Live |
| pages [url_count, count] | URLs in the group; blank means 1 |
| topic [category, product_line, cluster] | For coverage by topic |
| clicks [organic_clicks, gsc_clicks, current clicks] | **Search Console** clicks in the current period. Never analytics sessions |
| clicks_previous [previous clicks, prior clicks] | Search Console clicks in the comparison period. Preferred over a percentage |
| clicks_change_pct [click_change, yoy, change_pct] | Only if counts aren't available. Unit: see change_unit below |
| impressions, impressions_previous, impressions_change_pct | Same, for impressions. Used only to point investigations |
| sessions [analytics_sessions] | Analytics sessions; reported, never mixed with clicks |
| conversions [leads, transactions, goal_completions] | Direct conversion count. Not revenue, and not assisted conversions (keep those in notes) |
| revenue, currency | Revenue attributed to the page, with its currency. A column named only "value" is not read as revenue |
| tracking_verified | Y if conversion and revenue tracking is verified for the period; otherwise conversions are reported but don't lower business value |
| ai_cited_groups [ai_citations, cited_prompt_groups] | Distinct tracked prompt groups in which the page was cited |
| ai_tracked_groups [tracked_prompt_groups] | Distinct relevant prompt groups tracked under the same protocol (the denominator) |
| ai_scope [ai_platforms] | Platform, market, language and dates of the tracking. Keep different scopes in separate runs |
| ai_cited (Y/N) [cited] | Accepted from older inventories: reported in the row notes as a flag, never as a rate, and never used to change a score |
| gsc_ai_impressions | Impressions in Google's AI features from Search Console. A separate metric: not prompt groups, not citations |
| first_party_data (Y/N) [distinctive_value, proprietary_data] | Y if the page adds something hard to reproduce: own data, testing, access, expertise or functionality. A clue to confirm on the page; it never changes a score |
| last_verified [last_updated, last_modified] | Date the page's facts were last substantively checked or updated |
| referring_domains [backlinks, ref_domains] | Unique referring domains to the URL |
| required (Y/N) | Y if the page has a legal, regulatory, contractual, support or accessibility role. Blank means unknown, and a blank is not a no |
| value_reviewed (Y/N) | Y once a person has considered the page's assisted, support and audience value. A zero in the conversions column is not that review |
| same_intent_confirmed (Y/N) | Y once a person has confirmed the consolidate_into destination serves the same need. A destination merely appearing in the inventory is not proof |
| consolidate_into [canonical, merge_into, redirect_to] | Proposed destination for a merge |
| owner [team] | Responsible team or person |
| notes | Anything relevant, including what was read on the page |
| cr, cp, bm, bv, pa, ef | Scores. Write a level, optionally followed by its basis: `H`, `M page`, `L measured`, `H set`. A level alone counts as User set. Blank uses the framework default. The script never derives a score from a metric |
| score_notes | One-line reasons for page assessments |

## Settings
In the template's Settings tab, a JSON "settings" object, or command-line options. All optional. The 100-click floor, the material-traffic share, the −35% flag, the 6- and 12-month freshness windows and the priority rule (shared with the companion evaluator) are **skill settings, not part of the framework**.

| Setting | Default | Meaning |
|---|---|---|
| brand, site_model, objective, market, vertical | unknown | Context, reported in the results |
| current_period, previous_period | unknown | Dates for the comparison |
| same_period_last_year | unknown | Y if the comparison is year over year; N triggers a seasonality warning |
| inventory_complete | N | Y only if the inventory covers all relevant content; otherwise shares and gaps are reported for the sample only |
| change_unit | points | How plain numbers in *_change_pct columns are read: points (-22 = -22%) or fraction (-0.22 = -22%). Values written with % and Excel percentage cells are always read correctly |
| min_comparison_clicks | 100 | Below this many earlier-period clicks, a change is too small to read much into |
| material_share | 0.5 | Material traffic: at least this percentage of all clicks in the supplied rows in a period, and at least min_comparison_clicks. Scales the threshold to the site |
| decline_threshold | -35 | Click change (%) that triggers Investigate click loss |
| review_months, review_months_current_facts | 12, 6 | Freshness review cycles |

## Running it
```bash
python scripts/evaluate.py INPUT.(xlsx|csv|json) --out-dir OUTPUT_FOLDER [--setting key=value ...]
```
It writes `scored-inventory.xlsx` (the user's columns plus `result_` columns, a Findings tab and a Review tab) and `results.json`. Its actions are drafts: where several rework options are listed, choose the one that matches the page's job and say why. Reading or writing .xlsx needs openpyxl (`pip install openpyxl`); CSV and JSON need nothing extra.

Workflow: run it once to get defaults and data flags. Read and classify the unclassified or sampled pages, write the types and any page assessments (with reasons) into the inventory, then run it again for the final results. The script does arithmetic and applies the documented rules; classification, page assessments and the written recommendations are yours, and the user decides.
