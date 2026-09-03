# P-ZERO — Testing Methodology

**Read this before adding a feature, changing a tax number, or writing a test.**

This is the operating manual. `CONTEXT.md` is the chronological log of *what happened*; this is
the standing account of *how the testing works and what it demands of you*.

> ### ⚠️ CURRENT DEFAULT BASELINES (today's $) — updated 2026-08-30
> - **MFJ default EOL = `$1,215,092`**
> - **Single default EOL = `$540,113`**
>
> These moved with the 2026-08-30 RMD "spend-first" engine change. Any inline baseline figures
> below that predate that date (e.g. `$1,176,702` MFJ, or `$528,223` / `$524,584` Single) are
> SUPERSEDED — they reflect the engine before the constants fix and/or the RMD change. Use the two
> values above as the current regression baselines. (For the full QA scenario benchmarks, the
> canonical source is `qa_independent_model.py`.)

---

## ⭐ FOR AN LLM ASKED TO "DEEP TEST" — START HERE

If a human has handed you the app files and asked you to **"deep test"**, "audit," or "verify the
accuracy of" this app (or any subsystem of it), **this section is your assignment.** Read it fully,
then follow the playbook below. Do not shortcut it. Do not declare success on a green suite alone —
the entire reason this document exists is that **a 180-test all-green suite hid six real bugs**.

### The files you were given, and what each is for

| file | what it is | how you use it |
|---|---|---|
| `index.html` | the **MFJ app** (married filing jointly). Contains the engine, the UI, **and the Help docs** (the `<section id="help">` — this is the behavioral spec, §1–§21) | read the engine code AND the Help docs here |
| `p-zero-single.html` | the **Single/HoH app** — a fork of the same engine | every engine change must be spliced here **byte-identical**; verify parity |
| `test-suite.html` | the **browser suite** (Tiers 0–10, both builds) | the machine that runs the checks — but it only tests what's already been thought of |
| `CONTEXT.md` | the **decision log** — why things were built the way they were | read BEFORE concluding the engine is wrong. Several "bugs" this project were documented design choices |
| `TESTING.md` | **this file** — the methodology, rules, and this playbook | your instruction manual |

### What "accuracy" means here (and what it does NOT)

- A **green suite means "the specific things we already checked are still true."** It does **not**
  mean the engine is correct. A wrong tax bracket, wrong RMD divisor, or wrong subsidy **conserves
  money perfectly and stays green.** (Proven: bracket 22%→32% passed 216/216. RMD divisors halved
  passed 216/216.)
- **Deep testing = adding NEW known-answer coverage** for a subsystem that doesn't have it yet, by
  independently verifying the engine against **published sources** and **hand computation** — not by
  re-running what exists.

### THE DEEP-TEST PLAYBOOK — run this loop for each subsystem

1. **Read the intent first (rule 8).** Read that subsystem's **Help doc** (in `index.html`, §1–§21)
   AND its **CONTEXT.md** decision-log entries. A gap between doc and code is either a bug or a
   documented limitation — you cannot tell which without reading both. *Skipping this wastes time
   "finding" known limitations, and risks "fixing" deliberate designs (see the RE/BI recapture
   near-miss in CONTEXT).*
2. **Read the engine code** for the subsystem. Find where the number/mechanic is actually computed
   in the year loop (the function behind `triggerRecalculate()`).
3. **Verify every constant against a PUBLISHED source — never from memory.** Web-search the IRS
   figure, bracket, divisor, threshold. *Recalled RMD divisors "proved" 14 of 29 engine values
   wrong; the published tables showed the ENGINE was right. Memory is not a source.*
4. **Verify behavior in a live headless run, and reconcile any surprising number BY HAND.** Use
   Playwright to drive the app, read `window.__chartSeries` (rich per-year detail) or
   `window.__scenarioB`. If a value surprises you, hand-compute it before believing OR doubting it.
   *Confirm the lever you're setting actually moves the number — writing to a non-existent element
   id is silently invisible.*
5. **Lock it with a Tier 7 known-answer test.** Assert the engine's output against the published
   figure. **If the value isn't observable, publish an `aud`-prefixed field** in the
   `chartSeries.push({...})` call first — a test can only check what the engine exposes.
6. **MUTATION-TEST the new test.** Reintroduce the bug on purpose (change the rate, flip the age,
   zero the term) and confirm the test goes **red**. *A test that stays green when you break the
   thing is worthless — this caught an entire 4-test LTCG set that tested a helper, not the engine.*
7. **Triangulate — see the full "TRIANGULATION" section below.** Which triangle depends on what you
   touched: **(A)** a tax constant → §21 fact + engine constant + Tier 7 test (Tier 0 checks four
   edges); **(B)** a money-moving mechanic → Help doc describes it + engine publishes an `aud` field
   + test reads that field + Tier 8 scenario; **(C)** ANY engine change → splice byte-identical into
   both apps and assert parity. If doc and code disagree, read CONTEXT first, then apply the
   disagreement-resolution rule. Do all triangles that apply, or you've left a place to rot.
