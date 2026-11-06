# Framework reference: the 21 content types

Source: [Content Prioritization in an AI Search Era](https://www.aleydasolis.com/en/ai-search/content-prioritization-ai-search/) by Aleyda Solis and its [worksheet](https://docs.google.com/spreadsheets/d/18myHCvxeylIyc6zGnE5HWLYw8nN7rQz-TfMQslAfiko/edit).

**What is the framework, and what isn't.** The framework is the 21 content types: their roles, related prompts, examples and the six High/Medium/Low default scores. Those are reproduced below in the worksheet's own words (with obvious typos corrected). For the 8 types to deprioritize, the framework's guidance is the **Why** sentence of each type. Everything else in this skill is a skill setting, not a framework rule: the judging anchors, the sort score, the priority rule, the thresholds, the freshness windows, the likely directions and short labels (summaries of the Why), and the rework options (a skill translation: the worksheet never names one destination type). Default scores are directional starting points for a type, not findings about a page.

Dimension codes: CR click resilience · CP citation potential · BM brand mention potential · BV business value · PA proprietary advantage · EF expected effort (higher = costlier).


## How to judge each dimension for a specific page

These anchors are a skill aid for consistent judgement, not part of the worksheet. Use them when you make a page assessment, and score what the page actually does for its audience and objective.

| Dimension | Low | Medium | High |
|---|---|---|---|
| Click resilience | An AI answer fully satisfies the need; nothing remains to do or check on the page. | A visit helps some users verify details, see context or take a next step. | The need depends on something the page enables: an action, an interaction, a personalized result, current facts or verification. |
| Citation potential | Few verifiable, relevant claims; little reason to cite it over other sources. | Relevant, supported information or useful synthesis with clear attribution. | A primary or uniquely useful source with clear, verifiable, current evidence for a defined need. |
| Brand mention potential | Little legitimate connection between the brand and the need. | A credible association between the brand and the topic or product. | The brand is central to solving the need or supplying the evidence. |
| Business value | Weak or no connection to the site's objective. | A credible supporting role in acquisition, conversion, retention, support or mission. | A strong, direct role in the objective, shown by a clear journey or measured contribution. |
| Proprietary advantage | Easily reproduced from common sources. | Useful original analysis, expertise, verification or functionality that takes real work to reproduce. | Hard to reproduce: own data, testing, access, expertise or systems. Owning the page alone doesn't make it High; the content has to show it. |
| Expected effort | Little production and maintenance work for this organization. | Moderate editorial, technical, expert or upkeep work. | Substantial production or ongoing data, verification, technical or upkeep work. |

## Telling similar types apart

Classify by the job the content does for the user, not by its URL, title or format.

| If it looks like… | It is the prioritized type when… | Otherwise |
|---|---|---|
| Calculator, quiz, finder, configurator | it returns a useful result for this user from live, proprietary, account-level or distinctive inputs | D7 Generic calculators & quizzes |
| "Best", vs, alternatives | criteria are disclosed, evidence is shown, trade-offs are explained, and it says when another option wins | D6 Biased or mass comparisons |
| News, press, announcement | it adds a first-hand source, interviews, documents or original analysis | D4 News & press rewrites |
| Templated pages at scale | each URL shows distinctive data or analysis and serves a different task | D8 Programmatic public-data pages |
| How-to, guide, explainer | it is product-, version- or context-specific, or adds testing, expert input, original data or tools | D2 Rehashed explainers |
| FAQ or variant URLs | location, audience, regulation, platform or task genuinely changes the answer | D3 Fragmented FAQ & variants |
| Definition or glossary | it is brand-specific, sits inside a product, docs or topic hub, or demonstrably serves customers (for example support) | D1 Commodity definitions |

Other boundaries:
- First-hand tests cover one product under stated conditions. Customer outcomes show what changed for a real customer. Original research finds patterns across many users, products or periods with a repeatable method.
- Live data hubs display current facts across many items. Personalized tools calculate an answer for this user. Scalable first-party data pages are one useful page per real entity, each with distinctive data.
- Official docs and policies are the source of record. Implementation and troubleshooting guides help make it work in a specific context.
- A page that mixes types is classified by its main job; note the secondary one.
- Public data isn't a reason to deprioritize on its own: original analysis, verification or useful functionality on top of it can make content worth investing in.
- **Hubs, category and index pages** (resource hubs, blog listings, category pages) aren't one of the 21 types. Classify them as Transaction & task when they route users to the brand's own action (buy, install, send, sign up); otherwise mark them X (hub or other) and judge their routing: where they lead, whether they add anything only the brand has. Don't copy their destinations' scores.
- **X** is for pages no type describes well. X has no default scores; assess them or leave them unknown.


## Content types to prioritize (13)

### P1 · Brand and entity pages (Brand & entity)
- **Defaults:** CR M · CP H · BM H · BV H · PA H · EF L
- **Role:** This content establishes the canonical facts about the organization: What it is and what it offers, who owns or represents it, where it operates and why it can be trusted. Its role is to provide entity clarity and verification, not detailed product instructions, live availability or conversion.
- **Related prompts:** What is [Brand] and what does it offer?; Who owns or operates [Brand]?; Is [Brand] legitimate and available in [Market]?
- **Examples:** About, organization, leadership, author, trust, location and product or service overview pages with consistent facts, disclosed ownership or authorship, verifiable claims and a clear internal hierarchy.

### P2 · Transaction and task-completion pages (Transaction & task)
- **Defaults:** CR H · CP H · BM M · BV H · PA H · EF M
- **Role:** This content lets a person or agent complete a high-value action on the site: buy, book, apply, download, request, cancel, contact or resolve an account task. Its role is about the conversion, so it should show the current price or value, eligibility, safety constraints, required inputs and next step.
- **Related prompts:** Buy [Product] online in [Country]; Book [Service] in [Location] for [Date]; Start a trial, download [Product] or request a quote
- **Examples:** Pricing, sign-up, checkout, booking, download, application, quote, claim, contact, account and support-resolution pages with complete, structured action requirements.

### P3 · Official product documentation, specifications and policies (Official docs & policies)
- **Defaults:** CR M · CP H · BM H · BV H · PA H · EF M
- **Role:** This content publishes authoritative facts only the organization can provide: product or service requirements, feature behavior, compatibility, pricing rules, policies, warranties and release changes. Its role is to be the current source of record, not persuade, compare options or troubleshoot every possible context.
- **Related prompts:** What are [Product]'s requirements or specifications?; How does [Feature, Policy or Plan] work?; What changed in [Product or Service] version [X]?
- **Examples:** Release notes, documentation, compatibility matrices, policy and warranty pages, specifications, eligibility rules and official answers within maintained hubs.

### P4 · First-hand product tests and performance reviews (First-hand tests)
- **Defaults:** CR H · CP H · BM M · BV H · PA H · EF H
- **Role:** This content tests one product or service under specified conditions and reports what was observed or measured. Its role is to answer ‘How did this specific option perform?’ with a transparent method, evidence, expert judgement and limitations, not infer market trends or prove a customer's before and after outcome.
- **Related prompts:** How did [Product] perform under [Test condition]?; Does [Product] work for [Specific use case]?; What are [Product]'s measured strengths and limitations?
- **Examples:** Hands-on tests, benchmarks, teardowns, trials, demonstrations and measured reviews documenting the method, sample, conditions, results, pros, cons and limitations.

### P5 · Original market, audience and usage research (Original research)
- **Defaults:** CR M · CP H · BM H · BV M · PA H · EF H
- **Role:** This content analyzes a product or service relevant dataset across many users, customers, products, markets or periods to reveal a pattern, benchmark or trend that hasn't been previously covered, with a reproducible method, not review one item or explain one implementation.
- **Related prompts:** What is the average [Metric] for [Audience or Industry]?; How has [Customer behavior] changed over time?; Which [Features or Products] are most used by [Segment]?
- **Examples:** Surveys, indexes, anonymized usage studies, industry benchmarks, trend reports and recurring datasets with a clear, repeatable methodology.

### P6 · Live first-party databases and reference hubs (Live data hubs)
- **Defaults:** CR H · CP H · BM M · BV H · PA H · EF H
- **Role:** This content lets users look up current product or service facts that change, such as price, availability, inventory, status, eligibility, schedules or rates. Its role is current state reference across a set of relevant items; showing verified facts rather than calculating a personalized answer or creating one URL per keyword variation.
- **Related prompts:** Is [Product or Service] available in [Location] now?; What are the current prices, rates or availability for [Item]?; Which offers, events or status updates are active today?
- **Examples:** Live inventories, availability databases, status pages, rate or price trackers, store locators, event calendars and frequently updated reference hubs.

### P7 · Documented customer outcomes, experiments and case studies (Customer outcomes)
- **Defaults:** CR H · CP M · BM M · BV H · PA H · EF M
- **Role:** This content documents what changed after a real product, service or approach was used, including the starting point, actions, constraints, timeline and measured outcome. Its role is ‘Show me that it worked in a comparable situation’, not teach the general process, test one product in isolation or compare alternatives.
- **Related prompts:** What results did [Customer type] achieve with [Product or Approach]?; What changed before and after [Action]?; What did [Experiment] show under [Condition]?
- **Examples:** Customer case studies, before and after analyses, documented experiments and implementation stories supported by real inputs, screenshots, outputs and measurable results.

### P8 · Product specific implementation and troubleshooting guides (Implementation & troubleshooting)
- **Defaults:** CR H · CP M · BM M · BV H · PA H · EF M
- **Role:** This content helps an existing user configure, implement or fix a specific product when the correct steps depend on the version, device, environment, error, location or constraint. Its role is ‘Help me make it work here’, not proving a past outcome or choosing between products.
- **Related prompts:** Why doesn't [Product] work on [Device or Version]?; How do I configure [Feature] for [Use case or Constraint]?; How do I resolve [Error] in [Specific environment]?
- **Examples:** Troubleshooting trees, configuration guides, advanced implementation instructions and support content segmented by version, device, symptom, customer stage or operating environment.

### P9 · Evidence led comparisons and selection guides (Evidence-led comparisons)
- **Defaults:** CR M · CP L · BM M · BV H · PA M · EF M
- **Role:** This content helps users to choose between two or more viable options for a defined scenario. Its role is to ‘Help me decide’ by applying transparent criteria, evidence and trade-offs, then explaining who each option is best for.
- **Related prompts:** [Product] vs [Alternative] for [Specific use case]; Best [Category] for [Audience, budget or constraint]; Which [Option] is right for [Specific need]?
- **Examples:** X vs Y comparisons, alternatives pages, shortlists and best of guides with disclosed criteria, supporting evidence, limitations and scenarios in which different options win.

### P10 · Personalized tools using live or proprietary data (Personalized tools)
- **Defaults:** CR H · CP L · BM L · BV H · PA H · EF H
- **Role:** These are personalized tools using product or service data to help users solve needs related and complementary to the core ones provided by the brand products or services, with calculated, configured or recommended results. Its role is to produce a usable answer for this user or situation rather than simply display current facts or run a generic formula that an AI interface can reproduce.
- **Related prompts:** Calculate the total cost or ROI using my inputs; Which plan or product fits my needs and current setup?; Am I eligible for [Offer or Service] in my location or account?
- **Examples:** Calculators, configurators, planners, recommenders, eligibility checkers and comparison tools driven by live, proprietary, account-level or user-specific inputs.

### P11 · Curated community and practitioner knowledge (Curated community)
- **Defaults:** CR M · CP M · BM M · BV H · PA M · EF H
- **Role:** This content captures useful experience from customers, creators or practitioners, then adds authorship, moderation and editorial context. Its role is to feature real-world know-how and edge cases, rather than the brand's official answer or commissioned reporting as community evidence.
- **Related prompts:** How do experienced customers use [Product] for [Use case]?; Which mistakes do practitioners recommend avoiding?; What worked for organizations or people like mine?
- **Examples:** Curated community Q&A, expert columns, creator hubs, customer showcases and moderated discussion archives with disclosed authorship and editorial context.

### P12 · Original reporting and source analysis (Original reporting)
- **Defaults:** CR H · CP M · BM H · BV M · PA H · EF H
- **Role:** This content is original reporting: interviews, event access, documents, observation or specialist analysis. Its role is to explain what happened and why using first-hand sources, not summarize another publisher's report or turn a dataset into a market benchmark.
- **Related prompts:** Why did [Company or Industry] change [Product or Policy]?; What did [Expert or Executive] reveal about [Topic]?; What does [Recent development] mean for [Audience]?
- **Examples:** Interviews, event coverage, investigations, expert analysis, behind the scenes reporting and original commentary supported by first-hand sources or media.

### P13 · Scalable pages featuring genuine, useful insights powered by unique first-party data (Scalable first-party data pages)
- **Defaults:** CR M · CP H · BM M · BV H · PA H · EF H
- **Role:** This content provides a useful page for each real entity, product, location or integration because every page shows uniquely different owned data and serves a different task. Its role is scalable coverage of genuine, useful and relevant insights for the brand audience, not publishing keyword variants or templating public facts.
- **Related prompts:** [Product model] specifications, availability and change history; [Location] service availability, prices and local requirements; [Integration] setup, supported features and current status
- **Examples:** Entity, product, location and integration pages featuring unique and useful metrics, availability, change history, comparisons and context from owned data, with editorial quality assurance.


## Content types to deprioritize (8)

These are the types an AI answer can satisfy on its own. For each one, the **Why** is the framework's own guidance. Below it, the skill adds:
- a **likely direction** and a **short label**, which summarize the Why;
- **rework options**, a skill translation listing the prioritized types a page could become. After reading a page, pick the one option that matches its job, and say why.

Any removal or merge still goes through the review gate in SKILL.md.

### D1 · Standalone commodity definitions without brand or journey context (Commodity definitions)
- **Defaults:** CR L · CP L · BM M · BV L · PA L · EF L
- **Why (framework):** This content defines a common term or acronym using information already available everywhere. Search features and AI can answer it without a click; keep it only inside a relevant product, service or topic hub, or when the definition is genuinely brand specific.
- **Related prompts:** What is [Basic term]?; What does [Acronym] mean?; What is the difference between [Common term A] and [Common term B]?
- **Examples:** Dictionary style definitions, basic explainers and acronym pages compiled from common knowledge with no distinctive brand, product, audience or next step context.
- **Likely direction (skill summary of the Why):** Consolidate into the relevant product, service or topic hubs, and keep standalone only the definitions that are genuinely brand-specific. Short label: Consolidate.
- **Rework options (skill translation; choose the one that matches the page's job):** Official docs & policies; Brand & entity, when the definition is about the brand; the product or topic hub it actually supports

### D2 · Rehashed explainers and how to guides without original value (Rehashed explainers)
- **Defaults:** CR L · CP L · BM L · BV L · PA L · EF M
- **Why (framework):** This content repackages common advice or existing sources without first-hand testing, expert contribution, original data, tools or distinctive media. Changing the length or title doesn't fix the problem: AI can summarize the same consensus and the page gives users no extra reason to visit.
- **Related prompts:** How do I get started with [Broad topic]?; Complete guide to [Common process]; How can I improve [Generic outcome]?
- **Examples:** Broad how-tos, expanded rewrites, exhaustive introductions and ‘everything you need to know’ guides assembled from public sources without original evidence or practical utility.
- **Likely direction (skill summary of the Why):** Rework the pages worth keeping into a format that adds what an AI summary can't, and stop producing new ones. Short label: Rework or retire.
- **Rework options (skill translation; choose the one that matches the page's job):** Evidence-led comparisons, when the job is choosing; First-hand tests, when the job is how something performed; Implementation & troubleshooting, only when the job is setup or fixing; Original research, when the job is a pattern across many cases

### D3 · Fragmented FAQ and keyword variant pages serving one intent (Fragmented FAQ & variants)
- **Defaults:** CR L · CP M · BM L · BV L · PA L · EF L
- **Why (framework):** This content distributes one user need across different URLs because the questions or keywords are worded differently, not because the answer really changes. Consolidate them into the relevant canonical product, policy, support or transaction page unless a location, audience, regulation, platform or task creates a genuinely different answer.
- **Related prompts:** Is [Product] free? / Does [Product] cost anything?; Buy [Product] online / Where can I order [Product]?; Can I cancel [Plan]? / How do I end [Plan]?
- **Examples:** Single question FAQ URLs and near duplicate pages created for wording, keyword or minor audience variations that a single, stronger canonical page can satisfy.
- **Likely direction (skill summary of the Why):** Consolidate into the relevant canonical product, policy, support or transaction page, unless location, audience, regulation, platform or task genuinely changes the answer. Short label: Consolidate.
- **Rework options (skill translation; choose the one that matches the page's job):** Transaction & task, when the question is about buying or doing the task; Official docs & policies, when it is about rules or specs; Implementation & troubleshooting, when it is about making it work

### D4 · Third-party news and press release rewrites without original input (News & press rewrites)
- **Defaults:** CR L · CP L · BM L · BV L · PA L · EF M
- **Why (framework):** This content repeats an announcement or another publisher's reporting without adding a first-hand source, new evidence, analysis or audience specific impact. It becomes stale quickly and gives search or AI systems no reason to cite or send users to the rewrite.
- **Related prompts:** What did [Company] announce today?; What changed in the latest [Third-party product] update?; What is the latest news in [Industry]?
- **Examples:** Press release rewrites, recaps copied from another source and summaries of third-party announcements with no original reporting, evidence or analysis.
- **Likely direction (skill summary of the Why):** Add a first-hand source, evidence, analysis or audience-specific impact, or stop producing them. Short label: Rework or retire.
- **Rework options (skill translation; choose the one that matches the page's job):** Original reporting, only if there is a first-hand source; otherwise stop producing them

### D5 · High volume tangential topics without a credible business journey (Tangential high-volume topics)
- **Defaults:** CR L · CP L · BM L · BV L · PA L · EF M
- **Why (framework):** This content targets search demand that is only loosely related to the organization's product, service, expertise or audience outcome. Even if it attracts visits, it has no credible next step or business value and is often fully satisfied by an AI answer.
- **Related prompts:** What are the biggest [Industry] trends in [Year]?; How do I start [Unrelated activity]?; What is the best [Unrelated product] for [Broad audience]?
- **Examples:** High volume lifestyle, career, trend or industry topics that are only loosely related to the site and offer no useful next step.
- **Likely direction (skill summary of the Why):** Stop investing in these topics, and decide what happens to the existing pages after the checks. Short label: Retire.
- **Rework options (skill translation; choose the one that matches the page's job):** none: there is no prioritized format to rework this into

### D6 · Biased or mass produced ‘best’, comparison and alternatives pages (Biased or mass comparisons)
- **Defaults:** CR L · CP L · BM L · BV M · PA L · EF M
- **Why (framework):** This content targets purchase decision queries but doesn't provide credible decision support: it ranks the publisher first, hides the method, repeats the same template at scale or cannot show a situation in which another option wins. Consolidate coverage and keep only comparisons with transparent criteria, evidence and meaningful trade-offs.
- **Related prompts:** What are the best [Category] brands?; [Brand] vs [Competitor] for [Use case]; What are the alternatives to [Product]?
- **Examples:** Self-serving best-of lists, thin X vs. Y comparisons and alternatives pages created at scale without disclosed criteria, testing, evidence, trade-offs or audience-specific recommendations.
- **Likely direction (skill summary of the Why):** Consolidate coverage, and keep only comparisons with transparent criteria, evidence and meaningful trade-offs. Short label: Rework or consolidate.
- **Rework options (skill translation; choose the one that matches the page's job):** Evidence-led comparisons

### D7 · Generic calculators, quizzes and generators without distinctive inputs (Generic calculators & quizzes)
- **Defaults:** CR L · CP L · BM L · BV L · PA L · EF M
- **Why (framework):** This content applies a basic formula or produces a shallow answer from inputs an AI interface can handle directly. Keep it only when live or proprietary data, meaningful personalization, repeat use or a clear product action makes the output actually useful.
- **Related prompts:** Which [Product type] should I choose?; Generate a [Topic] name; Calculate a basic percentage or conversion
- **Examples:** Generic quizzes, calculators and generators with no live data, personalization depth, recurring use, distinctive output or credible product journey.
- **Likely direction (skill summary of the Why):** Keep only tools with live or proprietary data, real personalization, repeat use or a clear product action. Short label: Rework or retire.
- **Rework options (skill translation; choose the one that matches the page's job):** Personalized tools

### D8 · Programmatic pages built from public or competitor data (Programmatic public-data pages)
- **Defaults:** CR L · CP L · BM L · BV L · PA L · EF H
- **Why (framework):** This content creates many templated pages from facts anyone can access, without unique first-party data, expert judgement or a genuinely different task on each URL. Scale multiplies duplication, maintenance and quality risks; it doesn't create real value.
- **Related prompts:** [Competitor] pricing and features; [Third-party product] specifications; [Generic term] glossary
- **Examples:** Location, definition, specification, pricing or entity pages generated from third-party or public datasets without first-party data, expert judgement or a distinct user task.
- **Likely direction (skill summary of the Why):** Keep only the URLs with distinctive data and a distinct task; scale alone doesn't create value. Short label: Rework or prune.
- **Rework options (skill translation; choose the one that matches the page's job):** Scalable first-party data pages (do not approve the template as one batch)
