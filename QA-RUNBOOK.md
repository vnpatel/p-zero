# QA-RUNBOOK — how to actually run the P-ZERO QA validation

This is the **procedure**. It tells you how to execute the QA scenarios and validate the engine
**without fooling yourself**. Read this before touching anything.

The three companion files:
- **`QA-SCENARIOS.md`** — the scenario definitions and the FROZEN benchmark outputs (the "answer key").
- **`qa_independent_model.py`** — the independent oracle: a from-scratch model that computes what
  each scenario's outputs SHOULD be, blind to the engine.
- **this file** — how to run them together.

---

## The core idea: a THREE-WAY check

For every scenario there are three numbers for each metric (EOL, lifetime tax, legacy):

| Symbol | Source | How you get it |
|---|---|---|
| **A** | Frozen benchmark | Read from `QA-SCENARIOS.md` (never recomputed) |
| **B** | Engine output | Run the app with the scenario inputs (steps below) |
| **C** | Independent model | Run `python3 qa_independent_model.py` |

**Validation passes only when `A == B == C`** (within tolerance: $100, since a 40-year compounding
projection carries ~$20-50 of floating-point rounding).

Why three and not two? Because comparing the engine only to a benchmark that was *captured from the
engine* proves nothing — if the engine was wrong, the benchmark is wrong too, and they'll always
agree. The independent model **C** is a second, engine-blind witness. The benchmark **A** is the
frozen anchor. This is what makes the QA non-circular.

### What each disagreement means
- **B ≠ A** (engine drifted from benchmark): the engine changed or broke. This is the primary
  regression signal. Investigate what code change moved it.
- **C ≠ A** (model drifted from benchmark): someone edited the model, an assumption changed, or an
  authoritative constant went stale. Investigate the model/constants, not the engine.
- **A == B but both ≠ C**: either a real engine bug that the model correctly does NOT reproduce, OR
  the model is missing/mis-implementing an assumption. Investigate which — this is the case that
  catches genuine correctness bugs.
- **All three agree**: pass.

---

## ⛔ ANTI-CIRCULARITY RULES (do not skip)

1. **Benchmarks (A) are FROZEN.** A mismatch is a *finding to investigate*, never a number to edit.
   Do NOT "make the test pass" by overwriting the benchmark. The only time a benchmark changes is
   when you *deliberately* redefine the scenario (and then you re-validate A==B==C from scratch and
   update `QA-SCENARIOS.md` with a changelog note).

2. **Do not derive B from the engine's own logic.** Reading the engine's code to learn *what inputs
   and assumptions it uses* is fine and necessary. Reading it to *copy its output* and calling that
   "validated" is the trap. B must come from actually RUNNING the app.

3. **Compute C independently.** `qa_independent_model.py` must not import from, scrape, or read the
   engine. It computes from raw inputs + authoritative constants + documented assumptions only.

4. **Validation is comparing against frozen benchmarks — not adding/subtracting rows to make totals
   tie.** A "reconciliation" that always balances because both sides come from the same source is
   worthless. The benchmark is external to both the engine run and the model run.

5. **If you find a real discrepancy, STOP and report it.** Do not change the engine to fix it
   without explicit developer sign-off. Engine changes are never made silently.

---

## Running the INDEPENDENT MODEL (C) — the easy part

```bash
python3 qa_independent_model.py          # all scenarios, prints C vs A (benchmark)
python3 qa_independent_model.py s3        # a single scenario
```
This gives you **C vs A** directly. If any row says FAIL, the model or a constant has drifted from
the benchmark — investigate before trusting anything else.

---

## Running the ENGINE (B) — the harder part

The app is a single HTML file with an embedded JS engine. It cannot be driven from `file://` (it
needs to be served), and it uses `confirm()` dialogs that must be auto-accepted.

### Environment
- The apps: `index.html` (MFJ) and `p-zero-single.html` (Single).
- Serve locally, then drive with Playwright (headless Chromium).

```bash
# from the directory containing the app files:
(python3 -m http.server 8199 >/dev/null 2>&1 &)      # serve
# ... run the Playwright capture script (below) ...
pkill -f "http.server 8199"                           # stop when done
```