8. **Gate and ship.** Full suite green (both apps), baselines unchanged (**MFJ $687,726 / Single
   $340,807** with zero RE/BI deals), zero page errors, engine change byte-identical across both
   apps. Then update CONTEXT.md with what you found.

### The traps that will bite you (each cost real time this project)

- **State leaks.** A test that mutates **module-scoped** state (`childrenProfiles`,
  `childGiftingProfile`, RE/BI deals) MUST snapshot and rebuild it in `finally` — `restoreInputs`
  only restores DOM inputs. **Tell: if your change breaks an UNRELATED later test, it's a leak, not
  a logic bug.** (Hit three times.)
- **A test computing its own expected value.** If the test derives the answer from its own inputs
  instead of reading what the engine produced, it's arithmetic, not a test — it passes the mutation
  it targets. Read an `aud` field the engine published.
- **"Wrong vs standard tax treatment" is meaningless if the model deliberately uses a different,
  documented treatment.** Read CONTEXT before calling it a bug.
- **Verify the checker before believing its verdict.** If a baseline with no deals fails your new
  audit, suspect the audit, not the engine.

**When you're done with a subsystem, it should have:** a Help §21 fact (if it involves a tax
constant), an engine value that reads live, a Tier 7 test asserting against a cited source, a
published `aud` field if needed, and a passing mutation test. That's what "deep tested" means here.

---

## ⭐ FOR AN LLM ASKED TO "DO THE ANNUAL IRS UPDATE" — START HERE

If a human says **"do the annual IRS update"** (or "update the tax year", "bump to 2027 figures",
etc.), this section is your assignment. The IRS inflation-adjusts many figures every year; this
playbook updates them in **both apps**, from authoritative sources, and lets the existing test tiers
prove nothing drifted out of sync.

### Non-negotiable ground rules
1. **Update BOTH apps.** `index.html` (MFJ) carries **both** the MFJ and Single filing tables (it
   needs Single for the survivor scenario). `p-zero-single.html` carries the Single tables. A figure
   that appears in both files must be changed in both, identically. After editing, diff the shared
   blocks and confirm parity — the two files drift if you hand-edit only one.
2. **Never source a number from memory.** Every figure comes from an authoritative primary source,
   cited in your summary. Memory is not a source — recalled RMD divisors once "proved" 14 of 29
   engine values wrong when the engine was right.
3. **This is a constants + prose update, NOT an engine change.** You are changing values inside
   `IRS_2026` and a few hardcoded numbers in the Help prose. You are NOT changing any formula, the
   solver, the year loop, or any mechanic. If you find yourself editing logic, stop — that's out of
   scope for an annual update.
4. **Gate on the full suite, both apps.** After updating, run `test-suite.html` over HTTP. Tier 0
   will fail on any §21 fact whose engine value you changed but whose doc/source you didn't update in
   lockstep; the worked-example guard (Tier 0 EDGE 5) will fail on stale ACA prose. Green in both
   apps is the finish line. Then update the §21 `data-fact` values + sources to the new year.

### ANNUAL_CONSTANTS_2026 — non-IRS assumptions (separate from IRS_2026)

A second constant block, `ANNUAL_CONSTANTS_2026`, holds planning assumptions that are reviewed annually
but are NOT statutory IRS figures. Keep it separate from `IRS_2026` so the IRS update stays a clean,
sourced, single-block edit. Current contents:

- **`hcTaperOn`** (default `true`) — whether the healthcare-inflation taper is active.
- **`hcConvergenceYears`** (default `25`) — the linear window over which healthcare's EXCESS over CPI
  fades to zero.

**Critical rule for the taper — do NOT hardcode the premium.** The excess premium is ALWAYS computed
live in the engine as `healthcareInflation - CPI` (both are panel inputs). Never store `1.5` or any
premium value in the constant block; if you ever see one there, it's a bug. The only taper values that
belong in `ANNUAL_CONSTANTS_2026` are the on/off flag and the window length.

**`hcConvergenceYears` is a WINDOW (a duration), not a calendar year.** It means "N years from the
projection start," which re-anchors automatically every time the app is run — so it does NOT need to be
advanced each year, and there is no stale calendar year to update. Only change it if your BELIEF about
how long healthcare's excess persists actually changes (a modeling decision, not a mechanical refresh).
This duration design is deliberate: it makes the same future calendar year get the same treatment
regardless of when the app is run, and it never goes stale.

**When you change any ANNUAL_CONSTANTS_2026 value, the baselines move.** Recompute and record the new
EOL baselines in CONTEXT.md, and re-derive any healthcare-affected worked examples in the Help prose
against the LIVE engine (not find-replace). The taper guards (Tier 1: taper on, window; Tier 5: far-out
healthcare grows slower than a flat premium) and the pinned-MC-reproduces-deterministic test (Tier 7)
must stay green.

