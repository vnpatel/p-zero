# P-ZERO — Project Index

Start here. This file is a **map** of the project: what each file is, who it's for, and when to
read it. It intentionally contains no analysis of its own — it points into the other files.

Everything below is current as of the 2026-08-30 "RMD spend-first" engine change. The two apps are
the product; everything else exists to keep them correct.

---

## The product (the apps themselves)

| File | What it is | Audience |
|---|---|---|
| `index.html` | The **MFJ** retirement planner (married filing jointly; models a survivor phase). Self-contained HTML/JS — open in a browser. | End users; developers |
| `p-zero-single.html` | The **Single** retirement planner (single filer; switches to Head-of-Household when dependents are present). | End users; developers |

Both are locked deliverables. Never ship changes without explicit sign-off. Current default
baseline (today's $): **MFJ $1,215,092 / Single $540,113** end-of-life spendable.

---

## The QA system (3 files + this index)

The quality system verifies the engine via a three-way check: **A** (frozen benchmark) == **B**
(engine output) == **C** (independent model). Do the hard verification once, freeze it, and re-run
on every future change.

| File | Purpose | Audience | Read when |
|---|---|---|---|
| `QA-SCENARIOS.md` | The **WHAT** — the frozen answer key. Scenario 0 (the shipped default baseline) + 14 test scenarios (7 MFJ, 7 Single), each with exact inputs and locked benchmark outputs. Includes the **CPA audit appendix** (independent tax certification) and Scenario 0's independent-verification status. | Anyone verifying the engine | Before changing the engine; when a number moves |
| `QA-RUNBOOK.md` | The **HOW** — step-by-step operating manual to run the check: serve the app, drive it with Playwright, the MFJ clearing recipe, the field-ID map, how to read output. Written so a fresh operator can reproduce everything. | Whoever runs the QA | When actually running a verification |
| `qa_independent_model.py` | The **PROOF** — a from-scratch reimplementation of the engine's math in Python. Computes what each scenario *should* produce, independently of the app (this is what makes the check non-circular). Holds the canonical frozen benchmarks. | Whoever validates results | `python3 qa_independent_model.py` (MFJ) / `... all single` (Single) |
| `README.md` | This index. | Everyone, first | First |

Also run `test-suite.html` (below) — it's the complementary fast invariant/known-answer suite.

---

## Supporting files

| File | Purpose | Audience |
|---|---|---|
| `test-suite.html` | In-browser automated test suite (666 tests: invariants, known-answer constants, cash-conservation "Tier 8", chart-reconciliation "Tier 9"). Open it, click Run All. Complements the scenario benchmarks — catches leaks/regressions the benchmarks don't. | Developers |
| `CONTEXT.md` | The **chronological log** — the full history of what was done, when, and why (decisions, changelogs, parked items). This is narrative history, not a how-to. Large; read for background or to trace a past decision. | Maintainers digging into history |
| `TESTING.md` | The **testing methodology manual** — the standing account of how testing works and what it demands (how to add a feature, change a tax number, write a test). | Developers changing the engine |
| `ACCURACY-AUDIT.md` | A dated point-in-time accuracy audit snapshot (historical record; not a live reference). | Historical reference |

---

## "I want to do X" — task router (start here for common jobs)

Point an LLM (or yourself) at the right files, in the right order, for the job at hand.

### → Update the IRS / tax numbers for a new year (2027, 2028, …)
Brackets, standard deductions, contribution limits, RMD divisors, IRMAA tiers, FPL, etc.
1. Read **`TESTING.md`** → the section **"⭐ FOR AN LLM ASKED TO 'DO THE ANNUAL IRS UPDATE' — START HERE"**. That is the complete playbook (ground rules, where every constant lives, both-apps parity, sourcing discipline, the test gate).
2. Update constants in **both** `index.html` and `p-zero-single.html` (`IRS_2026` block), the `qa_independent_model.py` header, and the test-suite's `IRS_2026_KNOWN` — all in lockstep, from authoritative primary sources (never memory).
3. Gate: run **`test-suite.html`** (both apps) to green, then re-run **`qa_independent_model.py`**. This is a **constants + prose** update, NOT an engine change — if you're editing a formula, stop.

### → Add new functionality / a new feature
1. Read **`README.md`** (this file) for orientation, then **`TESTING.md`** in full — it is the methodology manual and states the rules a feature must follow.
2. **The core rule:** any feature that *moves money* MUST (a) publish its cash flow in the engine's `chartSeries.push` with `aud`-prefixed fields, (b) add a cash-conservation ("Tier 8") test so money can't leak, (c) update the in-app Help prose, and (d) re-benchmark. Skipping any of these is how silent bugs enter.
3. Skim **`CONTEXT.md`** for prior art on similar features (it's the history log — search it, don't read it cover to cover).
4. Verify with the full three-way check per **`QA-RUNBOOK.md`**, then run **`test-suite.html`**. If the feature changes any scenario's numbers, re-lock benchmarks in `qa_independent_model.py` + `QA-SCENARIOS.md` and sweep the default baselines everywhere (see next task).

### → Change engine behavior / a calculation (not just constants)
1. Read **`TESTING.md`** (methodology) and the **`QA-RUNBOOK.md`** engine-change protocol.
2. Back up both apps first. Show the exact edit before making it. Make the minimal change.
3. Validate to the dollar against `qa_independent_model.py` for all scenarios; run tripwires (unchanged scenarios stay unchanged; pre-change years stay identical); run `test-suite.html` to green.
4. Re-benchmark and propagate the moved numbers through **all three** surfaces: (1) QA scenario benchmarks, (2) default-load baselines, (3) every doc citing either (QA-SCENARIOS, CONTEXT, TESTING, README). Missing one is the most common mistake — see the RMD-change changelog in CONTEXT.md for the full worked example.

### → Verify the engine is still correct (regression check)
1. **`QA-RUNBOOK.md`** — the how-to for the three-way A==B==C check.
2. Run **`qa_independent_model.py`** (both apps) and **`test-suite.html`**. Compare against the frozen benchmarks in **`QA-SCENARIOS.md`**. A mismatch is a *finding to investigate*, never a number to overwrite.

### → Understand what a specific number means, or trace a past decision
**`CONTEXT.md`** — the chronological log. Search it for the topic. For the independent tax certification, see the **CPA appendix** in `QA-SCENARIOS.md`.

---

## Open / parked items (see CONTEXT.md "PARKED ITEMS" for detail)

- **[D] Cashflow tab (2026-09-18, ported to Single + several bug fixes 2026-09-19+)** — a third Plan
  Details chart tab, display-only (no engine change), reconciling Sources==Spend for every retirement
  year including RE/Biz sale/refi and inheritance years (a gap Distribution Mix's own panel still has —
  documented, not fixed, by explicit scope decision). Full feature parity between MFJ and Single as of
  this pass. See CONTEXT.md and QA-SCENARIOS.md PART 4 (including its "Single port + subsequent fixes"
  table) for the full history — several real bugs (a double inflation-adjustment on the 4% Rule metric,
  a stuck orphaned tooltip, dollar-label crowding on long horizons, a milestone-icon filter that missed
  the common case) were found via direct user testing after the initial build and fixed in both apps.

- **[A] ✅ DONE (2026-09-09)** — Social Security now uses the IRC §86 provisional-income phase-in
  (recomputed yearly); the "% of SS Taxed" field is an optional override. Verified vs IRS Pub 915.
- **[C] Constants annual refresh** — 2026 IRS/CMS figures will change for 2027; update the model
  header, both engines, and the test-suite together when the IRS publishes.
- **Scenario 0 independent A==C** — the default baseline is A==B certified and independently
  reproduced to within ~3.7%, residual isolated to brokerage basis-ratio bookkeeping. See
  QA-SCENARIOS.md "SCENARIO 0" for the precise status.

(Item [B], RMD reinvestment → spend-first, was completed 2026-08-30.)

---

## Backups

Files named `*.PRE-*.bak` / `*.PRE-KIDS-REFACTOR-*.bak.*` are timestamped backups from before major
changes. Not live; kept for rollback.

- **`qa-panel-reconciliation.js`** — comprehensive Plan Details panel validator (display vs engine, 8-scenario matrix × both apps × all years). Run: serve outputs on :8199, `node qa-panel-reconciliation.js` → must be 0 violations. Scenarios documented in QA-SCENARIOS.md PART 3.