### Capture pattern (Playwright, Node)
```js
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newContext().then(c => c.newPage());
  p.on('dialog', d => d.accept());                    // REQUIRED: auto-accept confirm()s
  await p.goto('http://localhost:8199/index.html');
  await p.waitForTimeout(2800);                        // let the app initialize
  const out = await p.evaluate(() => {
    // 1) apply the CLEARING RECIPE (see below)
    // 2) set the scenario inputs (field-ID map below)
    // 3) apply the scenario's lever(s)
    triggerRecalculate();
    const B = window.__scenarioB;
    return { eol: Math.round(B.eolNetWorth||0),
             tax: Math.round(B.lifetimeTax||0),
             legacy: Math.round(B.legacyValue||0),
             dep: B.runwayDepletedYear };
  });
  console.log(JSON.stringify(out));
  await b.close();
})();
```
Then compare the printed EOL/tax/legacy to the benchmark **A** in `QA-SCENARIOS.md`.

### ⚠️ The CLEARING RECIPE (MANDATORY for MFJ)
`index.html` ships with **two default children** (born 2012 & 2015) plus **gifting ON** and
**education ON**. If you don't clear them, the engine correctly injects ~$1.7M of phantom gifts and
~$700K of 529 shortfalls into a scenario that's supposed to be childless. Clear them FIRST:

```js
// remove default children — MUTATE THE ARRAY IN PLACE (do NOT reassign; the engine holds a
// reference, so `childrenProfiles = []` leaves the engine looking at stale defaults):
childrenProfiles.length = 0; renderAllChildren();
// gifting OFF: set the checkbox false FIRST, then call the toggle (the toggle SYNCS the flag
// FROM the checkbox — calling it while checked=true turns gifting ON):
const gt = document.getElementById('giftingToggle'); if (gt) gt.checked = false;
if (typeof giftingEnabled !== 'undefined') giftingEnabled = false;
if (typeof toggleGifting === 'function') toggleGifting();
// education OFF (same pattern):
const et = document.getElementById('educationToggle'); if (et) et.checked = false;
if (typeof educationEnabled !== 'undefined') educationEnabled = false;
if (typeof toggleEducation === 'function') toggleEducation();
// belt-and-suspenders: clear the gift/recipient driver objects:
if (window.childGiftingProfile) window.childGiftingProfile = {};
if (window.giftingRecipients)   window.giftingRecipients   = {};
// clear RE/BI and inheritance via the intended test accessors:
window.__rebiSet([]); window.__inheritanceSet([], false);
```
Scenarios that ADD a child (S2) push exactly one child AFTER clearing, again mutating in place:
```js
childrenProfiles.length = 0;
childrenProfiles.push({ id:1, birthYear:2018, undergradCost:30500, undergradYears:4,
                        gradEnabled:false, gradCost:50000, gradYears:2 });
renderAllChildren();
// then turn education ON for the tuition to actually be charged.
```

### Field-ID map (setting inputs)
Use `setDollarMode('nominal')` first (all benchmarks are nominal $). Helper:
```js
const setV = (id,v) => { const e=document.getElementById(id); if(e){ e.value=String(v);
  e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); } };
const setChk = (id,on) => { const e=document.getElementById(id); if(e && e.checked!==on) e.click(); };
```
| Input | Field ID |
|---|---|
| Ages (birth year = currentYear − age) | `hBirthYear`, `wBirthYear` |
| Retirement ages | `hSemiAge`, `wSemiAge`, `hFullAge`, `wFullAge` |
| Balances | `poolTrad`, `poolRoth`, `poolBrok`, `poolHsa`, `pool529` |
| Contributions | `contTrad`, `contRoth`, `contBrok`, `contHsa`, `cont529` |
| Return / inflation | `roiNominal`, `inflationRate` |
| Spending | `distModel` ('fixed'/'pct'), `netDistribution`, `healthcareCost`, `medicareCost` |
| Social Security | `ssToggle`, `hSsAge`, `wSsAge`, `hSsAmount`, `wSsAmount`, `ssCola`, `ssTaxablePct` |
| Roth conversions | `rothConvToggle`, `rothConvStartAge`, `rothConvMethod`, `rothConvFixedAmt`, `rothConvBracketCap` |
| IRMAA | `irmaaToggle` |
| ACA | `acaToggle`, `acaBenchmarkPremium`, `acaHouseholdSize`, `acaPreserveSubsidy` |
| Tax/heir | `stateRate`, `countyRate`, `stateExemptsSS`, `heirTaxRate`, `heirHsaTaxRate` |
| Brokerage | `brokBasisPct`, `brokDivYield`, `brokDivQualifiedPct` |
| RE/BI (via accessor) | `window.__rebiSet([{...}])`, `window.__rebiGet()` |
| Inheritance (via accessor) | `window.__inheritanceSet([{...}], true)` |