### Authoritative sources (cite the specific document, not a summary site)
- **Ordinary brackets, standard deduction, LTCG breakpoints, contribution limits (401k/IRA/HSA),
  catch-ups** → the IRS annual **Revenue Procedure** (e.g. "Rev. Proc. 2026-XX") and the IRS
  cost-of-living / retirement-plan-limits notice.
- **IRMAA thresholds + surcharge amounts** → **CMS** annual Medicare Part B/D IRMAA announcement.
- **Federal Poverty Level** → **HHS** annual poverty guidelines.
- **SS wage base, COLA** → **SSA** annual fact sheet.
Prefer the primary .gov document. If you can only find secondary reporting, say so and flag the
figure as needs-confirmation rather than committing it silently.

### ✅ UPDATE these `IRS_2026` fields (IRS inflation-adjusts them annually)
Also rename the object's `taxYear` and consider whether to rename `IRS_2026` itself (optional; if you
do, it's a global rename in both files — the suite will catch a missed reference).

| Field(s) | What |
|---|---|
| `mfjOrdinary`, `singleOrdinary` | ordinary-income bracket lower edges |
| `mfjLtcg`, `singleLtcg` | long-term capital-gains breakpoints |
| `stdDedMfj`, `stdDedSingle` | standard deductions |
| `irmaaTiers`, `singleIrmaaTiers` | IRMAA MAGI thresholds **and** the per-person `annual` surcharge $ |
| `fplFirstPerson`, `fplAddlPerson` | Federal Poverty Level (first person + each additional) |
| `elective401k`, `totalAddition`, `iraLimit`, `iraCatchup` | contribution limits |
| `hsaFamily`, `hsaSelfOnly` | HSA contribution limits |
| `catchup401k`, `catchupHsa`, `superCatchup401k` | catch-up amounts |
| `rmdDivisors` | Uniform Lifetime Table — rarely changes, but IRS-published; verify against the current table |
| `taxYear` | bump the year label |

### ❌ DO NOT TOUCH these — they are statutory, fixed in law, NOT inflation-indexed
Changing these would introduce a bug, not an update.

| Field | Why it's frozen |
|---|---|
| `ssProvisionalMfjLower/Upper`, `ssProvisionalSingleLower/Upper` | SS-taxation thresholds, frozen in law since 1993, never indexed |
| `ssMaxTaxablePct` (0.85) | statutory maximum taxable share of SS |
| `seTaxRate` (0.153), `seTaxNetFactor` (0.9235) | the SE-tax formula is statutory |
| `acaCliffFplMult` (4.0), `acaMedicaidFloorMult` (1.38) | statutory FPL multiples |
| `catchupAge401k`, `catchupAgeHsa`, `superCatchupAgeStart/End` | statutory ages (SECURE 2.0) |

The RMD **start age** is not in `IRS_2026` — it's a UI input (`rmdAge`, default 75), a statutory
SECURE 2.0 rule, not an annual adjustment. Leave it.

