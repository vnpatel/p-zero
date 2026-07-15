# P-ZERO — Project Handoff & Decision Log

> **Read this first if you are a new LLM or developer picking up this project (or the original author returning after time away).**
> This single file is the entry point. **Part 1** orients you (what the project is, how to work on it safely). **Part 2** is the full decision log (why each thing was built the way it was). One file, two purposes — Part 1 is the "how to work," Part 2 is the "why we chose."

---

## ⚑ If you are the LLM (or developer) picking this up — YOUR operating rules

These are not history — they are the rules that bind **you**, the current reader, for as long as you work on this project. Read them before touching anything.

1. **The two app files are LOCKED. Never ship a change without the user's explicit go-ahead.** Ask "Do I have your go-ahead to ship?" and wait for a clear "yes"/"ship" every single time. Re-lock (stop editing, require re-authorization) after each ship. There is no literal lock file — this is a discipline you must honor. See §3.
2. **Never claim verification you did not actually perform.** If you say "EOL unchanged ✓" or "suite 146/146 ✓," you must have *actually run* it (§5), not inferred it from reading a diff. Faking a green check in a financial tool is the worst failure mode here. If you cannot run it, say so plainly.
3. **Work MFJ first, then replicate the verified pattern to Single.** Don't edit both blindly in parallel — see §2, §7.
4. **Do NOT "fix" the deliberate simplifications** (flat-rate SE tax, phantom-wife cruft, no cash-reserve bucket, etc.). They are intentional. See §6.
5. **Verify claims against the actual code, push back honestly, and retract your own over-statements** when you find you were wrong. The user expects a straight collaborator, not a yes-man. (This very handoff had a factual error — the `__chartSeries` claim — that was caught only by reading the code; assume you'll find more.)
6. **When in doubt, ask.** This is a working artifact someone relies on; a clarifying question is always cheaper than a wrong change.

Everything below explains the project so you can follow these rules well.

---

## How to use this document (and what it does NOT cover)

This file is **one layer of a three-layer system.** It is deliberately *not* a complete specification — it points to the other two layers rather than duplicating them. Do not mistake it for exhaustive.

| Layer | Where it lives | What it answers | When to read it |
|-------|---------------|-----------------|-----------------|
| **1. Orientation + decisions** | **This file (HANDOFF.md)** | *How do I work on this safely? Why were things built this way?* | **First.** Always start here. |
| **2. Product / behavior spec** | **In-app Help docs** (the Help modal inside each app — extensive, audited for accuracy) | *What does the app do? What does each feature, KPI, column, and phase mean?* | Second — when you need to know how a feature behaves. |
| **3. Ground truth** | **The code** (`index.html` / `p-zero-single.html`) + its inline comments | *How does every calculation actually run, line by line?* | Third — when you need exact mechanics. |

**What THIS file covers:** the architecture, the lock discipline, the verification recipe, the regression baselines, the known simplifications, the MFJ-vs-Single differences, current state, a **code-architecture map** (§10 — major functions grouped by subsystem + the data flow), and the full decision log for the work done to date.

**What THIS file does NOT cover (read the code / Help instead):** the *line-by-line internals* of each function (the exact withdrawal-ordering rules, the Roth-conversion sizing arithmetic, every KPI formula, the growth-timing math). §10 tells you *which function does what and how data flows between them* — it's a map to navigate by, not a reproduction of the logic. For exact mechanics, the map points you to the right function; read it there.

**Ideal reading order for a newcomer:** this file (orient + rules + why) → the in-app Help (what it does) → the code (how it does it). This file exists to make the other two *safe and efficient* to use, not to replace them.

---

## Table of Contents

**PART 1 — START HERE (orientation)**
1. [What P-ZERO is](#1-what-p-zero-is)
2. [The two-app architecture (MFJ + Single are forks)](#2-the-two-app-architecture)
3. [File map & the LOCK discipline](#3-file-map--the-lock-discipline)
4. [Engine mental model + key facts](#4-engine-mental-model--key-facts)
5. [The verification recipe (how to change anything safely)](#5-the-verification-recipe)
6. [Known simplifications — do NOT "fix" these](#6-known-simplifications--do-not-fix-these)
7. [MFJ vs Single — the differences that matter](#7-mfj-vs-single--the-differences-that-matter)
8. [Current state: done vs. deferred](#8-current-state-done-vs-deferred)
9. [How to do the most common tasks](#9-how-to-do-the-most-common-tasks)
10. [Code architecture map (functions & data flow)](#10-code-architecture-map)

**PART 2 — DECISION LOG (the deep "why")**
- [Full chronological record of every change + rationale](#part-2--decision-log)

---
---

# PART 1 — START HERE

## 1. What P-ZERO is

P-ZERO is a **deterministic, year-by-year retirement-drawdown simulator** delivered as a **single self-contained HTML file** (Tailwind browser build + Font Awesome, no backend, no build step). The user enters their financial picture (balances, contributions, ages, tax settings) and the engine projects the portfolio forward to a target end-of-life age, modeling withdrawals, taxes, Roth conversions, RMDs, Social Security, healthcare (ACA/IRMAA), and a legacy/heir KPI.

It is a **planning sandbox**, explicitly *not* financial advice (there's a disclaimer in the footer). It uses approximated tax tables and simplifying assumptions by design.

There are **two apps** (see §2): one for Married-Filing-Jointly households, one for Single/Head-of-Household filers.

Live (GitHub Pages, proprietary license):
- MFJ: `https://vnpatel.github.io/p-zero/`
- Single: `https://vnpatel.github.io/p-zero/p-zero-single.html`

## 2. The two-app architecture

**Single is a FORK of MFJ**, not an independent codebase. They share the same engine, the same `IRS_2026` constants structure, the same UI shell, the same verification methodology. Almost every change this project applies to *both apps in parallel*.

- **`index.html`** = the **MFJ** app (Married Filing Jointly, two people: "H" husband + "W" wife).
- **`p-zero-single.html`** = the **Single/HoH** app. It was forked from MFJ and the second person ("W") was **neutralized by mirroring** (`wBirthYear = hBirthYear`, etc.) rather than removed. It switches between Single and Head-of-Household treatment based on whether the user adds dependents (`isHoH()` returns `childrenProfiles.length > 0`).

Because Single is a fork, ~35 inert `wAge`/`wBirthYear` "phantom-wife" references remain in its code. **They are harmless** (`wAge === hAge` always; the survivor code that reads them is force-disabled). Purging them is deferred (see §6, §8).

**When you change one app, you almost always need to make the parallel change in the other.** The standard workflow is: build + fully verify MFJ first, then replicate the *proven* pattern to Single. This has caught bugs on MFJ before they were duplicated into Single every time.

## 3. File map & the LOCK discipline

### Canonical shipped files — `/mnt/user-data/outputs/`
| File | What it is |
|------|-----------|
| `index.html` | MFJ app (the shipped, live artifact) |
| `p-zero-single.html` | Single/HoH app (shipped, live) |
| `test-suite.html` | Browser test suite covering BOTH apps (loads them in iframes) |
| `LICENSE` | Proprietary license |
| `HANDOFF.md` | **This file** (was `FUTURE_ITEMS.md`, now merged) |

### Working copies — `/home/claude/`
Work on copies here (`mfj.html`, `single.html`, `test-suite.html`, plus `harness.js`), never edit the shipped files directly. Copy from outputs → working dir at the start of a task:
```bash
cp /mnt/user-data/outputs/index.html ./mfj.html
cp /mnt/user-data/outputs/p-zero-single.html ./single.html
```

### 🔒 THE LOCK DISCIPLINE — this is the single most important operational rule

Both `index.html` and `p-zero-single.html` are treated as **LOCKED**. That means:
1. **Do not change them without an explicit unlock** from the user.
2. **Before EVERY ship, confirm you have permission** ("Do I have your go-ahead to ship?"). The user says "ship" / "yes" to authorize.
3. **Re-lock after shipping** (conceptually — there's no literal lock file; it's a discipline: you stop editing and require re-authorization for the next change).
4. The user reviews frequently, asks probing "are you sure / how confident?" questions, and expects you to **verify claims against the actual code**, push back honestly, and **retract your own over-statements** when wrong. Do not be a yes-man.

If you ship without confirming, or edit a locked file freely, you have violated the core working agreement.

## 4. Engine mental model + key facts

### The engine
- Core function: **`triggerRecalculate()`**. It runs the full year-by-year projection and writes results.
- It exposes **`window.__scenarioB`** (the projection result) and **`window.IRS_2026`** (the tax constants).
- **`window.__scenarioB.series`** is a STRIPPED array: only `{year, spendableTotal, trad, roth, brok, hsa, f529}` per year. The rich per-year detail (income1099, tax, stage flags) lives in an internal `chartSeries` that is **not** exposed on `window`. If you need to verify internal tax values in a test, you must temporarily expose them (add a debug hook to `chartSeries`, verify, then REMOVE the hook before shipping — this was done for the W-2/1099 work).

### Buckets
Five asset pools: **Traditional, Roth, Brokerage, HSA, 529.**

### The phase model (drives everything age-based)
Each simulated year is in one of these stages:
- **Accumulation** — both working, contributing.
- **Covered** — exactly one spouse has stepped down (MFJ only); `isCovered = (hWorking || wWorking) && !(hWorking && wWorking)` (XOR). The still-working spouse's income is assumed to cover costs; contributions continue at a configurable covered-%.
- **Semi-retirement** — both past their semi age but not both past full age. Contributions stop; per-person part-time "semi-retirement income" flows (1099 or W-2, see decision log); withdrawals begin.
- **Full retirement** — both past full-retirement age. Portfolio + SS funds everything.
- `hWorking = hAge < hSemi`, `wWorking = wAge < wSemi`. Ages computed as `currentYear - birthYear`; `startYear = new Date().getFullYear()`.

### 🎯 THE REGRESSION BASELINES (memorize these)
The **default-scenario end-of-life (EOL) spendable total** is the invariant every change must preserve unless intentionally altering the default:
- **MFJ default EOL = `$693,546`**
- **Single default EOL = `$607,219`**

After ANY change, re-run the default and confirm the EOL is unchanged (or, if you intended to change behavior, that it changed by exactly the expected amount and for the right reason). A shifted EOL you didn't expect = a bug.

**Note on RE/BI:** the default scenario has **zero** Real Estate / Business deals (`rebiDeals = []`), so the baselines above still hold with the feature present. Any scenario *with* a deal is new ground — verify it against hand-computed arithmetic, not against the baseline. The permanent Tier 6 suite tests already lock in the hand-verified targets.

### `IRS_2026` — the single source of tax law
All federal statutory values live in the **`const IRS_2026 = { ... }`** block. The engine reads from it directly (not from the DOM). This means **annual tax-law maintenance is a single-block edit** — change the numbers in `IRS_2026` and the whole app (engine + the read-only Federal Tax Details display) updates automatically.

Key contents: `taxYear`, `mfjOrdinary`/`mfjLtcg` (MFJ) or `singleOrdinary`/`hohOrdinary`/`singleLtcg`/`hohLtcg` (Single), `stdDedMfj` / `stdDedSingle` / `stdDedHoH`, `fplFirstPerson`/`fplAddlPerson`, `irmaaTiers`, `seTaxRate` (0.153), `seTaxNetFactor` (0.9235), `acaCliffFplMult` (4.0), `acaMedicaidFloorMult` (1.38), `elective401k` (24500), `totalAddition` (72000), `iraLimit` (7500), `iraCatchup` (1100), `hsaFamily` (8750), `hsaSelfOnly` (4400), `catchup401k` (8000), `catchupHsa` (1000), `superCatchup401k` (11250), the catch-up age bands, and `rmdDivisors`.
- **`ACA_PCT_BANDS`** (the ACA applicable-percentage schedule) is a SEPARATE `const`, not inside `IRS_2026` — it's a table, left where it is but rendered read-only in the Federal tab.

### The "Federal Tax Details" tab is READ-ONLY
Every federal statutory value (brackets, std deduction, FPL, RMD divisors, IRMAA tiers, ACA schedule, SE tax, contribution limits) is displayed as **read-only reference**, sourced from `IRS_2026`. Users cannot edit these; they are never saved in an exported profile (federal law always comes fresh from the app's current tax-year data). The user's *personal* tax settings (state/county rate, SS-exemption choice, heir rates) live in the LEFT input panel and ARE saved with profiles.

## 5. The verification recipe

This is the **most valuable thing to hand off** — it's how every bug this project was caught. For any change:

1. **Work from fresh copies** (`cp /mnt/user-data/outputs/X ./`).
2. **Edit** via `str_replace` or a Python heredoc unique-string replace.
   - ⚠️ **GOTCHA:** Python heredocs write `\\u2013` as a literal double-backslash (breaks JS template literals). Fix with `sed 's/\\\\u2013/\\u2013/g'` or verify the rendered output. En-dashes and `×` (`\u00d7`) are the common victims.
3. **Syntax-check every `<script>`** via `new Function()`:
   ```bash
   node -e "const fs=require('fs');const h=fs.readFileSync('FILE','utf8');let ok=true;[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach((s)=>{try{new Function(s[1]);}catch(e){console.log(e.message);ok=false}});console.log(ok?'OK':'BROKEN')"
   ```
4. **Playwright pageerror check** — load the file headless, confirm no `pageerror`.
5. **Playwright behavior test** — verify the specific change did what you intended.
6. **`harness.js`** — the balance-identity validator. Run `node harness.js FILE`; every scenario must have `maxTradViol ≤ 5` and `maxPwdViol ≤ 5`.
7. **`test-suite.html` over HTTP** — serve `suite_test/` via `python3 -m http.server PORT`, load in Playwright, click `#runBtn`, read `#summary`. **Must be all-green** (currently **146/146** across both apps — Tiers 1–6, including 10 RE/BI tests per app).
8. **Compare default EOL to baseline** ($693,546 MFJ / $607,219 Single).
9. **Get ship permission.** 10. **Copy to outputs.** 11. **`present_files`.** 12. **Update this HANDOFF.** 13. **Re-lock.**

### Verification gotchas learned the hard way
- **Headless Playwright screenshots do NOT render inline for the assistant to see.** Verify visuals via `getComputedStyle` / `textContent` / computed colors instead (e.g. light-theme readable text = `rgb(15, 23, 42)`; muted = `rgb(100, 116, 139)`).
- **localStorage** works in `file://` Playwright AND on real GitHub Pages, but is blocked in the Claude artifacts sandbox only.
- **Playwright can't reach module-scoped vars** (e.g. `childrenProfiles`) via `window` — you must call the real app functions (e.g. `addChildProfile()`) to manipulate state.
- **Track div/section open-vs-close balance** after structural edits (`grep -c '<div' vs '</div>'`).
- **The default scenario does NOT exercise the semi-income / 1099 path** (the default person is "covered"/accumulating during the semi windows). To test semi-income behavior you must construct an active scenario (e.g. both spouses semi at 55, full at 65, born ~52 years ago, with a healthy portfolio so it doesn't deplete to a $0 floor that masks differences).
- **`window.__chartSeries` DOES expose rich per-year detail** — `{year, hAge, wAge, trad, roth, brok, hsa, f529, total, spendableTotal, incomeSS, income1099, assetDist, isSemiRetired, isFullyRetired, isCovered}`. Use this for most verification. Only the *deeper tax internals* (preWithdrawOrdinary, seTax, seDeduction) are NOT exposed — for those you add a temporary debug hook to the `chartSeries.push({...})` call, verify, then remove it. (`window.__scenarioB.series` is the *stripped* version — year + balances only — used for the compare/chart; don't rely on it for tax-detail verification.)

## 6. Known simplifications — do NOT "fix" these

These are **deliberate** modeling choices. A future editor "correcting" them would be reverting an intentional decision:
- **Flat-rate SE/FICA tax** — no Social Security wage-base cap, no 0.9% Additional Medicare tax. Consistent across the 1099 and W-2 paths. (Diminishing returns for a planning sandbox with modest semi-income.)
- **Cash-reserve / bucket strategy is NOT modeled** — decided against (small ~0.2% drag; users approximate via a slightly lower Nominal Return).
- **Phantom-wife cruft in Single** (~35 inert `wAge` refs) — left in place; purging is high-risk for zero functional gain.
- **State/county tax** = flat rates, no deductions/credits (only the optional SS exemption).
- **Early-withdrawal penalty** keyed to the older spouse; no 72(t)/SEPP/Rule-of-55 exceptions.
- **RE/BI (Real Estate / Business Investments):** depreciation recapture is approximated as a % of *invested capital* (capped at the gain) rather than tracked from a real depreciation schedule; the ongoing depreciation shelter is approximated by the user-set "distribution taxable %"; each position uses a single flat appreciation rate; no capital calls, deal-level debt/NOI modeling, K-1 passive-loss carryforwards, 1031 exchanges, or Opportunity-Zone rules; distributions are assumed received as entered (no suspended-distribution years).
- **Not modeled at all:** AMT, NIIT (3.8%), state-specific 529 recapture, tax-loss harvesting, age-curved ACA premiums, advance-credit reconciliation.

## 7. MFJ vs Single — the differences that matter

Where the two forks legitimately diverge:
- **People:** MFJ has H + W (two earners, two of everything). Single has one person; the "W" fields are inert mirrors.
- **Default EOL:** MFJ `$693,546` / Single `$607,219`.
- **Filing status:** Single uses `isHoH()` (= has dependents) to switch between **Single** and **Head-of-Household** brackets + standard deduction ($15,750 Single ↔ $23,625 HoH, switches live when a dependent is added via `addChildProfile()`).
- **IRMAA thresholds:** MFJ tiers start at $218K; Single/HoH start at ~half ($109K).
- **Contribution limits display:** identical grouped 3-column layout, but MFJ shows the household 2× logic in the note (401k/IRA are per-person, so a two-earner MFJ household can contribute 2×; HSA family is a single shared plan, NOT doubled). Single notes one-earner = household amount.
- **HSA:** MFJ Fill-Max uses family ($8,750); Single Fill-Max uses self-only ($4,400) — but both apps *display* both figures as reference, and the contribution input is editable so a HoH with a family HDHP can enter the family figure.
- **Semi-income:** MFJ has H + W income (each with its own 1099/W-2 type dropdown); Single has one earner (`wSemiType` is an inert hidden mirror).
- **Survivor scenario:** MFJ models a survivor/widow phase; in Single it is force-disabled (no spouse to lose).
- **Real Estate / Business Investments: NO divergence.** Unlike semi-income (per-spouse), RE/BI is a *household-level* subsystem — same data model, same engine logic, same UI, same Help text, byte-for-byte. This was verified, not assumed. It's the only major feature with zero fork divergence, which makes it the cleanest one to modify (change both apps identically).

## 8. Current state: done vs. deferred

**Everything is shipped and the apps are feature-complete.** Suite is 146/146. Help docs are audited and accurate.

**Done this project:** single-file carryovers (IRA figures, catch-up funding gate, first-year proration); Federal Tax Details tab made fully read-only from `IRS_2026`; hidden statutory values (IRMAA, ACA schedule, SE tax) exposed as read-only reference; Contribution Limits panel (grouped 3-column, moved to top, per-person/household clarity, cleaner labels, super-catch-up "instead of" fix); W-2 vs 1099 semi-retirement income modeling; full Help-doc sweep + audit; **Real Estate / Business Investments (RE/BI) subsystem** — the largest feature built to date (see the decision log for the full design rationale); two label fixes ("Account Balances (Today's $)", "Roth" not "Roth Core").

**Deferred by choice (good reasons — don't reopen without cause):**
- Phantom-wife cruft purge in Single (cosmetic, risky).
- Cash-reserve bucket strategy (small effect, decided against).

**Genuinely optional (small value, not required):**
- Bake the cross-app import-guard round-trip into the suite as a permanent test (currently verified via Playwright, not in the suite).
- Family-HSA modeling for HoH in the engine (currently handled via the editable input).
- SS wage-base cap + Additional Medicare tax (deliberate simplification).

## 9. How to do the most common tasks

- **Annual tax-law update:** edit the `IRS_2026` block (and `ACA_PCT_BANDS` if the schedule changes) in BOTH apps. The engine + read-only Federal tab update automatically. Re-verify EOL baselines (they WILL change if the tax law changed — that's expected; recompute and record the new baseline).
- **Add/adjust a feature:** follow §5 top to bottom. MFJ first, then Single.
- **Debug the tax spine:** remember `__scenarioB.series` is stripped — temporarily expose `chartSeries` internals, verify, then remove the hook.
- **Check the suite:** `cp` both apps + `test-suite.html` into `suite_test/`, serve over HTTP, run headless, read `#summary`.

---

## 10. Code architecture map

> Documents the major functions and data flow so you don't have to reverse-engineer un-touched subsystems from scratch. **Line numbers are approximate and drift as the code changes — grep by function name, not line.** This maps MFJ (`index.html`); Single mirrors it (see §7 for divergences). This is a *map*, not a line-by-line spec — the code remains ground truth.

### Core data structures (all near the top of the main `<script>`)
- **`IRS_2026`** (`const`) — the single source of federal tax law (see §4). Engine reads from here.
- **`ACA_PCT_BANDS`** (`const`) — ACA applicable-percentage schedule (6 bands). Separate from `IRS_2026`.
- **`inputIds`** (`const`) — the master list of input element IDs. Doubles as (a) the recalc-listener registry and (b) the export/import field set. **Adding an input? It usually needs to go here.**
- **`EXPORT_CHECK_IGNORE`** / **`EXPORT_EXCLUDE`** (Single) — fields intentionally kept out of saved profiles (e.g. federal statutory values).
- **`ordinaryBrackets` / `ltcgBrackets` / `rmdTable`** (`let`) — working copies initialized FROM `IRS_2026` at load; the engine reads these.
- **`childrenProfiles` / giftRows** (`let`) — dependent and gifting schedules (module-scoped; not on `window` — call the real functions to mutate).
- **`rebiDeals`** (`let`, default `[]`) — Real Estate / Business Investment (passive LP) positions. Module-scoped; use the `window.__rebiGet()` / `window.__rebiSet(arr)` accessors from tests. Shape: `{ id, name, capital(basis), currentValue, apprPct, annualDist, distTaxablePct, distCola, refiYear, refiCapital, exitYear, exitValue, recapturePct }`.

### Output/state exposed on `window`
- **`window.IRS_2026`** — the constants (for tests/inspection).
- **`window.__scenarioB`** — the current projection result; `.series` is STRIPPED (year + balances only).
- **`window.__chartSeries`** — the FULL per-year detail (income1099, stage flags, ages — see §5 gotchas).
- **`window.__mcPath`**, **`window.__legacyValue`**, **`window.__depletionAgeLabel`** — Monte Carlo path, legacy KPI, depletion label.
- **`window.__rebiGet()` / `window.__rebiSet(arr)`** — live accessors for the module-scoped `rebiDeals` array (test hooks; harmless in production, same rationale as `__chartSeries`).

### THE ENGINE (the heart)
- **`triggerRecalculate()`** — the core engine. Reads every input, runs the year-by-year loop (ages, phases, contributions, growth, withdrawals, taxes, conversions, RMDs, SS, healthcare), builds `chartSeries`, computes KPIs, and triggers render. **Everything flows from here.** Call it after any programmatic input change.
- **`accountGrowth(startBal, contribs, withdrawals, rate)`** — applies one year of growth to a bucket, honoring the growth-timing convention (simple / half-year "Realistically Conservative").
- **`computeTaxForWithdrawal(withdrawalAmt, tradAvail, rothAvail, brokAvail)`** — given a needed withdrawal, decides the draw ordering across Traditional/Roth/Brokerage and computes the resulting tax. Core of the withdrawal + tax logic.
- **`marginalTax(taxableIncome, brackets)`**, **`topBracketRate(...)`**, **`roomToBracketCap(...)`** — bracket math helpers (used by both the tax calc and the Roth-conversion sizing).

### Tax display (read-only Federal tab) — all render FROM `IRS_2026`
- **`populateFederalDisplays()`** — fills the read-only scalar displays (std deduction, FPL) + calls the sub-renderers below. Called on load.
- **`renderBracketRows()` / `renderLtcgRows()` / `renderRmdDivisorRows()`** — render the read-only bracket/LTCG/RMD tables.
- **`renderIrmaaTierRows()`** — renders the IRMAA reference table.
- **`renderContribLimits()`** — renders the grouped 3-column Contribution Limits panel (401k / IRA / HSA).
- **`acaApplicablePct(...)`** — interpolates the ACA applicable % from `ACA_PCT_BANDS`.
- (`updateBracketFrom` / `updateLtcgFrom` / `updateRmdDivisor` still exist but are ORPHANED — the tables are read-only now; harmless dead code.)

### Contributions & catch-ups
- **`fillMaxContributions()`** — the "Fill Max" button. Sets Traditional/Roth/HSA to household IRS maxima (MFJ doubles 401k/IRA, NOT HSA — see decision log).
- **`updateCatchupTip()`** — live per-spouse catch-up breakdown tooltip.

### Inputs, UI toggles, formatting
- **`populateDropdownSelects()`**, **`initMoneyInputFormatting()`**, **`formatMoneyInput()`**, **`cleanNum()`**, **`currency()`** — input population + money formatting.
- **`toggleColorTheme()`** (light/dark), **`toggleSidebar()`**, **`switchTab()`** (proj/sys), **`toggleColumnGroup()` / `applyColumnGroupVisibility()`** (bucket column show/hide), **`setViewMode()` / `setDollarMode()`** (condensed/full, today's/future $).
- **`toggleDistInputs()` / `toggleSsInputs()` / `toggleSurvivorInputs()` / `toggleRothConvInputs()`** — show/hide conditional input groups.
- **Children/gifts:** `renderChildrenProfiles()`, `addChildProfile()`, `removeChildProfile()`, `updateChildField()`; `renderGiftRows()`, `addGiftRow()`, `removeGiftRow()`, `updateGiftAmt/Year()`. NOTE: `addChildProfile()` is what flips Single into HoH.

### Real Estate / Business Investments (RE/BI)
- **`renderRebiDeals()`** — renders the repeatable deal cards into `#rebiDealRows` (red-X remove, matching the gifts/children pattern).
- **`addRebiDeal()` / `removeRebiDeal(id)` / `updateRebiField(el)`** — list mutation; each calls `renderRebiDeals()` + `triggerRecalculate()`.
- The **engine logic has no dedicated function** — it lives inline in `triggerRecalculate()`'s year loop, in a block right after the `gross1099` payroll block (search for `Real Estate / Business Investments (RE/BI)`). It computes, per year: `rebiDistTotal`, `rebiDistTaxable`, `rebiStartValue`, `rebiEndValue`, `rebiRefiCash`, `rebiExitProceedsGross`, `rebiExitGainLtcg`, `rebiRecaptureTax`. Those feed the tax machinery at seven integration points (see the decision log for the full list).

### Rendering & charts
- **`renderNetWorthChart()`** — draws the main projection chart; **`showChartTooltip()` / `hideChartTooltip()`** (uses `__chartSeries`).
- **`renderCompare()`** — the A/B compare view; **`pinScenarioA()` / `clearScenarioA()` / `swapScenarios()` / `toggleCompareMode()`**.

### Profiles (export/import/reset)
- **`exportConfig()`** — serializes `inputIds` (minus excluded) to a downloadable profile; writes a `__filingStatus` flag.
- **`importConfig()`** — restores a profile; REJECTS mismatched or flag-less profiles (the cross-app import guard).
- **`currentInputsSnapshot()` / `applyInputsSnapshot()`** — snapshot/restore used by solve + compare.
- **`resetToDefaults()`** — restores all inputs to defaults (selects use `data-default-value`).

### Solver ("Solve For")
- **`runSolve()`** dispatches to **`solveMaxSpend()`** (max sustainable spend), **`solveEarliestRetire()`** (earliest retirement age), **`solveRequiredPortfolio()`** (required starting portfolio). Each binary-searches by repeatedly running the projection via **`probePlan()`**. **`showSolveResult()` / `applySolve()` / `undoSolve()`** handle the result UI.

### Monte Carlo
- **`runMonteCarlo()`** → **`mcRunOnce()`** (one path) using **`mcGeneratePath()`** + **`mcStockBondMix()`**; historical block-bootstrap or parametric. **`showMcResult()` / `drawMcFan()` / `drawMcFailRun()`** render the fan chart + success rate.

### Help & misc
- **`openHelp()` / `closeHelp()` / `inlineHelp()`** — the Help modal.
- **`maybeShowHelpCoach()` / `dismissHelpCoach()`** — first-visit Help nudge (localStorage `pzHelpCoachSeen`).
- **`showProfileBanner()`** — the top-center banner (import success/error).
- **`positionInfoTip()`** — positions the ⓘ tooltips.

### Data flow in one line
`inputs → triggerRecalculate() → [year loop: phase → contributions/accountGrowth → RE/BI distributions+capital events → withdrawals/computeTaxForWithdrawal → conversions → RMDs → SS → healthcare(ACA/IRMAA)] → chartSeries → KPIs + renderNetWorthChart() + renderCompare()`. Solver and Monte Carlo wrap this by running the projection many times with varied inputs/returns.

---
---

# PART 2 — DECISION LOG

> The full chronological "why" behind every change. Part 1 above is the orientation; this is the reference detail. When Part 1 says "see the decision log," it means here.

<!-- The entries below are preserved verbatim from the project's running decision record (formerly FUTURE_ITEMS.md). Newest context is generally toward the bottom. -->

## Single-file carryovers — COMPLETED (shipped)
All three were ported to p-zero-single.html and verified:
1. ~~Stale IRA figure~~ — DONE: iraLimit now $7,500 + iraCatchup $1,100.
2. ~~Catch-up funding bug~~ — DONE: catch-ups now gated on a funded base (tradRothFunded); no phantom catch-up on $0 accounts.
3. ~~First-year contribution proration~~ — DONE: proration + dynamic start-year (new Date().getFullYear()) ported, with in-table marker.
Also completed this session in single: tax-tab rename to "Federal Tax Details" + state/local moved to left panel + federal tables/stdDeduction/FPL excluded from profiles (EXPORT_EXCLUDE); "All Buckets" table toggle; import guard + banners + Help coach-mark; full Help audit/persona rewrite; $90K default re-tune.

## Cash-reserve / bucket strategy (considered, decided Tier 1 — note only)
Idea: retirees often hold N years (3-5) of expenses (living target + healthcare) in a low-yield
cash/HYSA/Treasuries reserve earning ~4% while the rest of the portfolio earns the ~6% growth rate,
lowering the blended return.
Decision: NOT building the mechanic. Magnitude is small (in a $5M/$558K-reserve example the drag is
~0.2% of blended return, and it shrinks as the portfolio grows and the reserve becomes a smaller
share). It would also interact with the half-year growth convention and raise a "which bucket holds
the cash / how is the interest taxed" question that a blended-rate approximation can't answer faithfully.
Workaround: users can approximate by entering a slightly lower Nominal Return.
If revisited: Tier 2 = optional "cash reserve: N years at X%" input modeled as a return drag (no separate
tax tracking); Tier 3 = full physical cash bucket with its own tax treatment (big build, low ROI).
Documented for users in Help §19 and nudged in the Nominal Return tooltip.

## Phantom-wife cruft in single file (deferred — cosmetic, low priority)
p-zero-single.html is a fork of MFJ; the second person was neutralized by mirroring
(wBirthYear = hBirthYear) rather than removed. ~35 wAge/wBirthYear references remain across
catch-up, Roth-auto-year, survivor, and KPI code. All are harmless: wAge === hAge always, and
the survivor code that uses them is inert (survivorOn hardcoded false, line ~1644). A full purge
touches 35 sites with real regression risk for zero functional benefit, so it's deferred. The one
catch-up line that was being edited anyway was cleaned to a single-person calc. Survivor scenario
confirmed force-disabled by design (single person has no spouse to lose).

## MFJ: standard-deduction & FPL fields recalc when edited — FIXED (shipped)
RESOLVED: added recalc listeners (input+change) to stdDeduction/fplFirstPerson/fplAddlPerson,
kept OUT of inputIds so they remain export-excluded (federal law still comes from IRS_2026, never a
profile). Verified: stdDeduction edits live-recalc; FPL edits fire the listener and move the projection
when ACA is on (FPL only affects ACA-subsidy math, so no effect with ACA off is correct). Default EOL
unchanged ($693,546); suite 122/122; harness ALL OK. MFJ and single now behave identically here.
CORRECTION/REFINEMENT (verified): the quirk is NARROWER than first logged. The editable bracket/LTCG
tables DO recalc — on blur/commit (their inputs have onchange->triggerRecalculate). The truly-affected
fields are only the three SCALAR federal inputs — stdDeduction, fplFirstPerson, fplAddlPerson — which
have NO recalc handler at all (not on keystroke, not on blur), because they're absent from inputIds
(the recalc-listener list) and have no inline handler. Editing them leaves the projection stale until
another input changes. Single was fixed this session (kept in inputIds + EXPORT_EXCLUDE). Low urgency
(users rarely edit federal statutory scalars). Fix for MFJ: add a change-listener to those three fields
(or add them to inputIds while keeping them in EXPORT_CHECK_IGNORE). Requires unlocking index.html.
[SUPERSEDED: these fields were later made fully read-only, so the recalc question is moot — see below.]

## Federal Tax Details tab made READ-ONLY — DONE (shipped, both apps)
All federal statutory fields are now read-only displays sourced from IRS_2026: standard deduction,
FPL, ordinary brackets, LTCG brackets, RMD divisors. IRMAA tiers newly EXPOSED as a read-only
reference table (MFJ thresholds start $218K; single/HoH start $109K) — previously hidden in constants.
Engine reads these from IRS_2026 directly (not the DOM), so the annual update is a single code edit in
the IRS_2026 block. Single's std-deduction display is filing-status-aware ($15,750 Single / $23,625 HoH,
switches when dependents added). Still excluded from exported profiles. Help docs updated ("read-only
reference" not "editable"). Supersedes the earlier "MFJ recalc quirk fix" — those fields are no longer
editable at all, so the recalc-listener question is moot. Verified: EOLs unchanged (MFJ $693,546, single
$607,219), suite 122/122 (one stale test that assumed stdDeduction was an editable input was updated).
NOTE: annual maintenance = edit the IRS_2026 block only (brackets, std deduction, FPL, RMD divisors,
IRMAA tiers). The UI reflects changes automatically.

## Hidden statutory values EXPOSED + Federal tab readability — DONE (shipped, both apps)
Audit found statutory values the engine used but didn't show (the "hidden like IRMAA" pattern), all
ACA/SE-tax related. Now exposed as read-only reference in the Federal Tax Details tab (both apps):
- ACA applicable-% schedule (ACA_PCT_BANDS): 6-band table 2.10%->9.96% of MAGI by FPL ratio.
- ACA subsidy bounds: cliff 400% FPL, Medicaid floor 138% FPL.
- Self-employment tax: 15.3% on 92.35% net-earnings factor.
SE tax + cliff/floor were inline magic numbers; moved into IRS_2026 (seTaxRate, seTaxNetFactor,
acaCliffFplMult, acaMedicaidFloorMult) so annual maintenance stays one-block. Also fixed two visual
bugs in the read-only Federal tab: (1) values were hardcoded text-slate-200 / text-white (washed out or
invisible in light theme) -> now theme-aware var(--text-primary); (2) stdDeduction/FPL kept mini-input
class (input-box look) -> removed for uniform read-only display. EOLs unchanged (MFJ $693,546, single
$607,219); suite 122/122; harness OK. Federal tab is now a COMPLETE reference — no remaining hidden
statutory values in the tax engine (audit confirmed no other stray magic numbers).
Contribution limits (401k/IRA/HSA + catch-ups) remain visible via "Fill Max" — intentionally not
duplicated into the Federal tab. [Later reversed: a dedicated Contribution Limits panel WAS added — see below.]

## Contribution Limits panel added to Federal tab — DONE (shipped, both apps)
Read-only "Contribution Limits (2026)" panel added to the Federal Tax Details tab in both apps,
populated from IRS_2026: 401(k) elective $24,500, overall 401(k) $72,000, IRA $7,500 + catch-ups,
401(k) catch-up $8,000 + super catch-up $11,250 (ages 60-63), HSA + catch-up, all age bands from
constants. HSA shows BOTH figures (family $8,750 + self-only $4,400) in both apps as IRS reference —
added hsaSelfOnly to MFJ and hsaFamily to single so each maintains both. Rationale (per user): the HSA
contribution is an editable input; Fill Max just suggests self-only ($4,400) for single, but a single
parent with a family HDHP can enter $8,750 themselves — so documenting both is transparent without any
engine change. Pure display addition; EOLs unchanged (MFJ $693,546, single $607,219); suite 122/122.
NOTE (possible future item): the engine/Fill Max always uses self-only HSA for single; could add
family-HDHP detection for HoH filers, but deliberately deferred (kid could be on other parent's plan;
user retains full control via the editable input).

## Contribution Limits panel — moved to top, full-width, per-person/household columns (shipped, both apps)
Refinements to the Contribution Limits panel: (1) moved to the FIRST/top position in the Federal Tax
Details tab (before brackets) — most actionable federal reference for active planners; (2) MFJ now shows
TWO columns, Per person + Household (2x), since 401k/IRA/catch-ups are individual limits — e.g. 401k
$24,500/person -> $49,000 household, IRA $7,500 -> $15,000. HSA family ($8,750) correctly NOT doubled
(single shared plan, shown "—"). Matches Fill Max behavior (doubles 401k/IRA, not HSA). (3) Single/HoH
keeps per-person figures with a note clarifying one earner = household amount (not doubled). EOLs
unchanged; suite 122/122. [Layout later reworked into grouped 3-column — see below.]

## Federal tab layout cleanup — grouped contribution limits + panel reorder (shipped, both apps)
Fixed layout messiness the user flagged (screenshots): (1) the two apps had DIVERGED (MFJ 1-col value
layout vs single 3-col) — now IDENTICAL. (2) Contribution Limits reorganized into 3 columns grouped by
account type: 401(k) [employee / total / catch-up / super catch-up], IRA [base / catch-up], HSA
[self-only / family / catch-up]. Cleaner labels (dropped redundant account prefix per row since the
column header carries it). Per-person values; MFJ explains 2x household in the note only, single notes
one-earner. (3) Panel order fixed via 6-col grid: Contribution Limits (full-width top) -> row 2:
Ordinary Brackets, LTCG, RMD divisors (span-2 each) -> row 3: ACA, IRMAA (span-3 each). IRMAA moved to
after ACA. EOLs unchanged (MFJ $693,546, single $607,219); suite 122/122; both apps at layout parity.

## Contribution Limits label polish + correctness clarity (shipped, both apps)
- Header: "401(k)" -> "401(k) / 457(b) / 403(b)". Note now mentions self-employed Solo 401(k) follows
  similar limits.
- Consistent parenthetical convention: "Trad or Roth (Employee)", "Total (Employee + Employer)",
  "Catch-up (age 50+)", "Super Catch-up (ages 60-63)", "Trad or Roth", "Self-Only", "Family".
- IMPORTANT correctness clarity: Super Catch-up (ages 60-63) now displays "+$11,250 (instead of the
  +$8,000)" — the SECURE 2.0 super catch-up REPLACES the regular 50+ catch-up, it does NOT stack. The
  engine already modeled this correctly (ternary at ~line 1661: 60-63 ? superCatchup : catchup); this was
  purely a display-clarity fix so users don't read the two catch-up rows as additive ($19,250 wrong).
- Confirmed (no change needed): HSA +$1,000 catch-up (55+) applies to BOTH self-only and family (added
  on top of whichever base); engine adds it regardless of coverage type.
- "Super Catch-up" capital C for consistency with "Catch-up" rows.

## W-2 vs 1099 semi-retirement income — BUILT (Option C "correct-ish", shipped, both apps)
Relabeled "H/W Semi Income (1099)" -> "H/W Semi-Ret Income" (single: "Semi-Ret Income"); dropped the
misleading "1099" (semi income can be W-2 part-time). Added a per-person income-type dropdown
(hSemiType / wSemiType, default 1099). Engine now models both:
  - 1099 (self-employed): 15.3% SE tax on 92.35% of gross; gets the 1/2-SE income-tax deduction. (unchanged)
  - W-2 (employee): 7.65% employee FICA on gross; NO 1/2 deduction (W-2 wages fully taxable -> higher MAGI).
H and W may elect different types (MFJ). Single has one earner; wSemiType is an inert hidden mirror.
Implementation: payrollFor(grossNominal, type) helper returns {tax, halfDeduction} per person, summed into
seTax (total payroll) + seDeduction (total 1/2-deduction); seDeductionFinal now = seDeduction (was seTax/2).
Hand-verified target ($50k gross): 1099 net=$42,935 (gross - $7,064.77 SE), W-2 net=$46,175 (gross - $3,825
FICA); W-2 taxable base higher by exactly the 1/2-deduction ($4,609) -> confirmed both payroll AND deduction
mechanics. Scope matches existing flat-rate model (NO SS wage-base cap, NO Additional Medicare tax -
consistent with the pre-existing 1099 simplification, confirmed during read-only investigation). Type
selects added to inputIds (export/import/reset via data-default-value="1099"); round-trip verified. Default
EOLs UNCHANGED (MFJ $693,546, single $607,219 - 1099 default path preserved exactly). Suite now 126/126
(added 2 W-2 behavioral tests per app: W-2 EOL >= 1099 EOL, and toggle changes projection). Verification
used a temporary __debugFull/__seTax/__seDeduction hook on chartSeries (since __scenarioB.series is stripped
to year+balances) - hooks REMOVED before ship. NOTE (possible future refinement): add SS wage-base cap +
0.9% Additional Medicare for high earners; deferred as diminishing returns for a planning sandbox.

## Help-doc sweep for W-2/1099 + full Help audit (shipped, both apps)
Comprehensive sweep of both apps' Help docs after the W-2/1099 feature made the semi-income
descriptions stale (they described "1099 consulting income (subject to SE tax)" as the only option).
MFJ: ~13 references updated (phase descriptions, KPI glossary, tax-base/MAGI defs, examples, survivor).
Single: ~16 references updated (same structure). Preserved genuinely-1099-specific references (SE-tax
glossary "15.3% on 92.35%"; the 1/2-SE-deduction explanations now explicitly say "applies to 1099 only —
W-2 wages fully taxable"). Generic phase/example text -> "semi-retirement income".
Then a FULL Help-doc audit of both apps (every section vs current code) caught one additional real bug:
Single's state/local tax Help still said rates were "editable in the Tax & Other Details tab" — but that
tab was renamed to "Federal Tax Details" AND the state/local rates were moved to the left input panel.
Fixed to match MFJ ("in the State & Local Tax section of the left input panel"). Confirmed zero remaining
stale "Tax & Other Details" references and no stale "editable" federal-field language in either app.
EOLs unchanged; suite 126/126.

## Handoff documentation — this file
Merged the running decision log (formerly FUTURE_ITEMS.md) with a new orientation layer (Part 1 above)
into this single HANDOFF.md, per the author's preference for one file. Part 1 = operational onboarding
(architecture, lock discipline, engine model, verification recipe, known simplifications, MFJ-vs-Single
differences, current state). Part 2 = this decision log, preserved verbatim. FUTURE_ITEMS.md is retired
(folded in here). Written LLM-first (precise/operational) but human-readable.

## Code-architecture map added to HANDOFF (§10)
Added a full function-and-data-flow map (§10) documenting ~100 engine functions grouped by subsystem
(engine core, tax display, contributions, UI, rendering, profiles, solver, Monte Carlo, help) plus the
one-line data flow and the key global data structures. Built by reading the actual source, not from
memory — which caught an inaccuracy in an earlier handoff claim: window.__chartSeries IS exposed and
contains the rich per-year detail (income1099, stage flags, ages), so the "you must add a debug hook"
guidance was only half-right — the hook is needed ONLY for the deeper tax internals (preWithdrawOrdinary,
seTax, seDeduction), not for income1099/stage flags. The §5 gotcha and §10 both now state this correctly.
Line numbers in the map are marked approximate (grep by function name). This closes the "read the code
to understand un-touched subsystems" gap the author flagged.

## Real Estate / Business Investments (RE/BI) — the largest feature built to date (shipped, both apps)

### WHY — the user's actual situation and reasoning
The author asked how to model "other types of accounts/assets: real estate investments? annuities?" The first design pass assumed **direct property ownership** and got as far as debating mortgages, primary-residence exclusions, and depreciation schedules — then the author corrected a wrong premise: *"This person doesn't invest into any physical real estate directly. Instead they are invested as Limited Partner (LP) in commercial/multi-family real estate (i.e. apartments, storage units, etc.). You get quarterly distributions, payout on refinance or sale, etc."*

That correction **collapsed most of the complexity** and is the key to understanding the design:
- No mortgage modeling needed — deal-level debt is internal; the LP only sees net distributions.
- No primary-residence question — it's purely an investment.
- Depreciation shows up as *reduced taxable distributions* (via K-1), not a schedule to track.
- The whole thing reduces to: an income stream + capital events (refi, exit) on an illiquid asset.

The author wanted **both** the income *and* the asset value modeled (not just one). Naming evolved: "LP Investments" → too real-estate-coded → the author chose **"Real Estate / Business Investments"** because the same structure covers non-managing-partner stakes in *operating businesses*, not just RE syndications.

### WHAT — the feature
A repeatable list of passive LP / syndication / private-deal positions (`rebiDeals`, default `[]` so the baselines are untouched). Per deal: invested capital (basis), current value, appreciation %/yr, annual distribution + taxable %, distribution COLA, optional refi year/capital, exit year/value, recapture %. While held: distributions flow to income (taxed on the taxable %) and value appreciates. Refi returns capital tax-free (reduces basis). Exit pays proceeds with a three-way tax split. Held at death → step-up → 100% into legacy. Surfaced via a toggleable table column-group, a two-tier Net Worth KPI, and a dedicated illiquid tile.

### HOW — the design decisions and their rationale
- **[DECISION] Recapture = % of INVESTED CAPITAL, capped at the gain (Interpretation A), taxed at 25%.** The author asked "which is most accurate and/or conservative?" — the honest answer is they point the *same* direction: recapture is a real tax the simple view omits, so including it shows *more* tax and *lower* net proceeds (conservative) *and* is more accurate. Chosen over "% of the gain" because depreciation accrues on the property basis, not on how much the deal appreciated; Interpretation A also handles the edge case where a deal barely appreciates but was still depreciated. Cap at the gain because you can't recapture more than you made.
- **[DECISION] Ongoing depreciation shelter ≈ "distribution taxable %"** (default 25%). Captures the K-1 reality (distributions largely sheltered during the hold) *without* modeling depreciation schedules. One input, honest approximation.
- **[DECISION] Exit gains flow through the SAME LTCG + MAGI machinery as brokerage gains.** The author explicitly asked whether RE/BI profits/distros factor into overall taxes *and* Roth-conversion bracket-filling. The verified answer: **distributions' taxable portion goes into `preWithdrawOrdinary`, which is what the bracket-fill conversion sits on top of — so they consume conversion headroom automatically** (this was already true from the moment Stage 1 landed). **Exit gains are capital gains** — they don't consume *ordinary* bracket room, but they DO raise MAGI, so they were wired into `magiExConv` (the ACA preserve-subsidy conversion cap), `acaMagi`, `irmaaMagi`, and `preferentialGains` (LTCG tax). Net effect: a big exit year correctly risks the ACA cliff / an IRMAA tier exactly like a large conversion would.
- **[DECISION] Two-tier Net Worth KPI (the author's design, better than the assistant's proposal).** The assistant proposed a "hybrid" (include RE/BI in End Net Worth + a separate tile). The author instead proposed: **primary large number = LIQUID net worth; smaller secondary line = total incl. RE/Business; plus a dedicated RE/BI tile.** This is better because it solves the liquid-vs-illiquid conflation *at the point of display* — the big number stays the honest "can I actually spend this" figure, so a large illiquid holding can never make a thin spendable portfolio look safe. The assistant flagged one risk (labeling liquid-only as "Net Worth" is non-standard) → resolved by relabeling to **"Liquid Net Worth at EOL"**. Both the total line and the tile are **hidden when there are no deals** (no clutter for users without private investments).
- **[DECISION] Illiquid = never drawn on.** RE/BI sits *outside* the withdrawal sequence entirely — it can't fund a shortfall. Distributions/proceeds instead *reduce* the withdrawal the sequence must produce; sale proceeds land in Brokerage and join the liquid pool from that year on.
- **[DECISION] Excess capital proceeds are reinvested to Brokerage as after-tax basis.** Without this a big exit lump would partly *vanish* (the engine's `elecWithdrawal` floors at 0 and excess cash isn't otherwise banked). Adding to `brokBasis` prevents it being re-taxed as gain later.
- **[DECISION] Step-up at death → legacy at 100%**, same treatment as brokerage (the step-up erases the built-in gain for heirs).
- **[DECISION] Red-X remove button** (`fa-xmark`, `text-red-400`) matching the gifts/children pattern — the author caught that the mockup used a text "remove" link.
- **[DECISION] Table column-group** (`grpRebi`, purple): Start Value / Distributions / Refi / Sale-Exit / End Value. The author asked whether a 6th toggle button would break the layout — verified it wouldn't: the button row is `flex-wrap` and wraps cleanly.

### Engine integration points (seven, all in `triggerRecalculate()`)
The RE/BI block sits right after the `gross1099` payroll block. Its outputs wire in at:
1. `cashSources += rebiDistTotal + rebiRefiCash + rebiExitProceedsGross` (reduces withdrawal need)
2. `preWithdrawOrdinary += rebiDistTaxable` (ordinary income → brackets, state/local, **and conversion headroom**)
3. `magiExConv += rebiExitGainLtcg` (ACA preserve-subsidy conversion cap)
4. `acaMagi += rebiExitGainLtcg` 5. `irmaaMagi += rebiExitGainLtcg`
6. `preferentialGains += rebiExitGainLtcg` (LTCG tax)
7. `totalTax += rebiRecaptureTax` (25% recapture)
Plus: excess-proceeds reinvestment to `brok`/`brokBasis` after the solver; five permanent `chartSeries` fields; `L.rebiEndValue` in the legacy calc.

### HOW IT WAS BUILT — staged, hand-verified
Six stages, each fully verified before the next, with the zero-deal baselines re-checked every time:
- **Stage 0** — scaffolding (data model, input UI, add/remove/render, profile export/import/reset) + two bundled label fixes. Baseline held; the structure was inert until Stage 1.
- **Stage 1** — hold, distributions, appreciation. Hand-verified: $10k flat distribution → cashSources; 25% taxable → $2,500 ordinary; $100k @3% → $103,000; COLA yr5 → $11,593 (=10k×1.03⁵).
- **Stage 2** — refi + exit. Hand-verified against independent arithmetic: refi $30k → basis $100k→$70k; exit $180k → gain $110k; recapture 20%×$100k=$20k @25% = **$5,000**; LTCG portion **$90,000**.
- **Stage 3** — step-up legacy + permanent chartSeries fields. Verified legacy rises by exactly the final RE/BI value.
- **Stage 4** — table column-group (verified toggle + real cell values).
- **Stage 5** — two-tier KPI + tile (verified liquid + RE/BI = total, and hidden-when-empty).
- **Then**: permanent Tier 6 suite tests → **Single replication** → Help docs → this entry.

**Methodology note (reusable):** deep tax internals aren't exposed, so each stage used a **temporary debug hook** on the `chartSeries.push({...})` call to verify raw values, then **removed it before moving on** (`grep -c '__rebi'` = 0 confirms). The five *permanent* `rebi*` chartSeries fields are the ones the table/KPIs/legacy legitimately need.

### Tests-as-spec (worked well — repeat this)
The permanent **Tier 6** suite tests (10 per app, `tier6(win, fileKey)` in `test-suite.html`) were written **before** the Single replication, deliberately. They then served as the *specification* for the port: replicate → run suite → Tier 6 tells you instantly whether Single matches MFJ. Tier 6 **skips cleanly (returns no tests, not a failure)** if `addRebiDeal`/`__rebiGet` are absent, so it auto-activated on Single the moment the feature landed. Suite went 126 → **146**.
- **Gotcha found:** Tier 6's exact-value checks initially failed (COLA $10,000 vs $11,593; refi $28,278 vs $30,000) — **a test-harness bug, not an app bug**: the suite runs in the default "today's $" mode, whose `dispScale = 1/infScale` deflates nominal values. Fixed by `win.setDollarMode('future')` for the tier, restored in `finally`.
- **Accessors added:** `rebiDeals` is module-scoped so `win.rebiDeals` is `undefined` from the suite's iframe. Added `window.__rebiGet()` / `window.__rebiSet(arr)` (harmless in production; same rationale as `__chartSeries`).

### MFJ vs Single — zero divergence (verified, not assumed)
RE/BI is **household-level**, not per-spouse (unlike semi-income). The data model, engine block, UI, KPIs, and Help text are **identical** in both apps — the only app-specific facts remain the different baselines. This makes RE/BI the cleanest feature to modify: change both apps identically. The Single port was done by extracting the exact MFJ blocks verbatim and inserting at verified anchors, then confirming with Tier 6.

### Help docs — and an honest lesson
New **§15b "Real Estate / Business Investments"** in both apps (what it is, every input, money flow, the three-way exit tax split, two-tier net worth, step-up, simplifications), plus a TOC entry, 6 new glossary terms (LP, Distribution (RE/BI), Depreciation Recapture, Return of Capital, Step-Up in Basis, Illiquid), the KPI rows, the detail-columns entry, and a limitations entry. It also **fixed a dangling link**: the input tooltips referenced `openHelp('sec-rebi')` before any such section existed.

**The lesson worth carrying forward:** the assistant initially believed the Help docs were "done" after adding §15b. The author pushed — *"is all of the help docs and test-suite fully updated for both apps?"* — and an actual audit found **9 sections with real gaps** (sec-tax never mentioned RE/BI distributions or recapture; sec-roth never mentioned that distributions consume conversion headroom; sec-healthcare never mentioned exit gains raising MAGI; sec-inputs omitted the inputs entirely; plus overview, lifecycle, withdrawal, profiles, assumptions). All now covered: **13/13 relevant sections in both apps**, zero dangling links. *Adding a feature's own doc section ≠ documenting the feature.* Audit the sections the feature *participates in*, not just the one that describes it.

### Final verified state
Suite **146/146** (block-mfj 72/72 with 10/10 RE/BI; block-single 74/74 with 10/10 RE/BI). Baselines held: MFJ **$693,546**, Single **$607,219**. Harness ALL OK both. Syntax OK; div/section/table balanced; zero duplicate IDs; zero page errors. End-to-end smoke test on both apps: full lifecycle (distributions → refi → exit → post-exit value zeroes), columns toggle, tile visibility, profile export/restore/reset round-trip, reset returns exactly to baseline.