### Reading engine output
- Headline results: `window.__scenarioB` → `{eolNetWorth, lifetimeTax, legacyValue, runwayDepletedYear, rebiEndValue}`.
- Per-year detail: `window.__chartSeries` (array of yearly rows: `trad, roth, brok, hsa, audSolvedTax,
  audForcedRmd, audRothConv, audTaxableOrd, audPrefGains, incomeSS, audInheritanceGross, rebiDist, ...`).
- Sanity: after any engine change, confirm the app still loads with **0 page errors** and the
  `test-suite.html` still passes (see below).

---

## The automated test-suite (`test-suite.html`)

Separate from the scenarios: ~666 fast invariant/known-answer tests. Run it after ANY engine change.
```js
// serve, then:
await p.goto('http://localhost:8199/test-suite.html');
await p.waitForTimeout(4000);
await p.evaluate(() => runAll());
await p.waitForTimeout(16000);
// parse "Total: N  Pass: N  Fail: N" from document.body.innerText
```
Green = engine's internal invariants and known-answer constants hold. This complements the
scenarios (which check whole-projection outputs). Both must pass.

---

## Full QA procedure (checklist)

When you change the engine, or on a schedule:

1. **Model vs benchmark (C vs A):** `python3 qa_independent_model.py` → all rows OK.
   (If not, a constant or the model drifted — fix that first; the model must be trustworthy.)
2. **Test-suite:** run `test-suite.html` → 666/666 green, 0 page errors.
3. **Engine vs benchmark (B vs A):** for each scenario, run the app with its inputs (clearing recipe
   + field map + lever), read `__scenarioB`, compare EOL/tax/legacy to `QA-SCENARIOS.md`.
   - Within $100 → pass.
   - Drift → **investigate the code change**; do not touch the benchmark.
4. **If B and C disagree with each other** (even where one matches A): a real correctness question.
   Report it. Do not silently reconcile.
5. **Constants check (periodic / annually):** re-verify the authoritative constants in
   `qa_independent_model.py` (and the test-suite's `IRS_2026_KNOWN`) against the live IRS/CMS
   sources cited. Stale constants are a real, recurring bug class (five were found and fixed on
   2026-08-29). The engine, the model, and the test-suite must all reference the SAME external truth.

## What a mismatch is NOT
- It is not permission to edit the benchmark.
- It is not permission to change the engine without developer sign-off.
- It is not fixed by "adding a row" or re-deriving a number from the engine until it agrees.
It is a signal to find out **which** of {engine, model, constant, scenario definition} moved, and why.

---

## ✅ Cold-run verification (2026-08-29)

This runbook was verified end-to-end by a "cold run": driving the engine (**B**) using ONLY the
documented clearing recipe, field-ID map, and capture pattern below — no reliance on prior knowledge
of the app internals — then completing the full three-way check against the frozen benchmarks (**A**)
and the independent model (**C**).

Scenarios exercised: MFJ S1 (anchor) + S2 (add child/education), Single S1 (anchor) + S2 (dependent
-> Head-of-Household switch). Result: **all 12 checks (4 scenarios × 3 metrics) passed A == B == C.**
The MFJ clearing recipe correctly produced a clean childless anchor (no phantom gifts/529), and the
Single->HoH filing switch triggered correctly (filing pill read "Head of Household").

Conclusion: the runbook is sufficient for a fresh operator (LLM or developer) to reproduce the
benchmarks without additional context. If you extend it (new scenarios/levers), re-run this cold
check on the new cases.