### ⚠️ SPECIAL CASE — doc-only figures with NO engine home
The **Social Security wage base** ($184,500 for 2026) and the **0.9% Additional Medicare surtax
thresholds** ($250k MFJ / $200k single) are **not in `IRS_2026` and not used by any calculation** —
the engine deliberately does not model the SE wage-base cap (a documented simplification: SE tax is a
flat 15.3%, exact for this household's sub-cap income). But these numbers ARE quoted in the **Help
prose** and the wage base **does** rise annually. Because nothing computes them, **no test will catch
them going stale.** So you must update them **by hand in the Help text** — there are **two locations
per app** (the §18 SE-tax explanation and a short "Known simplification" note near the SE input),
**four total across both apps**. Search each file for the wage-base figure and the surtax thresholds
and update them, even though no constant or test references them.

### After updating — re-sync the guards (this is what makes it trustworthy)
1. Update the §21 **`data-fact` values and `data-source`** for every fact you changed (Triangle A).
   Tier 0 will tell you which you missed.
2. Update the **worked-example prose** for anything derived from a changed figure — the ACA examples
   especially. The Tier 0 EDGE 5 resolver recomputes these from the engine, so if you changed the
   engine value but not the prose, it fails and names the number.
3. Re-verify the two **whole-plan worked examples** (the 2035 drawdown lines) by hand against a fresh
   default run — they're not auto-guarded, and new brackets will shift their tax figures.
4. **Refresh the example CALENDAR YEARS.** Separate from tax figures: the help examples cite concrete
   projection years (2035 step-down, 2036 conversion start, the 2026–2034 accumulation span, etc.)
   that assume the plan starts in the base year. The app's projection start is `new Date().getFullYear()`,
   so these drift forward by one every January regardless of any tax change. The "About the examples"
   section carries a disclaimer that years are offsets from the current start — but for accuracy, bump
   the concrete years to match the new base year when you do the annual pass. Key spots: the Auto
   conversion label (`53 (YYYY)` MFJ / `56 (YYYY)` single — must equal `autoRothConvLabel()`, which is
   step-down year + 1), the accumulation-span example, the semi-retirement-timeline example, and the
   drawdown worked examples. Run `autoRothConvLabel()` in each app and make the doc match it exactly.
4. **Confirm both baselines** moved sensibly and are documented. New brackets WILL change the default
   EOL (that's expected and correct) — update the baseline numbers recorded in CONTEXT.md and in the
   test harness to the new values, and note the change. (This is the one time baselines are *supposed*
   to move; every other change must leave them fixed.)
5. Run the full suite in both apps until green, then record the update in CONTEXT.md with the source
   citations.

---



---

## TRIANGULATION — the full rules (do not skip; this is what keeps the artifacts honest)

"Triangulate everything" means: **the same fact must be stated in every place it lives, and those
places must be forced to agree.** There is not one triangle — there are THREE, depending on what
you touched. Work through whichever apply.

### Triangle A — a TAX CONSTANT (a rate, bracket, divisor, threshold, surcharge)
The fact lives in **three languages** and all three must match:

```
Help §21:  <li data-fact="rmd.startAge" data-value="75" data-source="SECURE 2.0 §107">   (the spec)
engine:    IRS_2026.rmdStartAge = 75  (read live by the resolver — NEVER copied into the test)
test:      a Tier 7 assertion checking the engine's OUTPUT against 75, sourced independently
```

To add or change one, edit **all three**. Tier 0 checks four edges every run and names the one you
missed: **doc↔engine** (stated value = value the engine actually uses), **doc↔test** (every fact
has a Tier 7 assertion), **fact↔wiring** (no orphan facts), **fact↔source** (every number cites a
publication). **Never keep the number in a fourth place** (e.g. hard-coded in the test) — that's
just another thing to rot.

### Triangle B — a MECHANIC that moves money (no published constant: 529 burn, HSA order, gifting, a shortfall path)
These don't get a §21 fact — there's no IRS number to cite. They triangulate through a **published
flow** instead:

```
Help doc:  the §-section describes the behavior ("shortfall paid from brokerage, basis pro-rata,
           gain realized")                                                           (the spec)
engine:    publishes an aud-prefixed field for the flow (audF529ShortfallGain)  (makes it observable)
test:      a Tier 7 test READS that aud field and asserts the behavior; a Tier 8
           CONSERVATION_SCENARIOS entry proves the money doesn't leak             (locks it)
```

The rule: **if a mechanic's behavior is worth asserting, the engine must publish an `aud` field for
it** — a test can only check what the engine exposes, and computing the expected value inside the
test instead is arithmetic, not a test (it passes its own mutation). Then the **Help doc must
describe the same behavior the test asserts.** If the doc is silent on a behavior you're locking,
add a sentence — that's the doc↔test edge for mechanics.

### Triangle A2 — WORKED EXAMPLES in the help prose (numbers derived from the engine)
Prose examples that cite engine-derived numbers (an ACA applicable-%, a contribution limit, a resulting subsidy) are a triangulation blind spot: unlike §21 facts they have no edge, so they rot silently when the engine changes. **Two drifted in a single session before this guard existed.**

Guard them with Tier 0 EDGE 5:
1. Wrap the derived number in the help HTML: `<span data-example="aca.pct" data-magi="60000" data-fpl="21150">9.46%</span>`. The displayed text is unchanged; the span only makes the number machine-findable, so the number a reader sees and the number the test checks are the SAME element.
2. Add a resolver to `EXAMPLE_RESOLVERS` in tier0 that recomputes the value from the live engine and asserts the shown text matches within tolerance.
3. Mutation-test both directions: stale the prose (engine unchanged) → red; skew the engine (prose unchanged) → red.

**Only tag DERIVED-FROM-FUNCTION examples** (ACA calcs, contribution limits). **Do NOT tag whole-plan-scenario numbers** (e.g. "2035 drawdown total = $68,506") — recomputing those needs the full default run and is brittle; guard the constants they cite instead, or keep them manually verified with a note.

### Triangle C — the TWO-APP FORK (applies to EVERY engine change, always)
`index.html` (MFJ) and `p-zero-single.html` (Single) are forks of one engine. **They drift.** So:

1. Build and verify the change on MFJ first.
2. Splice the **byte-identical** block into Single — never hand-edit the same logic twice.
3. **Assert parity** — extract the changed block from both files and compare; they must be identical
   (byte-for-byte for shared logic; the only allowed differences are MFJ-vs-Single tax tables).
4. Confirm **both** baselines are unchanged: **MFJ $687,726 / Single $340,807** (zero RE/BI deals).
5. The suite runs Tier 0/7/8 against **both** apps — a mutation caught in MFJ but missed in Single
   usually means a flat scenario, not an engine difference (see rule 4).

### When the three artifacts DISAGREE — how to decide which is wrong
Doc/code disagreements are not noise; **three real bugs this project were exactly this** (survivor
help blocks, the SS-threshold tautology, the 529 "proportionally" wording). When doc and code (or
test) conflict:

1. **Read CONTEXT.md first.** If the decision log documents the current behavior as deliberate, the
   DOC is stale — fix the doc. (RE/BI recapture: the "off" behavior was the intended one.)
2. **If CONTEXT is silent, and the doc states a specific, correct tax treatment the code doesn't
   implement, the CODE is the bug** — the doc was the spec and the code drifted from it. (529: the
   doc promised "proportionally"; the code did full-basis. The code was wrong.)
3. **Precedence when otherwise unresolved:** Help is authoritative on *behavior*, TESTING on
   *method*, CONTEXT on *history/rationale*, and the **code is ground truth for what actually
   runs**. Fix the loser immediately and record it in CONTEXT — a doc that lies is worse than no doc.

> **A "green suite" does not mean the three artifacts agree — it means the CHECKS agree.** Tier 0 is
> what forces the artifacts themselves into agreement. If you add a fact or a mechanic without
> wiring its Tier 0 edge, you've left a place for the next silent drift.

---

## Why this exists (the short version)

A **180-test suite was ALL GREEN** while the default plan **understated final wealth by 60%**.

In one session, six bugs surfaced: **four found by the user, two by an ad-hoc audit, zero by the
suite.** The reason is structural, not sloppiness: every test had been written *after* a bug, so
the tests only ever confirmed what was already known. They checked that things **fire** and are
**taxed**. Nothing asked whether money was **conserved**, or whether the rates were **right**.

Two mutations prove the point. Both passed **216/216**:

| mutation | result |
|---|---|
| Tax bracket 22% → 32% (a 45% error, both apps) | **ALL GREEN** |
| Every RMD divisor halved (doubling every RMD) | **ALL GREEN** |

Tiers 0, 7 and 8 exist to close exactly those holes.

---

## The eight tiers

| tier | catches | why it can't be skipped |
|---|---|---|
| **0 — Triangulation** | docs ↔ engine ↔ tests drifting apart | the survivor fix shipped and left 3 help blocks describing the old behaviour |
| 1 — Structural | the page or engine is broken outright | fast smoke |
| 2 — Invariants | negative balances, depletion misdetected | 7 scenarios |
| 3 — Known-answer | `marginalTax` bracket arithmetic | hand-derived |
| 5 — Features | session features still fire | regression |
| 6 — RE/BI | deals fire and are taxed | regression |
| **7 — Known-answer (IRS)** | **wrong rates, brackets, divisors** | the ONLY tier that catches a wrong number |
| **8 — Conservation** | **money created or destroyed** | ~1,000 year-checks/run |

### The critical relationship

**Tier 8 is necessary but NOT sufficient.** It proves no money leaks. It *cannot* prove the
amounts are right — a wrong bracket, wrong divisor, or wrong subsidy **conserves perfectly** and
stays green.

**Tier 7 is the only tier that catches a wrong number.** It asserts against **published figures**,
transcribed from sources, deliberately independent of the app's own tables. (Asserting the app
equals itself proves nothing.)

**Tier 0 keeps all three artifacts honest** — see below.

---

## Tier 0 — Triangulation: the help doc IS the spec

The same fact lives in three places, in three languages:

```
engine:  data-default="75"          (an HTML attribute)
docs:    "RMD age (default 75)"     (English prose)
test:    rmdAgeEl.value === '75'    (a JS assertion)
```

Three independent edits. **Any two can agree while the third rots.**

The fix: help **§21 "Verified Facts"** carries machine-readable entries that render for the user
*and* are read by the suite:

```html
<li data-fact="rmd.startAge" data-value="75" data-source="SECURE 2.0 Act §107">
    RMD start age: <strong>75</strong> for anyone born 1960 or later…
</li>
```

Tier 0 checks four edges on both apps, every run:

1. **doc ↔ engine** — the stated value must equal what the engine *actually uses*. Resolvers read
   `IRS_2026` / the DOM live. **Never keep a copy in the test file** — that's just a fourth place
   to rot.
2. **doc ↔ tests** — every fact must have a Tier 7 assertion behind it.
3. **fact ↔ wiring** — no orphan claims that resolve to nothing.
4. **fact ↔ source** — every number cites a publication.

Break any edge → red. **Mutation-verified in all three drift directions** (engine-only, doc-only,
test-renamed), in both apps.

> Tier 0 earned its keep on its first run: it caught that **SE tax had no Tier 7 test at all** —
> rates I'd verified against 8 sources during an audit and never written an assertion for.

---

## THE MAINTENANCE CONTRACT

### To change a tax fact
Edit **all three**, or the suite names the one you forgot:
1. the `<li data-fact>` in help §21 (value **and** source)
2. the engine constant
3. the Tier 7 assertion

### To add a feature that moves money
1. publish its flow in `chartSeries.push` (the `aud`-prefixed fields)
2. add a `CONSERVATION_SCENARIOS` entry

Because the conservation invariant is **general**, it already covers features that don't exist
yet — a future annuity or pension **cannot quietly leak money**. Tier 8 fails the moment its cash
path doesn't balance, without anyone writing an annuity-specific test.

### To add a tax constant
It needs a §21 fact, a source citation, and a Tier 7 assertion. **Tier 0 fails otherwise.**

---

## The five rules (each was learned the hard way)

### 1. Mutation-test every new test
Reintroduce the bug; confirm the test **fails**. **A test that doesn't fail on a known bug is
worthless.**

This caught an entire LTCG test set — four green tests — that passed the very mutation they were
written to catch. They exercised the `marginalTax` **helper**, not the engine's **use** of it.

### 2. Never source a number from memory
Recalled RMD divisors "proved" **14 of 29 were wrong**. Two published tables confirmed the
**engine was right and the memory was wrong**. Trusting that arithmetic would have corrupted a
correct table *and locked the corruption in*, because Tier 7 asserts whatever constant you type.

**A known-answer test is only as good as its source.**

### 3. Verify the lever moves the number
**Writing to a non-existent element id is INVISIBLE** — no error, no effect.

`targetDraw` does not exist in **either** app. The real lever is `distModel='fixed'` +
`netDistribution`. A test using the phantom id **passed in MFJ by luck** and **falsely failed in
Single**, which looked exactly like an engine bug and wasn't.

Related traps, all hit in one session:
- Module-scoped `let`/`function` are **not on `window`** — wrapping them to trace yields empty traces.
- `inflationRate` is read as `parseFloat(...) || 3` — setting it to `"0"` is **falsy** and
  silently becomes **3%**.
- `FileReader.onload` does not fire for synthetic files in headless Playwright.

> **When new code and known-good code fail identically, suspect the harness.**

### 4. Check the scenario has signal
A mutation caught in one app but **missed in the other** usually means the scenario is flat, not
that the engines differ. The IRMAA lookback mutation was invisible in the Single app because MAGI
was nearly constant across the lookback window — a 1-year and 2-year lookback selected the *same
tier*. Fixed by forcing a deliberate MAGI spike.

> **A green mutation test can mean the test is weak OR the scenario has no signal.**

### 5. Read the help docs before auditing a subsystem
They state **intent**. A gap between doc and code is either a bug or a known limitation — both are
exactly what an audit is looking for.

- **§18 already documented** the SE wage-base gap. It was a disclosed, deliberate limitation —
  "found" as a bug, wasting time.
- **§11 was RIGHT while the code was WRONG**: *"any excess beyond what spending required is
  reinvested into the Brokerage account — **it never disappears**."* That is precisely the
  invariant `excessRmd` violated as dead code. **Reading §11 would have found the 60% bug
  immediately.**

---

## Verify the checker before believing the verdict

An audit is code, and code has bugs. **Validate it against a hand-proved case before trusting a
single number it prints.**

The conservation audit's first run reported **423 failures**. Three were bugs in the audit itself:

1. **Miscounted the RMD as spendable** → 423 false failures. The invariant tallied cash *by
   source*, which required guessing the engine's internal conventions. **Fix: switched to
   total-portfolio conservation, which has no interpretation in it.**
2. **Omitted `hsaDist` as spending** → ~11 false failures/scenario (~$47k/yr phantom leak).
3. **Used net `income1099` instead of gross** → phantom **+$23,736/yr created**.

**The tell each time: the baseline with no deals failed.** A no-deal plan has no RE/BI cash at
all — if the audit flags it, suspect the audit.

The real RMD bug was hand-computed to **−$1,213,097** *first*; only when the audit reproduced that
exactly was its other output believable.

---

## How to run the suite

```bash
mkdir -p suite_test
cp mfj.html    suite_test/index.html          # the suite loads apps by these names
cp single.html suite_test/p-zero-single.html
cp test-suite.html suite_test/
cd suite_test && python3 -m http.server 8000
# open http://localhost:8000/test-suite.html and click Run All
```

It **must** be served over HTTP — the suite loads both apps in iframes and reads across them.
Container resets wipe `suite_test/`; recreate it with the commands above.

**Note:** the Tailwind CDN is 403-blocked in the sandbox, so grids collapse in headless runs.
Geometry assertions are unreliable there — assert **DOM structure** (`.contains()`,
`compareDocumentPosition`), not pixels. Appearance is browser-only; user screenshots are ground truth.

---

## The honest status

**Verified:** structure, cash-flow conservation, and the tax *tables* — brackets + rates, LTCG
breakpoints **and stacking behaviour**, standard deductions, IRMAA (tiers + surcharges + 2-year
lookback), survivor tables, RMD divisors + start age, FPL/ACA cliff + applicable-% schedule, SE
tax rates.

**Documented simplifications (deliberate, not bugs):** SS wage-base cap not modelled (exact below
~$199,783 of gross 1099 per person, overstated above); **SS taxability is a flat 85% rather than
the statutory phase-in** — exact for any plan whose provisional income clears $44,000 MFJ /
$34,000 Single (the default plan runs at ~$375k, 8.5x over), and it can only *overstate* for
low-income retirees inside the phase-in, so it is conservative; IRMAA thresholds all
inflation-indexed though the top tier is frozen until 2028 in law.

**Not yet covered by known-answer tests:** survivor SS/healthcare/basis-step-up mechanics.

> **Never read a green suite as "the engine is verified."** Read it as "the specific things we
> thought to check are still true." That distinction is the entire lesson of this project.

---

## Lesson: a Monte Carlo path must reproduce the deterministic result when pinned

When adding a second escalation rate (healthcare inflation, above general CPI), the first
implementation scaled the Monte Carlo path by *adding* the premium to the drawn inflation:

```js
hcInfScale = infScale * Math.pow(1 + (hcInfFlat - infFlat), i);   // WRONG
```

That compounds the premium on top of the draw. With CPI 3% and healthcare 4.5%:
`1.03 × 1.015 = 1.04545`, not the `1.045` the deterministic path uses. Tiny per year, material over
50+ years — a pinned MC path returned **$654,875** against a deterministic **$687,726**.

The fix is a **ratio**, which is algebraically exact when the draw equals the flat rate:

```js
hcInfScale = infScale * Math.pow((1 + hcInfFlat) / (1 + infFlat), i);   // RIGHT
```

**The general rule:** any time you introduce a second rate that rides the stochastic path, express it
as a ratio to the drawn rate, never as an additive premium — otherwise the two code paths diverge and
Monte Carlo silently stops being "the same engine with different draws."

**Why this was caught:** the Tier 7 test *"Monte Carlo: each path runs the REAL engine (pinned path
reproduces the baseline)"* exists precisely for this. It is the only test that can catch a divergence
between the deterministic and stochastic code paths. Keep it.

---

## Playbook: adding an off-by-default stress-test feature (LTC as the worked example)

Long-term care was added as an optional cost. The pattern generalizes to any feature that must be
invisible until opted into:

1. **Off-by-default is an invariant, not a preference.** The toggle must start unchecked AND the
   baseline with it off must reproduce the pre-feature number to the dollar. Guard BOTH: a Tier-1
   structural check (`toggle.checked === false`) and a Tier-5 behavioral check (off-state EOL ===
   pre-feature baseline; on-state EOL < off-state). The behavioral reversibility check is what proves
   the toggle doesn't leave residue.

2. **Mutation-test by flipping the default ON.** The correct result is a CASCADE: the direct guard
   fires (`checked=true`) and the baseline/Monte-Carlo guards also fail because on-by-default moves the
   baseline. Nine failures from one mutation is the feature being locked from multiple directions —
   exactly what you want.

3. **Escalation on a stochastic path uses a RATIO, never an additive premium.** LTC rides `hcInfScale`,
   which already had the ratio fix (see the healthcare-inflation lesson above). Reusing it meant LTC
   inherited the correct Monte-Carlo behaviour for free — a second reason to route new costs through an
   existing escalation variable rather than rolling a new one.

4. **Evidence-based defaults, web-verified, cited in the help doc.** Onset 84, duration 2/4, cost
   $110k all came from current sources, not recall. When a default encodes a real-world number, the
   help text should state the basis so a future editor knows it's deliberate, not arbitrary.

5. **New inputs MUST join the export inputIds list.** Six LTC ids were added; the export-coverage
   dev-warning stays clean only if every input is either exported or explicitly ignored. Verify the
   warning after adding inputs.

## Inheritance feature — what the tests cover
The Inheritance section is off by default and reconciliation-safe by construction (it plugs into the same
three engine sinks RE/BI uses). If you change it, keep these invariants green:
- **Off is a no-op.** With the toggle off, both baselines must stay exact ($1,215,092 MFJ / $540,113
  Single). The Tier 5 guard asserts off-returns-exactly-to-baseline.
- **Three tax types behave distinctly.** taxfree = cash to brokerage, no tax. taxable_now = full amount
  as ordinary income in the arrival year. taxable_10yr = 1/10 as ordinary income each year for EXACTLY
  10 years (linear, no growth wrapper). The guards check the 10-year count is exactly 10 and that
  taxable_now fires in the arrival year.
- **Nominal vs today's-$.** A nominal amount is used as-entered at the arrival year; a today's-$ amount is
  escalated by CPI. The guard checks nominal $1M stays $1M while today's-$ $1M escalates higher.
- **Column lookups must stay tooltip/iframe-safe.** The Inheritance and Gifting columns are looked up by
  header name. ALWAYS read headers via __hdrLabel (direct text nodes), never innerText — innerText leaks
  hidden tooltip text in the suite's hidden iframes (see the header-tooltip bug lesson). The Healthcare
  column tooltip bug was exactly this class.
- **Gifting toggle default is app-specific.** ON when childGiftingProfile is non-empty (MFJ), OFF when
  empty (Single). If you change the default gifting schedule, update the Tier 1 expectation.
- **MC gate.** The pinned-Monte-Carlo-equals-deterministic gate must still MATCH with inheritance active;
  the feature only adds nominal cash/income, never a stochastic term.

---

## Reconciliation redesign — Phase 1 & Phase 2 guards (Tier 1)

The reconciliation redesign added a click-to-expand panel (Phase 1) and zone-band headers + column
reorder (Phase 2) to the combined "Household Summary" table in both apps. Tier 1 guards protect the
invariants that broke (or nearly broke) during the build:

**Phase 1 — expand panel:**
- `reconciliation expand row exists for every ledger row` — one hidden `.recon-exp` row per `.recon-row`.
- `expand-row colspan matches live column count (not hardcoded)` — the panel spans the full table; its
  colspan is set from the live `#ledgerHeaderRow2` th count in `wireReconExpandRows()`, so it can't go
  stale when columns toggle. (A hardcoded colspan here is what caused the original blank-table bug.)
- `expand panel reconciles (Starting+Contribs+Growth−W/D=Ending)` — reads the panel's "Year reconciles"
  numbers and checks the identity to ±$2.

**Phase 2 — zone bands + surplus:**
- `six zone bands present` — zoneGrows/Outflows/CashIn/Reference/Withdrawal/Ending all exist.
- `zone colspans sum to visible columns (default)` and `... after ACA toggle` — THE key Phase 2 guard.
  The six band colspans must sum to the number of visible combined data columns. This desynced twice
  during the build (DOM-visibility race) and shifted Withdrawal/Ending sideways. The fix computes colspans
  from the flags (giftingEnabled/inheritanceEnabled/magiVisible), NOT from DOM reads. The guard toggles ACA
  (which shows/hides MAGI) to confirm the Reference band re-sizes and everything stays summed. **If this
  guard ever fails, do NOT go back to DOM-counting visible cells — that is what raced. Keep it flag-based.**
- `surplus year shows "+ Surplus" term and reconciles` — forces a surplus with a $300k tax-free inheritance
  in 2050, opens that row, and checks the panel shows a "+ Surplus" term with S+C+G−W+Su=E to ±$2. In
  surplus years W/D is $0 and the leftover is banked to Brokerage; without the surplus term the row doesn't
  reconcile on a calculator.

All six guards pass in both MFJ and Single. Baselines must stay MFJ $1,215,092 / Single $540,113 (current as of the 2026-08-30 RMD change).

**Sandbox limitation:** the harness can't fully render the app's Tailwind grid/flex (CDN blocked headless),
so these guards check DOM/colspan/reconciliation math — NOT pixel alignment. Actual visual misalignment
(e.g. a band overhanging its columns) must be confirmed from a real browser / user screenshot.

## Tier 10 — Recent Features (timeline / gifting / exec parity)

Behavioral + structural coverage for the timeline/gifting/exec-parity work, run against **both** builds.
Written build-agnostic and branching on `fileKey`, because the two builds differ by design:

- **Plan Timeline structure** — the multi-lane widget renders in the Exec Summary with milestone
  nodes on the main line, 5-year gridlines, and a "Plan Ends · $legacy" end-cap.
- **Kid lanes** — MFJ defaults to 2 children, so kid swimlanes + Total-Support end-caps render by
  default; Single defaults to **0 children**, so the test asserts **no** kid lanes appear until
  education is enabled and a child is added. (This is the key MFJ/Single engine difference.)
- **Exec Summary parity** — exactly 8 stat cards (incl. Retirement Spending, Lifetime Spending,
  Effective Tax Rate), the strong/watch callout pair, and the Net-Worth chart embedded in Exec.
- **KPI cards hidden by default** on Plan Details (shown only in Compare mode).
- **Plan Details header block** present with a populated context strip (Horizon / Peak / End / …).
- **Recon-header scoping** — after expanding a ledger row, the recon panel's "cost" / "from portfolio"
  headers must NOT carry the colored zone-header background, and their text must stay readable
  (not white-on-light). This is a regression guard for the over-broad `#planDetailsView thead
  tr:first-child` selector that leaked into the recon sub-table; the fix scopes it to
  `#ledgerHeaderRow1`.
- **Gift routing is display-only** — tagging a gift to a different recipient (`other` → `donation`)
  must NOT change the engine's EOL. The `giftingRecipients` map is a display-layer routing hint for
  the timeline; the engine must never read it.
- **Header chrome** — the orange top-border signature (`#e49a62`) and the Exec/Plan-Details tabs.

**Sandbox limitation (same as the other tiers):** the full iframe harness needs same-origin loading,
which requires serving the folder over HTTP. In a hardened sandbox the headless browser may be unable
to reach localhost; when that happens, the Tier 10 assertions can still be validated by running them
directly against each app opened via `file://` (existence/computed-style/behavioral checks are all
reliable that way). Pixel alignment still requires a real browser / user screenshot.
