# P-ZERO — Project Context & Decision Log

> **Read this first if you are a new LLM or developer picking up this project (or the original author returning after time away).**
> This single file is the entry point. **Part 1** orients you (what the project is, how to work on it safely). **Part 2** is the full decision log (why each thing was built the way it was). One file, two purposes — Part 1 is the "how to work," Part 2 is the "why we chose."

> ### 🧪 QA VALIDATION SYSTEM — use it before and after any engine change
> A three-file QA system independently validates the projection engine. **Before AND after changing
> anything in an app's engine, run it.**
> - **`QA-RUNBOOK.md`** — how to run the QA (start here for QA).
> - **`QA-SCENARIOS.md`** — named scenarios with FROZEN benchmark outputs (the answer key).
> - **`qa_independent_model.py`** — an engine-blind Python model that reproduces every benchmark
>   from scratch; run `python3 qa_independent_model.py`.
>
> It works as a three-way check: **A** (frozen benchmark) == **B** (engine output) == **C** (independent
> model). All 7 MFJ scenarios AND all 7 Single-app scenarios currently reproduce to the dollar. **The
> benchmarks are FROZEN — a mismatch is a finding to investigate, NEVER a number to overwrite, and
> NEVER a reason to change the engine without explicit developer sign-off.** (`test-suite.html` is the
> complementary fast invariant/known-answer suite — run it too.) Run: `python3 qa_independent_model.py`
> (MFJ) or `python3 qa_independent_model.py all single` (Single app).

---


## 📌 PARKED ITEMS (open, not yet actioned — need developer decision)

These surfaced during QA validation. None are bugs; all are disclosed. Listed so they are not lost.

- **[A] Flat-85% Social Security taxation.** The engine taxes SS at a flat user-editable % (default
  85%) rather than the statutory IRC §86 provisional-income phase-in. Accurate for high-provisional-
  income retirees; OVERSTATES taxable SS (and thus tax) for retirees whose provisional income is
  below ~$108k. Disclosed in-app. Decision: leave as documented simplification, or implement the
  phase-in. (Product/engine change — needs explicit sign-off.)
- **[B] ✅ DONE 2026-08-30 — RMD reinvestment changed to spend-first.** In RMD years the engine funds spending from the
  drawdown order (brokerage first) while banking the full RMD to brokerage — internally consistent,
  but realizes brokerage capital gains a tax-optimizing person might defer. Arguably suboptimal
  modeled strategy. Decision: accept as-is, or model RMD cash as funding spending first. (Engine
  change — needs sign-off.)
- **[C] Constants annual refresh.** The authoritative 2026 IRS/CMS constants (brackets, deductions,
  LTCG, RMD divisors, IRMAA tiers, FPL) will change for 2027. They live in `qa_independent_model.py`
  (header + SINGLE/HOH/MFJ blocks) and the engines + test-suite `IRS_2026_KNOWN`. When the new
  Rev. Proc. drops, re-verify all three against IRS.gov/CMS and update together. No automated
  reminder exists yet.

## 2026-09-02 — Distribution Mix chart reskin (visual only, both apps)

Reskinned the Distribution Mix Sankey in BOTH apps to the "v5" look. Purely visual — no engine,
no data, no numbers changed. Replaced only the two drawing functions (distSized + distBuildSVG):
flush label columns with slack spread as gaps (single spine, both sides flush top & bottom); every
ribbon edge an S-curve incl. top/bottom (flat-top gone); ribbons use the app's DIST_COLORS hues as
a faded horizontal GRADIENT (not solid), hover strengthens; rounded label boxes with a color tab.
ALL functionality preserved: 3 milestone panels, per-panel year selectors, mouse+touch tooltip,
compact/zoom sizing, dollar reactivity, distFlowsFor data flow, {svg,inTot,outTot} contract.
Validation: both apps render clean (0 JS errors); test-suite 666/666 incl Tier 9 chart<->engine
reconciliation (unchanged — data flow untouched); engine math still A==C to the dollar both apps.
Backups: index.html.PRE-SANKEY-RESKIN.2026-09-02-204602.bak,
p-zero-single.html.PRE-SANKEY-RESKIN.2026-09-03-011228.bak. Design ideated in SANKEY-MOCKUP.html.

## 2026-08-29 — Single-app QA built (7 scenarios locked, reproduced to the dollar)

Extended the independent QA system to the Single app (`p-zero-single.html`). Built 7 Single-app
scenarios mirroring the MFJ set and reproduced every one to the dollar via `qa_independent_model.py`
(now covering BOTH apps in one file, `python3 qa_independent_model.py all single`).

Single-app model confirmed: it is a SINGLE-person filer that files as SINGLE when childless and
switches to HEAD-OF-HOUSEHOLD when a dependent is present (`isHoH()` = childrenProfiles.length > 0).
No survivor phase (removed for single filers), so `filingScale` is always 1. Ships with no default
children (unlike MFJ), so no clearing recipe is needed for a childless anchor. Uses single/HoH
brackets, deduction, LTCG breakpoints, and single IRMAA tiers (cliff at $109k MAGI, 1 person).

Key result: the SAME independent projection engine reproduced BOTH apps to the dollar with only a
constants swap (SINGLE / HOH blocks added). This is strong evidence the engine is internally
consistent across filing statuses — the Single app is not a separate engine, just different
constants + the Single->HoH switch. The S2-single scenario specifically validates that filing
switch (adding a dependent drops lifetime tax via the wider HoH brackets + larger deduction).

All benchmarks in QA-SCENARIOS.md PART 2. Engine files untouched (index.html e82edbd0,
p-zero-single.html c3ab1a6c). All validation was the independent Python model, never engine edits.

## 2026-08-29 — Professional constants audit + corrections (external-truth verification)

Re-validated the engine's tax constants against AUTHORITATIVE 2026 sources (IRS Rev. Proc.
2025-32, CMS 2026 IRMAA, IRS Uniform Lifetime Table) via web research — NOT against the engine's
own tables (which would be circular). This was prompted by the recognition that prior
"hand-verification" was largely math-validation (re-adding the engine's own numbers) rather than
independent professional validation. The audit found and fixed 5 stale/mis-transcribed constants:

FIXED (all verified vs authoritative 2026):
  1. stdDedSingle   15750 -> 16100   (both apps) — was the 2025 value
  2. stdDedHoH       23625 -> 24150   (single app) — was the 2025 value
  3. Single LTCG 20% 545050 -> 545500 (both apps) — transcription error, off $450
  4. HoH LTCG 20%    577350 -> 579600 (single app) — off $2,250
  5. HoH ordinary 35% 256250 -> 256225 (single app) — off $25

VERIFIED CORRECT (no change): MFJ ordinary brackets, single ordinary brackets, MFJ LTCG,
MFJ + single IRMAA tiers, FPL first/addl person, stdDed MFJ, RMD divisor 24.6 @ 75, RMD start
age 75 (SECURE 2.0, born 1971).

KEY META-FINDING: the test-suite's `IRS_2026_KNOWN` "independent" reference table contained the
SAME transcription typos as the engine (545050, 15750), so the anti-circularity check was itself
circular — validating the engine against a copy of its own mistakes. Corrected the reference
table + assertions to authoritative values; the straddle-test expected value moved 9247.5 ->
9225.0 (engine was right). Test-suite re-run: 666/666 green, 0 JS errors.

BASELINE MOVED: Single default EOL 524,584 -> 528,223 (higher std deduction -> lower tax ->
slightly more wealth). MFJ default EOL unchanged (1,176,702) — default MFJ barely touches
survivor-phase single filing. MFJ scenarios 1-7 in QA-SCENARIOS.md unaffected (they don't reach
the corrected single/HoH upper thresholds).

Engine self-documentation ("facts" panel data-value + visible text) and stale code comments also
updated to authoritative values. NIIT (3.8%) and AMT remain deliberately unmodeled and are
DISCLOSED in-app — professionally acceptable simplification.

New md5s after fixes: index.html (post std-ded+LTCG), p-zero-single.html (post all 5),
test-suite.html (reference + assertions corrected). See backups/*.PRE-STDDED-FIX.* and
*.PRE-LTCG-FIX.* and *.PRE-CONST-FIX.*


## ⚑ If you are the LLM (or developer) picking this up — YOUR operating rules

These are not history — they are the rules that bind **you**, the current reader, for as long as you work on this project. Read them before touching anything.

1. **The two app files are LOCKED. Never ship a change without the user's explicit go-ahead.** Ask "Do I have your go-ahead to ship?" and wait for a clear "yes"/"ship" every single time. Re-lock (stop editing, require re-authorization) after each ship. There is no literal lock file — this is a discipline you must honor. See §3.
2. **Never claim verification you did not actually perform.** If you say "EOL unchanged ✓" or "suite all-green ✓," you must have *actually run* it (§5), not inferred it from reading a diff. Faking a green check in a financial tool is the worst failure mode here. If you cannot run it, say so plainly.
3. **Work MFJ first, then replicate the verified pattern to Single.** Don't edit both blindly in parallel — see §2, §7.
4. **Do NOT "fix" the deliberate simplifications** (flat-rate SE tax, phantom-wife cruft, no cash-reserve bucket, etc.). They are intentional. See §6.
5. **Verify claims against the actual code, push back honestly, and retract your own over-statements** when you find you were wrong. The user expects a straight collaborator, not a yes-man. (This very document had a factual error — the `__chartSeries` claim — that was caught only by reading the code; assume you'll find more.)
6. **When in doubt, ask.** This is a working artifact someone relies on; a clarifying question is always cheaper than a wrong change.
7. **Read `TESTING.md` before you change a tax number, add anything that moves money, or write a test.** It is the operating manual for the 356-test suite and it makes non-negotiable demands: change a tax fact → update help §21 + the engine + the Tier 7 test (all three, or Tier 0 fails); add a money path → publish its `aud`-prefixed flow + add a conservation scenario; **mutation-test every new test** (a test that doesn't fail on the known bug is worthless); **never source a number from memory** (recalled RMD divisors nearly corrupted a correct table). A 180-test suite was ALL GREEN while the default plan was 60% wrong — that is the failure this discipline exists to prevent.
8. **Read the in-app Help for a subsystem BEFORE auditing it.** The docs state *intent*. §11 correctly described RMD surplus banking while the code silently dropped it — reading it would have found the 60% bug immediately. §18 already documented the SE wage-base gap that was later "found" as a bug. A doc/code gap is either a bug or a known limitation; both are what you're looking for.

Everything below explains the project so you can follow these rules well.

---

## Most-recent session changes (newest first)

- **Monte Carlo discrepancy: investigated (read-only) -> NOT a bug -> added a UI explainer (this session).**
  The user asked about the MC median/tail EOL looking wildly larger than the deterministic projection
  (e.g. median ~$30M, 90th pct ~$112M in today's dollars vs deterministic $1.18M). Investigated with the
  engine untouched, and reached a firm, verified conclusion: **the MC engine is mathematically correct.**
  - **Control test (definitive):** injecting a FLAT 6% return path into the MC path-runner (`mcRunOnce`)
    reproduces the deterministic EOL **to the dollar** ($1,176,702 == $1,176,702). Same engine, same math —
    the MC and deterministic paths only differ in the return sequence they're fed.
  - **Root cause of the "huge numbers" = expected log-normal behavior, not an error.** With realistic
    year-to-year variation (15% vol) around the same ~6% mean: (a) the compounded terminal factor is
    LOG-NORMALLY distributed, so the upper tail explodes (median growth ~14x, but max ~274x over 53yr vs
    deterministic 21.9x) -> that's the giant 90th-pct/max; (b) the MEDIAN sits *below* the deterministic
    figure due to **volatility drag** (arithmetic-vs-geometric gap: a steady 6% compounds to more than a
    wobbly 6% averaging the same). Both are correct, well-known finance. Verified: avg annual return across
    paths = 6.08% (mean is right); the parametric path draws `mean + gauss()*sd` on simple returns, so the
    geometric drag is a consequence of that (correct) modeling choice. `mcGeneratePath`/`mcRunOnce` @ ~6740+;
    `runMonteCarlo` @ ~6763.
  - **The real problem was UI, not math:** the "how to read these" explanation was buried at the bottom of
    the MC modal, so a user saw a $30M median with no framing and assumed a bug. **Fix (Option A, both apps,
    display/copy only):** inserted a prominent blue "How to read these" box DIRECTLY ABOVE the three
    percentile cards in `#mcPctText` (built in the `showMcResult` innerHTML @ ~6835). It decodes all three at
    once (Unlucky = 1 in 10 did worse; Typical = middle run; Lucky = 1 in 10 did better), states the wide
    spread is the point (ending wealth hinges on WHEN good/bad years land), and redirects "will I be OK?" to
    the success rate. The existing detailed `<details>` explainer at the bottom is unchanged. Baselines held
    ($1,176,702 / $528,223), 0 errors. **No engine change.**
  - **Modeling alternative NOT taken (would need explicit sign-off):** could switch the parametric draw to
    LOG-return sampling (normal in log space) so the target *median* CAGR is preserved and the MC median lines
    up more intuitively with the deterministic figure. That's a real modeling change that would shift everyone's
    MC numbers and needs re-validation — deliberately deferred. The engine is correct as-is.
  - **Backups:** before the MC investigation, all shipped files were backed up to
    `/mnt/user-data/outputs/backups/*.PRE-MC-INVESTIGATION.2026-08-27-145526.bak.*`.


- **Full test-suite run + honest corrections of 8 pre-existing failures (this session, after the exec redesign).**
  Ran the complete harness over `python3 -m http.server` (first full run this session). Started at 656/8,
  ended **666/666 GREEN**. Every fix was a TEST correction verified against CORRECT engine behavior — the
  engine was never touched (EOL/tax/legacy byte-identical to session start). None were caused by the redesign.
  - **6 redesign-related tests** (stale/brittle, my responsibility): updated `.es-hero` -> `.es-hero-bar`;
    "8 stat cards" -> "6 KPI cards" (`.es-kpi-card`); print "8 tiles" -> "6 pd-kpi"; and hardened the pillar
    + header-border + kpiGrid-hidden checks to read CSS rules / inline style / classes instead of
    `getComputedStyle` computed-layout (which returns empty/0 inside a `display:none` iframe). Also relocated
    the new exec-KPI test block to the END of Tier 10 so it doesn't disturb the header/kpiGrid tests' state.
  - **"Children" -> "Education Planning" label:** CORRECTED as stale. The child ROSTER ("Children", incl. the
    Add-Child UI) was intentionally moved under **Household** (identity: how many kids, birth years), while
    **Education Planning** is its own section for costs. Both labels SHOULD exist; the old "renamed away"
    assertion predated that restructure. Test now asserts both are present.
  - **W-2 vs 1099 toggle:** engine is CORRECT (1099 $4.14M vs W-2 $4.15M differ, W-2 higher from lower payroll
    tax). The test scenario's pools were too small ($2M/$0.5M/$1M) and depleted to $0/$0, masking the delta.
    Bumped to $5M/$2M/$3M so it survives to EOL and the difference shows.
  - **529 shortfall capital gain (2 tests):** engine is CORRECT. The gain from the brokerage sale that covers a
    529 tuition shortfall IS realized and taxed — it flows through the general `brokGain` -> `audPrefGains`
    path (LTCG-stacked), per the engine comment. The standalone `audF529ShortfallGain` audit field is
    vestigial (always 0). Tests now read `audPrefGains` (and accept $0 LTCG tax when gains fall in the 0%
    bracket, which is correct).
  - **"zero-education child leaks into tuition" (Single):** engine is CORRECT; test premise was wrong. Adding a
    dependent child flips the Single filer to **Head of Household** (`isHoH()` keys off childrenProfiles.length),
    which legitimately widens brackets / raises the standard deduction, cutting lifetime tax ~$66k and RAISING
    EOL ~$147k. (A fresh child also defaults to undergrad $30,500x4, but education is toggled OFF on Single so
    no tuition is charged.) Test now asserts the real guarantees: no tuition while education is off, AND that
    adding a child correctly triggers HoH.
  - **Reconciliation panel tie-out (both apps) — rebuilt as a REAL, adversarially-verified identity.**
    The original test scraped two DOM panel numbers and asserted `fromPortfolio − cash ~ Withdrawn`, which was
    MIS-SPECIFIED (real spending years fund living costs from MULTIPLE sources at once: SS, 1099/semi, RMDs,
    portfolio) and produced false reds (38/53, 39/50). After deriving the true funding identity empirically
    from the engine's own `aud*` fields, the check now enforces, for every spending year (audBaseNeed > 0):
    `(audCashSources + audElecTrad + audElecRoth + audElecBrok) == (audBaseNeed + audSolvedTax +
    audHcFromPortfolio)`. Notes: audBaseNeed already includes gifts; HSA-funded healthcare (audHsaDist) and
    529-funded tuition are self-contained (earmarked bucket-internal moves) and NOT part of this cash-funding
    identity; accumulation years (audBaseNeed == 0) are skipped. **VERIFIED: balances 44/44 MFJ + 41/41 Single.**
    **ADVERSARIALLY verified:** injecting a phantom $5k into any spending year's audBaseNeed drops the balanced
    count (44/44 -> 43/44), proving the check genuinely catches money discrepancies (not a false-green). It
    reads engine fields directly (no fragile DOM scraping). This is a real conservation check, complementary to
    Tier 8's per-bucket/household path-independent invariant (which independently also passes).


- **Exec-summary KPI redesign + Legacy-card clarity (this session).** Shipped to BOTH apps, app + print.
  Baselines held throughout (**MFJ $1,176,702 / Single $528,223**).
  - **Replaced the old 95+ hero + 8 stat tiles with a new 6-card KPI grid** in the exec summary AND the print
    document (per user: "print needs to mimic the kpi cards in the app -- period!"). Card order is a plan
    narrative: **Legacy (Leave) first, then Build - Spend - Give - Protect - Tax.** Navy hero bar on top
    ("Plan Health Score" + colour-coded status pill + big score). Everything else (header/logo, narrative,
    callouts, timeline, chart, ledger, Plan Inputs) is unchanged.
  - **The 6 cards:** (1) **Leave** = Plan End & Legacy (teal); (2) **Build** = Peak Portfolio (blue);
    (3) **Spend** = Lifetime Living Costs (amber) with the **W/D-rate pill colour-coded** green <4% / amber
    4-5% / red >5% (reuses `_wr<4?green:(_wr<=5?amber:red)`), sub-rows retirement spending/yr + avg annual
    healthcare in retirement; (4) **Give** = Lifetime Giving (slate), gifts-to-kids + donations, "None planned"
    when $0; (5) **Protect** = Education & Healthcare (crimson), tuition + lifetime healthcare;
    (6) **Tax** = Tax Impact (violet), effective tax rate + **lifetime Roth conversions** ($0 when off).
  - **Four lifetime flows now surfaced** (closes the ACCURACY-AUDIT gap): gifts-to-kids, donations, tuition,
    lifetime healthcare - all computed READ-ONLY by summing per-year `aud*` fields
    (`audGift` split by `giftingRecipients` tag=donation vs else; `audTuitionBurn`;
    `audHcFromPortfolio + audHsaDist`; `audRothConv`). No engine math changed.
  - **Legacy card clarity redesign (Option 1):** headline is **Total Estate Value** at plan end (all assets),
    then a reconciling breakdown. When leftover pre-tax (Trad/HSA) triggers heir tax, an explicit
    **Liquid accounts -> Heir tax (Trad/HSA) -> Liquid after-tax legacy** bridge shows; when there's NO heir
    tax the bridge **collapses to a single "Liquid after-tax legacy" row** (wallet icon). Business & Illiquid
    and 529 (earmarked) shown as separate carve-outs. Numbers reconcile:
    total = liquid-face + business + 529; liquid-legacy = liquid-face - heir-tax.
    Derived from `B.legacyValue` (which already = liquid-after-tax + rebi), `rebiEndValue`, last-year `f529`,
    and `heirTaxRate`/`heirHsaTaxRate` inputs. **Display-only - no engine change.**
  - **Modeling notes surfaced but NOT changed (need explicit sign-off if ever revisited):** business/RE passes
    at full grown value with NO tax modeled (approximates a step-up but isn't explicit); 529 is EXCLUDED from
    legacy (earmarked for education), with no non-qualified-withdrawal tax/penalty modeled. The
    `legacyValue` formula (line ~5567): Roth + Brok + HSA*(1-heirHsaTaxRate) + Trad*(1-heirTaxRate) + rebiEnd.
  - **CSS namespacing gotcha (fixed):** the app already has an UNRELATED `.kpi-card` component (~55 refs, with
    `border-left:none !important`). The new exec cards were renamed to **`.es-kpi-card` / `.es-kpi-grid`** to
    avoid the collision that was killing the coloured left-pillars. Print uses separate `pd-kpi-*` classes.
  - **Icon bugs fixed:** reused reference SVG icons; corrected mis-mapped ones (Gifting->dollar, Effective Tax
    Rate->pie); added a **wallet** icon for liquid legacy (its SVG was double-escaped at first -> blank circle;
    fixed the `\"` escaping).
  - **A real bug the redesign surfaced (fixed):** the spending vars `_lifeSpend/_retSpend/_wr/_effRate` were
    block-scoped inside a `try`, so the Spend card first rendered $0 - hoisted them to the outer scope.
  - **In-app Help updated (both apps):** the exec-summary "Stat cards" subsection rewritten for the 6-card
    Build-Spend-Give-Protect-Tax-Leave design incl. the Legacy total-estate/liquid-legacy breakdown; intro
    sentence updated.


- **Print/PDF redesign + Single parity + timeline/education fixes (Aug-22-2026 session).** Large multi-part
  session; everything below shipped to **both** apps unless noted. Baselines held throughout
  (**MFJ $1,176,702 / Single $528,223**).
  - **Full Single port COMPLETE** (was the big PENDING item): the gifting-**reason** feature, the timeline
    "Household" main-line label + tiered dots, and the **entire redesigned print document** are now on Single,
    with single-filer adaptations (one "You" row not H/W; filing label "Single"/"Head of Household" via
    `isHoH()`; ledger age shows ONE age not "46/46"). MFJ and Single are at parity again.
  - **Redesigned print document (`printPlanDocument` -> `#printDoc`, both apps):** branded navy header +
    logo, plan-health hero, 8 stat tiles + "today's dollars" captions, **conditional Monte Carlo block**
    (success rate + p10/median/p90 — appears ONLY if MC was run this session; reads module-scoped
    `mcLastResults`, not persisted), cloned Net-Worth chart, native-SVG **Plan Timeline**, 5-col Plan
    Trajectory ledger (sampled every 5 yrs), Plan Inputs appendix, disclaimer. Profile-menu "Print / Save PDF"
    item + `profileMenuAction('print')`. Critical print CSS: `print-color-adjust:exact` on `#printDoc` + `*`
    (stops the browser stripping the navy header); `.pd-sec{break-inside:avoid}`.
  - **Gifting REASON feature:** display-only reason tag per personal gift (`giftingReasons` map, parallel to
    `giftingRecipients`; ENGINE never reads it). Values home/business/wedding/other; disabled for
    Charitable/Donation. 2-line gift card. Wired into export/import/reset (backward-compatible: old profiles
    w/o the map import clean). Recipient relabeled "Donation" -> "Charitable/Donation".
  - **Timeline tiered dots** sized by gift/flow $ amount: **sm/md/lg = 11/13/15 px** (base 12). Boundaries
    `>200k -> lg`, `>100k -> md`, else `sm`. Applies to both main-line and kid-lane dots. **(NOTE: an earlier
    working summary said 12/16/20 — that was an intermediate iteration; the SHIPPED value is 11/13/15.)**
    Added a "Household" label to the main line.
  - **Education-lane gate BUG fixed (both apps):** kid lanes were gated entirely on `educationEnabled`, so a
    gifts-only child (no education plan) got no lane and their gifts vanished from the timeline. Now a child
    gets a lane if they have education content (when edu on) **OR** tagged gifts; a child with neither is
    omitted. Helpers `_eduOn`/`_childHasGifts`/`_childHasEdu`/`_childHasLane`. Also fixed: education
    bars/rings/`eduTotal` were rendering off the child's own data even when the education TOGGLE was off — now
    all gated on `_eduOn`. **Engine verified correct** (empirically): tuition burn -> $0 and 529 no longer
    drained when edu off; the toggle DOES move spendable EOL when tuition would hit the portfolio (proven by
    forcing a 529 shortfall). The bug was timeline DISPLAY showing phantom education; the engine was already
    right.
  - **Education span bars added to the PRINT timeline (Option B, both apps):** undergrad (orange `#d9822b`) /
    grad (purple `#7c5cbf`) as duration bars in a band below the axis, one row per child, tagged C1/C2, with a
    legend. Print SVG H bumped 168->188. Gated on `educationEnabled`. (Rationale: the print timeline is a
    single line with no kid lanes, so education was previously invisible on it — a real gap for a plan doc.)
  - **Chart contrast:** shared Net-Worth chart gradient opacity **0.55/0.12 -> 0.85/0.45** (Option 1 of a
    rendered 3-way mockup). One gradient def; affects BOTH the live app chart and the print clone (author
    explicitly approved touching the shared chart).
  - **[PARKED] Monte Carlo engine discrepancy:** MC median EOL is ~27-49x the deterministic result in BOTH
    dollar modes (not a units/nominal issue). It's inside the app's MC path-compounding engine. The print MC
    percentile cards are left AS-IS pending a separate authorized MC-engine investigation. Do not "fix" the
    MC print without addressing the engine.
  - **In-app Help updated (both apps):** new section "18b. Printing / Exporting a Plan PDF" (+ TOC entry);
    gifting-reason paragraph in the Children section; child-lane wording corrected for the gate fix.
  - **[SEPARATE, NOT BUILT] Four "lifetime totals"** the author asked about — lifetime gifts-to-kids,
    donations/non-kid gifts, healthcare, tuition/education — are NOT surfaced as clean totals (only Lifetime
    Tax is). All computable read-only by summing existing per-year `aud*` fields (`audGift`, `audTuitionBurn`,
    etc.). Proposed as a future "Lifetime Flows" strip (print + exec summary). See ACCURACY-AUDIT.md.
  - **ACCURACY-AUDIT.md** produced — a full triangulation of docs vs shipped code (findings-only). Numbers all
    checked out; the gaps were feature-DESCRIPTIONS (print, reasons) which the Help fixes above address.

*Keep this list short  it's a pointer to what changed last, not a full history. Details live in the
relevant sections below and in the code.*

- **Kids refactor (MFJ shipped; Single NOT yet ported).** Children are now **Household members**,
  decoupled from Education. A new "Children" sub-section inside the Household input group defines each
  child by birth year only (a year dropdown, matching H/W); it collapses/expands with Household.
  **Education** and **Gifting** now *reference* those children rather than owning them. This fixes a
  real gap: you can model **adult children you want to gift to but have no education/529 for** -- add
  them in Household, leave Education empty, tag gifts to them. Chose **Option B** (keep the single
  `childrenProfiles` array, decouple existence from education) over a full split -- far less blast
  radius, and old exported profiles still import with **no migration** (same array shape).
  - Renderers split: `renderHouseholdChildren()` (identity -> #householdChildrenRows) +
    `renderChildrenProfiles()` (education-cost blocks -> #childrenProfileRows), both refreshed by
    `renderAllChildren()`. The coupling `educationEnabled = childrenProfiles.length > 0` no longer
    gates child *existence*; the Education toggle still gates whether tuition *costs apply*.
  - Verified: MFJ baseline $1,176,702 held throughout; zero-education child does NOT leak into tuition;
    added child is immediately a gift recipient; add/remove/export/import round-trip clean. New Tier-1
    "Children architecture" test added (scoping-safe: drives window fns + observes DOM, since
    `childrenProfiles` is module-scoped and not on window). Help section 15 rewritten.
  - **~~PENDING: port to Single~~ → DONE (Aug-22-2026 session).** Single's `isHoH()` keys off children;
    Single defaults to 0 kids; baseline $528,223 held. See newest session entry at top.


- **529 shortfall re-fixed (engine).** Now routed through the withdrawal solver (cascades
  Brokerage->Trad->Roth, never negative, taxed correctly). Supersedes the earlier pro-rata-basis fix.
  See "529 shortfall  CURRENT MECHANISM" section. Baselines unchanged ($1,176,702 / $528,223).
- **Recon expansion-panel expense table redesigned** to a self-proving 5-column format:
  Expenses | Cost | From HSA | From 529 | From Portfolio, where every row and the total prove
  `Cost = HSA + 529 + Portfolio`. The "From HSA" / "From 529" columns appear ONLY in years that use
  them (collapses to 3 columns otherwise). Old "HSA paid" / "529 paid" bubbles removed. The recon
  "Year reconciles" line gained a `- HSA` term. The confusing "none / -$0" cash-in row is now hidden
  when there is no cash-in.
- **Ledger zone-header colors** (light theme): Roth `#a21caf` magenta, Brokerage `#059669` emerald,
  529 `#ca8a04` gold  chosen to stop Brokerage/529 clashing with the Household-side zone teal/orange.
  Header row in the recon panel darkened with white text. Ported to Single (which previously used pale
  Tailwind-tint headers  now matched to MFJ's saturated style for cross-app consistency).
- **Single: "All years" view toggle button ADDED.** The feature (full vs every-5th-year condensed) was
  fully implemented in Single but had NO button  it was unreachable. Now present, matching MFJ.
- **Disclaimer banner: "Don't show again" button** added inside the orange box (both apps). Persists via
  `localStorage` (`pzero_disclaimer_dismissed`)  hides on future loads until site data is cleared.
  The `x` remains session-only. Fails open (shows banner) if storage is blocked (e.g. sandboxed preview).
- **Parity swept.** MFJ vs Single: click handlers, toggles, IDs, column groups, and help docs are all at
  functional parity. Remaining function-name differences are expected filing-status divergences, not gaps.


---

## How to use this document (and what it does NOT cover)

This file is **one layer of a five-layer system.** It is deliberately *not* a complete specification — it points to the other layers rather than duplicating them. Do not mistake it for exhaustive.

| Layer | Where it lives | What it answers | When to read it |
|-------|---------------|-----------------|-----------------|
| **1. Orientation + decisions** | **This file (CONTEXT.md)** | *How do I work on this safely? Why were things built this way?* | **First.** Always start here. |
| **2. Testing methodology** | **`TESTING.md`** (+ the header comment in `test-suite.html`) | *How is this verified? What does a green run actually prove? What does the suite demand of me before I change anything?* | **Before** you change a tax number, add a money path, or write a test. |
| **3. Product / behavior spec** | **In-app Help docs** (the Help modal inside each app — extensive, audited for accuracy) | *What does the app do? What does each feature, KPI, column, and phase mean?* | When you need to know how a feature behaves. **Help §21 is the machine-readable tax spec** — it is read by the test suite, not just by humans. |
| **4. Ground truth** | **The code** (`index.html` / `p-zero-single.html`) + its inline comments | *How does every calculation actually run, line by line?* | When you need exact mechanics. |
| **5. The verifier** | **`test-suite.html`** | *Is it still right?* | Every time you change anything. Open it, click Run All, read green/red. |

### Which file do I open? — by situation

| You are… | Open | Why |
|---|---|---|
| **an LLM asked to "deep test" / audit / verify accuracy** | `TESTING.md` → the **"FOR AN LLM ASKED TO DEEP TEST"** section at the very top | That is your assignment: the file map, the 8-step playbook, and the traps. Do **not** just run the suite and report green — a 180-green suite hid six bugs. |
| **doing the annual IRS figures update** | `TESTING.md` → the **"FOR AN LLM ASKED TO DO THE ANNUAL IRS UPDATE"** section | Lists which `IRS_2026` fields to update vs leave (statutory), the doc-only SS wage base, authoritative sources, and the both-apps + re-sync steps. |
| **verifying a change you just made** | `test-suite.html` | Serve over HTTP, click Run All. 363 tests, both apps, ~30s. That's the whole interaction — it's a smoke alarm, not a manual. |
| **about to change a tax number** (new tax year, new bracket) | `TESTING.md` **first** | It names the contract: help §21 fact + engine constant + Tier 7 test. **All three, or Tier 0 fails and tells you which one you missed.** |
| **adding a feature that moves money** | `TESTING.md` | Publish the `aud`-prefixed flow + add a conservation scenario. Tier 8's invariant is general, so it already guards features that don't exist yet. |
| **asking "why is it built like this?"** | **CONTEXT.md** (this file) | The decision log. Every non-obvious choice, the reasoning, and what it cost. |
| **asking "what does this feature do?"** | in-app Help | The behavior spec. **Read it before auditing a subsystem** — it states intent (see rule 8). |
| **handing this to a new developer or LLM** | **CONTEXT.md** | It's the entry point and routes them onward. |
| **wondering whether to trust a green run** | `TESTING.md`, honest-status section | Green means *"the specific things we thought to check are still true."* **Not** *"the engine is verified."* That distinction is the whole lesson of this project. |

**If two documents ever contradict each other:** `TESTING.md` is authoritative on **method**; the in-app Help is authoritative on **behavior**; this file is authoritative on **history and rationale**; the **code** is ground truth for mechanics. Fix the loser immediately — a doc that lies is worse than no doc. (This is not hypothetical: a survivor fix once shipped and left three help blocks describing the removed behavior. Tier 0 now exists to catch exactly that.)

**In practice:** most sessions you will only ever touch `test-suite.html`. The rest exist for the person who isn't you, or for you in a year.



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
| `TESTING.md` | Testing methodology + tier-by-tier documentation (Tiers 0–10); the maintenance contract for tax-logic changes |
| `LICENSE` | Proprietary license |
| `CONTEXT.md` | **This file** (was `HANDOFF.md`; before that `FUTURE_ITEMS.md`) |

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
- **MFJ default EOL = `$1,215,092`**
- **Single default EOL = `$540,113`**
- (These moved on 2026-08-30 with the RMD spend-first change; pre-change they were
  $1,176,702 / $528,223. Historical log entries below cite the old values and are left intact.)

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
7. **`test-suite.html` over HTTP** *(green ≠ verified — see the coverage map in Part 2 before trusting it)* — serve the folder via `python3 -m http.server PORT`, load in Playwright (or a browser), click `#runBtn`, read `#summary`. **Must be all-green** (Tiers 0–10 across both apps, including 10 RE/BI tests per app and the Tier 10 recent-features guards). Note: `file://` won't work — the harness reads the apps through same-origin iframes, so it must be served over HTTP.
8. **Compare default EOL to baseline** ($1,215,092 MFJ / $540,113 Single).  [pre-2026-08-30: 1,176,702 / 528,223]
9. **Get ship permission.** 10. **Copy to outputs.** 11. **`present_files`.** 12. **Update this CONTEXT.** 13. **Re-lock.**

### Verification gotchas learned the hard way
- **Headless Playwright screenshots do NOT render inline for the assistant to see.** Verify visuals via `getComputedStyle` / `textContent` / computed colors instead (e.g. light-theme readable text = `rgb(15, 23, 42)`; muted = `rgb(100, 116, 139)`).
- **⚠️ The Tailwind CDN is 403-BLOCKED in the sandbox** (`cdn.tailwindcss.com` and the jsdelivr `@tailwindcss/browser@4` mirror). **Every Tailwind utility is therefore ABSENT in headless Playwright** — `.grid` computes to `display:block`, `lg:grid-cols-*` does nothing, flex classes vanish. Any layout measurement is meaningless by default, and this convincingly masquerades as an app bug. **Workaround:** inject the specific utilities under test via `page.addStyleTag({content: '.grid{display:grid} ...'})`, *then* measure geometry. **Consequence: logic is verifiable here; APPEARANCE IS NOT.** Density, type size, and "does it look right" are browser-only judgments — say so rather than implying a visual was checked.
- **A layout test that doesn't assert a plausible tile width is measuring nothing.** With Tailwind 403-blocked the KPI grid collapses to ~28px, and every overflow check returns a false positive ("8 tiles BLEEDING" — all wrong). Shim real geometry first (`#kpiGrid{display:grid;width:1500px}` + per-tile padding/flex), *then* measure.
- **A JS-built Tailwind class name silently no-ops** (`'lg:grid-cols-' + n`). The browser build only ships classes it can *see* in the static markup. Set the style property directly (e.g. `el.style.gridTemplateColumns`) instead. The code looks correct and does nothing.
- **Wholesale `className =` reassignments are landmines during a restructure.** Several places rebuild a card's full class string on every recalc; if you add a class the markup needs (or change the DOM depth a `parentElement.parentElement` chain walks), those lines silently revert your work. Grep for `.className =` and `parentElement.parentElement` before restructuring any component; prefer `closest('.thing')`.
- **Do not trust a grep *count* as proof a field exists** — read the surrounding context. A `rebiEndValue` match in `chartSeries` was mistaken for the `__scenarioB` snapshot field, and the real gap was only caught when a UI-level test failed on one app after passing on the other.
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
- **Default EOL:** MFJ `$1,215,092` / Single `$540,113`.  [pre-2026-08-30 RMD change: 1,176,702 / 528,223]
- **Filing status:** Single uses `isHoH()` (= has dependents) to switch between **Single** and **Head-of-Household** brackets + standard deduction ($16,100 Single ↔ $24,150 HoH, switches live when a dependent is added via `addChildProfile()`).
- **IRMAA thresholds:** MFJ tiers start at $218K; Single/HoH start at ~half ($109K).
- **Contribution limits display:** identical grouped 3-column layout, but MFJ shows the household 2× logic in the note (401k/IRA are per-person, so a two-earner MFJ household can contribute 2×; HSA family is a single shared plan, NOT doubled). Single notes one-earner = household amount.
- **HSA:** MFJ Fill-Max uses family ($8,750); Single Fill-Max uses self-only ($4,400) — but both apps *display* both figures as reference, and the contribution input is editable so a HoH with a family HDHP can enter the family figure.
- **Semi-income:** MFJ has H + W income (each with its own 1099/W-2 type dropdown); Single has one earner (`wSemiType` is an inert hidden mirror).
- **Survivor scenario:** MFJ models a survivor/widow phase; in Single it is force-disabled (no spouse to lose).
- **Real Estate / Business Investments: NO divergence.** Unlike semi-income (per-spouse), RE/BI is a *household-level* subsystem — same data model, same engine logic, same UI, same Help text, byte-for-byte. This was verified, not assumed. It's the only major feature with zero fork divergence, which makes it the cleanest one to modify (change both apps identically).
- **KPI tiles / compact numbers: NO divergence either.** The KPI grid+tiles markup, the `.kpi-*` CSS, `compactCurrency`/`kpiNum`/`applyKpiGridColumns`, and `setKpiNumberMode` are **byte-identical** in both apps (verified block-by-block, not assumed). The Single port was done by transplanting the *verified* MFJ blocks wholesale rather than re-deriving the edits — the recommended approach for any zero-divergence subsystem. Two unrelated fork facts still bite here: Single's reset calls `setViewMode('condensed')` (MFJ uses `'full'`), and Single's column-group array has no `grpCombined`.
- **Executive Summary / Plan Timeline / gifting recipients + reasons / print document / header chrome: NO divergence (parity re-confirmed through the Aug-22-2026 print+port session).** The multi-lane Plan Timeline, the 8 stat cards + callouts + embedded chart, the Plan Details header block/context strip, the KPI-hidden-by-default behavior, gifting-recipient tagging, and the header chrome (orange border, tab position/styling) were all ported into Single by transplanting the MFJ blocks — but with the engine differences respected and every claim re-validated against Single's engine. Concretely: Single's timeline uses single-person ages ("age N", not "H:/W:"), shows **0 kid lanes by default** (children off), and adds Semi-retires/Fully-retired/Plan-Ends nodes appropriate to a single filer; the stat-card *values* differ (Single's smaller defaults) even though the card *structure* is identical. The color layer was reconciled by aligning Single's 10 drifted light-theme `--` variables to MFJ (MFJ = source of truth) plus restoring the `aside.w-88 { background:#fff }` rule; this is a *rule + variable* reconciliation, so when a color/layout differs between builds, check both the variable values AND whether a CSS rule is simply missing from one build.

## 8. Current state: done vs. deferred

**Everything is shipped and the apps are feature-complete — and as of the Aug-2026 parity session (extended through the timeline/gifting/exec-summary work), MFJ and Single are at full feature parity** (the only intentional difference is the survivor-scenario toggle/section, which is N/A for a single filer). The browser suite runs Tiers 0–10 against **both** builds (Triangulation, Structural, UI-parity, Recon, Invariants, Known-answer IRS ×2, Session, RE/BI, Conservation, Distribution Mix, and Tier 10 Recent-Features); it passes green on both. Help docs are audited, accurate, and now cover the redesign-era UI **and** the Executive Summary / Plan Timeline in **both** apps (see §1c of each app's Help modal). Engine integrity re-verified on both post-parity: MFJ EOL $1,176,702 / Single EOL $528,223, 0 console errors, no NaN.

**Most recent additions (all shipped, both builds):** the multi-lane **Plan Timeline** in the Executive Summary (macro-milestone main line + per-child education/gifting swimlanes with Total-Support end-caps, 5-year gridlines, compression breaks); **gifting-recipient tagging** (`giftingRecipients` map — display-only routing of gift dots to child lanes vs the main line, engine never reads it); the **8-card Executive Summary** (added Retirement Spending, Lifetime Spending, Effective Tax Rate) with strong/watch callouts and an embedded Net-Worth chart; the **Plan Details header block** + populated context strip; KPI cards **hidden by default** on Plan Details (shown in Compare); the **recon-header scoping fix** (scoped to `#ledgerHeaderRow1` so the row-expansion sub-table headers aren't mis-colored); full **header-chrome parity** (orange top-border, workspace-tab position/styling, header height clamp, brand min-width); and a **light-theme color-variable reconciliation** (10 `--` vars aligned to MFJ as source of truth, plus the `aside.w-88` white-background rule). Single's Help docs were reorganized to match MFJ (§1c Executive Summary, §3 group map, §4 KPI dedup, §15 gifting recipients) and validated against Single's engine — catching two real MFJ-leftover doc bugs (children defaults, ACA table row). Tier 10 was added to the suite for both builds.

> ⚠️ **But do not read "all-green" as "the engine is verified."** Green means *"the specific things we thought to check are still true"* — not *"every code path is correct."* That said, the items this note once flagged as untested — **ACA cliff, IRMAA tiers + 2-year lookback, LTCG stacking, the survivor scenario, and RMD×conversion / Roth bracket-fill** — now ALL have targeted Tier 7 coverage, mutation-verified. Coverage is complete across every subsystem (see the Roth-conversion and coverage-complete entries at the end of this file). The standing caution is general, not a list of specific holes: a wrong number still only fails if a known-answer test asserts against an independent source, so keep the maintenance contract (TESTING.md) whenever you touch tax logic.

**Done this project:** single-file carryovers (IRA figures, catch-up funding gate, first-year proration); Federal Tax Details tab made fully read-only from `IRS_2026`; hidden statutory values (IRMAA, ACA schedule, SE tax) exposed as read-only reference; Contribution Limits panel (grouped 3-column, moved to top, per-person/household clarity, cleaner labels, super-catch-up "instead of" fix); W-2 vs 1099 semi-retirement income modeling; full Help-doc sweep + audit; **Real Estate / Business Investments (RE/BI) subsystem** — the largest feature built to date (see the decision log for the full design rationale); **KPI tile redesign** (compact 2dp numbers + hover-expand, dynamic 6/7/8 column grid, compare-mode delta pills, Compact/Exact toggle — see the decision log, and note the Tailwind-403 limit it exposed); two label fixes ("Account Balances (Today's $)", "Roth" not "Roth Core").

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
- **`childrenProfiles` / giftRows** (`let`) — dependent and gifting schedules (module-scoped; call the real functions to mutate). **`giftingRecipients` and `childGiftingProfile`** are also `let`-scoped but are additionally published to `window` at load (`window.giftingRecipients = giftingRecipients; window.childGiftingProfile = childGiftingProfile;`, right after `DEFAULT_GIFTING_RECIPIENTS`) so the Tier 10 gift-routing test can mutate them cross-frame. Inert to the engine (display-layer data); baselines unchanged by the exposure. Note the ref is captured at load — an import/reset *reassigns* `giftingRecipients`, so a stale `window` ref is possible after those; fine for the test's immediate mutate-and-read pattern.
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
- **`compactCurrency()`** — KPI-tile money (`$1.31M` / `$694K`; 2dp at the millions scale, matching the chart axis). **`kpiNum()`** — emits BOTH forms as `.kpi-compact` + `.kpi-exact` spans; CSS swaps them on hover / in Exact mode. **The projection table deliberately uses `currency()`, never these** — tiles scan, the table is the precision home.
- **`toggleColorTheme()`** (light/dark), **`toggleSidebar()`**, **`switchTab()`** (proj/sys), **`toggleColumnGroup()` / `applyColumnGroupVisibility()`** (bucket column show/hide), **`setViewMode()` / `setDollarMode()`** (condensed/full, today's/future $).
- **`setKpiNumberMode('compact'|'exact')`** — toggles `body.kpi-exact-mode`; display-only, runs no math. **Persisted in `snapshot.preferences`** — `checkExportCoverage()` cannot see button-driven modes, so new ones must be added there by hand.
- **`#kpi529Badge`** — 529 status is a badge on the Portfolio Horizon tile, not a tile (one bit of information). Its compare renders on the badge and only when A and B differ. **The ACA tile shows only when `acaOn && totalLifetimeAcaSubsidy > 0`** — enabling ACA is not enough; it must actually earn something. **`applyKpiGridColumns()`** — sets the KPI row's `gridTemplateColumns` from the *live visible tile count* (6/7/8: 6 always-on + RE/BI when deals exist + ACA when enabled), so the row never orphans a tile. Called after every tile show/hide, at init, on font-ready, and on resize. **Sets the style property inline on purpose** — a JS-built `lg:grid-cols-N` class silently no-ops.
- **`toggleDistInputs()` / `toggleSsInputs()` / `toggleSurvivorInputs()` / `toggleRothConvInputs()`** — show/hide conditional input groups.
- **Children/gifts:** children are Household members (post-refactor). Renderers: `renderAllChildren()` -> `renderHouseholdChildren()` (identity/birth-year in Household) + `renderChildrenProfiles()` (education-cost blocks in Education). Also `addChildProfile()`, `removeChildProfile()`, `updateChildField()`; `renderGiftRows()`, `addGiftRow()`, `removeGiftRow()`, `updateGiftAmt/Year()`. NOTE: `addChildProfile()` is what flips Single into HoH (Single port still pending).

### Real Estate / Business Investments (RE/BI)
- **`renderRebiDeals()`** — renders the repeatable deal cards into `#rebiDealRows` (red-X remove, matching the gifts/children pattern).
- **`addRebiDeal()` / `removeRebiDeal(id)` / `updateRebiField(el)`** — list mutation; each calls `renderRebiDeals()` + `triggerRecalculate()`.
- The **engine logic has no dedicated function** — it lives inline in `triggerRecalculate()`'s year loop, in a block right after the `gross1099` payroll block (search for `Real Estate / Business Investments (RE/BI)`). It computes, per year: `rebiDistTotal`, `rebiDistTaxable`, `rebiStartValue`, `rebiEndValue`, `rebiRefiCash`, `rebiExitProceedsGross`, `rebiExitGainLtcg`, `rebiRecaptureTax`. Those feed the tax machinery at seven integration points (see the decision log for the full list).

### Rendering & charts
- **`renderNetWorthChart()`** — draws the main projection chart; **`showChartTooltip()` / `hideChartTooltip()`** (uses `__chartSeries`).
- **`renderCompare()`** — the A/B compare view; **`pinScenarioA()` / `clearScenarioA()` / `swapScenarios()` / `toggleCompareMode()`**. Tiles show a bold `A:` value + a coloured delta pill (green = B better, red = worse, grey = neutral); deltas are **B − A**. The scenario *name* appears once in `#compareBar`, never repeated per tile. `window.__scenarioB` carries `rebiEndValue` for the RE/BI compare row — **if you add a KPI, add its field to that snapshot or its compare row silently reads 0.**

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
the IRS_2026 block. Single's std-deduction display is filing-status-aware ($16,100 Single / $24,150 HoH,
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

## KPI tile redesign — compact numbers, dynamic grid, hover-expand, compare pills (shipped, both apps)

### WHY — the user's actual complaint and the reframe that mattered
After RE/BI shipped, a 7th KPI tile joined the row and the author sent a screenshot: the tiles wrapped to a second row with a single orphaned tile stranded below. The obvious reading is "too many tiles." The author's own diagnosis was better and became the whole design: **the numbers are too WIDE, not too numerous** (`$1,309,908` is 10 characters of precision nobody scans a dashboard for). That reframe pointed at compaction rather than at deleting or hiding KPIs.

### WHAT — the feature
KPI cards now show **compact figures by default** (`$1.31M`, `$694K`) and expand to exact dollars on hover, in place, with no layout shift. The row **sizes its own column count** to however many tiles are actually visible. Compare mode drops the repeated scenario name and shows a bold `A:` reference value plus a coloured delta pill. A **Compact/Exact toggle** sits beside the Dollars toggle for when hover isn't available.

### HOW — the design decisions and their rationale
- **[DECISION] Compact format with TWO decimals at the millions scale** (`$1.31M`, not `$1.3M`). The author was explicit that 2dp is a must, and the reason is sound: at 1dp, a $10,000 difference between two scenarios is invisible (`$1.3M` vs `$1.3M`) — which defeats the entire point of Compare mode. Reuses the convention the net-worth chart axis already used, so the app speaks one dialect.
- **[DECISION] Compact applies to KPI TILES ONLY — the projection table keeps full exact dollars.** The author confirmed this explicitly. The division of labour: tiles are for *scanning*, the table is the *precision home*. Compacting the table would have destroyed the auditability that makes the year-by-year math checkable.
- **[DECISION] Dynamic column count (6/7/8), not a fixed grid.** This one changed mid-build and is worth understanding. The author approved "7-across" from a screenshot showing 7 tiles — but the screenshot had **ACA off**. There are in fact **8 possible tiles**: 6 always-on, plus RE/BI (only with deals) and ACA Subsidy (only when ACA is on). A fixed `grid-cols-7` therefore **reproduces the exact orphan bug being fixed** in the RE/BI-on + ACA-on case. Flagged before building; the author chose dynamic. The grid now reads its own visible-child count and sets `gridTemplateColumns` inline. **Verified at 6→6 cols, 7→7 cols, 8→8 cols, one clean row each.**
- **[DECISION] Set `gridTemplateColumns` inline, NOT via a JS-built Tailwind class.** `'lg:grid-cols-' + n` silently no-ops: the Tailwind browser build only ships classes it can *see* in the static markup. This is a real trap — the code looks right and does nothing.
- **[DECISION] Hover-expand shrinks the type so nothing reflows.** Both forms of every number are emitted (`kpiNum()` → a `.kpi-compact` span + a `.kpi-exact` span); CSS swaps them on `.kpi-card:hover` and drops the font size. Native `title` tooltips were rejected by the author. Verified: zero width change on expand.
- **[DECISION] Keep BOTH hover and a global Compact/Exact toggle.** Hover doesn't survive a screenshot and doesn't exist on touch. The toggle is pure display — one body class, no recalculation.
- **[DECISION] Compare mode "P3": scenario name ONCE, bold `A:` value, coloured delta pill.** The old tiles repeated the user-typed scenario name in every card — the single biggest space-waster, and a long name could break the row on its own. The name already lives in the existing `compareBar` above the grid, so the tiles just say `A:`. Deltas are **B − A**; green = B better, red = worse, grey = neutral.
- **[DECISION] Fixed label height (`.kpi-lbl` min-height) + bottom-pinned deltas (`margin-top:auto`).** Puts every primary number on one baseline and bottom-aligns every compare row without inventing filler content. The author considered trimming labels to help alignment and chose **no trims** — alignment holds regardless.

### HOW IT WAS BUILT — and the six bugs verification caught
MFJ first, fully verified, then transplanted to Single (the KPI markup was **byte-identical** between the apps, so the verified blocks were ported wholesale rather than re-derived — no drift). Every one of these was found by checking, not by reading the diff:
1. **A pre-existing `classList.toggle('lg:grid-cols-7', acaOn)` pair** was still fighting the new dynamic grid — the old mechanism for the conditional ACA tile.
2. **Five `className` rewrites** rebuilt tiles wholesale from stale class strings and reached them via `parentElement.parentElement` chains that the new label wrapper broke — silently dropping tiles out of the aligned/hover layout on **every recalc**. Now `closest('.kpi-card')` (4 real call sites per app).
3. **MFJ's `__scenarioB` snapshot never carried `rebiEndValue`** → the new RE/BI compare row would have always read $0.
4. **Single's snapshot was missing it too.** Caught only because a UI-level test failed on Single after passing on MFJ. A grep had *appeared* to confirm the field's presence — it was matching the unrelated `chartSeries` field. **Trusting a match count instead of reading the context nearly shipped this.**
5. **`currency()` was deleted** while inserting `setKpiNumberMode` — the app's most-used formatter. Threw on every recalculate; caught by the page-error check.
6. **Help docs described the old `Total incl. RE/Business` label** after the UI shortened it to `incl. RE/Biz` (in §4 *and* §15b).

### A methodology limit worth knowing about (NEW — affects all future layout work)
**The Tailwind CDN returns 403 in the sandbox** (`cdn.tailwindcss.com` and the jsdelivr `@tailwindcss/browser@4` mirror are both network-blocked). Every Tailwind utility is therefore **absent** in headless Playwright — `.grid` computes to `display:block`, so *any* layout measurement is meaningless by default. This masqueraded as an app bug for several debugging rounds. **Workaround:** inject a CSS shim with the specific utilities under test via `page.addStyleTag({content: SHIM})`, then measure geometry. **Consequence:** logic is verifiable here; *appearance* is not. Tile density at 8-across and how `$1.31M` reads at `text-lg` were explicitly flagged to the author as browser-only judgments.

### Help docs
New **"KPI number format — Compact vs Exact"** block in §4 of both apps: the 2dp rationale, hover-expand, the toggle, the tiles-vs-table division, and the 6/7/8 dynamic row. Both stale `Total incl. RE/Business` references synced to `incl. RE/Biz`. Zero dangling links in either app.

### Final verified state
Suite **146/146 ALL GREEN** with both modified apps loaded (no test read KPI tile strings — they read the projection table and `__scenarioB`, which is why compaction broke nothing). Baselines held: MFJ **$693,546**, Single **$607,219**. Harness ALL OK both (violations ≤1). Syntax OK; div/section balanced; zero duplicate IDs; zero page errors. Verified per app: compact at rest / exact on hover with **zero width shift**; toggle flips the body class and button states; Reset restores Compact; 6/7/8 → one clean row; compare shows bold `A:` + pills with no repeated name; RE/BI compare row reads `A: $206K  +$206K` with a correct green pill. KPI subsystem confirmed **byte-identical** across both apps (grid+tiles, CSS, helpers, `setKpiNumberMode`).

## Renamed HANDOFF.md → CONTEXT.md (shipped)

The author's observation: *"We shouldn't really call this 'Handoff' file .... more like 'context' for LLMs and future developers right?"* — correct, and not merely cosmetic.

**Why the old name was wrong.** "Handoff" describes a *one-time transfer* — I'm leaving, you're arriving, here's the baton. That is not what this file is or how it has ever been used. It's read at the **start** of sessions, consulted **mid-build** ("what's the baseline?", "is this a known simplification?", "what does `dispScale` do?"), and appended to at the **end**. It is a persistent, continuously-consulted context document. The name quietly misdescribed the artifact from the day it was created.

**Why it matters practically, not just semantically.** An LLM handed a file called `HANDOFF.md` may reasonably read it once and move on — a handoff is, by definition, a thing you receive. `CONTEXT.md` invites *re-reading*, which is exactly the behavior this file's own operating rules (§⚑) ask for. The name should reinforce the intended usage pattern, not fight it. `CONTEXT.md` is also where LLM tooling convention has landed (`AGENTS.md`, `CLAUDE.md`, `.cursorrules` occupy the same niche); `PROJECT_CONTEXT.md` was considered and rejected as redundant inside a project repo.

**[DECISION] Live references were rewritten; historical entries were NOT.** The word appeared in two distinct roles, and conflating them would have corrupted the record:
- **Live self-references** (title, the §⚑ operating rules, the "how to use this document" table, the file map, verification-recipe step 12) → updated to CONTEXT.
- **Historical decision-log entries** ("Handoff documentation — this file", "Code-architecture map added to HANDOFF (§10)") → **left verbatim**. Those entries describe decisions made at a time when the file genuinely *was* named HANDOFF.md. Rewriting them would falsify the history. This follows the same rule already applied to the stale `126/126` suite counts preserved in older entries: **the log is a record of what happened, not a mirror of the current state.** Only Part 1 tracks current state.

The file map row deliberately records the full lineage (`CONTEXT.md` ← `HANDOFF.md` ← `FUTURE_ITEMS.md`) so the rename is discoverable rather than mysterious. `FUTURE_ITEMS.md` (a stub since the merge) was re-pointed at the new name. Zero references existed in either app, so no app changes were needed.

## KPI follow-up: doc sweep, a persistence bug, and the tile-count reduction (shipped, both apps)

### The doc sweep the author asked for — it found real problems (again)
The author asked *"All help docs are updated w the latest app updates for both apps? Do we need to do one more sweep?"* The answer was **no, they weren't** — the same lesson as the RE/BI Help audit, one level deeper. Three findings:
1. **A shipped formatting bug in BOTH apps.** The RE/BI doc pass had spliced its sentence *mid-sentence* into §18: *"It deliberately does **Real Estate...travel with it.**not save the federal tax tables"*. Live in production. The two apps had **different surrounding prose**, so a single find/replace correctly failed on one rather than mangling it — fixed separately.
2. **`sec-dollars` never mentioned the new KPI Numbers toggle** despite documenting the control sitting *directly beside it*. Added a cross-reference: Dollars changes what numbers **mean**; KPI Numbers changes how they're **written**.
3. **A real feature bug hiding behind a doc gap** (below).

### [BUG] `kpiNumberMode` was not persisted — found by checking a doc claim
§18 listed saved preferences as "(theme, view mode, dollar mode, visible column groups)". Checking whether that list was merely stale revealed **the new Compact/Exact preference was never saved at all**: set Exact → export → import → silently back to Compact. **`checkExportCoverage()` structurally cannot catch this** — it only scans `input`/`select`/`textarea`, and the toggle is a pair of `<button>`s (same reason `dollarMode` had to be added to `preferences` by hand). Now saved + restored, verified through the real `exportConfig()` blob. **Lesson: any new button-driven display mode must be added to `snapshot.preferences` manually; the guard will not warn you.**

### The screenshot that logic tests could not replace
The author sent a screenshot of the 8-tile row. It exposed **three** bugs, two of which were invisible to every test written:
1. **Labels wrapped to 3+ lines and overflowed.** `.kpi-lbl` used `min-height:26px` — **a floor, not a ceiling.** At 8-across (~175px tiles) four labels needed 3–6 lines. Fixed: hard `height:26px` + `-webkit-line-clamp:2` + `title` on the label for the full text.
2. **Compare pills bled outside the tile.** `whitespace-nowrap` had been put on the **entire delta row**, making `A: 95+ Secure` + pill one unbreakable 195px line in a 175px tile. The pill already carries its own nowrap (correct — pills shouldn't break internally); the row-level one was redundant *and* harmful. Removed from all 8 rows × 2 apps.
3. **A 6th `className` rewrite** (`kpiAcaSubsidy`, ~line 2721) still used pre-redesign classes and stripped `kpi-val`, silently breaking the ACA tile's hover-expand. Five had been caught during the build; this one shipped. **Grep `.className =` exhaustively — five is never all of them.**

**A verification trap worth remembering:** the first geometry test reported *"8 tiles BLEEDING"* — a **false positive**. With Tailwind 403-blocked the grid collapses to ~28px, so every overflow reading was garbage. Measuring anything required a shim forcing real geometry (`#kpiGrid{display:grid;width:1500px}` + per-tile padding/flex). **A layout test that doesn't first assert a plausible tile width is measuring nothing.**

### [DECISION] Reduce the tile count rather than shrink the tiles (author's call: "A+B")
The author asked whether tiles could be combined or removed. Analysis of the screenshot by *information density*:
- **529 Status** — a full tile for **one bit** (Funded / Underfunded), almost always the boring value.
- **Lifetime ACA Subsidy** — read **$0**, and was visible whenever the ACA toggle was on *even when the plan can never earn a subsidy* (e.g. retiring after 65 straight onto Medicare). A slot spent saying "nothing happened".
- **RE/BI $103K** — partially duplicated the `incl. RE/Biz` sub-line on the Liquid Net Worth tile.
- Liquid Net Worth **already proved** two values can share one tile (primary + sub-line).

Options presented: **(A)** 529 → badge, **(B)** hide ACA when $0, **(C)** merge RE/BI into Liquid Net Worth as a second sub-line, **(D)** two rows of 4. Author chose **A+B** — both remove *zero* information while freeing two slots. **C was explicitly kept in reserve** (RE/BI is a real asset class worth its own tile when held); D was rejected as abandoning the single-row goal.

- **[DECISION] 529 → badge on Portfolio Horizon** (`#kpi529Badge`). Thematically right: Portfolio Horizon *already excludes* 529, so the badge completes that picture ("...and the education money is fine too"). Underfunded gets the loud red; Funded is muted. **Its compare moved onto the badge and only renders when A and B differ** — "both funded" is the boring default and doesn't earn pixels. `d529` was deleted, so it was removed from the compare-reset loop — where **`dRebi` turned out to have been missing**, and was added.
- **[DECISION] ACA tile shows only when `acaOn && totalLifetimeAcaSubsidy > 0`.** Verified in both directions and it immediately proved itself: **MFJ default earns $0 → hidden; Single default earns $61,804 → shown.**
- **[DECISION] RE/BI tile moved to sit directly after Liquid Net Worth, before After-Tax Legacy** (author's suggestion). Legacy had been wedged between the two asset tiles, so the eye couldn't compare `$2.54M liquid` against `$103K illiquid` without jumping. Order now reads: *what you have* (liquid → illiquid) → *what you leave* (legacy) → *mechanics* (brokerage, tax).
- **[DECISION] "After-Tax Legacy (to heirs)" → "After-Tax Legacy."** The author: *"that is already known by the word 'legacy'."* Correct — pure redundancy.

**Result: worst case 8 tiles → 7; default 5.** Tile width at worst case went 175px → 202px (Single) / 238px (MFJ, 6 tiles). Zero overflow anywhere, one row, verified both apps.

### Final verified state
Suite **146/146 ALL GREEN** (no test touched the 529/ACA tiles). Baselines held: MFJ **$693,546**, Single **$607,219**. Harness ALL OK. Syntax/div/section/tr balanced; zero duplicate IDs; zero dangling help links; zero page errors. KPI subsystem still **byte-identical** across both apps. Docs updated for all of it: the 529 badge, the ACA >$0 rule, and the tile-count claim (corrected from "6, 7, or 8" to "5 by default, up to 7").

## ⚠️ TEST COVERAGE — an honest map of what 146/146 does NOT prove (READ THIS)

The author asked: *"Do we need to do a thorough QA ... this is a financial planning/projection app — accuracy matters."* The honest answer is **yes**, and this section exists so no future session mistakes a green suite for a verified engine.

**"146/146 ALL GREEN" is a narrower claim than it sounds.** What the suite actually covers:

| Category | Coverage | Verdict |
|---|---|---|
| Structural (loads, functions exist, years contiguous, series shape) | Tier 1–2 | **Solid** |
| Invariants (no negative balances, spendable ≥ buckets, balance identity ≤$5) | Tier 2 + `harness.js` | **Solid** |
| **Isolated** tax math vs hand-derived IRS values | Tier 3 | **Genuinely good** — brackets (Single/HoH/MFJ across all 7 tiers), standard deductions, RMD divisors, SE tax |
| Feature behaviour (directional: "X raises EOL", "toggle changes output") | Tier 5 | Adequate |
| RE/BI exact values (distribution, appreciation, COLA, refi, exit) | Tier 6 | **Good** — 10 tests/app |
| **Composed, end-to-end scenarios** | — | **LARGELY ABSENT** ⚠️ |

### Live engine subsystems with ZERO targeted tests
Verified by grepping both the engine and the suite — these are **implemented, shipped, and unverified**:

| Subsystem | Engine refs | Suite tests |
|---|---|---|
| ACA cliff / `acaMagi` / `ACA_PCT` | 9 / 5 | **0** |
| IRMAA tiers / `irmaaMagi` | 9 / 3 | **0** |
| LTCG stacking / `preferentialGains` (incl. the 0% bracket) | 3 | **0** |
| Survivor / widow scenario (`survivorSpendPct`) | 3 | **0** |
| RMD × Roth-conversion interaction | — | **0** |

**Why this is the real risk.** Tier 3 proves the *pieces* are right (`marginalTax()` on a known income). Almost nothing proves the *composition* is — and composition is exactly where a projection engine goes wrong: a large RE/BI exit pushing MAGI over the **ACA cliff**, or across an **IRMAA tier**, in a year when **RMDs stack on top of a conversion** and **LTCG** fills the 0% bracket from below. Every one of those paths is live code the suite never exercises. The harness catches *balance* violations, not *tax* errors — a wrong-but-consistent tax number sails through every check currently in the project.

### NEXT WORK ITEM — Tier 7: composed known-answer scenarios (agreed with the author)
Build hand-computed, full-year known-answer tests asserting **exact** figures (the Tier 3 method, applied to whole years instead of single functions):
1. **ACA cliff edge** — MAGI just under vs just over; assert the subsidy delta.
2. **IRMAA tier boundary** — MAGI at a tier edge (remember the **2-year lookback**); assert the premium.
3. **0% LTCG bracket** — gains stacking on ordinary income; assert preferential tax.
4. **Survivor transition** — MFJ → single brackets + `survivorSpendPct`; assert the year's tax.
5. **RMD + conversion in one year** — assert ordinary income, the conversion headroom consumed, and the tax.

Method that works (proven by Tier 3 and Tier 6): hand-derive the expected value in a comment block *first*, then assert against it with `TOL = 0.02`. Use `setDollarMode('future')` for exact checks and restore in a `finally`. Remember `window.__chartSeries` exposes rich per-year detail but **not** the deep tax internals (`preWithdrawOrdinary`, `seTax`, `seDeduction`) — for those, add a temporary debug hook to the `chartSeries.push({...})` call, verify, then remove it.

## RE/BI refi & exit year: a silent data-loss bug, fixed with dropdowns (shipped, both apps)

### What the author reported (and what each report turned out to be)
Three observations from a screenshot of the RE/BI detail table. **One was not a bug; two were serious.**

**1. "End value / distribution never changes" — NOT A BUG. The engine is correct.**
The default deal appreciates at **3%** and default inflation is **3%**, so in *Today's $* mode they **cancel exactly**. $100k growing at 3% genuinely *is* worth $100k in today's purchasing power when prices rise 3%. Verified by switching modes:
- *Future $* (nominal): 100,000 → 103,000 → 106,090 → … and distributions COLA 7,000 → 7,210 → 7,426. **Compounding works.**
- *Today's $* @ 6% appreciation: 100,000 → 102,913 → 105,910. **Grows, because 6% beats 3% inflation.**
- *Today's $* @ 3% appreciation: flat — **correct**, zero real gain.

This is now documented in §15b ("Why the table can look flat in Today's $"). **Do not 'fix' this.** It is the same real-vs-nominal property already documented for the projection table in §2.

**2. [BUG] Refi never fired.** The engine matches `currentYear === refiYear` — a **calendar** year (2026) — but the label only said *"Refi year"*, so entering `4` (meaning "year 4 of the plan") was the natural reading, and `2026 === 4` is never true. Silent no-op.

**3. [BUG — the dangerous one] Exit year zeroed the entire position.** `held = (exitYr === 0) || (currentYear < exitYr)`. With `exitYear = 5`, `2026 < 5` is **false**, so the engine concluded the deal had *already sold before the projection began*. The position vanished from every year — and since `exitValue` defaults to 0, **the asset disappeared with $0 proceeds. No error, no warning.** Silent data loss in a financial planning tool.

**Root cause (mine, from the original RE/BI build):** the UI invited a plan-relative year while the engine demanded a calendar year, and nothing anywhere made the contract visible. The design decision was recorded as "refiYear/exitYear" without ever stating *which kind of year*.

### [DECISION] Fix with a dropdown, not validation (author's call)
Options offered: **(A)** accept both and disambiguate by magnitude (<100 = plan-relative), **(B)** explicit calendar year + validation, **(C)** explicit plan-relative. Author chose **B — but as a dropdown rather than a validated text field**, which is strictly better than what was proposed: it makes the invalid input **structurally unreachable** instead of caught after the fact. Bug #3 becomes *impossible*, not merely *detected*.

- `rebiYearOptions(selected)` builds `—` (value 0 = no event) plus every calendar year the projection covers (`startYear` … `startYear+80`, matching the engine's `for (let i=0; i<=80; i++)` loop). 82 options.
- Label deliberately **unchanged** ("Refi year" / "Exit year") — the author's call; the dropdown contents now make the units self-evident, so the label doesn't have to.
- `updateRebiField()` needed **no change** — it already did `parseInt(el.value) || 0` for these fields, which works identically for a `<select>`, and `"0"` → `0` = no event.
- **B was chosen over A** because the rest of the app is absolute (ages, calendar years) — one mental model beats a magic <100 rule.

### [DECISION] Sanitize legacy profiles — the dropdown alone was not enough
A saved profile from before this fix can still carry `exitYear: 5`. The dropdown would fall back to `—` (looking correct) **while the data still said 5 and the asset still vanished** — the UI and the data disagreeing, arguably *worse* than the original bug because it looks fine. `sanitizeRebiYears()` normalises any non-zero year earlier than `startYear` to `0` (= no event, deal held — the safe, visible default) and warns to console. Wired into **`renderRebiDeals()`**, which is the single choke point covering init, import, and reset. Verified: a legacy `{refiYear:4, exitYear:5}` profile is rescued — the asset survives instead of vanishing.

### Verified
Full lifecycle in *Future $*, both apps identical: compounds 100,000 → 130,477, distributions COLA 7,000 → 8,867, **refi fires 2030 = $30,000**, **exit fires 2035 = $180,000**, zeroes after. Exit tax math unchanged and still matches the original hand-derivation (basis 100,000 − 30,000 refi = 70,000; gain 110,000; recapture min(110,000, 20,000) = 20,000 @25% = $5,000; LTCG 90,000). Suite **146/146**, baselines held ($693,546 / $607,219), harness ALL OK, zero dangling links, zero page errors, `rebiYearOptions`/`sanitizeRebiYears` byte-identical across apps.

### The lesson
**A field whose bad value silently destroys data is worse than one that errors.** The original build hand-verified the *arithmetic* of refi and exit thoroughly (see the RE/BI entry) but never tested **what a plausible user input does** — every test passed a calendar year, because the author of the tests was the author of the engine and already knew the contract. **Tier 6 has 10 RE/BI tests and not one of them would have caught this.** Worth remembering when building Tier 7: test the inputs a *user* would plausibly type, not just the ones the engine expects.

## RE/BI input card: 2-column grid + grouped sections (shipped, both apps)

### WHY — the author's report was "ugly, messy, none of the fields align"
A screenshot of the left panel. The card wasn't merely unattractive; **three distinct defects** were compounding:
1. **The column count changed per row** — the card stacked `grid-cols-3`, `grid-cols-3`, `grid-cols-4`, `grid-cols-4`. No vertical edge lined up anywhere down the card. This is the "nothing aligns" complaint, and it wasn't a styling accident — the card simply grew a row at a time.
2. **Long labels wrapped, short ones didn't.** At ~110px per 3-col cell, roughly 16–18 characters fit on one line. **Four of the eleven labels exceed that** ("Distribution taxable %" = 22, "Annual distribution" = 19, "Appreciation %/yr" = 17, "Recapture %" wrapped in situ). A wrapped label is taller, so **its input dropped below its row-mates** — the actual misalignment visible in the screenshot (the Appreciation box sitting lower than Invested/Current).
3. **The last row was a 4-col grid holding one field plus a prose blurb**, so "Recapture %" sat stranded beside a paragraph.

### [DECISION] One 2-column grid throughout + three grouped sections (author's call)
At 2-col the cells are ~165px, where **every label fits on one line** — so the wrap-induced misalignment cannot occur at all, rather than being patched. Options offered were 2-col grouped / 2-col flat / one-field-per-row (the pattern the Children cards use); the author chose **2-col + grouping**, and grouping earns its keep because 11 flat fields is a wall of inputs with no structure:
- **Position** — Invested (Basis), Current Value, Appreciation %/Yr
- **Income** — Annual Distribution, Distribution Taxable %, Dist. COLA
- **Capital Events** — Refi Year, Refi Capital, Exit Year, Exit Value, Recapture %

- **[DECISION] Title Case on every label** (author's call, in place of shortening them). Shortening was offered ("Taxable %", "Appreciation %") and **declined** — consistent with the earlier KPI decision to keep labels intact. At 2-col the extra width costs nothing, so there's no reason to abbreviate.
- **[DECISION] `.rebi-lbl { min-height: 13px }`** — belt-and-braces. Every label fits on one line *today*; the pinned height means a longer label added later still can't break the shared baseline. Same technique that fixed the KPI tiles.
- **[DECISION] The three orphan fields span both columns.** Each group has an **odd** field count (3/3/5), so exactly one field per group is unpaired — that's unavoidable, not a pairing mistake. A half-width input sitting beside empty space reads as a rendering bug; the same field at full width (`col-span-2`) reads as deliberate. Verified: 154px for paired fields, 316px for the three spanned ones.
- **[DECISION] The "On exit:" prose left the grid** and became a full-width footnote, which is what it always was semantically.

### MFJ vs Single — the author explicitly asked
RE/BI is **household-level, so this panel has zero filing-status divergence by design** (unlike semi-income, which *is* per-spouse). Verified **byte-identical before** the change (5,857 chars each) and **byte-identical after** (renderRebiDeals 6,733 chars; card CSS 794 chars). Method: build and verify on MFJ, then splice the identical block into Single — never hand-edit twice, which is how forks drift. Nothing in this card is filing-status dependent, so there was nothing to make "contextual"; the honest answer to *"make it contextual to MFJ vs Single"* is that **for this subsystem there is no contextual difference, and inventing one would be a bug.**

### Verified
All **12 fields wired** in both apps (name, capital, currentValue, apprPct, annualDist, distTaxablePct, distCola, refiYear, refiCapital, exitYear, exitValue, recapturePct) — set through real `change` events, read back off the live deal object. **Zero misaligned rows, zero wrapping labels, every 2-col row sharing identical column edges (20, 182).** Zero legacy 3/4-col grids remain. Full RE/BI lifecycle unaffected: refi 2030 = $30,000, exit 2035 = $180,000, zeroes after. Suite **146/146**, baselines held ($693,546 / $607,219), harness ALL OK, zero page errors.

### Note for whoever styles this next
The measurement trap from the KPI work applies here too and cost real time again: **with Tailwind 403-blocked, the card collapses and every alignment reading is a false positive** (an early run reported everything "✓ aligned" purely because the shim gave labels infinite room — the exact opposite of the truth in the author's screenshot). Force the real geometry first (`#rebiDealRows > div{width:340px}` + grid/label/input rules, **including `col-span-2`**), then measure. And note what the shim can't tell you: **the author's screenshot remains the ground truth for appearance.**

## Docs + suite follow-up: 12 new regression tests, mutation-verified (shipped, 146 → 158)

The author asked *"Do we need any docs updated here? or test suite updates?"* Checking rather than asserting found **yes to both**.

### Docs — §15b named every field in the old casing
The card redesign put labels in Title Case, but §15b still said "Current value", "Appreciation %/yr", "Annual distribution", "Distribution taxable %", "Refi year", "Refi capital", "Exit year", "Exit value" — so the help text no longer matched what the panel showed. All synced in both apps, plus the intro now names the **Position / Income / Capital Events** grouping so the doc reads in the same order as the UI. **Verified programmatically rather than by eye: all 11 live UI labels are now present in §15b in both apps.**

### Suite — the card redesign broke nothing, and that was the problem
Zero tests touch the card DOM (`rebiDealRows`, `data-field`, `grid-cols` — all 0 hits). That's *why* 146/146 stayed green through a full layout rewrite: **Tier 6 drives the data accessors, never the UI.** Robust, but it's precisely the blind spot that let the refi/exit bug ship. Every bug fixed in the last few sessions was still unguarded:

| Shipped bug | Test existed? |
|---|---|
| refi/exit accepted a plan-relative year → **silent data loss** | **No** — every test fed a calendar year |
| legacy profile with `exitYear:5` destroys the asset | **No** — no test loads a stale profile |
| `kpiNumberMode` not persisted in export | **No** — no test round-trips preferences |
| `kpiAcaSubsidy` className stripped `kpi-val` | No — no test reads tile classes |

**Added 12 tests (6 per app), 146 → 158, all green:**
- **Tier 6 ×3** — stale plan-relative years sanitise to 0 on load; a deal with stale years still holds its value (*"asset not silently destroyed"*); the year dropdown offers only `0` or calendar years ≥ startYear.
- **Tier 5 ×3** — the Compact/Exact toggle drives the display mode; `exportConfig()` runs and produces a blob; **`kpiNumberMode` is included in saved preferences**.

### [DECISION] Mutation-test the new tests before trusting them
A green test proves nothing until you've seen it fail. Both bugs were **reintroduced into a throwaway copy** (sanitizer call deleted; `kpiNumberMode` dropped from `snapshot.preferences`) → **6 failures, each caught by the right test, in both apps.** These are real regression guards, not decorative checkmarks. **Do this for any test claiming to guard a specific bug** — otherwise you've written a test that asserts the sun rose.

### The `let`-not-on-`window` gotcha bit again
The first version of the KPI test read `win.kpiNumberMode` → `undefined`. It's a module-scoped `let`, exactly like `childrenProfiles` and `rebiDeals` — **a gotcha already documented in this file, walked into anyway.** The feature was fine; the test was wrong. Rewritten to assert **observable state** (`body.kpi-exact-mode`, button classes) plus a source check on `exportConfig.toString()`. That's the better test regardless: it verifies what the user actually experiences rather than an internal variable, and it can't be fooled by a rename.

## RE/BI capital-events DOUBLE-COUNT — the most serious bug in this project (shipped, both apps)

### The path here
The user asked three plain questions about a screenshot — "when does the RE/BI tile show?", "where do refi/sale $$ go?", "why is 2030 spending anything, both spouses are working?" — and pushing on the third one uncovered a bug that had been silently overstating every RE/BI projection's wealth for the whole session. **A $100,000 refi was adding ~$198,700 to brokerage — roughly 2x.**

### Root cause
Two independent code paths both credit RE/BI capital proceeds to `brok`, and neither knew about the other:
1. **`excessCapital`** (correct, ~line 2645): proceeds minus what they funded, banked to brokerage.
2. **`excessRmd`** (the leak, ~line 2621): `rmdUsedForSpending = Math.min(forcedRmd, need - cashSources - draws + forcedRmd)`. With `forcedRmd = 0` (any pre-RMD-age year — i.e. virtually the whole plan) and `cashSources` inflated by a large refi, the inner expression goes deeply negative (e.g. `-98,648`), so `Math.min(0, -98,648) = -98,648`. Then `excessRmd = Math.max(0, forcedRmd - rmdUsedForSpending) = Math.max(0, 0 - (-98,648)) = +98,648` — **a negative "amount of RMD used" flips sign into a positive "excess RMD," which gets banked to brokerage a second time.** Phantom money, from a formula that was never guarding its lower bound.

**Why 10/10 Tier 6 tests and every prior harness run missed it:** the leak only fires when `cashSources` is large, which only happens when a refi/exit exists. Every test that predates RE/BI passed cleanly (small `cashSources`). Every RE/BI test that existed checked that a refi/exit **fires** and that its **tax** is correct — none checked that net worth moved by the **right amount**. A test suite can be 100% green and still certify a number that's 2x wrong.

### The fix — one line
```js
let rmdUsedForSpending = Math.max(0, Math.min(forcedRmd, ...));
```
`rmdUsedForSpending` means "how much of this year's forced RMD went to covering need" — it cannot be negative (you can't spend a negative amount of your RMD). The missing floor was the entire bug.

### [DECISION] Traced through three of the user's questions before touching engine math — each one killed a wrong plan
1. **"Why is 2030 spending anything — both spouses are working?"** → led to discovering the refi was silently absorbing that year's *routine tax draw* (not spending), diverting real cash into a role the portfolio was already covering.
2. **My first proposal** ("stop netting proceeds against need") was wrong and would have made the plan *worse*: a brokerage withdrawal realizes capital gains, so having the refi pay tax directly (current behavior) legitimately avoids ~$82 of extra tax vs. selling shares. **The netting itself was correct; only the display was unreconcilable.**
3. **"What about semi-retirement?"** → the user's scoping question ("only fix this while not retired/semi-retired and not drawing from brokerage") caught a second near-miss: 2036 (semi-retired) has portfolio-wd = $0 *and* a genuine $85,053 living need that the refi correctly absorbs. A phase-based or withdrawal-based gate would have banked the FULL $100k in 2036 and **fabricated $85,053 of wealth from nothing** — a worse bug than the one being fixed. This is why the eventual fix targets the `excessRmd` formula's missing floor specifically, not a phase/need heuristic layered on top.
4. **"Isn't the net outcome the same either way?"** → correct on the economics (verified: `98,648 banked + $0 withdrawn` = `100,000 banked - 1,352 withdrawn`, same ending balance), which is what let the double-count hide in plain sight — the balance chain (`brokStart` = prior `brok`) looked internally consistent every single year, because BOTH phantom copies carried forward together. The tell was never the chain; it was that **`2 × RE/BI` closed the reconciliation gap to $1**, found only by testing the arithmetic identity directly, not by eyeballing continuity.

### Verified
- **Magnitude**: $100k refi (no spending need) now adds **$100,063 (MFJ) / $100,032 (Single)** — was $198,711/$199,352. The small excess over $100k is the legitimate tax-draw-avoided effect from point 2 above.
- **Reconciliation**: every brokerage row — including capital-event years, which could never reconcile before — now satisfies `Start + Contribs + RE/BI Proceeds + Growth − Dists = Ending` to the dollar. Verified via `chartSeries` fields directly, not the DOM (DOM column order can drift independent of the math).
- **2036 semi-retirement**: still correctly banks only $14,947 of a $100k refi (real living need absorbs $92,296) — the near-miss case did NOT regress.
- **Baselines held**: $693,546 / $607,219, zero-deal, unchanged (the bug requires `cashSources` inflated by a deal, so it never touched the baseline).
- **Lifetime Tax KPI was genuinely distorted, confirmed by direct pre/post A-B** on an early (2030) sale with decades left to compound: EOL delta **$4,795,414 → $2,579,060**, lifetime-tax delta **$566,359 → $287,105** — both roughly halved, exactly as expected from a bug that doubled the banked capital and therefore doubled the taxable growth it threw off for decades.
- **Same-year MAGI is unaffected** (confirmed identical pre/post for a sale evaluated in its own year) — MAGI is computed from that year's income/gain before the end-of-year brokerage banking runs, so the corruption only ever hit *future* years via the inflated balance, never the sale's own year.
- Exposed `brokCont`/`brokGrow`/`brokDrawn`/`rebiToBrok` on `chartSeries` (previously only `brok` was exposed) so both the reconciliation and future tooling can verify the row without scraping the DOM.
- Suite **164/164** (was 158 + 1 magnitude test + 2×2 reconciliation-year tests). **Mutation-tested**: reintroduced the exact one-line bug into a throwaway copy → 6 failures in both apps, magnitude test reporting **$198,711** — the exact historical bug value — and both reconciliation years failing with the exact phantom gap. Harness ALL OK, zero page errors, engine fix byte-identical across apps.

### The lesson, stated plainly for next time
**A green test suite proves the code does what the tests check — nothing more.** Ten RE/BI tests all passed while a core balance was consistently 2x wrong, because "does it fire" and "is the tax right" were checked and "does net worth move by the right amount" never was. The fix going forward (already applied above): any new capital-flow feature gets a **magnitude** test — an A/B delta compared against the known input — before it's considered covered, not just a fires/doesn't-fire test.

## RE/BI KPI tile: today's value primary + EOL sub-line (shipped, both apps)

### The original problem, restated precisely
The tile gated on `eolRebiValue > 0` alone — the LAST row of the projection. A deal held today but fully sold before Target EOL vanished from the KPI row entirely: the user's screenshot showed a real $100k position and an empty tile. Every other KPI tile samples an *outcome* (what you end with), which is right for them; RE/BI is a **position you hold now and deliberately exit**, so sampling only the terminal moment answers the wrong question for the tile whose whole point was "give me a quick picture of what I own."

### [DECISION] Two numbers, not one — today primary, EOL sub-line (option B, user's call)
- **Primary** (`kpiRebiValue`): `chartSeries[0].rebiStartValue` — what you hold **today**.
- **Sub-line** (`kpiRebiEolSub`, new): `EOL: $X` — what's left (and passes to heirs) at Target EOL. Reuses the `.kpi-sub` class already established for the Liquid Net Worth tile's "incl. RE/Biz" line, so the visual language is consistent rather than inventing a new pattern.
- **Gate changed from `eolRebiValue > 0` to `rebiDeals.length > 0`** — show the tile whenever ANY deal exists, not conditioned on either value individually. This also naturally covers `today>0`, `eol>0`, or both without a compound OR condition, and correctly surfaces an edge case neither old nor new value-based gates would: a deal at `currentValue: 0` with active ongoing distributions is still a position worth showing.
- The two-tier **Liquid Net Worth** tile's "incl. RE/Biz" sub-line is unchanged — it's specifically an end-of-plan net worth summary, so EOL remains the right figure there. Only the RE/BI tile's OWN primary number changed.

### [DECISION] Compare mode gets both lines their own delta — not shared (user's explicit requirement)
The user's exact instruction: *"for B, i like primary and sub-line but just ensure that when do compare scenario a and b, that the primary and sub-line comparison is done well."* Checked first and confirmed the existing "incl. RE/Biz" sub-line had **zero** compare wiring — no precedent to copy, had to design it.
- `dRebi` (existing) now compares **today** values (`rebiTodayValue`, new field captured in the `window.__scenarioB` snapshot alongside the existing `rebiEndValue`).
- `dRebiEol` (new) compares **EOL** values, reusing the same `rebiEndValue` field already in the snapshot.
- Both fire from `A.rebiTodayValue > 0 || B.rebiTodayValue > 0 || A.rebiEndValue > 0 || B.rebiEndValue > 0` — a deal sold before EOL in one scenario but not the other can show a real "today" delta and a `$0` "EOL" delta simultaneously (verified live: A held-forever vs B sold-in-2033 showed `dRebi: "A: $100K same"` and `dRebiEol: "A: $172K (EOL) −$172K"` — same deal, opposite conclusions per line, which is exactly why collapsing to one number would have hidden half the comparison).
- **Caught mid-build**: `clearScenarioA()`'s hidden-list (`['dRunway','dEol',...,'dRebi','dAca']`) didn't include `dRebiEol` — the new delta line would have stayed visible with stale numbers after compare mode ended. Added to the list and verified: `dRebiEol` now correctly hides on clear, same as every other delta.
- Wording iterated once: `'EOL ' + money(...)` read as "A: EOL $172K" (subject-verb-flipped); changed to `money(...) + ' (EOL)'` → "A: $172K (EOL)", which reads correctly.

### Verified
- **The exact original screenshot scenario**: deal refi'd 2030, sold 2033. Tile now shows `$100K` primary / `EOL: $0` sub — visible, where it was previously hidden entirely.
- **Zero-deal regression**: tile stays hidden, baselines unchanged ($693,546 / $607,219) — confirmed from the shipped output files, not just the working copies.
- **Both apps byte-identical**: engine block (`todayRebiValue` computation through `applyKpiGridColumns()`) and compare block (`renderCompare`'s RE/BI section) diffed character-for-character equal.
- Suite **168/168** (164 + 2 new: tile-shows-with-EOL-zero, snapshot-exposes-both-fields). **Mutation-tested**: reverted the gate to `eolRebiValue > 0` in a throwaway copy → reproduces the exact original bug (`tile visible=false`), caught in both apps.
- Added a help-doc row for the tile itself (previously only mentioned in passing inside the Liquid Net Worth row's explanation) covering the two-number split, the "EOL: $0 is correct, not a bug" point, and the compare-mode behavior.
- Harness ALL OK both apps, zero page errors, zero dangling help links.

### What's still queued
**Tier 7** — composed known-answer scenarios (ACA cliff, IRMAA tier boundary with 2-yr lookback, 0% LTCG stacking, survivor transition, RMD+conversion) at TOL=0.02. Nothing else from the RE/BI thread remains open; Q1 (tile) and Q2 (proceeds column, shipped earlier this session) are both closed.

## Layout: collapsible chart + global display controls moved to a Key Metrics header (shipped, both apps)

### WHY — the user's goal: "see the KPI tiles along with scrolling the table in the same view"
Measured the real vertical budget first rather than assuming. With Tailwind shimmed to realistic geometry, the chart section was **~307px — the single largest block** between the KPI tiles and the table. Collapsing it is the change that actually buys the one-view goal; nothing else in that stretch is close.

### [DECISION] Chart collapse — header stays, only the body folds
`#chartCollapseBody` wraps the SVG + its footnote; the header (title, chevron, HSA/529 checkboxes) is deliberately **outside** it. Collapsing must never take the chart's own controls with it. `setChartCollapsed(bool)` / `toggleChartCollapse()`, chevron flips down↔right, `aria-expanded` tracks state, persisted in `snapshot.preferences.chartCollapsed`, **defaults expanded** (don't change what existing users see on load).
- **Deliberately does NOT call `triggerRecalculate()`** — the SVG is already rendered and hiding a div changes no number. Re-running the engine on every click would be pure waste.
- Import restore uses `typeof ... === 'boolean'`, not truthiness: `false` is a real saved value here and `if (prefs.chartCollapsed)` would silently drop it.

### [DECISION] Both global controls onto a Key Metrics header — the user's idea, and better than either of mine
Checked scope in the code before designing, which reframed the whole question:
- **Dollars** → `dispScale` (line ~2704, inside the engine loop) — rescales KPI tiles, chart **and** every table cell. Genuinely global.
- **KPI Numbers** → only `body.kpi-exact-mode` CSS on `.kpi-val`/`.kpi-sub`/`.kpi-delta`. Verified by counting: **18 such elements in `#kpiGrid`, 0 in the table.** It was filed in the *table* toolbar under a heading for a thing it cannot affect.

I proposed two options (split by scope, or both in the chart header) and mocked them up. **The user asked "why not put both with Key Metrics at the top?" — which was right, and beat both.** My error: I treated *scope* as the only axis and concluded "a global control shouldn't live on the KPI strip." But **global doesn't mean homeless** — a control governing everything belongs *above* everything, and Key Metrics is the topmost permanent row. Both controls answer one question ("how do I want numbers displayed?"), so they get one home.
- Rejected **both-in-chart-header**: the mockup showed six things competing in one row (chevron, title, HSA, 529, Dollars, Numbers), and — fatally — collapsing the chart would leave a folded panel whose header still formats your KPI tiles.
- Rejected **split across two strips**: two places to look for two view toggles, to satisfy a scoping rule that was mine, not the user's.
- **Chart header keeps HSA/529** (genuinely chart-only). **Table toolbar keeps Show Detail + All years** (genuinely table-only) — it drops from 4 control groups to 2 and stops lying about scope.
- Width verified before committing: the two groups measure **154px + 169px ≈ 339px** (inline-styled, so the measurement is real even with Tailwind blocked) against ~1500px of strip. Fits with room to spare.
- **Disclaimer left alone** — user's call, and correct: at 206px it's the second-largest block, but a financial disclaimer that hides itself is a disclaimer doing less of its job.

### Verified
Collapse/expand/re-expand restores exactly; chevron + `aria-expanded` track state; export blob **read back and confirmed** to contain `chartCollapsed: true`; both moved controls still function (`setDollarMode` toggles button state, `setKpiNumberMode` drives `body.kpi-exact-mode`); zero duplicate IDs (the move was a move, not a copy); Key Metrics header + collapse JS **byte-identical across apps**; baselines held ($693,546 / $607,219); harness ALL OK; suite **176/176**; zero page errors.
**Mutation-tested** — dropping `chartCollapsed` from the export, and collapsing the whole `<section>` instead of just the body, each caught in both apps.

### Three test-methodology lessons this cost real time to relearn
1. **The `let`-not-on-`window` trap bit for the THIRD time.** Wrapping `window.setChartCollapsed` to trace import behaviour produced an empty trace — these are module-scoped `let`/`function` declarations, not window properties, so the wrapper never intercepted anything. The trace was meaningless, not evidence.
2. **A shipped, mutation-tested feature "failing" is a signal about the harness, not the feature.** Chasing a false import-restore failure through six probes, the tell was that **`kpiNumberMode` — pre-existing, known-good — failed identically.** `FileReader.onload` doesn't fire for synthetic files in this headless environment, so `importConfig` never ran at all. Executing the restore statements directly proved both prefs restore correctly. **When new code and known-good code fail the same way, suspect the harness.**
3. **Geometry assertions are unreliable inside the suite's iframes.** Two new tests using `offsetParent` and `getBoundingClientRect()` failed despite the facts being true (proved by direct Playwright). Rewrote them to assert **structure** instead — `body.contains(hsa)` for containment, `compareDocumentPosition` for document order. Better tests anyway: they encode the actual contract ("the header is outside the collapsing body") rather than a pixel coincidence.
4. **A test that pins its neighbours is brittle.** My own `kpiNumberMode` export test regexed `/kpiNumberMode\s*,\s*visibleGroups/` and broke the instant `chartCollapsed` was inserted between them — the export was fine, the test was over-specified. Now `/\bkpiNumberMode\b/`: assert the one thing the test cares about.

## "◐ tax only" marker on Portfolio W/D + the dividend-tax explanation (shipped, both apps)

### The user's questions, and what the code actually said
Four questions off a screenshot of a **full-time working** household (H:46/W:43): why is there a Portfolio W/D at all, why are there taxes with no withdrawals, why do brokerage distributions start in 2030?

**Root cause — the brokerage taxes itself.** `brokDividendTotal = brok × brokDivYield` = $1,000,000 × 2% = **$20,000/yr** of dividends. That IS the screenshot's MAGI ($21,750 ≈ $20,000 + proration), and "Total Taxable $3,000" is exactly the **ordinary (15%) slice** — 85% is qualified and taxed at LTCG rates instead. The IRS taxes dividends whether or not you spend them. But **the model deliberately doesn't simulate W-2 salary during working years** (it assumes the paycheck covers living costs), so there is no paycheck in the model to pay that tax from — **the portfolio sells a sliver of itself to cover its own tax bill.** Economically a wash (in reality you'd pay from salary; net worth lands the same), but it renders as a "retirement withdrawal" at age 46.

**Why 2030 specifically** (the user's sharpest question): nothing broke in 2030. Their RE/BI deal paid **$7,000/yr in distributions through 2029** — real cash that covered the small dividend tax, so no portfolio sale was needed (W/D = $0). They **sold the deal in 2029**, the distributions stopped, and the portfolio resumed paying its own tax. Verified against a no-deals baseline: **without any RE/BI deal there's a W/D from 2026 onward.** The deal was masking it for four years.

### [RESOLVED — no action] "Should qualified dividends be reinvested vs spent?"
I raised this, then checked and **withdrew it — the premise was wrong.** Dividends are already inside the 6% total return; `brok` is never separately incremented by them (correctly — that would be the same double-count class as the RE/BI bug). Their only effect is line ~2661: `brokBasis = min(max(1, brok), brokBasis + brokDividendTotal)` — they **raise cost basis**, which is exactly right in tax terms (you paid tax on that $20k this year, so it becomes basis and isn't taxed again at sale). The dividend model is internally consistent. **Do not "fix" this.**

### When RE/BI tax actually lands (user asked; verified by A/B against a no-deal run)
- **Refi ($25,000 in 2027): $0 tax. Ever.** A refinance is a *loan against equity* — borrowed money isn't income. IRS: no taxable event; return of capital reduces basis instead (you pay later, at sale). The ~$64 delta in 2027 is tax on that year's **$7,210 distribution**, not the refi.
- **Sale ($175,000 in 2029): the entire bill, in the sale year only — $8,526.** MAGI leaps $26,951 → $108,130. Nothing before, nothing after (2030's delta is $174).
- **Shown in the table? Yes, but blended** into `MAGI` and `Taxes` — there's no itemized "RE/BI tax" line because the engine computes one household tax bill.

### [DECISION] The marker: Portfolio W/D only, conditional (user's call on both)
Measured the decomposition across every phase first. The split is stark and self-justifying:

| Year | Age | W/D | Living | Healthcare | Tax | tax/W/D |
|---|---|---|---|---|---|---|
| 2026 | 46 | $895 | $0 | $0 | $895 | **100%** |
| 2034 | 54 | $2,281 | $0 | $0 | $2,282 | **100%** |
| 2035 | 55 | $89,385 | $195,716 | $0 | $56,766 | **63.5%** |
| 2045 | 65 | $318,390 | $263,026 | $47,302 | $8,062 | 2.5% |

**The 90% threshold isn't arbitrary — the data chose it.** Nine working years sit at ~100%, then it drops straight to 63.5% at semi-retirement. **Zero years land in the 85–95% band**, so there's no flicker risk at the boundary.
- **Portfolio W/D, not Taxes** (user's call, and right): the Taxes column isn't confusing — $957 of tax on $21,750 of dividend income is unsurprising. The **W/D** is the cell that looks broken. Fix the confusing cell, not its neighbour.
- **Conditional, mirroring "prorated 42%"**: fires only when `wd > 0 && baseNeedFixed <= 0 && hcFromPortfolio <= 0 && solvedTax >= wd * 0.9`. A sub-line on all 81 rows is noise; in retirement a withdrawal is self-explanatory and gets nothing.
- **Guard uses `>= 0.9`, never `=== 1`**: solver rounding makes `tax` slightly *exceed* `wd` in some years ($1,713 W/D vs $1,714 tax). An equality check would silently miss those.
- **[DECISION] "tax only", not a percentage** — I pushed back on the user's "give me the # that clarifies": "◐ 96% tax" invites *"what's the other 4%?"*, and rounding noise makes exact percentages fragile. `tax only` is cleaner and true.
- Same styling as the prorated marker (`block text-[9px] text-amber-500 font-sans cursor-help` + `title` tooltip) — reuse the established visual language rather than invent one.

### Verified
Byte-identical cell across apps. **Exactly 2 lines changed** — one `<td>` for one `<td>`, **zero engine lines** (confirmed by diffing against the shipped file; this is why the missing harness wasn't a blocker, and baselines held to the dollar anyway: $693,546 / $607,219). Marker appears on exactly the 9 working years with no deals, and on **2030–2034 only** with the user's screenshot config — i.e. precisely the years that confused them, absent where their RE/BI distributions covered the tax, and gone from 2035 when real retirement spending begins. Suite **180/180**. **Mutation-tested**: dropping the `>= 0.9` guard makes the marker fire on a real $68,506 retirement withdrawal → caught in both apps.

### Two test-harness lessons (both cost a false failure)
1. **`tr.innerText.startsWith(year)` does not work on these rows.** innerText carries leading newlines/indentation and tbody contains empty spacer rows, so the matcher found nothing and every assertion read `""` — looking exactly like a broken feature. Match on the row's **first cell, trimmed** instead.
2. **Don't hardcode a year in a cross-app test.** `startYear + 30` landed on a row that doesn't exist in Single (its default plan depletes earlier) → `""` → false failure. The test now **finds** the first real living-cost draw from `__chartSeries` rather than assuming one.

# ═══════════════════════════════════════════════════════════════════════
# CONSERVATION AUDIT — TWO ENGINE BUGS FOUND AND FIXED. BASELINES MOVED.
# ═══════════════════════════════════════════════════════════════════════

## Why this happened at all (read this before writing another test)
Four RE/BI bugs shipped past a 180-test green suite — **every one found by the user, none by the tests.** Root cause of the *testing* failure: the tests were written AFTER each bug, targeting bugs already known. They check that things **FIRE** and are **TAXED** correctly. Not one asked **"cash arrived — where did it go?"** All four were cash-flow bugs. That is how 180/180 green coexisted with a balance that was 2× wrong.

The user lost confidence and demanded a conservation audit for the **entire app, both apps** — not RE/BI-only. Correct call: the bugs were never RE/BI bugs, they were cash-flow bugs that happened to surface there.

## THE HEADLINE: the default plan was wrong by 60%

| App | OLD baseline | NEW baseline | Delta |
|---|---|---|---|
| MFJ | $693,546 | **$687,726** | **+$417,941 (+60.3%)** |
| Single | $607,219 | **$340,807** | **+$201,305 (+33.2%)** |

**Zero RE/BI deals involved.** This is BUG A hitting the default plan. Every baseline recorded in this document before this section is wrong.

## BUG A — RMD cash evaporates *(found by the audit, NOT by the user)*
The most serious defect found in this codebase. Hit **every plan reaching age 73**, including the default.

Rich plan (trad $5M / brok $3M), 2055: RMD **$1,213,097** forced out of Traditional; need was $839,366; elective draw from Traditional **$0**; the need was paid **from Brokerage**; `excessRmd` = **$0**. Total-portfolio conservation gap that year: **exactly −$1,213,097**.

**Root cause — `excessRmd` was ALGEBRAICALLY DEAD CODE.** The solver (line ~2612) sizes the elective draw as `need + hc + tax - cashSources` and **never credits `forcedRmd`**. That *guarantees* `need+hc+tax-cashSources === elecTrad+elecBrok+elecRoth`. Substituting that identity into the old `excessRmd` expression, everything cancels:
```
inner = need+hc+tax-cashSources - elecTrad-elecBrok-elecRoth + forcedRmd  =  forcedRmd
excessRmd = forcedRmd - min(forcedRmd, forcedRmd) = 0.    ALWAYS.
```
It could only fire when balance caps bind. **In normal operation it was structurally incapable of firing.**

**Why nobody ever saw it:** in the *default* plan the brokerage is exhausted **before** RMD age, so there was never a year where banking *could* happen. It only manifests for retirees with large Traditional balances — precisely the people RMDs exist to force money out of. Also note `cashSources` (line ~2602) includes 1099 + Social Security + all RE/BI cash but **not `forcedRmd`**.

## BUG B — surplus external cash evaporates *(the distributions bug the user found)*
Banking was gated `if (rebiCapitalProceeds > 0)` — refi/exit **only**. RE/BI distributions offset need via `cashSources`, but surplus was never banked. **Proof: $7,000/yr and $100,000/yr distributions produced an IDENTICAL brokerage balance ($1,715,208).** 14× the cash, zero difference. Post-fix: 14.2× the cash → **14.2× the banking** ✓.

## THE FIX — one unified banking path (replaces two partial ones)
Both bugs are **the same defect: cash arrives, nothing banks it.** So there is now **one rule**, byte-identical in both apps:
```js
totalCashIn  = gross1099 + currentSsPayout + rebiDistTotal + rebiRefiCash + rebiExitProceedsGross
             + forcedRmd + elecTradDrawn + elecRothDrawn + elecBrokDrawn;
totalCashOut = baseNeedFixed + hcFromPortfolio + solvedTax;
surplusCash  = Math.max(0, totalCashIn - totalCashOut);
if (surplusCash > 0) { brok += surplusCash; brokBasis += surplusCash; }
```
Surplus is real, already-taxed cash → banked to Brokerage as after-tax principal (added to basis, never re-taxed as gain). `rebiToBrok` is attributed **first** so the RE/BI Proceeds column keeps its meaning; the remainder is RMD/income surplus. `Math.max(0, ...)` is **load-bearing** — an earlier version without it banked a $100k refi twice (~$197,300).

## TIER 8 — CONSERVATION. The answer to "this can't be one and done."
**Suite is now 216/216** (was 180). Tier 8 runs **9 scenarios × 2 apps × ~50 years ≈ 1,000 year-checks** every run.

Two invariants:
1. **Per bucket:** `ending = starting + inflows - outflows` (trad, roth, brok, hsa, 529)
2. **Household:** `end_total = start_total + growth + contribs + externalIn - spending`

**Invariant 2 is the strong one.** Internal shuffles — RMDs, conversions, elective draws, banking — **must net to zero**, because they only move money between the household's own pockets. So it cannot be fooled by which account money came from, or by how many code paths touch it. **If a transfer loses money, this catches it and nothing else has to be right.**

**Diagnostic signature worth knowing:** when all "every bucket balances" tests PASS but "no money created or destroyed" FAILS, that is a **transfer bug** — each account's own arithmetic is right, money vanishes *between* them. That is exactly what both bugs looked like.

**Mutation-tested:** reverting to the old two-path banking reproduces both bugs exactly (`−$128,911` Bug A; distribution leaks Bug B) — caught in all 18 conservation tests across both apps.

### [DECISION] How Tier 8 stays alive — the ratchet
`audit.js` (shipped to outputs as a **diagnostic-only** tool) was the *wrong shape* to rely on: it string-injects probes into the engine, so it rots the moment an anchor line moves, and nobody runs it unless they remember. So conservation was folded **into the suite**:
- **26 `aud*` flow fields** now published on `chartSeries.push` (`audForcedRmd`, `audExcessRmd`, `audRothConv`, `audHsaDist`, per-bucket starts/conts/grows, `audGross1099`, …). These were already computed — they just weren't published. **Zero logic change; baselines verified unchanged by that step alone.**
- Tier 8 is then **ordinary suite code** reading `__chartSeries`. No probes, no anchors, nothing to rot. Runs on both apps, every change, in the same green/red run.

> **THE RULE: any new feature that moves money MUST publish its flow in `chartSeries.push` and add a scenario to `CONSERVATION_SCENARIOS`.**

Because the invariant is **general**, it already covers features that don't exist yet: a future annuity or pension **cannot quietly leak money** — Tier 8 fails the moment its cash path doesn't balance, without anyone writing an annuity-specific test. That is what turns this from a one-off into a ratchet.

## THREE bugs in MY OWN audit (all found before reporting)
An audit is code, and code has bugs. **Validate it against a hand-proved case before trusting a single number it prints.** I hand-computed the −$1,213,097 RMD case first and required the audit to reproduce it exactly.
1. **Miscounted the RMD as spendable** → **423 false failures.** My first invariant tallied cash *by source*, which required guessing the engine's internal conventions. I guessed wrong. **Fix: switched to total-portfolio conservation, which has no interpretation in it.**
2. **Omitted `hsaDist` as spending** → ~11 false failures/scenario (~$47k/yr phantom leak). The HSA pays healthcare **directly** from its own bucket; that is *not* part of `hcFromPortfolio`.
3. **Used net `income1099` instead of `audGross1099`** → phantom **+$23,736/yr CREATED**. `cashSources` uses **gross**; the SE tax is accounted separately inside `solvedTax`. Using net double-deducts it. (`netEarnedIncome = gross1099 - seTax`, line ~2289.)

**Tell for #1 and #3:** the *baseline with no deals* failed. A no-deal plan has no RE/BI cash at all — if the audit flags it, suspect the audit. Same class as the earlier `FileReader`/`kpiNumberMode` false alarm: **when new code and known-good code fail identically, suspect the harness.**

## Also fixed this session
- **RE/BI defaults** (user request): appreciation **3% → 4%**, annual distribution **$7,000 → $4,000**. `distTaxablePct` stays **25%** — it *is* documented in §15b (syndication distributions are depreciation-sheltered; the K-1 often shows a paper loss, so ~25% is taxed as ordinary). Updated a stale doc note that still claimed "both default to 3%".
- **Fork drift found:** the two apps' capital-events block differed by **three comment lines**, which broke exact-match replacement on Single. Fixed by splicing the new block **from MFJ** so both converge. **Lesson: build on MFJ, splice identical text into Single, assert byte-parity — never hand-edit twice.**
- **False parity alarm:** my parity checker used a non-existent end-anchor and reported "banking block DIFFERS". The block was byte-identical. **A checker with a bad anchor silently compares garbage — verify the anchor exists before believing the verdict.**

## Remaining queue
> **⚠️ SUPERSEDED — this section is kept only as a record of what the queue looked like at 216 tests. Every item on it has since SHIPPED. For the live status, see the end of this file.**
>
> ~~**Tier 7** — composed known-answer scenarios (ACA cliff edge, IRMAA tier boundary w/ 2-yr lookback, 0% LTCG stacking, survivor transition, RMD+conversion) at TOL=0.02. Still zero targeted tests for those live subsystems.~~ **All five shipped.** ACA cliff ✓, IRMAA 2-yr lookback ✓, LTCG stacking ✓, survivor transition ✓, RMD+conversion ✓.
>
> The warning below it still stands, and always will: **green ≠ engine verified** — Tier 8 proves money is *conserved*, not that it's *taxed correctly*. That is why Tier 7 exists.

# ═══════════════════════════════════════════════════════════════════════
# TIER 7 — KNOWN-ANSWER TESTS. THE "WIDOW'S PENALTY" WAS MIS-MODELLED.
# ═══════════════════════════════════════════════════════════════════════

## Why Tier 7 had to exist (measured, not assumed)
Asked for a confidence level, I **mutation-tested the suite instead of estimating**. Two valid experiments, both damning:

| Mutation | Old suite result |
|---|---|
| Tax bracket **22% → 32%** (a 45% error, both apps) | **216/216 GREEN** |
| Every RMD divisor **halved** (RMDs doubled, both apps) | **216/216 GREEN** |

**I corrupted the US tax code two different ways and not one of 216 tests noticed.** Tier 8 proves money is *conserved*; it **cannot** prove amounts are *correct*. A wrong bracket, divisor, subsidy or rule conserves perfectly and stays green. **Conservation is necessary, not sufficient.**

Coverage audit at that moment: Survivor **47 engine refs / 0 tests** (largest untested surface), IRMAA 18/0, LTCG 12/1, ACA 11/0, SE tax 11/0. Survivor was picked first on exposure.

## BUG FOUND — the survivor `filingScale = 0.5` shortcut (fixed, MFJ app)
The survivor scenario modelled Single filing by **literally halving the MFJ numbers**. That is exact for the lower brackets and **WRONG at every top threshold**, because Congress deliberately did not halve them:

| Item | MFJ | half-MFJ (engine) | TRUE Single | error |
|---|---|---|---|---|
| 37% ordinary | $768,700 | $384,350 | **$640,600** | **$256,250** |
| 20% LTCG | $613,700 | $306,850 | **$545,050** | **$238,200** |
| top IRMAA | $750,000 | $375,000 | **$500,000** | **$125,000** |
| std deduction | $32,200 | $16,100 | **$16,100** | $350 |

**Impact (measured, high-income survivor, H dies at 72, trad $6M/brok $4M):**
- lifetime tax **$8,832,454 → $8,729,311 = $103,143 of OVERTAX removed**
- EOL legacy **+$145,309**
- Up to **~$5,125/yr** of ordinary overtax alone, *every survivor year*, plus the top Medicare surcharge charged to survivors who never owed it.

**Root cause:** the MFJ app carried **no Single tables at all** — `filingScale = 0.5` was a shortcut around missing data, not a modelling choice.

**Fix:** added the true `singleOrdinary` / `singleLtcg` / `singleIrmaaTiers` / `stdDedSingle` to `IRS_2026` (mirroring the Single app exactly — single source of truth), and replaced the scale hack at **all 7 use sites** with real table selection (`survOrdinaryBrackets`, `survLtcgBrackets`, `survIrmaaTiers`, `survStdDedBase`). **No live `filingScale` remains.**

**Single app deliberately untouched** — it already files Single, so the bug never applied. Verified byte-identical to the previously shipped file.

## TIER 7 — the tier that catches WRONG RATES
**Suite now 234/234** (was 216). 18 new tests. Constants are transcribed from published IRS 2026 figures and are **deliberately independent of the app's own tables** — asserting the app equals itself would prove nothing.

Covers: MFJ + Single ordinary thresholds AND rates, LTCG breakpoints, standard deductions, IRMAA tiers, the survivor tables, three explicit "top threshold is **NOT** half of MFJ" regression tests, and one **end-to-end** test driving a real survivor scenario (a correct table nothing reads is worthless).

**Mutation-verified — this is the whole point:**
- **22% → 32% bracket** (the mutation that beat the old suite): now **CAUGHT in both apps**, naming the corruption exactly (`app=[10,12,32,...] irs=[10,12,22,...]`).
- **Revert survivor tables to half-MFJ** (reintroduce the exact bug): **5 tests fire**, including the end-to-end one catching the $103k overtax.

## Baselines UNCHANGED ($687,726 MFJ / $340,807 Single)
Survivor is off by default, so the fix moves nothing until enabled. Both verified from the shipped files.

## Remaining known-answer gaps (Tier 7 is started, NOT finished)
Still **zero** targeted tests for: **IRMAA 2-yr lookback logic** (tiers now asserted, the lookback mechanism is not), **ACA subsidy/cliff**, **SE tax**, **LTCG stacking behaviour**, **RMD divisor values** (the halved-divisor mutation would STILL pass — the table isn't asserted yet), Social Security taxation, survivor SS/healthcare/basis-step-up mechanics.

> **Honest status: structure and cash-flow are verified. Tax correctness is now PARTIALLY verified — the tables the survivor path uses are locked; most of the rest is not.** The RMD-divisor mutation still passing is the clearest remaining hole and the obvious next target.

## Tier 7 extended — RMD divisors (suite 234 → 240). NO engine bug: the table was already right.

### The hole this closed
The mutation that **halved every RMD divisor (doubling every RMD in the tax code)** passed **216/216** and then **234/234**. Tier 8 conservation cannot catch it — a doubled RMD conserves perfectly, it just moves the wrong amount. Now **5 tests fire in both apps**, naming every wrong divisor and showing the arithmetic break ($75,758 vs the correct $37,736 at 73).

### ⚠️ I ALMOST "FIXED" A CORRECT TABLE — the most important lesson of this session
First pass, I compared the engine against IRS divisors **from memory** and reported **14 of 29 wrong** (ages 87–100), with a confident table of "RMD error at $1M balance" running to −$19,189/yr. **My memory was wrong. The engine was right.**

Two independent published sources — Fidelity's Uniform Lifetime Table PDF and a transcription of Pub 590-B — confirmed the engine's values exactly (87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 95: 8.9, 100: 6.4).

**Had I trusted my own arithmetic I would have corrupted a correct table and shipped it as a fix** — and Tier 7 would then have *locked the corruption in*, because the test asserts against the constant I typed. **A known-answer test is only as good as its source.** Tier 7's constants are now annotated with this warning; any future edit must cite a source, never recall.

This is the same failure mode as my three audit bugs, one level up: **verify the checker before believing the verdict.**

### What Tier 7 now asserts for RMDs (both apps)
- All **29 divisors, ages 72–100**, against Pub 590-B Table III (Treas. Reg. 1.401(a)(9)-9, unchanged since 2022).
- **Arithmetic the divisors drive:** $1M balance → **$37,736 at 73**, **$112,360 at 95** (hand-verified independently of the engine).
- **SECURE 2.0 start age = 75**, correct for anyone born 1960+ (both default profiles are 1980/1983). A default of 73 would force RMDs two years early. Confirmed the app already models this correctly and documents the rule in §11.

### RMD subsystem verdict: SOUND
29/29 divisors correct, correct SECURE 2.0 start age, correctly documented. **Both apps byte-identical to the previously shipped files — no engine change was needed.** Baselines unchanged ($687,726 / $340,807). Suite **240/240**.

### Remaining known-answer gaps (Tier 7 still unfinished)
Zero targeted tests for: **ACA subsidy/cliff** (11 refs), **IRMAA 2-yr lookback mechanism** (tiers asserted, lookback logic not), **SE tax** (11 refs), **LTCG stacking behaviour**, Social Security taxation, survivor SS/healthcare/basis-step-up mechanics.

> **Status: structure + cash-flow verified. Tax correctness partially verified — brackets, LTCG breakpoints, standard deductions, IRMAA tiers, survivor tables and RMD divisors are now locked against published figures. The mechanisms that USE them (ACA cliff, IRMAA lookback, SE tax, LTCG stacking) are still untested.**

## Tier 7 extended — ACA subsidy / 400% cliff (suite 240 → 256). NO engine bug: ACA was already correct.

### Verdict: the ACA subsystem is SOUND
Every constant checked against **published sources** (HHS/ASPE 2025 poverty guidelines, healthreformbeyondthebasics CY2026 reference chart, obamacarefacts), not recall:

| constant | engine | published | ✓ |
|---|---|---|---|
| `fplFirstPerson` | 15650 | $15,650 (1 person, 48 states + DC) | ✓ |
| `fplAddlPerson` | 5500 | +$5,500 per additional person | ✓ |
| `acaCliffFplMult` | 4 | **400% cliff APPLIES for 2026** — the ARPA no-cliff enhancement expired after 2025 | ✓ |
| `acaMedicaidFloorMult` | 1.38 | $15,650 × 1.38 = $21,597 published 138% threshold | ✓ |

Derived cross-checks against published figures: **1 person 400% = $62,600**; **family of 4 = $32,150 → $128,600**. Both exact.

**Prior-year FPL is correct**, not a bug: eligibility for coverage year 2026 is computed from the **2025** guidelines. The engine does exactly this.

**Hand-verified the full subsidy chain to the dollar.** MFJ hh2, year 2029: FPL $21,150 × 1.0927 (3 yrs @3%) = $23,111; ratio 83,334/23,111 = **3.606** → 3.0–4.0 band → flat **9.96%**; contribution 0.0996 × 83,334 = $8,300; benchmark $28,000 × 1.0927 = $30,596; subsidy = 30,596 − 8,300 = **$22,296**. **Engine reported $22,296.** Exact — FPL inflation, ratio, applicable %, contribution and subsidy all confirmed.

The applicable-percentage curve matches the post-ARPA statutory schedule at every band edge (1.0x→2.10%, 1.5x→4.19%, 2.0x→6.60%, 2.5x→8.44%, 3.0x→9.96%). `acaApplicablePct` returning 9.96% above 4.0x is **fine** — the cliff is enforced separately at line ~2590 (`acaMagi <= cliffMagi`), a genuine cliff, not a phase-out.

### What Tier 7 now asserts for ACA (both apps, 16 new tests)
FPL constants; 400% cliff multiplier; 138% Medicaid floor; derived cliff dollars vs published; the applicable-% schedule at all five band edges; **cliff fires end-to-end** (subsidy paid under, ZERO above); subsidy rises with household size.

**Mutation-verified (both fire in both apps):**
- **Cliff removed** (`acaCliffFplMult: 4 → 9999`, i.e. pretending ARPA never expired — the classic modelling error): **6 tests fail**, including end-to-end showing a subsidy still paid over the cliff.
- **Stale FPL** (`15650 → 15060`, the 2024 figure — the most likely real-world drift): **4 tests fail** in both apps.

### ⚠️ `targetDraw` DOES NOT EXIST IN EITHER APP — the spending lever is `netDistribution`
My first ACA test wrote `setInput(win,'targetDraw', …)` and **silently set nothing**. The MFJ assertion then **passed by luck** while Single failed — which looked exactly like an engine bug in Single and was not. Chasing it burned several probes ("MAGI frozen at $48,860 regardless of inputs" was the tell).

**The real lever is `distModel='fixed'` + `netDistribution`.** Once used, both apps cross the cliff identically:
- MFJ: MAGI $43,218 → **−$26,913 ACA**; MAGI $133,653 → **no subsidy**
- Single: MAGI $36,645 → **−$15,121 ACA**; MAGI $118,088 → **no subsidy**

> **LESSON (third instance this session): writing to a non-existent element id is INVISIBLE — no error, no effect.** Same family as the `let`-not-on-`window` trap and the `FileReader` false alarm. **Always confirm the lever actually moves the number before trusting a green OR a red.** A test that sets nothing can pass for the wrong reason.

Also noted: the default plan **cannot** test ACA (MAGI ~$760k, 9× over the cliff — no subsidy ever applies). The test builds a lean early-retirement plan deliberately. And `rothConvToggle` is unusable as a MAGI lever here: enabling it triggers a large bracket-fill conversion that swamps MAGI ($344k), drowning the signal.

### Status
Suite **256/256**. **Both apps byte-identical to the previously shipped files — no engine change needed.** Baselines unchanged ($687,726 / $340,807).

### Remaining known-answer gaps
Zero targeted tests for: **IRMAA 2-yr lookback mechanism** (tiers asserted, the lookback logic is not), **SE tax** (11 refs), **LTCG stacking behaviour**, Social Security taxation, survivor SS/healthcare/basis-step-up mechanics.

> **Locked against published figures:** brackets + rates, LTCG breakpoints, standard deductions, IRMAA tiers, survivor tables, RMD divisors + start age, FPL/ACA cliff + applicable-% schedule.
> **Still unverified:** the mechanisms that *use* them — IRMAA lookback, SE tax, LTCG stacking, SS taxation.

## Tier 7 extended — IRMAA (suite 256 → 263). NO engine bug: IRMAA was already correct.

### Verdict: the IRMAA subsystem is SOUND
Verified against **multiple independent published sources** (Kiplinger, NerdWallet's Part D table, Federal Pension Advisors, incomelaboratory), never recall:

| item | engine | published |
|---|---|---|
| MFJ thresholds | 218k/274k/342k/410k/**750k** | $218,000–$410,000 joint, top **$750,000** ✓ |
| Single thresholds | 109k/137k/171k/205k/**500k** | $109,000–$205,000 single, top **$500,000** ✓ |
| surcharges/person | [1148, 2885, 4620, 6355, 6936] | "**$1,148 to $6,936 per person**" — both endpoints exact ✓ |
| lookback | `magiHistory[currentYear - 2]` | "2026 IRMAA is based on your **2024** tax returns" ✓ |
| cliff | strict `>`, full tier, no proration | "$1 over a boundary owes the **FULL** surcharge, not prorated" ✓ |

**Independent cross-check:** an advisor worked example puts a couple at MAGI $258,000 (tier 1) at **$2,297/yr**; the engine's $1,148 × 2 people = **$2,296**. Reconciles to $1.

**Lookback proven behaviourally, not just read.** With inflation held ~static: 2043 MAGI **$374,332** (spike) → 2044 $179,744 → 2045 $180,138, and **IRMAA fires in 2045 at $4,629**. A 0-year or 1-year lookback would have found MAGI *under* the $218k tier-0 line and charged nothing. Only year−2 explains the charge. Tier selection also confirmed ($374,332 → the $342k–$410k tier → $4,620/person), as does `persons65`: only H had turned 65, so it charged **once**, not twice.

### The latent trap (documented, not a live bug)
Engine line ~2426 reads `IRMAA_TIERS[t].annual` (always MFJ) while line ~2425 tests `survIrmaaTiers[t].from` (survivor-aware). **Not a live bug** — surcharge amounts are identical across filing statuses, so indices align and values match. But if a future edit diverges the two tables' `.annual`, the survivor path silently charges the MFJ amount. **A test now pins `.annual` equality across both tables** to catch that.

### What Tier 7 now asserts for IRMAA (7 new tests, both apps)
Per-person surcharges vs published; MFJ/Single `.annual` equality (the trap guard); **2-year lookback end-to-end**; surcharge equals a published per-person tier (×1 or ×2 enrollees). Plus the existing tier-threshold and survivor-tier tests.

**Mutation-verified (all fire in BOTH apps):**
- **lookback 2yr → 1yr**: caught — `charged tier 4; MAGI year−2 = tier −1` names the break exactly.
- **tier-0 surcharge $1,148 → $2,148**: caught in both apps.

### ⚠️ TWO more silent-probe traps hit while building this
1. **`inflationRate` is read as `parseFloat(...) || 3`** — setting it to **"0" is FALSY** and silently becomes **3%**. My probe "disabled inflation" three times and changed nothing; output was byte-identical each run and looked like a frozen engine. **Use a truthy near-zero (0.01).** (Not an engine bug: 0% inflation is a degenerate input.)
2. **A mutation caught in MFJ was silently MISSED in Single.** Cause: Single's MAGI was nearly flat (~$194k) across the lookback window, so a 1-year and 2-year lookback selected the *same tier* — the scenario had **no signal**, so the test could not fail. Fixed by driving a deliberate **MAGI spike** (large RE/BI exit) so the lookback is observable; the mutation is now caught in both apps.

> **LESSON: a green mutation test can mean the test is weak OR the scenario has no signal. If a mutation is caught in one app but not the other, the scenario — not the engine — is usually the difference.** Also: the first draft of the lookback assertion ("current and prior year must be under tier 0") was too restrictive and **falsely failed Single**, where MAGI legitimately sat above tier 0 in all three years. Comparing the **selected tier** instead is app-agnostic and still decisive.

### Status
Suite **263/263**. **Both apps byte-identical to shipped — no engine change needed.** Baselines unchanged ($687,726 / $340,807).

### Remaining known-answer gaps
Zero targeted tests for: **SE tax** (11 refs), **LTCG stacking behaviour**, **Social Security taxation**, survivor SS/healthcare/basis-step-up mechanics.

> **Locked against published figures:** brackets + rates, LTCG breakpoints, standard deductions, IRMAA tiers + surcharges + 2-yr lookback, survivor tables, RMD divisors + start age, FPL/ACA cliff + applicable-% schedule.
> **Still unverified:** SE tax, LTCG stacking, SS taxation.

## SE tax reviewed — DOCUMENTED, NOT FIXED (user decision). Suite 263 → 265. Docs corrected.

### SE tax verdict: correct below the cap, deliberately simplified above it
Verified against ~8 published sources. **Correct:** 15.3% (12.4% SS + 2.9% Medicare), 92.35% net factor, half deductible, W-2 path at 7.65% with no half-deduction. Reproduces a published worked example **exactly**: $50,000 → **$7,065**.

**Not modelled (two caps):** the **SS wage base $184,500 (2026)** — the 12.4% stops there while 2.9% Medicare continues uncapped — and the **0.9% Additional Medicare** above $250k MFJ / $200k single.

**Impact, per person (MFJ):** exact to ~$199,783 gross; **+$5,750/yr at $250k**; **+$32,473/yr at $500k** (overstates).

**Default plan UNAFFECTED** — verified empirically, not assumed: H $25,000 / W $100,000 (ids `hSemiInc1099` / `wSemiInc1099`), nominal peak **$167,990**, never reaching the $199,783 threshold.

### [DECISION] Do NOT fix. Document instead. (user's call, Claude concurred)
User set the bar at "VERY VERY VERY HIGH confidence of no new risk". **Claude honestly assessed ~85-90% and said so — below the bar.** Three specific risks:
1. **The solver is ITERATIVE.** `seTax` feeds `totalTax`, which the solver converges on. The SS cap injects a **hard kink** into a currently smooth tax curve; convergence stability under a piecewise function is unproven.
2. **The wage base must inflate** (it rose **4.8%** for 2026 alone) and tracks **wages, not CPI**. Using the app's `infScale` would be an approximation **invented, not sourced** — the exact failure mode that nearly corrupted the RMD table.
3. **The 0.9% threshold must NOT inflate** — unindexed since 2013 — while every other threshold in the app does. That asymmetry is a bug-generator.

User's domain reasoning settled it: *"semi-retirement is semi-retirement and not exceeding ss caps."* Fixing buys nothing at the defaults and risks the solver. **Blast radius was small (`payrollFor()` is pure; `seTax` has 3 consumers, `seDeduction` 1) — the risk was never the callers, it was the solver + invented inflation basis.**

### ⚠️ THE DOCS WERE NOT BEING READ — a real process failure (user caught this)
User asked: *"are you reviewing the help docs? Lot of this is likely documented in there."* **No, and it cost real time.**

- **§18 ALREADY documented the SE gap** — *"(the Social Security wage-base cap is not modeled)"*. Claude "found" a bug that was a **disclosed, deliberate limitation**.
- **§11 was RIGHT while the CODE was WRONG.** It states: *"any excess beyond what spending required is reinvested into the Brokerage account — **it never disappears**."* That is exactly the invariant `excessRmd` violated as dead code. **Reading §11 would have found the 60%-baseline RMD bug immediately.** The doc described intent correctly; the code lied.

> **RULE: read the help docs BEFORE auditing a subsystem. They state intent. A gap between doc and code is either a bug (§11) or a known limitation (§18) — both are exactly what an audit is looking for.**

### THREE stale doc blocks fixed (docs lied about today's own survivor fix)
Hours after replacing `filingScale=0.5` with the true Single tables, three help blocks still claimed the opposite:
1. MFJ §Roth-conversion limitation: *"Single filing (survivor) brackets are approximated as half of MFJ."*
2. MFJ §Survivor limitations: *"Single brackets are approximated as exactly half of MFJ (slightly off above the 24% bracket)"*
3. MFJ §Survivor narrative (most explicit): *"the engine **approximates by halving** the MFJ bracket thresholds and standard deduction **rather than applying the true IRS single-filer tables**"* — precisely backwards.
4. Single app carried claim #1 too.

All four now state what the engine actually does, with the real thresholds ($640,600 / $545,050 / $500,000) and the ~$100k lifetime-tax impact of getting it wrong. Both apps' SE-tax sections now **quantify** the wage-base decision rather than parenthesising it.

### Single app: survivor path is INERT (verified, not assumed)
`survivorOn = false` is **hardcoded** — the survivor UI was removed as inapplicable to a single filer; the IDs remain as hidden inert inputs for the shared engine/import path. So its `filingScale` is always 1 and never halves its (already-Single) tables. **Not a bug.** Its docs already read correctly: *"Both use the true IRS tables for that status — not a scaled approximation."*

### NEW: Tier 7 doc-accuracy guard (2 tests, both apps)
Scans rendered help HTML for stale claims (`approximated as half of MFJ`, `approximates by halving`, …). **Mutation-verified:** reintroducing the stale sentence fails the test in both apps.

> **This tier is now the ratchet for docs as well as numbers.** Any future edit that makes the help text contradict the engine on this point fails the suite.

### Status
Suite **265/265**. Baselines unchanged ($687,726 / $340,807). Doc-only engine changes; no logic touched.

### Remaining known-answer gaps
Zero targeted tests for: **LTCG stacking behaviour**, **Social Security taxation**, survivor SS/healthcare/basis-step-up mechanics.

## Tier 7 extended — LTCG stacking (suite 265 → 273). NO engine bug: stacking is CORRECT.

### Read the docs FIRST this time (the new rule worked)
§8 states the intent precisely: *"LTCG on the brokerage gain portion (**stacked on top of ordinary income** against the LTCG brackets)"*. The code (line ~2609) implements exactly that:
```js
ltcgTax = marginalTax(taxableOrd + preferentialGains, ltcgBrackets, infScale)
        - marginalTax(taxableOrd, ltcgBrackets, infScale);
```
**Doc and code agree.** Eight hand-computed cases match the engine **to the dollar**, including the subtle ones: the $165 partial-fill and the $9,315 straddle of the 15%/20% line.

`preferentialGains = brokGain + rebiExitGainLtcg + brokDivQualified` — all three defensible. `basisRatioSnapshot = min(1, brokBasis / max(1, brokStart+brokCont))` is pro-rata, guarded both ways, and used consistently at all three sites.

### ⚠️ MY FIRST TEST SET WAS WORTHLESS — the mutation PASSED
Four green tests, and the mutation replacing the stacked formula with `marginalTax(gains)` alone **passed 269/269**. Cause: they exercised `win.marginalTax` **directly** — the helper the mutation never touches. **I was testing the helper, not the engine's USE of it.** Same family as the `targetDraw` phantom-id trap, one level up.

**Fix:** published `audLtcgTax` / `audTaxableOrd` / `audPrefGains` on `chartSeries` (per the Tier 8 ratchet rule — any behaviour worth asserting must be observable), then recomputed each year's LTCG from the **published brackets** using the engine's own inputs and compared BOTH ways:
- `stacked  = marginalTax(ord+gains) - marginalTax(ord)`  ← the IRS rule
- `isolated = marginalTax(gains)`                          ← the classic bug

Plus a **discriminator** assertion: the scenario must CONTAIN years where the two formulas differ, else the test proves nothing.

**Now mutation-verified in BOTH apps**, with a diagnosis the helper tests could never produce:
> `19/53 years match stacked; e.g. 2078: engine $0, stacked $26,644, isolated would be $0`
> `34/53 years where stacked != isolated; engine matched isolated in 53/53`

### A false alarm I ran down (engine was right, my expectation was wrong)
A $60k draw on a brokerage-only plan showed **$9,152** tax where I expected ~$0. Not a bug — I'd forgotten **(a)** a $3M brokerage throws off **$60k+ of dividends every year** regardless of draws, and **(b)** state/county tax (4.4%) has **no preferential 0% band**. Reconciling with the engine's *own* published internals (`audSolvedTax` $5,211, `audHcFromPortfolio` $39,139 forcing a $109,914 draw — not the $65,564 I assumed) closed to **$179**: the preferential pool of $103,805 sits just inside the inflated 0% ceiling of $108,071, so **federal LTCG really is $0** and the whole tax is state/county. **Reconcile against the engine's actual internals, not against a mental model of the scenario.**

### Also caught by verifying before trusting
- My Single straddle expectation was **$8,257.50**; hand-computation gave **$9,247.50**. Corrected before running.
- My "same gain, different tax" assertion used a $50,000 gain for both apps — but that **overflows Single's $49,450 0% band** ($82.50, not $0). The engine was right; the assertion was sloppy. Now sizes the gain to each status's band.

### Status
Suite **273/273**. Baselines unchanged ($687,726 / $340,807). Engine change was **publication only** (zero logic); new block byte-identical across apps.

### Remaining known-answer gaps
Zero targeted tests for: **Social Security taxation** (the `ssTaxablePct` flat-input simplification), survivor SS/healthcare/basis-step-up mechanics.

> **Locked against published figures:** brackets + rates, LTCG breakpoints **and stacking behaviour**, standard deductions, IRMAA (tiers + surcharges + 2-yr lookback), survivor tables, RMD divisors + start age, FPL/ACA cliff + applicable-% schedule, SE tax rates (cap documented as a deliberate simplification).

# ═══════════════════════════════════════════════════════════════════════
# TIER 0 — TRIANGULATION. THE ANSWER TO "HOW DO WE TEST ALL THREE?"
# ═══════════════════════════════════════════════════════════════════════

## The question (user, verbatim)
> *"Somehow need to triangulate help docs, test-suite.html, and whatever you've done now .... all 3 of those to test the apps? how do we do that?"*

## The problem, stated precisely
The same fact lives in **three places, in three languages**:
```
engine:  data-default="75"              (an HTML attribute)
docs:    "RMD age (default 75)"         (English prose)
test:    rmdAgeEl.value === '75'        (a JS assertion)
```
Three independent edits. **Any two can agree while the third rots.** Not hypothetical — this session shipped the survivor fix and left THREE help blocks describing the old behaviour for hours.

The earlier doc guard was a **BLACKLIST**: it grepped three phrases I happened to know were stale. **It cannot catch a claim nobody thought to grep for.**

## The fix: THE HELP DOC IS THE SPEC
New help **§21 "Verified Facts"** carries 19 machine-readable entries, rendered for the user AND read by the suite:
```html
<li data-fact="rmd.startAge" data-value="75" data-source="SECURE 2.0 Act §107">
    RMD start age: <strong>75</strong> for anyone born 1960 or later…
</li>
```

**Tier 0 then checks FOUR edges every run, on both apps:**
1. **doc ↔ engine** — the stated value must equal what the engine *actually uses* (resolvers read `IRS_2026` / the DOM live, never a copy — a copy would just be a fourth place to rot)
2. **doc ↔ tests** — every fact must have a Tier 7 assertion behind it
3. **fact ↔ engine wiring** — no orphan claims that resolve to nothing
4. **fact ↔ source** — every number must cite a publication (never recall)

> **Break any edge → red.** Edit prose without code → fails. Edit code without prose → fails. Add a fact with no test → fails. Rename a test and lose its fact → fails.

### Mutation-verified — all three drift directions, both apps
| mutation | caught? | diagnosis |
|---|---|---|
| **engine drifts** (FPL 15650→16000, docs unchanged) | ✓ **6 tests** | Tier 7 + cliff arithmetic |
| **DOC drifts** (`data-value` 75→73, engine unchanged) | ✓ **2 tests** | *"rmd.startAge: doc says 73, engine uses 75"* |
| **TEST disappears** (SE-rate test renamed) | ✓ **2 tests** | *"se.rate (no Tier 7 test matching 'Self-employment tax rate')"* |

**The doc-only mutation is the one the old blacklist could never catch.** That was the actual hole.

## Tier 0 immediately found a REAL gap in my own work
It failed on first run and was right twice over:
1. **SE tax had NO Tier 7 test.** I verified the rates against ~8 sources during the audit and **never wrote an assertion**. Nothing would have caught a future edit. → 3 SE tests added (rate 15.3%, factor 92.35%, and the published $50,000 → $7,065 worked example).
2. **My spec was MFJ-centric.** The Single app has no `stdDedMfj`, and its `irmaaTiers` **are** the Single tiers. → resolvers made app-aware; `MFJ_ONLY_FACTS` skipped (not failed) in the Single app.

## Honest correction recorded
I initially claimed a coordinated engine+doc change to RMD age 73 would slip through. **I tested it: it does NOT** — Tier 7 asserts 75 against the published SECURE 2.0 rule, so the *published source* is the anchor that survives a coordinated edit. My concern was overstated and I said so rather than build against a false premise. (The Tier 5 W-2/1099 failure in that run was collateral from the mutation, not a real bug — confirmed 273/273 clean on unmutated files.)

## THE MAINTENANCE CONTRACT (read this before changing anything)
> **To change a tax fact:** edit §21's `<li>` (value + source), edit the engine, edit/confirm the Tier 7 test. **All three, or the suite names the one you forgot.**
> **To add a feature that moves money:** publish its flow in `chartSeries.push` (`aud*`) and add a `CONSERVATION_SCENARIOS` entry (Tier 8 ratchet).
> **To add a tax constant:** it needs a §21 fact, a source citation, and a Tier 7 assertion — Tier 0 fails otherwise.
> **Never source a number from memory.** Recalled RMD divisors nearly corrupted a correct table this session.

## The full defense-in-depth picture
| tier | catches | verified how |
|---|---|---|
| **0 — Triangulation** | docs/engine/tests drift | 3 mutations, both apps |
| **7 — Known-answer** | wrong rates, brackets, divisors | published sources + mutations |
| **8 — Conservation** | money created/destroyed | ~1,000 year-checks + mutations |
| 1/2/5/6 | structure, features, RE/BI | pre-existing |

**Suite 273 → 289.** Baselines unchanged ($687,726 / $340,807). Engine change is **doc-only** (§21 added; zero logic).

## Tier 7 — Social Security taxation (suite 291 → 301). NO engine bug. Tier 7 is now COMPLETE.

### Rule 8 worked: read the docs first
§20 already disclosed it: *"The SS taxability phase-in… simplified to flat inputs."* A **known limitation**, not a bug — found by reading, not by probing.

### Verdict: the flat 85% is EXACT for this household
Thresholds verified against **Congress.gov (CRS IF11397)** plus six sources — never recall:
- provisional income = AGI (ex-SS) + tax-exempt interest + **50% of benefits**
- MFJ: **$32,000** (0%) / **$44,000** (→85%). Single: $25,000 / $34,000. **Frozen since 1993, never indexed.**
- 85% is a **cap**, not a rate: `taxable = min(0.85×benefits, 0.85×(provisional − 44,000) + 6,000)`

**The default plan's first SS year: provisional income ≈ $374,716 vs a $44,000 threshold — 8.5× over, rising every year.** The first term binds, so the statutory rule returns **exactly 85%**. Verified: true taxable SS **$86,394** vs flat-85% of $101,640 = **$86,394**. **Identical.**

The flat rate can only **overstate** (for low-income retirees inside the phase-in — e.g. SS $40k + other $10k: true 0%, flat 85%). **Conservative, never understates**, and the input is user-editable.

### MAGI treatment verified — the subtle part the engine gets RIGHT
- **ACA MAGI** (line ~2588) adds back `SS × (1 − ssTaxablePct)` — `totalOrdinary` already carries the taxable slice, so this reconstitutes the **full benefit**. Correct per **26 USC 36B**.
- **IRMAA MAGI** (line ~2604) does **NOT** add it back. Correct — a **different statutory definition**. Easy to get wrong; the engine doesn't.

### ⚠️ A REAL GAP FOUND AND CLOSED (mutation passed 299/299)
Removing the untaxed-SS add-back from `acaMagi` **passed the entire suite**. Cause: **the default plan claims SS at 70 while ACA ends at 65 — zero overlap years**, so the path was unreachable and untested. **Early claiming at 62 is a common plan, so it IS reachable.**

**Fix:** published `audAcaMagi`; added an end-to-end test driving SS at 62 + early retirement. The assertion is elegant: **ACA MAGI must NOT move when only `ssTaxablePct` changes**, because the *full* benefit counts either way. Now caught in both apps:
> *"2042: ACA MAGI $34,114 at 85% taxable vs $20,073 at 50% — must match"*

> **LESSON: "the mutation passed" can mean the scenario never exercises the path. Check reachability before concluding the code is guarded.** (Same family as the flat-MAGI IRMAA scenario that hid a lookback bug in the Single app.)

### What Tier 7 now asserts for SS (10 tests, both apps)
Default 85%; the reference phase-in reproducing the **published worked example** ($36k SS + $46k → **$23,000 taxable**, exact); that the statutory rule returns exactly 85% at this plan's income (so the flat rate is lossless *here*); that the error direction is conservative; and the **SS↔ACA MAGI add-back** end-to-end.

**Mutation-verified:** default 85%→50% fires **Tier 7 AND Tier 0** (`"doc says 85, engine uses 50"`); removing the ACA add-back fires the new interaction test in both apps.

### Docs updated
§21 gained **3 facts** (`ss.taxablePctDefault`, both provisional thresholds — 22 facts total). §20's one-line limitation is now a **quantified explanation**: what the real rule is, why 85% is exact here, which direction the error runs, and when to change the input.

### Status: TIER 7 IS COMPLETE
Suite **301/301**. Baselines unchanged. Engine change = **publication only** (`audAcaMagi`); parity verified byte-identical.

**Every tax subsystem now has known-answer coverage:** brackets + rates, LTCG breakpoints **and stacking**, standard deductions, IRMAA (tiers + surcharges + 2-yr lookback), survivor tables, RMD divisors + start age, FPL/ACA cliff + schedule, SE tax rates, **SS taxation + the ACA MAGI interaction**.

**Remaining (minor):** survivor SS/healthcare/basis-step-up mechanics — the survivor *tables* are locked; these are the mechanics around them.

## SS triangulation AUDIT — user challenged it, and they were RIGHT. Suite 301 → 307.

### The question
> *"for social security taxation, did you triangulate: the apps, help docs, test suite, etc. and rectify/update ALL as necessary?"*

**Answer: NO, not properly. Two real defects, found only because the claim was checked instead of asserted.**

### DEFECT 1 — the resolvers were TAUTOLOGIES
```js
'ss.provisionalThreshold.mfj': () => 44000,   // compared against a doc that says 44000
```
Doc says 44000, resolver returns 44000 → **always green, proves nothing.** Worse, when the doc value was mutated to 99999 the failure message read *"engine uses 44000"* — **a lie**, because the engine had no such constant.

**This is the exact "fourth place to rot" that Tier 0's own design notes warn against**, and I wrote it anyway.

### DEFECT 2 — the engine didn't contain the thresholds at all
The engine uses a flat rate, so `32000/44000/25000/34000` existed **only in the doc and the test file**. I documented facts the engine didn't implement.

### The fix
Added the statutory thresholds to `IRS_2026` as **real, commented reference constants** (`ssProvisionalMfjLower/Upper`, `ssProvisionalSingleLower/Upper`, `ssMaxTaxablePct`), explaining they are the reference values the flat 85% default derives from. Then:
- **resolvers now read `IRS_2026`** instead of echoing literals
- **the Tier 7 reference implementation reads the engine's constants too** — otherwise the test file stays a second source of truth
- added `ss.maxTaxablePct` as a 23rd §21 fact + its own assertion

**Proof the fix is real:** mutating the ENGINE constant (44000 → 50000) now fires **6 tests**, including the published worked example — because the reference implementation reads the engine. **The old tautology would have stayed green.**

> **LESSON: a resolver that echoes the expected value is not a test. If a Tier 0 edge cannot fail when the ENGINE changes, it is decoration.** Verify the checker, not just the verdict — the same rule that caught 3 bugs in the conservation audit.

## Survivor mechanics — Tier 7 COMPLETE (307/307)
Docs made three specific claims; each verified against code AND behaviour:
1. **"survivor SS = the larger of the two configured amounts"** — line ~2395 `Math.max(hSsAmount, wSsAmount)`, payable from the survivor's own claim age. ✓ Behaviourally: H $60k / W $30k, H dies at 75 → joint $212,091 → survivor $145,636 = **66.7%**, exactly 60k-of-90k plus one year of COLA.
2. **household drops to one** — `persons` and `persons65` are both survivor-aware (healthcare + per-person IRMAA). ✓
3. **the death year still files MFJ** — Single applies only from the year after (IRS rule). ✓

**Mutation-verified:** survivor keeping their OWN benefit ($30k) instead of the larger ($60k) → caught, *"34.3% (expect ~66.7%)"*. That is the realistic wrong implementation, and the ratio test rejects it.

**Single app:** survivor tests correctly skipped — `survivorOn = false` is hardcoded (no surviving spouse for a single filer).

## CONTEXT entry section rewritten (user's suggestion, adopted over a README)
Replaced the vague 3-layer table with a **5-layer table** + a **"which file do I open?" situation router** + an explicit **precedence rule** (TESTING = method, Help = behavior, CONTEXT = history, code = mechanics; fix the loser immediately). Caught a stale *"three-layer system"* claim in the process — the same rot this section now guards against.

**[DECISION] No README.** CONTEXT's entry section *is* the router; a README would be a fifth artifact restating the first, which is precisely how the three stale survivor blocks happened. Revisit only if the project goes public on GitHub, and then as a thin pointer.

## Status
Suite **307/307**. Baselines unchanged. §21 now carries **23 facts**. SS constants verified byte-identical across both apps (a parity checker false-alarmed on neighbouring lines that legitimately differ between the forks — **the checker was wrong, not the code**).

## Early-withdrawal penalty — DOCUMENTED + LOCKED, engine untouched. Suite 307 → 312.

### The question: "is this an issue?"
**It is a real modelling limitation, but not a bug, and fixing it would make it worse.**

### What the engine does
Line ~2629: `if (maxAge < 59.5) penaltyTax = (elecTradDrawn + elecRothDrawn) * 0.10;` — `maxAge` is the **OLDER** spouse.

### Why that is defensible
In law the 10% penalty is assessed **per account owner**: your age governs your account, a spouse's age is irrelevant to it, and there is **no household-level 59½ test**. This engine pools Traditional and Roth into **one shared balance** (a documented simplification), so it **cannot know whose account a dollar came from** and must pick one age.

- `maxAge` (current) **UNDERSTATES** — exempts once the older spouse clears 59½, ~**2.8 years** early for the default birthdates (H Jul 1980, W May 1983).
- `minAge` would **OVERSTATE** — penalising the older spouse's own money.
- **Neither is correct for a pooled bucket.** A "fix" swaps one wrong answer for a differently wrong one.

The real fix is **per-spouse account buckets** (split Trad/Roth by owner, per-owner age tests) — a structural change touching the solver, RMDs, the survivor path, and every conservation scenario. Large, risky, **buys nothing at the defaults**.

### Rule 8 again: the doc was already accurate
§8 states it plainly: *"the 10% early-withdrawal penalty on Trad/Roth draws **if the older spouse** is under 59½."* Disclosed, not hidden.

### INERT at the defaults (verified, not assumed)
**Zero** Trad/Roth draws occur before 59½ — the withdrawal sequence draws brokerage first, so the penalty never fires at all. This also **corrects my own earlier claim** that it was "HIGH stakes, reachable": it is reachable only in plans funding early retirement from tax-advantaged accounts. Forced scenario (no brokerage): 2040–2042 draw **$863,514** with **$0** penalty — ~**$86,351** understated *if that money were the younger spouse's*.

### What shipped
- **Help §20 (MFJ):** a full limitation entry — the per-owner rule, why one age must be picked, the **direction** of the error, the **~2.8-year window**, and **when it bites** (early retirees drawing Trad/Roth; the default plan never triggers it).
- **Help §20 (Single):** the age test is **unambiguous** for a single filer (one owner, no older/younger question) — noted as such.
- **Tier 7 (5 tests):** penalty reachable + fires; equals exactly 10% of Trad+Roth draws; **the age test uses the OLDER spouse** — pinning the documented choice so a future "fix" announces itself.

### ⚠️ MY FIRST PENALTY TEST WAS WORTHLESS — the maxAge→minAge mutation PASSED
It computed `draws * 0.10` **itself** and asserted the result was positive — **arithmetic on the test's own numbers**, which cannot see the engine's age test at all. Same family as the LTCG helper tests.

**Fix:** published `audPenaltyTax` (the Tier 8 ratchet again — behaviour worth asserting must be observable) and rewrote the tests to read **what the engine actually charged**.

**Now mutation-verified, both directions:**
- `maxAge → minAge`: caught — *"3 year(s)… drew $863,514 and were charged $86,351 — must be $0"*
- rate `10% → 5%`: caught — *"2028: draws $138,275 -> engine charged $6,914, expected $13,828"*

> **LESSON (third time this session): if a test computes the expected value from its own inputs rather than reading the engine's output, it is arithmetic, not a test.**

### Stale queue fixed
The **"Remaining queue"** section was written at 216 tests and listed five items — **all five had shipped**. It was actively misleading a future reader. Marked SUPERSEDED with each item ticked off. *The doc-rot we spent the session hunting was in this file too.*

### Status
Suite **312/312**. Baselines unchanged ($687,726 / $340,807). Engine change = **publication only** (`audPenaltyTax`); no logic touched.

## RE/BI recapture — investigated, LEFT AS-IS. A near-miss caught by cross-referencing the design.

### What happened
Auditing RE/BI recapture (the last "what's left" item), I found the engine does **not** step the invested basis down for depreciation taken, and — comparing against §1250 rules and a published worked example ($500k→$700k, $100k depreciation) — concluded it **understated exit gain** by roughly the depreciation amount (~$58k gain / ~$12.5k tax on the default deal). I verified the 25% ceiling against ~10 sources, confirmed the direction was "less conservative for planning," mapped the blast radius, and was about to mock up a basis-step-down fix.

### Why that was WRONG — the user's question saved it
The user asked: *"have you cross-referenced the help docs and context to see if there's a reason why this was built the way it was built?"* I had **not**. Doing so overturned the whole premise:

1. **These are passive LP / syndication stakes, not directly-owned property.** The user corrected exactly this wrong premise when the feature was built: *"This person doesn't invest into any physical real estate directly. Instead they are invested as Limited Partner (LP)... quarterly distributions, payout on refinance or sale."*
2. **Depreciation is ALREADY modeled — during the hold, as the sheltered portion of distributions** (`distTaxablePct`, default 25%; the K-1 shelters most of the cash). CONTEXT [DECISION]: *"Ongoing depreciation shelter ≈ 'distribution taxable %'... Captures the K-1 reality without modeling depreciation schedules."*
3. **My "fix" would have DOUBLE-COUNTED depreciation** — once as the hold-period shelter, again as extra exit gain. It would have *overstated* exit tax, not corrected it.
4. **The exact conservatism question was already asked and answered** at design time. [DECISION]: recapture = % of invested capital, capped at gain, at 25% — *"chosen because depreciation accrues on the property basis, not on how much the deal appreciated,"* and it *"handles the edge case where a deal barely appreciates but was still depreciated."* Both more accurate AND conservative **for this asset class**.

The engine is correct and internally consistent. My analysis compared an LP-syndication model against a direct-owner §1250 regime it was deliberately not using.

### What shipped
One clarifying line in §15b (both apps): the invested figure is treated as cost basis at exit and is **not** separately stepped down for depreciation, **because** depreciation's benefit is already captured in the distribution shelter — doing both would count it twice. This is precisely the trap I fell into; the doc now prevents the next reader (human or LLM) from "correcting" a correct model.

### THE LESSON (worth more than the line of doc)
> **Rule 8 said read the Help before auditing. The deeper rule: read the Help AND the decision log before concluding the engine is WRONG.** "Wrong vs standard tax treatment" is meaningless if the model deliberately uses a different, documented treatment for a good reason. I ran the tax-law research (§1250, the 25% cap) but not the *design* research — and tax-law correctness against the wrong asset class is just a confident error. The design-mockup gate is what caught it: nothing shipped because the user stops big engine changes at mockup review.

### Status
Doc-only change; engine untouched. Baselines unchanged ($687,726 / $340,807). Suite **312/312**. Both apps re-locked.

**RE/BI recapture: CLOSED — working as designed, now better documented.**

## HSA distribution mechanics — verified SOUND, locked. Suite 312 → 320. No engine change.

### Read docs + decision log first (rules 8 and 8-deeper)
No prior HSA design decision beyond "MFJ doubles 401k/IRA but NOT HSA" (a contribution-limit rule, unrelated). The mechanic itself:
- line ~2451 `hsaAvailForHc = max(0, hsa)` — the whole balance is available
- line ~2614 `hsaCover = min(hsaAvailForHc, netHealthcare)` — **HSA pays qualified healthcare FIRST**, up to balance
- line ~2615 `hcFromPortfolio = netHealthcare - hsaCover` — portfolio covers the rest
- line ~2680 `hsaDist = hsaCover; hsa -= hsaDist` — HSA drawn only by what it covered

### Verdict: correct, and correctly tax-free
The engine draws the HSA **only** to pay qualified healthcare — never for non-medical spending — so every distribution is a qualified medical distribution and rightly carries **no tax**. The "HSA as backdoor Traditional after 65" strategy is not modeled; that's a conservative omission (it would only ever *add* tax-advantaged flexibility, never remove tax). At death, leftover HSA flows to legacy taxed at `heirHsaTaxRate` (line ~3023) — correct: a non-spouse heir owes ordinary income tax on an inherited HSA. **Docs confirm intent:** *"inherited Traditional/HSA get taxed (SECURE Act 10-yr drain)."*

### Verified behaviourally
Default plan: **44 years** of HSA distributions. Early years show the HSA covering the full bill ($46,972) with **$0 from the portfolio** while the balance lasts — HSA-first confirmed.

### Locked (4 tests, both apps)
Mechanic is live; **HSA pays healthcare before the portfolio**; a distribution never exceeds the balance; qualified-medical distributions are tax-free.

**Mutation-verified:**
- `hsaCover = 0` (portfolio pays all) → caught (no distributions fire).
- `hsaCover * 0.5` (portfolio pays half despite balance) → caught by the ordering test: *"5 year(s) drew from the portfolio while the HSA still had balance."*
- `hsaAvailForHc + 50000` (overdraw) → caught by the balance test **AND** Tier 2's negative-balance invariant (`hsa -6755`) — defense in depth.

### Status
Test-only; engine byte-identical to shipped. Baselines unchanged. Suite **320/320**.

**HSA: CLOSED — working as designed, now locked.**

### What genuinely remains (honest inventory)
- **529 / tuition burn** — 10 live years; mechanical (Tier 8 proves no leak, order/cap untested).
- **Monte Carlo** — separate stochastic path; wholly untested, but low tax-accuracy stakes (wraps the same engine).
- **Gifting** — simple subtraction; Tier 8 conserves it.
None are tax-*table* errors. Tier 7's core mission is complete; these are lower-stakes mechanics.

## 529 shortfall  CURRENT MECHANISM (supersedes the "shortfall gain" section below)

> **UPDATED THIS SESSION  the fix described in the section immediately below was itself
> superseded.** The pro-rata-basis approach (`brok -= shortfall` with `__sfBasisRatio` /
> `__auditShortfallGain`) still drew the shortfall **directly from brokerage, outside the
> withdrawal solver**. That had two further defects, both found by the user via a simple
> tuition bump: (1) when the shortfall EXCEEDED the brokerage balance, brokerage went
> **negative** (phantom money, e.g. -$2.56M in stress) instead of cascading to Trad/Roth;
> (2) the display columns (Portfolio W/D, Brokerage Dists, recon panel) omitted the shortfall
> draw, so they didn't reconcile.

### The current fix (both apps, byte-matched by code)
The 529 shortfall is now **routed through the withdrawal-sequence solver** (`computeTaxForWithdrawal`),
exactly like living expenses, gifting, healthcare, and LTC. Concretely:
- The tuition-shortfall block no longer does `brok -= shortfall`; it only depletes the 529
  (`f529 = 0`) and records `__auditShortfall = tuitionBurn - f529` for display + the solver need.
- `baseNeedFixed = plannedTargetDraw + childGiftAmt + __auditShortfall`  the shortfall enters
  the solver's cash need, so it **cascades Brokerage -> Trad -> Roth**, caps each bucket at
  `Math.max(0, balance)` (never negative), and is taxed correctly (LTCG on brokerage gains via the
  solver's own `brokGain`, ORDINARY income on any Traditional spillover, none on Roth).
- `__auditShortfallGain` was REMOVED from `preferentialGains` (the solver's `brokGain` now already
  includes the shortfall's brokerage portion via `elecBrokDrawn`  keeping it would double-count).
- Display: `tuitionFromPortfolio: __auditShortfall` (was hardcoded 0); the recon tuition row shows
  "529 paid $<covered>" + the from-portfolio shortfall; `pwd`/Brokerage Dists now include the
  shortfall automatically (it flows through `brokDrawn`); the recon "Year reconciles" line gained a
  `- HSA` term (HSA is in the 4-bucket pool but not in W/D).

**Why this is the RIGHT fix, not just a patch:** an audit confirmed the 529 shortfall was the ONLY
cost that bypassed the solver. Gifting (in `baseNeedFixed`), healthcare + LTC (in `grossHealthcareBase`
-> `hcFromPortfolio` -> solver) all already cascade correctly and never go negative  verified by
stress test. So routing 529 through the same solver makes ALL costs consistent.

**Verified:** default baselines UNCHANGED (MFJ $1,176,702 / Single $528,223  default has $0 shortfall);
stress (empty 529, huge tuition, tiny brokerage)  no bucket ever negative, cascades brok->trad->roth
floored at 0; Traditional spillover taxed as ordinary income (e.g. 2033: tradDrawn $213,592 ->
taxableOrd $174,580, previously untaxed-negative); user's repro reconciles to the dollar.

**Test hardening:** the suite missed the negative-brokerage bug because the `edge-zero-balances`
fixture had been SOFTENED (poolBrok 800000) to dodge it and the fix was demoted to a code comment.
Restored the fixture to honest all-$0, added an `edge-tuition-shortfall` fixture, and added TWO Tier-8
conservation invariants (run nominal, every scenario, every year): **non-negativity** (no bucket < -1)
and **carry-forward** (each bucket's nominal end == next year's start).

---

## 529 shortfall gain — REAL BUG FOUND AND FIXED (engine change). Suite 320 → 326.

### The bug
When a 529 can't cover tuition, the engine sells brokerage to fund the shortfall. It was reducing basis by the **full** shortfall (`brokBasis -= shortfall`) and realizing **no capital gain** — the appreciated portion of a real brokerage sale went entirely untaxed. **Direction: understates tax, overstates final wealth** (the unsafe-for-planning direction).

### The triangulation failure that flagged it
The help doc said the shortfall reduces basis *"proportionally"* — implying pro-rata basis (which realizes gain). The code subtracted the **full** shortfall (no gain). **Doc and code disagreed.** Unlike RE/BI recapture (a documented, deliberate simplification), the decision log had **no** entry making this intentional — so it was a genuine bug, not a design choice.

### Why it was safe to fix (blast-radius investigation, at user's request)
The shortfall is computed at position ~198,997 in the year loop — **before** preferentialGains (~209,372) and the tax solver (~212,420). Crucially, the shortfall does **not** depend on the solver's output, so taxing the gain creates **no circular dependency** (the thing that made the SE wage-base cap risky). The fix reuses the already-verified, mutation-tested LTCG stacking pipe — no new tax math.

### The fix (byte-identical in both apps)
At the shortfall branch: compute `__sfBasisRatio = min(1, brokBasis/brok)` BEFORE mutating, realize `__auditShortfallGain = shortfall * (1 - basisRatio)`, reduce basis **pro-rata** (`- shortfall * basisRatio`), hoist the gain to loop scope, and add it to `preferentialGains` so the LTCG solver taxes it. Published `audF529ShortfallGain`.

**Verified:** baseline unchanged (default 529 fully funds tuition → the path never runs); forced-underfunded case realizes ~60% of the shortfall as gain (matching 40% basis) and taxes it via stacking ($16,290 LTCG once ordinary income clears the 0% band). **Mutation-verified:** reverting to untaxed/full-basis fails with *"realized gain $0 (0% of the sale; ~60% expected)."* Conservation holds (326/326 including Tier 8).

### ⚠️ MY TEST WORK LEAKED STATE — caught by the suite, not shipped
Seeding a child in the Single app (which has none by default) to exercise the 529 path **leaked tuition into the LTCG end-to-end test** — because `childrenProfiles` is module-scoped (not on window), so my cleanup guard silently never ran, and `restoreInputs` can't undo a non-DOM array. Symptom: a later test failed with *matching* values ($26,014 == $26,014), the tell that the SCENARIO was contaminated, not the math wrong. **Fix:** dropped child-seeding entirely — MFJ has children and proves the shared engine path; the Single app skips gracefully with a recorded note. Verified the shipped suite was 320/320 clean before re-adding, to prove the engine fix wasn't the culprit.

> **LESSON: a test that mutates module state (not just DOM inputs) must clean it up, and `restoreInputs`/`snapshotInputs` only cover the DOM. When a later test fails with values that MATCH, suspect cross-test contamination, not the assertion.** (Same family as the earlier "verify the lever moves the number.")

### Doc + spec updated
§College Funding now states: basis reduced **pro-rata**, the appreciated portion realized as LTCG (stacked), and the 529 burn itself tax-free (qualified education) — only the shortfall sale is taxed. This is the third doc/code disagreement triangulation caught this project (after the survivor blocks and the SS threshold tautology).

### Status
Engine change, both apps byte-identical. Baselines unchanged ($687,726 / $340,807). Suite **326/326**.

### Remaining (honest)
- **Monte Carlo** — separate stochastic path, wholly untested, low tax-accuracy stakes.
- **Gifting** — simple subtraction, Tier 8 conserves it.
Everything with real tax stakes is now covered.

## Monte Carlo — verified SOUND, locked. Suite 326 → 336. No engine change.

### What "accuracy" means for MC (it's not a published number)
The success rate is random by design, so testing an exact % would be testing noise. Instead the tests pin the MACHINERY — four properties, investigated empirically before locking:

1. **Fair dice (parametric generator).** 80,000 samples: mean **6.02%** vs 6% ROI (0.4 SE — noise), vol **15.00%** vs 15% input. The Box-Muller Gaussian is correct (a wrong one couldn't produce a right mean AND SD). ✓
2. Same check, folded in — no standalone Gaussian test (redundant with #1).
3. **THE LINCHPIN — each path reuses the REAL engine.** `mcRunOnce` sets `window.__mcPath` then calls `triggerRecalculate()` (the actual 81-year loop, which reads `mcPath.returns[i]`). Proof: a path pinned to constant 6%/3% reproduces the deterministic baseline **to the dollar** ($687,726). No shadow engine. ✓
4. **Riskier → lower.** Success falls monotonically as vol rises: 100% → 41% → 29% → 15%. ✓

### A real insight about THIS plan (not a bug)
The baseline's **minimum spendable across the whole path IS the EOL** ($687,726) — it ends at its lowest point with the target intact but zero cushion. That's why mild vol (10%) drops survival to 41%: the plan is tuned tightly to its target, so it's genuinely sensitive to sequence-of-returns risk in early years. Correct behaviour; worth the user knowing.

### Locked (5 assertions, both apps)
Fair-dice mean; fair-dice vol; **engine-reuse (pinned path = baseline)**; monotonicity (riskier not safer); success rate ∈ [0,100%].

**Built for stochastic safety:** wide tolerance bands (mean ±1.2% ≈ 4.5 SE, vol ±2%), high sample counts, direction-only monotonicity check. **Verified NOT flaky** — 10/10 across two consecutive clean runs.

**Mutation-verified (all three caught):**
- dice skewed +3% → *"mean 9.11% (expected ~6%)"*
- engine reuse broken (mcRunOnce corrupts injected returns +2%) → *"deterministic $687,726 vs pinned MC $16,969,708"*
- survival test inverted (depleted counts as survived) → *"low-vol 30% vs high-vol 82% (must not increase with risk)"* — exactly the sign error the monotonicity test exists for.

### Status
Test-only; both apps byte-identical to shipped. Baselines unchanged. Suite **336/336**.

**Monte Carlo: CLOSED — machinery verified, locked.**

### Remaining
- **Gifting** — simple subtraction; Tier 8 conserves it. The only untested item left, and the lowest-stakes thing in the app.

Every subsystem with real stakes — tax tables, cash flows, RE/BI, HSA, 529, and now the Monte Carlo apparatus — is verified and triangulated.

## Gifting — verified SOUND, locked. Suite 336 → 342. THE LAST ITEM. Coverage complete.

### Rule 8: docs described it accurately, and it's MORE than "simple subtraction"
The decision log called gifting "simple subtraction" — that was an understatement. Docs (§College Funding & Gifting) and code agree: gifts are one-off transfers in **today's dollars, inflated to the gift year** (`childGiftAmt = childGiftingProfile[currentYear] * infScale`, line ~2056), then added to the spending need (`baseNeedFixed = plannedTargetDraw + childGiftAmt`) — so they're **funded through the full tax/withdrawal solver**, not subtracted raw. Shown in the Life Event column.

### Verified behaviourally + reconciled
Default plan already gifts **$1.1M** (2038–2043). Clearing all gifts raises EOL from $687,726 to **$4,400,271** — confirming gifts cost ~$3.3M of legacy (compounding of money given away decades early). A single $100k gift in 2030 reduces EOL by **$349,601** = the inflated amount ($112,551) compounded at ~**2.4%/yr** — which reconciles exactly: 6% nominal − 3% inflation (EOL shown in today's dollars) − tax drag on the funding withdrawal. Not a naive $100k subtraction; correctly integrated.

### Locked (3 tests, both apps)
Gift reduces legacy (funded, not free); legacy cost exceeds the nominal gift (inflation + forgone growth); **gift is inflation-adjusted to its year** — the tight test asserts the exact nominal value 100000·(1.03^years) in FUTURE-dollar mode. Published `audGift` for observability.

**Mutation-verified (both apps):**
- inflation removed (`* infScale` dropped) → caught directly by the nominal-value test.
- funding removed (gift not added to baseNeed) → caught: *"zero-gift EOL $4,400,271 → with a $100k gift $4,400,271 (down $0)"* (free money detected).

### ⚠️ THE MODULE-STATE LEAK — I walked into it AGAIN, then fixed it properly
My first gift test called `clearGifts()` (removing the default $1.1M) but `restoreInputs` only restores DOM inputs, not the module array `childGiftingProfile` — so the cleared defaults leaked into later tests and **broke the SS/ACA and survivor tests**. This is the THIRD instance of the same trap this project (529 child-seeding, and the earlier phantom-lever family).

**Fix:** snapshot the gift rows from the DOM, and in `finally` rebuild each one EXACTLY (year + amount) through the app's own `addGiftRow` + `updateGiftYear` + `updateGiftAmt` handlers. **Verified exact restore** — years and amounts identical before/after — and **two clean consecutive full runs** (not flaky).

> **LESSON (reinforced, now a hard rule): any test that mutates module-scoped state — childrenProfiles, childGiftingProfile, rebi deals — MUST snapshot and rebuild it in finally. `snapshotInputs`/`restoreInputs` cover ONLY DOM inputs. When a test change breaks UNRELATED later tests, it's a state leak, not a logic error.**

### Also weak-then-fixed: the first inflation test was too loose
It compared audGift to ~$100k in TODAY-dollar mode, where the value is ~$100k regardless of inflation (±50% tolerance) — so it couldn't catch a missing infScale. Switched to FUTURE-dollar mode with the exact 1.03^years factor. The mutation that previously slipped past it is now caught directly.

### Triangulation: doc already correct — nothing to change
The §Gifting doc already states all three tested properties (today's dollars, inflated, funded via withdrawals). Verified, not assumed. No §21 fact needed (those are for tax constants; the 3% inflation input is already tested).

### Status
Both apps byte-identical to shipped except the `audGift` publication (parity verified). Baselines unchanged. Suite **342/342**.

**Gifting: CLOSED. Every subsystem in the app now has known-answer coverage.**

## ═══ PROJECT COVERAGE: COMPLETE ═══
Tax tables, cash-flow conservation, RE/BI, HSA, 529 (+ a real shortfall-gain bug fixed), Monte Carlo machinery, and gifting — all verified, mutation-tested, and triangulated (docs ↔ engine ↔ tests enforced by Tier 0). **342 tests, both apps, mutation-verified throughout.** Nothing with material stakes remains untested.

## Roth conversion — verified SOUND, locked. Suite 342 → 350. THE last untested feature. No engine change.

### Why this one: CONTEXT itself flagged it
The honest-status note called **"RMD × conversion interactions… live code with ZERO targeted tests"** the *"highest-value open work item."* A coverage sweep confirmed it: 55 engine references, two methods, a `roomToBracketCap` helper — and zero known-answer tests. Exactly what a green suite hides.

### The mechanic (verified against the code, not memory)
- **bracket-fill:** `taxableExConv = ordinaryExConv − stdDed`; `room = roomToBracketCap(taxableExConv, capRate, brackets)` = (top of the cap bracket) − taxableExConv; `dynConv = min(room, tradAvail)`. Fills ordinary income to the top of the chosen bracket. Also has an **ACA preserve-subsidy cap** (sizes conversion so MAGI lands AT the 400%-FPL cliff, never over) — a documented interaction.
- **fixed:** converts `rothConvFixedAmt * infScale`, capped at the Traditional balance.
- A conversion **moves trad→roth; it does not leave the portfolio** (Tier 8 conservation edge).
- Eligibility: `rothConvOn && !isSaving && !isCovered && convStartOk && trad > 0`.

### Verified behaviourally + reconciled to the dollar
Bracket-fill to the 12% top, spending funded from brokerage (so the only ordinary income is the conversion): **MFJ converts exactly $100,800, Single exactly $50,400** — each app's own 12% ceiling (`IRS_2026.mfjOrdinary` / `singleOrdinary`, the 22% start). Fixed method: $50k → nominal $82,642 = 50000·1.03^years, exact.

### Locked (4 tests, both apps)
bracket-fill live; **bracket-fill converts exactly up to the 12% ceiling**; fixed converts the exact inflation-adjusted amount; conversion shifts buckets without leaving the portfolio. **Mutation-verified:** overshoot `room+50000` → *"converted $131,051 vs top $100,800 (30% off)"*; fixed drops `*infScale` → *"$50,000 vs expected $82,642."* Not flaky (2 clean runs).

### ⚠️ MY FIRST BRACKET-FILL TEST WAS FRAGILE — and it surfaced real engine understanding
First version asserted **post-deduction taxable income** lands at the ceiling. It passed MFJ but the Single app landed **$35,667 vs the $50,400 top** — which looked like a Single-app bug. Investigation showed the engine is CORRECT: with only the conversion as income, part of it fills the standard deduction, so post-deduction taxable lands *below* the ceiling by (stdDed − otherOrdinary). The **conversion AMOUNT** equalling the ceiling is the real, universal contract; post-deduction taxable only equals the ceiling when base ordinary income already exceeds the deduction. **Rewrote to assert `conv === bracket12top`** with brokerage-funded spending — exact in both apps.

> **LESSON: when a new test fails in one app but not the other, suspect the TEST's assumption before the engine (rule 4 extended). The Single "discrepancy" was the standard deduction doing its job — the fragile assertion, not the engine, was wrong. Assert the direct engine contract (the conversion amount), not a downstream quantity (taxable income) that other correct mechanics also move.**

### Triangulation (Triangle B — a mechanic)
Doc already describes both methods ("Fill Bracket Up To", "fixed dollar", "Conversion Method") — no doc change needed. Engine publishes `audRothConv`; tests read it. The bracket EDGES it fills are §21 facts already tested by the bracket tests. Per-app bracket table selected via `fileKey`, never hardcoded MFJ.

### Status
Test-only; both apps byte-identical to shipped. Baselines unchanged. Suite **350/350**.

**Roth conversion: CLOSED.**

## ═══ COVERAGE NOW GENUINELY COMPLETE ═══
Every subsystem in the app — tax tables, conservation, RE/BI, HSA, 529, Monte Carlo, gifting, **and Roth conversion (incl. the RMD×conversion-era bracket-fill that CONTEXT flagged as the top gap)** — has known-answer coverage, mutation-verified and triangulated. **350 tests, both apps.** The honest-status caveat about "composed scenarios with zero targeted tests" is now resolved. Nothing with material stakes remains untested.

## Worked-example drift — 2 stale examples found & fixed, then GUARDED with a new Tier 0 edge. Suite 350 → 352.

### The trigger (a user question, not the suite)
"Examples in the help docs should be based on the app defaults unless stated otherwise — are they still accurate after the recent engine changes?" Correct instinct. Two had gone stale:

1. **MFJ 2035 drawdown example** — said tax **$43,695** → total **$68,695**; current engine on defaults produces **$43,506 → $68,506** (a recent-cycle change shifted 2035 tax by $189). Fixed.
2. **Single ACA worked example** — said applicable % **≈8.4%** at ratio 2.56×; engine's `acaApplicablePct` now returns **8.61%**, cascading through contribution/subsidy/net ($3,360→$3,444, $10,640→$10,556, $7,360→$7,444). Fixed.

Verified-still-correct (checked, not assumed): MFJ semi-retirement income example (defaults $25k+$100k, ages 57/60), MFJ IRMAA example (>$410K → $6,355/$12,710 = the tier's `annual`×2), MFJ ACA example (9.46% = engine 9.464%, $5,678 exact), Single 2035 drawdown ($90k/$8,623/$73,623), the $3M deflation illustrations, and all inline tooltips (the one claim-bearing one, ACA MAGI, computes `totalOrdinary + gains + full SS` — accurate; app-to-app tooltip differences are correct singular/plural).

### The durable fix: Tier 0 EDGE 5 — worked-example resolvers
Prose numbers derived from the engine had **no triangulation edge**, so they rotted silently when the engine changed (unlike §21 facts). New edge:
- **Markup only** in the apps: the example's engine-derived numbers are wrapped in `<span data-example="aca.pct" data-magi="60000" data-fpl="21150">9.46%</span>`. **Displayed text is unchanged** — the reader sees exactly the same thing; the span just makes the number machine-findable. The number a human reads and the number the test checks are now the SAME DOM element, so they cannot diverge.
- **Resolver in the suite** (`EXAMPLE_RESOLVERS` in tier0): recomputes each tagged value from the live engine (`acaApplicablePct`) and asserts the displayed text matches within tolerance. Untagged/unsupported keys are ignored; if the engine fn isn't reachable in an app it skips cleanly.

Scope: only **derived-from-function** examples tagged (the ACA calcs in both apps — the ones that actually drift with tax years). Whole-plan scenario examples (the 2035 drawdown) are NOT tagged — recomputing them needs the full default run and is brittle; they stay manually verified.

**Mutation-verified both directions:**
- prose reverted to stale 8.4% (engine unchanged) → caught: *"page shows '8.4%' but engine computes 8.61%"*
- engine skewed +1% (prose unchanged) → caught both tagged values: *"page shows '9.46%' but engine computes 10.46%"* — THIS is the real-world case (you edit a tax constant next tax year).

### ⚠️ NO ENGINE/MATH CHANGE
The only edits to the app files are the cosmetic `<span>` wrappers around already-displayed numbers. Engine, constants, solver, defaults untouched. Baselines unchanged ($687,726 / $340,807). Suite **352/352**.

### LESSON
> **Prose that cites engine-derived numbers is a triangulation blind spot.** §21 facts were guarded; worked examples were not, and two drifted in a single session's edits. Tagging derived numbers with `data-example` + a Tier 0 resolver turns "verified once by hand" into "recomputed every run." The pattern extends to any future example: wrap the number, add a resolver, done. Whole-plan-scenario numbers are the exception — guard the constants they cite, not the derived total.

### Status
Two doc fixes + one new Tier 0 edge + 4 tagged values (2 per app). Test-suite gains the resolver. **352/352.** This is the third drift a user question caught that the green suite missed (after the stale suite subtitle and these examples) — reinforcing that prose/label rot is the residual risk class, now partly automated away.

## Pass 1 — three default/UX changes (user-directed). Suite 352 → 356. Baselines UNCHANGED.

Driven by the Roth-conversion investigation (below): aggressive "fill to 22%" default made EOL look like it halved on toggle-on. User directed three changes.

### 1. Roth conversion bracket-fill cap default 22% → 12% (BOTH apps)
Two touch-points per app: the `<option ... selected>` in markup + the `|| 22` JS fallback (now `|| 12`). **Baseline-neutral** — conversions are OFF by default, so the cap only matters once a user turns them on. Rationale: 12% is far less punishing (EOL ~$944k vs ~$543k at 22% in the default plan) and won't make a user's legacy appear to halve the instant they enable conversions. (The least-misleading choice is arguably OFF, since any fill hurts this particular all-Roth-anyway plan, but 12% is the gentler on-state.) Guarded by a new Tier 1 default check; mutation-verified (revert to 22 → red).

### 2. Single app 529 default $275,000 → $100,000 (SINGLE ONLY; MFJ stays $275k)
One touch-point: `pool529 value=` in single.html. **Baseline-neutral** — the Single app has no children by default, never spends the 529, and the 529 is EXCLUDED from Liquid Net Worth EOL, so EOL stays $340,807 either way. Guarded by the same Tier 1 check (expects $100k for single, $275k for mfj); mutation-verified.

### 3. RE/BI Refi Capital + Exit Value $-formatting (BOTH apps) — Option A (full consistency)
**Root cause:** RE/BI money fields are rendered dynamically (when a deal is added), AFTER `initMoneyInputFormatting()` ran at load — so they never got the blur/focus formatter and showed raw `10000`. **Option A fix:** after the RE/BI render loop, attach a `$`-prefixed formatter (`fmtRebiMoney`) to all `[data-money]` fields in the section, formatting on load+blur and stripping to raw digits on focus. Now Refi Capital, Exit Value, AND the siblings (capital/currentValue/annualDist) all show `$10,000` consistently — fixing a pre-existing inconsistency where siblings showed `$` on render but dropped it after any edit.
- **⚠️ LANDMINE AVOIDED:** `cleanNum` only stripped commas, NOT `$`. Adding `$` to fields without fixing this would make `parseFloat(cleanNum("$10,000"))` = NaN → 0, silently zeroing every RE/BI value into the engine. Fix included **`cleanNum` now strips `$` and whitespace too** (`/[$,\s]/g`) — safe across all 44 call sites (stripping more formatting can only help parsing). Verified: stored deal values parse to clean numbers (cap=200000, refi=10000, exit=250000) while displaying `$`.
- **Display-only** otherwise: zero math impact, both baselines unchanged.

### Verification
Both baselines exact ($687,726 / $340,807), no page errors, suite **373/373** (2 new default guards × 2 apps), not flaky (2 runs), both default guards mutation-verified. Both apps byte-identical for the shared RE/BI + cleanNum logic.

**Still LOCKED after this pass.** Pass 2 (doc-only: example-drift rewrite to age-relative + the "53 (2035)→(2036)" label) is separate and not yet done.

## Input-panel currency formatting — made CONSISTENT (comma-only, no $). Both apps. Baselines UNCHANGED. Suite 373/373.

User flagged three formatting styles coexisting in the left input panel:
- balances/contributions (Traditional/Roth/Brokerage): `10,000` (comma) — the desired style
- Undergrad/Grad $/yr, Gifting amounts: `10000` / `$10000` (no commas — they were `type="number"`, which browsers won't comma-format)
- RE/BI cards: `$10,000` (the $ added in Pass 1)

**Chosen target: comma-only `10,000`** for ALL input-panel currency fields (majority convention, safest — extends the proven `initMoneyInputFormatting` pattern). The year-by-year projection RESULTS GRID is left AS-IS (keeps its own $/comma display) per user.

### Changes (both apps, byte-identical shared logic)
1. **Undergrad/Grad cost** (`updateChildField`): `type="number"` → `type="text" inputmode="decimal" data-money="true"`; render via a comma-only `money()` helper added to `renderChildrenProfiles`; parser fixed to `parseFloat(cleanNum(...))`; comma formatter attached after the dynamic render loop.
2. **Gifting amounts** (`renderGiftRows`): same field conversion; **removed the separate `$` span**; parser `updateGiftAmt` → `cleanNum`; formatter attached after loop.
3. **RE/BI cards**: reverted Pass 1's `$` — `fmtRebiMoney` now emits comma-only.

### ⚠️ SAME LANDMINE CLASS AS PASS 1 (avoided)
`type="number"` fields' parsers used `parseFloat(el.value)`. Once values show commas, `"10,000"` would parse as `10` — silently corrupting child tuition + gift amounts into the engine. Every parser was fixed to `cleanNum` in lockstep with the display change. `cleanNum` already strips `$`+commas+whitespace (from Pass 1), so it's robust.

### WHY type=number was the root cause
Browsers refuse commas in `<input type="number">`. So comma formatting is impossible without converting to `type="text"`. That's why these specific fields were the inconsistent ones — not an oversight, a technical constraint of the input type.

### Verification
Both baselines exact ($687,726 / $340,807); lifetime gifts still $1,100,000 (proves gift fields parse through the full engine); children undergrad sets/stores correctly (a mid-test "bug" was a stale-node artifact — MFJ has 2 default kids, so querySelector grabbed child #1's field while the test read child #3's value; matching ids confirmed correct). No `type=number` currency fields or stray `$`-spans remain in either input panel. No page errors. Suite 373/373, not flaky.

**Still LOCKED. Pass 2 (doc-only example-drift rewrite) remains separate and pending.**

## Pass 2 — example calendar-year drift (doc-only, Option B). Both apps. Baselines UNCHANGED. Suite 373/373.

Help examples cite concrete projection years (2035 step-down, 2036 conversion start, 2026–2034 accumulation, etc.). The app's projection start is `new Date().getFullYear()`, so these drift forward by one EVERY January regardless of any tax change — a recurring doc-rot generator, worse than tax drift because it needs no code change.

**Chose Option B (anchor + surgical) over a full age-relative rewrite of all 39 mentions.** Rationale: concrete years read far more clearly than "the year both spouses reach semi-retirement age" — rewriting all of them would make the docs worse and risk new errors. Instead:

1. **Anchor sentence** added to the "About the examples" section (both apps): concrete years assume the plan starts in the current year and shift as the calendar advances; read them as offsets from the start (step-down in the plan's 9th year, conversions the year after). One edit immunizes all 39 mentions by reference. (Single app phrased "you step down"; MFJ "both spouses step down.")
2. **Fixed the genuinely-wrong Auto-label** — this was stale independent of drift:
   - MFJ: `53 (2035)` → `53 (2036)` (×2) — engine's `autoRothConvLabel()` returns `53 (2036)`.
   - Single: `53 (2035)` → `56 (2036)` (×1) — was doubly wrong (wrong age AND year for a single filer); now matches the engine's `56 (2036)` and the sibling reference that already said so.
   Both apps now internally consistent: MFJ `53 (2036)` ×2, Single `56 (2036)` ×2, each equal to its live `autoRothConvLabel()`.
3. **Backstop** folded into the annual-IRS-update playbook (TESTING.md, new re-sync step 4): refresh example calendar years to the new base year, and make the Auto label equal `autoRothConvLabel()` exactly.

### WHY not auto-guard these (like the ACA worked examples)?
The Auto label COULD be guarded (it's a pure function output). But the accumulation-span / semi-retirement-timeline years depend on the live `new Date().getFullYear()`, so a test would have to compute "current year + offset" — which just re-encodes the drift rather than catching a real error. The anchor disclaimer + playbook step is the honest treatment; the label fix is a one-time correctness fix.

### Verification
Anchor sentence renders cleanly (no broken HTML); both baselines exact; suite 373/373; worked-example guard (Tier 0 EDGE 5) still green (help-prose edits didn't disturb tagged examples). Both apps byte-identical for the shared anchor text (modulo the spouse/filer wording).

**Pass 2 COMPLETE. Both apps re-locked.**

## ═══ ALL QUEUED WORK COMPLETE ═══
Pass 1 (three app changes: Roth cap default 12%, Single 529 $100k, input-panel $ formatting) + input-panel comma consistency + Pass 2 (example calendar-year drift) all shipped. Suite 373/373. Baselines $687,726 / $340,807 unchanged throughout. Both apps locked.

## FUTURE TO-DO (parked, not started) — self-guarding doc examples
User parked this. Several help-doc numbers mirror engine outputs but aren't auto-guarded, so they can silently drift on a future default-change or annual IRS update (correct today; risk is slow future rot):
- **Auto conversion label** (2 spots: MFJ `53 (2036)`, Single `56 (2036)`) — mirrors `autoRothConvLabel()`; cleanly guardable via a Tier 0 resolver (recompute + assert doc text matches), exactly like the ACA `aca.pct` guard.
- **~15 bare tax-figure mentions in prose examples** (IRMAA `$6,355`/`$12,710`, contribution limits `$24,500`/`$8,000`/`$11,250`/`$1,100`/`$49,000`) — mirror engine constants; not tagged. The §21 Verified-Facts table IS guarded; these prose repeats are not.
Options when picked up: (1) guard all via data-example tags + resolvers, (2) guard just the label, (3) rely on the annual-update playbook's "refresh examples" step. Building the guard tags the app files (invisible, baseline-neutral) + extends the suite resolver — same safe pattern as ACA. No correctness issue today; this is drift-protection only.

## ═══ DISTRIBUTION MIX CHART — COMPLETE, BOTH APPS. Suite 356 → 363. Baselines UNCHANGED. ═══

A new "Distribution Mix" tab in the hideable chart area: a Sankey-style cash-flow view showing, for a
given year, where money comes from (Sources) and what it pays for (Spend). Three panels default to
life-phase milestones (semi-retirement / full retirement / SS-claim age), each with an independent year
dropdown. **NO ENGINE CHANGES** — the chart is a pure VIEW over published `__chartSeries` fields;
baselines stay $687,726 / $340,807. Render call is wrapped in try/catch so a view bug can never break
the engine path.

### VERIFIED FLOW MAPPING (locked; matches the ledger table cell-for-cell; guarded by Tier 9)
User's "do the numbers match the detailed table?" caught FOUR double-count/mismatch bugs before build:
- **SOURCES:** Traditional `audElecTrad` · Roth `audElecRoth` · Brokerage `audElecBrok` · Social Security
  `incomeSS` · RE/Business `rebiDist` · **1099 `audGross1099`** (gross cash, NOT tax-adjusted income1099)
  · HSA `audHsaDist` · 529 `audTuitionBurn − audF529Shortfall`
- **SPEND:** Living `audBaseNeed − audGift` (baseNeed BUNDLES gifts) · Healthcare `audHcFromPortfolio +
  audHsaDist` (HSA-funded HC not in hcFromPortfolio) · Taxes `audSolvedTax` (ALREADY includes LTCG — do
  NOT add audLtcgTax) · Gifting `audGift` · Tuition `audTuitionBurn`
- The four corrections: (1) Taxes double-counted LTCG, (2) Living double-counted gifts, (3) Healthcare
  missed HSA-funded portion, (4) 1099 gross-vs-net. **With this mapping, Sources = Spend to the dollar
  every year** — strongest evidence the mapping is right. SS is OFF by default (ssToggle unchecked), so
  the SS ribbon shows $0 unless enabled — correct behavior, not a bug.

### DESIGN (evolved over many mockups; all shipped for approval)
- **Hybrid-3**: three compact panels side-by-side. (Zoom was built then REMOVED — it showed identical
  data, added a click with no new info.)
- **Constant-thickness ribbons** (a $69k flow = one thickness on both edges); the flowing look comes from
  gapped outer edge + flush spine edge, ribbons sliding vertically. NOT tapered (taper misrepresents the
  amount). Spine sized to the taller of the two stacks, top-aligned (no overhang), square edges.
- **Palette "Slate & Clay, brighter"**: editorial hues, saturation ~70% (cool Sources / warm Spend, no
  brown). Theme-aware via CSS vars `--dist-spine` (white on dark / dark on light), `--dist-sources`
  (mint/emerald), `--dist-spend` (coral/red) — all also used for the Sources/Spend words in the intro
  sentence and panel totals so they match in both themes.
- Labels: name on line 1, `$X (N%)` on line 2 (side-relative %). **Hover any ribbon** → native SVG
  `<title>` with exact $ and 2dp % ("$28,610 (6.12% of sources)"). NOTE: native tooltips don't fire on
  touch — mobile users get the rounded labels only. (Custom tooltip offered, not built.)
- Zero/immaterial flows hidden via a `>= $1` threshold (the engine leaves float dust like 3.9e-33 that a
  `>0` test would draw as a "$0 (0%)" min-floor ribbon).
- Responds to the global Today's $ / Future $ toggle (hooked at the `__chartSeries` publish point, which
  runs on every recalc incl. setDollarMode). Include HSA / Include 529 toggles are HIDDEN on this tab
  (they scope the trajectory chart's balances, meaningless for a flow view).
- Single app: no spouse → ages read "Age 55" not "H55 · W52" (via `distAgesFor` checking whether the
  wife INPUT is visible — `wBirthYear` offsetParent — since Single mirrors wAge internally); no children/
  529 by default so those ribbons are absent. Default years still resolve (2035/2040/2050).

### The header restructure
Merged two rows into one: collapse chevron + tab labels (Net Worth Trajectory / Distribution Mix) on the
left, Include HSA/529 toggles on the right. Removed the redundant "Net Worth Trajectory by Bucket" h3
(the tab says it). Tab row lives OUTSIDE #chartCollapseBody so tabs/toggles stay put when collapsed;
collapse still works.

### Tier 9 guard (test-suite.html) — the permanent chart-vs-ledger check
Re-derives the verified mapping and asserts: (a) the app's own `distFlowsFor` matches it every year,
(b) Taxes excludes the LTCG double-count, (c) Living strips bundled gifts, (d) Sources balances Spend to
the dollar. **Mutation-verified**: reintroducing the LTCG double-count → red (`2035 spend Taxes: ref
43506 vs app 51081`); 1099 gross→net → red (`2035 src 1099 Income: ref 125000 vs app 107338`). This is
the automated version of the by-hand check that caught the four bugs.

### Docs
New Help section "4b. Distribution Mix" + TOC link, both apps. Explains the tab, the source/spend
categories, hover-for-exact, table reconciliation, dollar-toggle response, and why HSA/529 toggles hide.

### Byte-parity
JS module, distribution pane markup, tab header row, recalc hook, and all three theme vars are
BYTE-IDENTICAL between the two apps (asserted via md5 of each region). Single differs only in runtime
behavior driven by its own inputs (no spouse, no kids).

### PARKED (user's call, not forgotten)
- **Colorblind safety**: Brokerage `#1da29b` and Social Security `#22b5c0` sit close in hue — likely
  collapse under deuteranopia. Not checked/adjusted.
- **Custom (non-native) hover tooltip** for touch-device support — offered, not built.
- (Earlier) self-guarding doc examples: Auto-label + ~15 bare tax figures in prose.

### SHIP HASHES (this feature, final)
index.html `2cc1d1f78a13d2950b6dc1756e143f5b` · p-zero-single.html `60f9708f7987a73bac05c193b65d854a` ·
test-suite.html `305411fa9e0b65ba5ed671ef29f9f607`. Suite 373/373 both apps, not flaky (2 runs).

**Both apps RE-LOCKED.**

## ═══ DISTRIBUTION MIX CHART — COMPLETE (both apps) ═══

A "Distribution Mix" tab in the hideable chart area: a Sankey cash-flow view showing, for a given year,
where money comes from (Sources) and what it pays for (Spend). Pure VIEW over published `__chartSeries`
fields — ZERO engine changes. Baselines unchanged ($687,726 / $340,807). Suite 356 → 363.

### Design (settled over many iterations with user)
- **Hybrid-3**: three compact center-spine Sankey panels side by side (Semi-Retirement / Full Retirement /
  SS-Claim Age), each with its own year dropdown. Zoom was built then REMOVED (added a click, no new info).
- **Ribbon geometry**: CONSTANT thickness end to end (a $69k flow = one thickness). The flowing look comes
  from the outer edge being gapped (labels get room) while the spine edge packs flush; ribbons slide
  vertically to close gaps. Spine sized to the taller stack, top-aligned (tops of first ribbon + spine +
  first spend ribbon all on one line), square edges, thin (6px).
- **Labels**: source/category name on line 1, `$X (N%)` on line 2. Hover any ribbon → native SVG `<title>`
  with exact `$28,610 (6.12% of sources/spend)`. (Native tooltip = no touch support; noted, not fixed.)
- **Palette "Slate & Clay, brighter"**: B's editorial hues, saturation lifted ~48%→70%. Cool Sources /
  warm Spend so left=in / right=out reads without a legend; no hue on both sides. No brown.
- **Dual totals**: Total Sources (green) / Total Spend (red), shown separately — they balance to the dollar
  in retirement years but legitimately differ in working years, which is why both are shown.
- **Theme-aware** via `--dist-spine` (white on dark / dark on light), `--dist-sources` (mint/emerald),
  `--dist-spend` (coral/red). Intro-sentence "(Sources)"/"(Spend)" and panel totals all use these vars.
- Responds to the global Today's $ / Future $ toggle (renders from the recalc path).
- **Include HSA / Include 529 toggles HIDDEN on this tab** — they pick which balances stack in the
  trajectory chart; meaningless for a flow view. Reappear on the trajectory tab, state preserved.
- **Single app**: no spouse → ages read "Age N" not "H.. · W.." (keyed on spouse-input VISIBILITY, since
  the series always carries a mirrored wAge). No children/529 by default → those flows absent. Balances $0.

### THE VERIFIED FIELD MAPPING (locked; guarded by Tier 9) — 4 bugs the user's questions caught
User asked "do the numbers match the detailed table?" — cross-checking caught FOUR double-count/mismatch
bugs before they shipped, each of which would have made the chart disagree with the ledger:
- **Taxes = `audSolvedTax`** (already includes LTCG via solvedResult.totalTax — do NOT add audLtcgTax)
- **Living = `audBaseNeed − audGift`** (baseNeed BUNDLES gifts; subtracting prevents double-count)
- **Healthcare = `audHcFromPortfolio + audHsaDist`** (HSA-funded HC isn't in hcFromPortfolio)
- **1099 = `audGross1099`** (gross cash received, NOT the SE-tax-adjusted income1099)
- Sources: Traditional `audElecTrad` · Roth `audElecRoth` · Brokerage `audElecBrok` · SS `incomeSS` ·
  RE/Business `rebiDist` · HSA `audHsaDist` · 529 `audTuitionBurn − audF529Shortfall`
- Spend also: Gifting `audGift` · Tuition `audTuitionBurn`
- **With this mapping, Sources = Spend to the dollar EVERY year** — strongest evidence it's right.

### Tier 9 guard (test-suite.html) — the PERMANENT version of the hand-check
Asserts: (1) app `distFlowsFor` matches an independent copy of the verified mapping across all years;
(2) Taxes excludes the LTCG double-count; (3) Living strips bundled gifts; (4) Sources balances Spend to
the dollar every year. Runs with SS force-enabled + restored after. **Mutation-verified**: reintroducing
the LTCG double-count → `✗ 2035 spend Taxes: ref 43506 vs app 51081`. 7 new assertions across both apps.

### Help docs
Section 4b "Distribution Mix" already existed (thorough) + TOC link. A duplicate 6b was accidentally added
during this build and REMOVED — one 4b section remains, byte-identical between apps.

### Parity
All shared regions byte-identical between apps (JS module, pane markup, header row, recalc hook, theme
vars, 4b help). Verified via md5 per region. The only app difference is runtime (spouse-input visibility).

### Ship md5s
index.html `667dab3c` · p-zero-single.html `8f2a2648` · test-suite.html `305411fa`.

**Both apps RE-LOCKED. Parked (user's call): colorblind safety (Brokerage #1da29b vs SocSec #22b5c0 close
under deuteranopia); native tooltip has no touch support; self-guarding doc examples (older to-do).**

## Distribution Mix — year-selector auto-tracking + reset (both apps). Baselines unchanged. Suite 373/373.

Bug: changing a birth year or semi/full-retirement age recomputed the distribution $ but the three panels'
year DROPDOWNS stayed put (the old persistence line only reset a year when undefined or out-of-range, so
any set value stuck). Fix distinguishes "tracking" from "pinned":
- **`distUserSet[i]`** flag per panel. Untouched (false) -> panel follows its life-phase milestone, so an
  input change moves the dropdown to the new milestone year. Pinned (true, after a manual pick) -> keeps
  the user's year even as inputs change, UNLESS that year falls out of range (then falls back to milestone).
- **`setDistYear` sets userSet=true** (pinning); **`resetDistYear` clears it** (back to auto-track).
- A **`↺` reset button** renders next to the dropdown ONLY when the panel is pinned; title names the exact
  milestone year it will restore. Theme-aware (muted colour, themed border).
Verified all 4 paths in-app: untouched tracks a birth-year change; pinned resists a semi-age change; reset
makes the button vanish and re-tracks; out-of-range pin falls back. View-only, no engine impact. Byte-
identical between apps (render fn / year fns / decl all md5-matched).

## TO-DO LIST STATUS (updated)
- DONE: year auto-track + reset (this entry).
- REMOVED permanently (user's call): colorblind-safety adjustment. Not a need.
- PARKED: touch tooltips — native <title> has no touch support. LOE moderate, risk moderate for the feature
  (zero for the app); reward marginal since desktop has it and mobile still shows rounded labels + totals.
  Low-risk path if ever needed: on touch, briefly swap a ribbon's label to the exact figure (no floating el).
- PARKED: self-guarding doc examples (Auto-label + ~15 bare tax figures could drift on default/IRS change).
- OPEN (undecided, very old): FUTURE_ITEMS.md redirect-stub deletion.

## Doc follow-up for year auto-track/reset
Help section 4b updated (both apps, byte-identical): the "changed independently with its dropdown" sentence
now explains auto-tracking, pinning via a manual pick, and the ↺ reset button. Test suite: NO new test added
by design — Tier 9 guards flow-DATA correctness (numbers reconcile to the ledger for whatever year shows),
which is the property that matters; auto-track/pin is view STATE with zero engine impact, and a UI-wiring
test would be brittle without protecting correctness. The 4 behavioral paths were verified in-app once.
Ship: index.html + p-zero-single.html re-shipped with the doc update. Suite 373/373, baselines unchanged.

## Top nav: Import/Export merged into a "Profile" menu (both apps). View-only. Baselines unchanged. Suite 373/373.

Two separate top-nav buttons ("Import Profile", "Export Profile") merged into one `Profile ▾` dropdown with
those two items. Saves a full button's width in a six-button row.

**Why this passed the merge test but the middle "Show Detail" row did NOT:** Import/Export are OCCASIONAL
actions (save/load a scenario now and then), so trading one extra click for permanent width is a good deal.
The Show Detail toggles are used FREQUENTLY and usually one-at-a-time — a dropdown there would turn a
1-click view swap into open→uncheck→check→close, making the common case worse. Left as buttons. Same
reasoning rejects merging Compare/Solve For/Monte Carlo: those are primary, frequently-reached actions.
(Label "Profile" chosen over "Save/Load" — names the thing, not the mechanism, and matches the app's
existing `exportConfig` / export-coverage vocabulary.)

Implementation: `toggleProfileMenu` / `closeProfileMenu` / `profileMenuAction`; closes on outside click and
Escape; `aria-haspopup` + `aria-expanded` tracked; menu styled with theme vars. Import still routes through
the existing hidden `#importFileInput`; Export still calls `exportConfig()` — no change to either action.
Verified in both apps: opens/closes both dismissal paths, aria state correct, import fires, export wired,
export-coverage check still clean, no page errors. Profile markup + JS byte-identical between apps.

**Still to do (agreed): top-nav responsive collapse at narrow width.** Middle row and SS-panel label: no
change, by decision.

## Doc follow-up for the Profile menu merge
Help section 18 ("Profiles: Import / Export / Reset") described Export/Import as if they were still separate
top-nav buttons. Its CONTENT was still accurate (both actions unchanged), but a reader would hunt for two
buttons that no longer exist. Added one locator sentence to both apps: the two actions live under the
Profile menu in the top bar; Reset remains its own button. (The surrounding section body legitimately
differs between apps — MFJ says "household" inputs, Single says "personal" — so only the added sentence is
byte-identical, not the whole section.)
TESTING.md: no references to the nav buttons — nothing to update. Test suite: the only import/export
reference is a Tier check that chart-collapse state is saved in `exportConfig()` — that tests BEHAVIOR, not
button markup, so it's unaffected by the merge and still passes. No new test added: the merge is view-only
and a test on menu markup would be brittle without protecting correctness.
Suite 373/373, baselines unchanged, both apps.

## ═══ HEALTHCARE INFLATION + RE-BASED DEFAULTS (both apps) — NEW BASELINES ═══
**MFJ $687,726 · Single $340,807 · Suite 373/373.** (Previous: $1,111,487 / $808,524, suite 363.)

### Why
Healthcare escalated at general CPI (`baseHealthcare * infScale`), understating the largest and most
certain retirement expense. Medical costs run ~1–1.5 points above headline CPI (medical CPI ~3.1–3.6%
vs ~2.2% headline over 20 yrs). Over a 50+ year horizon that gap compounds enormously.

### New input: Healthcare Inflation (default 4.5%)
Own rate in Macro Inputs, no bounds. Drives THREE lines that previously used `infScale`:
`baseHealthcare` (pre-65), `baseMedicare` (post-65), and `acaBenchPremBase` — the benchmark must move
with the premium it's compared against (`Math.min(benchPrem, preRate)`) or the subsidy math drifts.
**Why 4.5% and not 5.25%:** an NHE-based rate (5–6%) measures total SPEND growth incl. utilization; these
inputs are fixed all-in base amounts the user sets, so an NHE rate double-counts utilization. The right
anchor for a fixed base is a PRICE rate — medical CPI's ~1.4-pt premium over the 3% CPI default ≈ 4.4%.

### ⚠️ Monte Carlo bug caught by the suite
First implementation did `infScale * (1 + (hcInf - inf))^i` — ADDING the premium, which compounds it on
top of the draw: 1.03 × 1.015 = 1.04545 ≠ 1.045. A pinned MC path then drifted from deterministic
($654,875 vs $687,726) and Tier 7 failed. Fixed to a RATIO: `infScale * ((1+hcInf)/(1+inf))^i`, which
reproduces the deterministic rate exactly when pinned while still letting a bad inflation draw feed
healthcare. **The MC-reproduces-deterministic test earned its keep.**

### Re-based defaults (Single stays exactly half MFJ throughout)
| input | MFJ | Single | note |
|---|---|---|---|
| healthcareCost (pre-65) | 36,000 → **40,000** | 18,000 → **20,000** | ALL-IN, not premiums alone |
| medicareCost (post-65) | 18,000 (unchanged) | 9,000 (unchanged) | already conservative |
| acaBenchmarkPremium | 28,000 (unchanged) | 28,000 → **14,000** | **BUG FIX**: Single carried the couple's benchmark |
| poolTrad | 1,000,000 → **1,200,000** | 500,000 → **600,000** | recalibration (see below) |
| healthcareInflation | **4.5** (new) | **4.5** (new) | |

**Recalibration rationale:** at $40k/4.5% the old MFJ default household ended at $3,968 — effectively
broke. The old defaults were calibrated against understated healthcare, so that household was never
actually funded; the old baseline was solvent on a false premise. Raising Traditional (user's chosen
lever) restores a plausible shipped example rather than one that fails out of the box.

### Docs re-derived against the LIVE engine (not find-and-replace)
Every worked example whose arithmetic depends on the changed inputs: defaults summary; drawdown example
(HSA now covers $45,559 MFJ / $22,779 Single — the $68,506 / $73,623 totals still verify exactly);
healthcare-model section 14.1; ACA worked example (net = $40,000 − $22,322 = **$17,678** MFJ;
$20,000 − $10,556 = **$9,444** Single); the full subsidy table in each app (every net-healthcare cell,
both cliff rows); the subsidy-label illustration ($13,007 / $9,360) and its "best possible year shows
~$13,007, not $12,000" reasoning; the split-year blended base ($27,000 → **$29,000**); Single's SLCSP
slice reference. Both healthcare inputs gained an **all-in** tooltip (premiums + deductibles + copays +
Rx + dental/vision; LTC explicitly excluded).

### Suite: 10 new Tier 1 guards (5 per app), mutation-verified
pre-65 healthcare, post-65 Medicare, ACA benchmark, Traditional balance, healthcare inflation — each
app-specific. Mutation: reverting hcInflation→3 and healthcareCost→36000 fails with
`healthcareCost=36000` and `healthcareInflation=3`.

### KNOWN SIMPLIFICATION (documented, not a bug)
One flat rate applies to all healthcare for the full horizon. Real trend likely converges toward CPI at
very long horizons, and post-65 exposure is partly Medicare-capped. Users can lower the rate to model a
converging gap. **LTC is NOT modelled at all** — a genuine gap, larger than the inflation question;
belongs as a separate contingency pool or scenario toggle, not as annual expense inflation.

## Single Traditional held at $500,000 (user decision) — Single baseline $340,807
User chose to keep the Single app's Traditional balance at its original $500,000 rather than take the
proportional $600,000. This deliberately breaks the exact-half relationship the two apps hold on every
other default (healthcare 40k/20k, Medicare 18k/9k, ACA 28k/14k) — a leaner single-filer household by
choice. Baseline is $340,807: tighter than MFJ's $687,726 but a viable plan with real cushion.
Tier 1 guard expectation updated to '500000'.

### Stale balance-defaults doc lines corrected in BOTH apps (found while checking this change)
Both apps' "Defaults: Traditional … Roth … Brokerage … HSA … 529" help lines were wrong, and the Single
app's was wrong on EVERY value — it was carrying MFJ's figures.
- **Single**: Traditional 1,000,000→**500,000**, Roth 500,000→**250,000**, Brokerage 1,000,000→**500,000**,
  HSA 130,000→**100,000**, 529 260,000→**100,000**. All five were MFJ numbers in the Single app.
- **MFJ**: Traditional 1,000,000→**1,200,000** (today's change), HSA 130,000→**150,000** and
  529 260,000→**275,000** (both PRE-EXISTING errors, unrelated to this work).
- Also dropped the hardcoded "(2026 starting values)" from both — the projection start year is live
  (`new Date().getFullYear()`), so a pinned year would drift every January.
These were documentation-only errors; the engine always used the real input values.

## Fix: the three tooltips added with the healthcare change were never wired (both apps)
The info icons on **Healthcare Inflation**, **Pre-65 Healthcare Cost** and **Post-65 Medicare Cost**
rendered but did nothing on hover. Cause: I wrote the markup by hand instead of copying the working
pattern, and omitted `onmouseenter="positionInfoTip(this)"` — the handler that actually places the tip.
The bare `class="info-tip"` also lacked the sizing/styling classes (`w-64 p-3 rounded-lg …`) and the
fixed-position inline style, so even once shown it would have been unstyled.

**Lesson: an info icon with no working tooltip is worse than no icon** — it advertises help that isn't
there. When adding one, copy an existing working tooltip wholesale rather than reconstructing it; the
handler wiring is not obvious from the markup alone.

Fixed all 3 per app (6 total) to match the Nominal Return template exactly. Verified at runtime: handler
present, tip content 254–300 chars, and the element is positioned after a `mouseenter` in both apps.
Baselines unchanged ($687,726 / $340,807), suite 373/373.

## Distribution Mix: custom ribbon tooltip replacing native <title> (mouse + touch, both apps)
The native SVG `<title>` had a browser-imposed delay and **never fired on touch** — so on a phone, where
the compact labels are hardest to read, the exact figures were unreachable. Replaced with a custom
tooltip mirroring the trajectory chart's, so both charts in the collapsible area behave identically.

- `distTipShow(clientX, clientY, label, amount, pct, side)` / `distTipHide()`, plus a `#distTooltip`
  div styled like `#chartTooltip`. Shows a colour swatch, the exact dollar amount, and the 2-dp share
  of its own side ("Share of sources" / "Share of spend").
- Ribbons carry `onmousemove` / `onmouseleave` / `ontouchstart`. **Tap-away dismissal** is a single
  document-level `touchstart` listener registered ONCE at load, not per render — re-rendering the
  panels (year change, dollar toggle) would otherwise stack duplicate listeners.
- Edge clamping: near the right edge the tip flips to the left of the cursor, with a `left < 0` floor.

**Verification note:** Tailwind CDN is blocked in the sandbox, so the grid never lays out and the pane
measures 0px wide — an in-browser edge-clamp assertion is meaningless there and returned a false
negative. The clamp logic was instead verified directly against realistic geometry (pane 1200px, tip
170px): cursor at the left edge, middle, right edge and far right all produce a tooltip that fits
within the pane. Mouse show/position/hide, touch show, tap-away dismissal, and zero remaining native
`<title>` elements were all confirmed in-app.

**Still not verified: the feel on a real device.** Headless confirms the code paths fire; it can't tell
whether the tip is comfortably sized on a phone or obscures the ribbon just tapped. Worth a look on
actual hardware.

Baselines unchanged ($687,726 / $340,807), suite 373/373, tooltip code byte-identical across apps.

## Self-guarding doc examples — Tier 0 extended (both apps)
Doc figures that mirror engine values but were plain typed text could silently drift on a default or
annual-IRS change. Two now self-guard via `data-example` tags + resolvers, same pattern as the existing
`aca.pct`/`aca.contrib`:

- **autoRothConvLabel** — the Auto conversion-start label ("53 (2036)" MFJ / "56 (2036)" Single), which
  had ALREADY drifted once ("53 (2035)" vs engine "53 (2036)"). Tagged in both prose spots per app (4
  total). Resolver calls the app's OWN `autoRothConvLabel()` — tests the real code path, not a copy.
  This is a STRING value, so a `strValue` branch was added to the Tier 0 comparison loop (exact match,
  not numeric-with-tolerance).
- **stdDeduction** — the standard deduction quoted in prose ($32,200 MFJ / $16,100 Single). Tagged in
  both prose spots per app (4 total). Resolver reads the app's live `#stdDeduction` element.

Both mutation-verified: corrupting the label to "53 (2035)" and the std deduction to "$30,000" each
fail Tier 0 with `page shows "X" but engine computes "Y"`. Suite 373/373. No engine contact — doc
tagging + suite logic only. Baselines unchanged ($687,726 / $340,807).

**Scope note:** only DERIVED-from-function or live-element figures were tagged. The ~12 other IRS
constants in prose (catch-up limits, IRMAA thresholds, 37% bracket edge) change only on the annual IRS
refresh — a deliberate, low-frequency edit where the engine tables and prose are updated together — so
they were left untagged rather than adding tag surface for a rare risk. Revisit if that refresh ever
misses a prose figure in practice.

## ═══ LONG-TERM CARE (both apps) — new feature, OFF by default ═══
Baselines UNCHANGED ($687,726 / $340,807) because LTC is off by default. Suite 373 → 390.

### Design (Option A: deterministic scenario toggle)
LTC is categorically different from every other cost — low-probability, high-severity, late-onset,
finite-duration. ~70% of 65-yr-olds need some paid care but ~30% never do, so averaging it into every
year is wrong both ways. Modelled as an explicit user-controlled stress-test (matches the app's
ACA-off / stress-off posture), NOT probabilistic (false precision) and NOT an earmarked reserve (that
answers insurance-sizing, not "does the plan survive"). Option A is also the foundation the other two
would build on, so it's the right first piece regardless.

### Inputs (MFJ two rows H+W; Single one row)
Per person: onset age, annual cost (today's $), duration (years). Toggle `ltcToggle` OFF by default;
`toggleLtcInputs()` shows/hides `#ltcInputs`. Defaults are EVIDENCE-BASED (all web-verified):
- **Onset 84** — mean age of entry into paid care (two independent sources).
- **Duration 2 (H) / 4 (W)** — documented ~2.2 yr men / ~3.7 yr women; the gender gap is WHY each
  spouse is modelled separately, not a nicety. Single app uses the one row at 2 yrs.
- **Cost $110,000** — national median semi-private nursing room; assisted living ~$75k, private
  room ~$130k. $110k is a defensible midpoint, not the scariest or cheapest.

### Engine
Per-year LTC cost added into `grossHealthcareBase` (the same gross that flows through ACA/HSA/portfolio
logic) at the line `... + irmaaSurcharge + ltcCost`. Applies when a person's age ∈ [onset, onset+years);
escalated by `hcInfScale` (today's-$ entry, healthcare-inflation growth); **stacked** on top of regular
healthcare (conservative, not replacing); **portfolio-funded** via the normal waterfall, NOT HSA-first
(HSA is earmarked for regular healthcare and spent down by 84 — HSA-first would falsely cheapen LTC).
Survivor phase: applies whichever row's window the survivor's age hits. Single app: one row on the
filer's age. Reads default to 0 when elements absent, so the Single app safely has no W row.

### Visible impact
No new KPI (would be clutter). LTC flows through the healthcare line, so it already shows in: the
end-of-life KPI, the trajectory chart (a ~$2.2M drawdown across LTC years is a visible dive), the
Healthcare ledger column, and the Distribution Mix healthcare ribbon.

### Docs + tests
Help §14c "sec-ltc" added to BOTH apps + TOC entry; explains the stress-test framing, the window math,
the escalation/stack/funding choices, the evidence behind the defaults, and known simplifications
(single episode per person, no LTC-insurance modelling, not probabilistic). Suite: **8 Tier-1 default
guards** (5 shared + 3 MFJ-only wife-row) covering toggle-off, inputs-hidden, and all six values;
plus **2 Tier-5 behavioral guards** (LTC-on reduces EOL; toggle is reversible). All LTC ids added to
the export inputIds list (coverage check clean). Mutation-verified: flipping the toggle to checked-by-
default triggers 9 failures — the direct Tier-1 guard names it (`checked=true`), and the baseline/MC
guards catch the downstream damage, locking off-by-default from multiple directions.

### KNOWN SIMPLIFICATIONS (documented)
One continuous episode per person (not multiple/escalating stages); LTC insurance not modelled (reduce
the cost by expected benefit if insured); fixed scenario, not probabilistic.

### PENDING (user tabled): inheritance RECEIVED during the plan
App already models bequest (after-tax legacy KPI, heir tax rates = money you LEAVE). Money coming IN
(receiving an inheritance mid-plan) is genuinely absent — likely what the user means. Confirm direction
when picked up.

## In-context UX cues for balance discontinuity + working-year tax withdrawal (both apps)
Two things users trip on were moved from "buried in help docs" to hover-in-place:

1. **Ending ≠ next Starting in Today's $ mode.** Added styled info-tip tooltips to BOTH the Combined
   Starting and Ending column headers explaining each row is a purchasing-power snapshot: a year's
   Ending and next year's Starting are the same money one year apart, so Starting shows ~inflation
   lower — nothing lost — and Future $ mode matches them to the penny. (This is the presentation fix
   for the discontinuity two external LLMs flagged; investigation confirmed the math is inherent, not
   a bug. Fixed-base-year deflation does NOT restore continuity — we already deflate to a fixed 2026
   base; the same nominal pile is simply worth less in 2026 dollars each successive year.)

2. **Tiny "◐ tax only" Portfolio W/D during accumulation years — investigated, NOT a bug.** Traced to
   brokerage dividends: the $1M brokerage at 2% yield throws off ~$20k/yr of taxable dividends even
   while working; the tax (~$895 rising) is paid by selling just enough brokerage, since the model
   doesn't simulate W-2 salary. Correct behavior. The existing explanation was a native `title=`
   (delayed, unstyled); converted it to the same styled info-tip pattern used on the input panel, with
   tightened wording. Content was already good — only the mechanism was upgraded.

No engine contact — display/tooltip markup only. Baselines unchanged ($687,726 / $340,807). Test-suite
byte-identical (390/390 logic untouched). Note: the long Playwright suite run couldn't complete in-tool
this session (browser long-runs time out the sandbox), but the suite FILE is identical to the shipped
390/390 version and these are display-only changes that touch no tested computation; syntax, baselines,
tooltip presence, and zero page errors were all verified via short browser runs.

## STILL PARKED: HC/LTC healthcare-inflation display + tapering (context preserved)
The big unresolved thread. Healthcare/LTC inflated at 4.5% but deflated at CPI (3%) in Today's $ mode,
so healthcare cells + the balances that absorb them are OVERSTATED in today's-dollars — compounding to
~74% overstated 38 years out ($110k LTC shows ~$191k). Confirmed this affects ALL healthcare, not just
LTC. Balances reconcile WITHIN each row (uniform per-row deflator) but the overstatement lives in the
drawdown, so balances are never "near the pin." Options assessed:
  - Option A: leave it, explain. (Conservative display of an unchanged plan.)
  - Option B: deflate healthcare at its own rate through flows+balances. Makes balances accurate.
    ASSESSED AT ~60% naive / ~90% if done the SAFE way: DON'T touch the fixed-point tax solver — it
    stays byte-identical in nominal; instead tag its converged output (hcFromPortfolio fraction) and
    build a PARALLEL real-terms balance accumulated from per-line-deflated flows. Must preserve THREE
    invariants (ledger row, Distribution-Mix Sources=Spend [Tier 9], conservation [Tier 8]) under both
    deterministic AND Monte Carlo inflation. Highest-risk change in project history; gate on Future-$
    byte-identical + baselines. Steps documented in-conversation.
  - Option 3 (RECOMMENDED): TAPER healthcare inflation toward CPI over time — fixes an arguably-too-
    aggressive assumption (flat 1.5pt premium for 50yrs) AND shrinks the overstatement in cells+balances
    as a side effect, at a fraction of B's risk (only changes how hcInfScale is computed per year).
    Design 2 = linear taper of the premium (1.5pt -> 0) over a "years to converge" window, endpoint
    anchored to CPI. OPEN DECISIONS: (a) one input "years to converge" (default ~25) vs fully-fixed no
    input; leaning one input. (b) taper default-ON (moves baselines, more realistic) vs opt-in (large
    window = near-flat, baselines hold). This is the next decision to make when resuming.

## Balance-header tooltips (all 12) + help link + Single view-control alignment
- **All 12 Starting/Ending headers** (Combined, Traditional, Roth, Brokerage, HSA, 529 — both HSA & 529
  share data-group grpHsa) now carry the styled snapshot tooltip, each ending with a
  "See Help §2 →" link (`openHelp('sec-dollars')`) to the fuller Dollar Display Modes explanation.
  Previously only the 2 Combined headers had it, and without the help link.
- **Single app view control replaced.** It had an outdated two-button "Condensed / Full View" segmented
  control; MFJ uses a single toggle button ("All years" ↔ "Every 5 yrs (65+)"). Swapped Single to MFJ's
  `btnViewToggle` + `toggleViewMode()`, replaced its `setViewMode` to update the label/icon (not the old
  buttons), and aligned Single's default `viewMode` from 'condensed' to 'full' so both apps open on
  "All years". Display-only; baseline $340,807 unchanged.
Display/markup only, no engine contact. Baselines exact. Suite byte-identical (390/390 logic untouched);
verified via short browser runs (full suite run times out the sandbox this session).

## Fix: Household (Combined) balance headers were missing the help link + §2 doc cleanup
- The 2 grpCombined ("Household") Starting/Ending header tooltips still had the OLD link-less version
  (a strip regex the prior session missed them), while the 10 per-bucket headers had the linked one.
  Replaced both so ALL 12 headers (Combined, Trad, Roth, Brok, HSA, 529) carry the identical tooltip
  with the "See Help §2 →" link to sec-dollars. Verified 12/12 linked in both apps.
- **§2 (Dollar Display Modes) doc cleanup, both apps:** replaced "This is correct behavior, not a bug"
  (which needlessly contradicts the user's intuition) with "At first glance this can look surprising…
  it's expected, not an error" and LED with the reassuring verification ("switch to Future $ and they
  match to the penny"). Per external-LLM UX feedback that the fix should be stated first, tone softened.
Display/doc only, no engine contact. Baselines exact ($687,726 / $340,807). Suite byte-identical (390).

## ═══ HEALTHCARE INFLATION TAPER — shipped (default-on, moves baselines) ═══
**NEW BASELINES (today's $, taper on by default): MFJ $1,176,702 (was $687,726), Single $528,223 (was $340,807).**
The old flat-4.5% baselines are GONE — this is a deliberate rebaseline, not drift. If you need the old
numbers, set healthcareInflation == CPI (neutralizes the premium) OR ANNUAL_CONSTANTS_2026.hcTaperOn=false.

### What it is
Healthcare's EXCESS over CPI (healthcareInflation - CPI, computed LIVE from panel inputs — never
hardcoded) fades linearly to zero over a 25-year window from the projection start, after which healthcare
grows at CPI. Applies to regular healthcare AND LTC (shared hcInfScale). Replaces the old assumption that
the full premium persists flat for the whole ~50-year horizon (which implied healthcare eventually eats an
implausible share of spending).

### Why default-on, 25yr, calendar-duration (the long decision, settled)
- **Default-on**: the app is STATELESS (inputs->outputs live; import/export saves inputs only, no stored
  results), so there is no saved-plan "shock" — every engine change already re-computes for anyone who
  reopens. So pick the model on BELIEF, not optics. The taper is the model we consider more realistic ->
  it's the default. (PDF export of outputs is a pinned future enhancement; would be the first thing that
  persists a result.)
- **25-year window**: chosen on belief (premium persists through the retirement-transition years, gone by
  deep old age), NOT to soften the baseline jump. Sensitivity analysis (15/20/25/30) showed NO plateau —
  the curve is a smooth continuum (~$60-80k EOL per 5yr step), and the first-order effect is taper-vs-not
  (~$507k), so the exact window is second-order. That smoothness is reassuring (model isn't hypersensitive).
- **Duration, not calendar year**: hcConvergenceYears is "N years from projection start," re-anchors every
  run, never stales, no annual advance needed. (Rejected: anchoring to a fixed calendar year = stales;
  anchoring to age = would understate an 85-yr-old's imminent costs.)
- **Linear taper** for v1 (transparent, testable). Exponential/logistic is a possible v2 refinement.

### Engine (both apps, byte-identical taper block)
hcInfScale is built as a cumulative product of per-year rates: rate_y = CPI + excess*taperFrac(y), where
excess = max(0, hcInfFlat - infFlat) and taperFrac fades 1->0 over the window. Applied IDENTICALLY in the
deterministic and Monte-Carlo branches: deterministic uses hcNominalFactor directly; MC uses
infScale * (hcNominalFactor / (1+CPI)^i) — the RATIO form (not additive) so a pinned MC path reproduces
the deterministic result EXACTLY (verified 0.000% both apps — this was the #1 accuracy risk, the historical
MC-healthcare bug spot).

### Constants: ANNUAL_CONSTANTS_2026 (new block, separate from IRS_2026)
{ reviewYear:2026, hcTaperOn:true, hcConvergenceYears:25 }. IRS_2026 stays strictly IRS statutory numbers.
Premium is NEVER stored here (computed live). See TESTING.md annual-update playbook for the maintenance
rules (esp. "window is a duration, not a calendar year — don't advance it").

### Reconciliation: FULLY PRESERVED (this is why taper beat Option B)
The taper only changes how fast healthcare GROWS (the rate curve) — it does NOT touch deflation. Every
row still deflates uniformly by CPI, so: within-row coherence holds (verified both modes), Sources=Spend
gap $0 (verified), Ending->next-Starting ties (the nominal engine is unchanged structurally). Option B
would have deflated healthcare differently and broken all three; the taper sidesteps that entirely.

### Persona sanity (50/65/75/85): all well-behaved
Healthcare-spend reduction scales sensibly with horizon (longer horizon -> bigger effect: 50yr~19%,
65~8%, 75~4%; the 85's 28% is a healthcare-concentrated-short-plan denominator effect, not a distortion).
Reconciliation held for every persona.

### Docs + tests
Help §14.2 "sec-hc-taper" in BOTH apps: behavioral description (NO hardcoded window number, so it never
stales), the "why this exists" philosophy box, a worked example, and the design-note principle. UI tooltip
on the Healthcare Inflation input links to §14.2. Two flat-escalation doc lines updated to note the taper.
Worked examples re-derived against the LIVE engine: MFJ drawdown healthcare $45,559->$44,625, Single
$22,779->$22,313 (only the healthcare figure moved; W/D and taxes unchanged since HSA covers it). The ACA
worked examples were checked and correctly LEFT AS-IS — they're static input-based illustrations of the
subsidy formula, not taper-affected projected values. Test guards: Tier 1 (AC exists, taper on, window 25,
premium-not-hardcoded), Tier 5 (far-out healthcare grows slower than flat counterfactual). All verified
passing directly.

### DESIGN PRINCIPLE established (may generalize later, only if asked)
"When a long-term assumption is uncertain, prefer a model that gradually converges toward equilibrium
rather than assuming today's conditions persist forever." Could eventually apply to return assumptions,
tax policy, SS — but NOT applied anywhere else without explicit request.

### ✅ VERIFICATION COMPLETE — full suite green (400/400)
The user ran test-suite.html and confirmed **Total: 400, Pass: 400, Fail: 0 — ALL GREEN** (count rose
390->400 = the new taper guards). This closes the gap noted below: no pre-existing test regressed, and the
new taper guards pass. The taper build is fully gated. (Original in-session note retained below for record.)

### ⚠️ (RESOLVED) VERIFICATION GAP DURING BUILD SESSION
The full Playwright SUITE (both apps in iframes, ~390 tests) could NOT be run to completion in-tool this
session — long dual-app browser runs time out the sandbox, and repeated attempts left stray browser procs.
What WAS verified via short direct runs: new baselines exact (MFJ $1,176,702 / Single $528,223), pinned-MC
== deterministic 0.000% both apps, coherence both modes both apps, Sources=Spend gap $0, all new taper
guards pass, syntax clean, no page errors, taper engine block byte-identical across apps. NOT independently
executed: the full green suite run proving no PRE-EXISTING test regressed. The suite FILE has the new
guards added but its prior logic is otherwise untouched, and the taper changes only healthcare growth (a
rate the engine already handled at any value) while preserving all reconciliation — so regressions are
unlikely — but a full green run should be executed when the environment allows before treating this as
fully gated.


## ⚠️ BASELINE CORRECTION (recorded numbers were wrong during taper build)
The taper-build session recorded MFJ $1,251,814 / Single $562,028 as the new baselines. Those were
MEASUREMENT ERRORS. The TRUE shipped baselines (verified: throwaway-25yr == shipped, pinned-MC MATCH,
today's $) are **MFJ $1,176,702 / Single $528,223**. The engine was always correct and internally
consistent (the 400/400 suite tests structural coherence, not the EOL dollar, so it stayed green either
way); only the recorded reference figures were wrong. All references above have been corrected to the
true values. Lesson: when recording a new baseline, re-read it from the SHIPPED output file, not from an
intermediate build-state measurement.

## ═══ SWEEP: HC header tooltip + LTC cell subtext + §14.2 duplicate fix (shipped, sealed) ═══
Follow-on to the taper: added user-facing context on the Healthcare column and fixed a doc-numbering bug.

### What shipped (both apps)
1. **Healthcare column HEADER tooltip** — taper-aware wording: figure is in today's $ but grows at Healthcare
   Inflation whose excess over CPI tapers, so it can differ from what's entered (close near-term, no runaway
   later). Links openHelp('sec-hc-taper') = §14.2.
2. **LTC cell SUBTEXT** — in LTC years, a purple "◐ incl. $X LTC" info-tip (same styled pattern as ACA/IRMAA
   sublines). References the ENTERED value (today's $) rather than claiming displayed==entered; links
   openHelp('sec-ltc') = §14c. Implemented by publishing audLtcCost = ltcCost * dispScale on the row
   (display-scaled) so the LTC portion deflates consistently. ltcCost confirmed in render scope.
3. **DUPLICATE §14.2 FIXED** — there were TWO "14.2 —" headings: the new taper section AND the pre-existing
   "MAGI: the yardstick". Resolved by KEEPING the taper at 14.2 (so all the new tooltip links stay correct)
   and shifting MAGI 14.2->14.3, ACA ->14.4, cell-sublines ->14.5, IRMAA ->14.6, MAGI-arc ->14.7,
   ACA-toggle ->14.8. Fixed the one "Section 14.2" MAGI prose reference -> "Section 14.3". No cross-refs to
   14.3-14.7 existed; TOC doesn't list subsections. Both apps now have a clean unique 14.1-14.8.
4. **LTC sub-line DOCUMENTED** in the "Reading the Healthcare cell sub-lines" section (now 14.5) in both apps,
   alongside the ACA/IRMAA sub-line explanations.

### New test guards (sweep) — all mutation-checked, verified biting
- Tier 1 doc/tooltip: sec-hc-taper exists; exactly one "14.2 —" heading (regex matches the RENDERED U+2014
  em-dash, NOT the &mdash; entity — innerHTML renders it as the char; this was a real guard bug caught and
  fixed); taper section is numbered 14.2; Healthcare header tooltip links sec-hc-taper; taper doc is
  evergreen (no hardcoded "25 year"/"two decades"); cell-sublines doc mentions "◐ incl. $X LTC".
- Tier 5 behavioral: LTC subtext renders in LTC years; subtext links sec-ltc; audLtcCost field is published.

### Verified (both apps): baselines exact ($1,176,702 / $528,223), pinned-MC==deterministic MATCH, all doc
checks pass, no page errors. GOTCHA recorded: innerHTML renders &mdash; as U+2014 — any regex guard over
innerHTML must match the char, not the entity.

## ═══ SWEEP GUARD FIXES + TEST-SUITE FILTERS (shipped) ═══
Re-applied the header-tooltip/LTC-subtext/§14.2 sweep from a clean green base (user re-uploaded the
pre-sweep green files after the first sweep attempt shipped 10 failing guards). Root-caused and fixed the
failures, added result filters.

### The 10 failures from the first sweep attempt — root causes
- **2 real guard bugs (mine):** the "cell sub-lines documents LTC" guard checked for the HTML ENTITY
  '&#9680;' but innerHTML renders it as the CHAR '◐' (U+25D0). Same class as the em-dash bug (&mdash; ->
  U+2014). FIXED: guards now match the rendered char. Lesson (reinforced): any regex/includes over
  innerHTML must match the RENDERED char, never the &entity;.
- **8 IRMAA/ACA/triangulation failures:** these were NOT caused by the taper engine (proven: pre-taper vs
  taper produce byte-identical DOM, column indices, and IRMAA-firing for those tests in isolation). They
  did not reproduce outside the full sequential suite. The re-applied sweep guards now RESTORE state
  (ltcToggle + dollarMode) after running, which was the likely culprit — the first attempt's LTC-subtext
  guard left dollarMode='today' set, and a downstream Tier-7 test that assumes 'future' mode read the
  wrong column / no IRMAA. The fix: the behavioral guard snapshots and restores both ltcToggle AND
  dollarMode. (This is the most probable explanation; confirmed by design, pending the user's full-suite
  green run.)

### Test-suite RESULT FILTERS (new, test-suite.html only)
Added a filter bar (hidden until a run completes) with:
- **Pass/Fail checkboxes** — show/hide rows by result. Skipped rows follow the Pass filter.
- **App checkboxes** (MFJ / Single-HoH) — show/hide each app's whole block.
They compose (e.g. Fail + MFJ-only shows just MFJ failures). Pure DOM show/hide over rendered results;
NEVER re-runs tests, and the summary counts remain the TRUE totals (all tests) regardless of filter. A
"showing N of M" hint appears when a filter is active. Verified across all combinations via a synthetic
result set (pass/fail/skip × both apps). Implementation: applyFilters() hooked into updateSummary() so it
re-applies after every render; hidden-by-filter CSS class on .row/.tier/.file-block.

### Verified (both apps, isolated): baselines $1,176,702 / $528,223 exact, header tooltip + LTC subtext +
### one-14.2 all present, all sweep guards PASS, taper engine byte-identical across apps, no page errors,
### filter logic correct across all combinations. PENDING: user's full-suite green run (sandbox can't run
### the full dual-app suite to completion in-tool — same limitation as before).

## ═══ THE 8-FAILURE ROOT CAUSE (found via on-screen diagnostics) — FIXED ═══
After the header-tooltip sweep, the suite showed 8 persistent failures (IRMAA + ACA + triangulation, 4/app)
that could NOT be reproduced in isolation. Repeated hypotheses (state leak, mode pollution, LTC toggle)
were all disproven. Resolution came from adding ON-SCREEN DIAGNOSTICS to the failing tests, which printed:
`hcIdx=-1 hdrs=72 ... seriesHasIrmaa=false`.

### Root cause
The Tier 7 IRMAA/ACA tests locate the Healthcare column via `hdrs.indexOf('Healthcare')`, where hdrs was
built with `th.innerText.trim()`. My header-tooltip sweep added a hidden `.info-tip` span INSIDE the
Healthcare `<th>`. **In the suite's HIDDEN IFRAMES, `innerText` is not layout-aware and falls back to
returning ALL text including the hidden tooltip** — so the header read as "Healthcare Shown in today's
dollars, but..." and `indexOf('Healthcare')` returned -1. Every cell lookup then used column -1 (empty),
so no IRMAA/ACA was ever detected. (In a VISIBLE browser, innerText correctly hides the tooltip text,
which is why it never reproduced in isolation — the whole multi-round wild-goose-chase.)

This is why the balance-header tooltips (added earlier, on Starting/Ending) never caused this: the tests
never look those columns up BY NAME. Only the Healthcare column is `indexOf`'d, and only it got a tooltip.

### The fix (test-suite only; NO engine or app change)
All 3 `hdrs` builders now use `__hdrLabel(th)` which reads only the th's DIRECT text nodes (nodeType 3),
ignoring nested tooltip spans, with a textContent-first-line fallback. This is layout-INDEPENDENT, so it
returns "Healthcare" in both visible browsers AND hidden iframes. Verified by simulating the iframe leak:
old method -> "Healthcare Shown in today's..." (fails); new method -> "Healthcare" (passes). hcIdx now =5.

### LESSON (recorded)
- **NEVER use `innerText` in a test that runs against a HIDDEN IFRAME** — it leaks hidden-element text.
  Use direct text nodes or textContent parsing. This burned ~6 rounds because innerText behaves
  DIFFERENTLY in a visible page vs a hidden iframe, so isolation tests (visible) all passed while the
  suite (hidden iframe) failed.
- When a failure won't reproduce in isolation, STOP guessing and add on-screen diagnostics to the failing
  assertion. One diagnostic run beat six rounds of hypotheses.
- The engine was never involved; this was purely a test-harness DOM-scraping fragility exposed by adding a
  tooltip to a column the tests look up by name.

## ═══ INHERITANCE FEATURE (shipped) ═══
A repeatable line-item system for money arriving mid-plan (inheritance, sold home, life insurance,
inherited IRA). Off by default; a no-op until switched on. Also renamed the "Life Event" column to
"Gifting" and gave gifting a toggle.

### Design (locked with user over a long design dialogue)
- **Master on/off toggle**, default OFF. When on, repeatable rows (add/remove, mirrors RE/BI events UI).
- Each row: name, amount, a **today's-$ vs nominal** selector (THIS SECTION ONLY), arrival year, and a
  **type dropdown**: taxfree (Tax-free Lump: cash, sold home, Roth, life insurance) / taxable_now
  (Taxable Immediately: annuity gain/IRD) / taxable_10yr (Taxable over 10 Years: inherited Trad IRA).
- **Nominal vs today's-$**: life insurance is genuinely nominal ($1M pays $1M whenever); fuzzy estimates
  are today's-$. Per-row selector. NO read-only conversion field in the input (would recreate the §2
  purchasing-power confusion at data entry); conversion surfaces naturally in the results table via the
  existing dollar-mode toggle. Tooltip on the selector instead.
- **10-year type**: LINEAR 1/10 of amount as ordinary income each yr for 10 yrs, NO growth wrapper. The
  point is the 10-yr MAGI/ACA/IRMAA tax-timing impact, not modeling the draining account's growth.
- **All types**: proceeds land in the BROKERAGE bucket via the existing surplus mechanism.

### Engine (reconciliation-safe by construction)
Per-year computes inheritanceCashIn (nominal gross->brokerage) and inheritanceTaxable (nominal ordinary
income), inserted after the RE/BI forEach. today's-$ amounts x infScale; nominal used as-is. Wired into
the SAME three sinks RE/BI uses: preWithdrawOrdinary (+taxable), cashSources (+cashIn), totalCashIn
(+cashIn). Cash lands in brokerage via the existing surplus->brok path; added inheritanceToBrok
attribution for the display column. Published audInheritance / audInheritanceTaxable / audInheritanceGross.
Engine code is byte-identical across both apps. Test hooks: window.__inheritanceSet(arr, enabled),
window.__inheritanceGet(), window.__giftingSet(enabled).

### Gifting column rename + toggle
- "Life Event" -> "Gifting" (header, cell, ALL doc refs, the column-description row). Column moved from
  grpCombined to its own grpGifting group.
- New grpInheritance column with a type sub-line (tax-free / taxable now / inherited IRA).
- Both columns show/hide via syncColumnGroups() driven by the FEATURE toggles (not the manual column
  button). Gifting toggle defaults ON when childGiftingProfile is non-empty (MFJ: 6 defaults preserved),
  OFF when empty (Single: {} -> off). Inheritance defaults OFF both apps.

### Docs
New Help section 15c (sec-inheritance) with all three types, a worked example each, and honest caveats
(annuity basis, no-growth-while-draining simplification, SECURE-Act 10-yr rationale, life-insurance
nominal, spousal-rollover not modeled). Nominal-vs-today's explained. Columns table + feature list
updated. Nominal-selector tooltip added. Zero "Life Event" references remain in either app.

### Tests (test-suite.html)
Tier 1 (6 structural): inheritance toggle defaults OFF; gifting toggle default per app (MFJ on/Single
off); Life-Event->Gifting rename; Inheritance column exists; sec-inheritance exists; hooks exposed.
Tier 5 (8 behavioral, fully snapshot/restore-isolated): tax-free raises EOL; column resolves by name
(via __hdrLabel, tooltip/iframe-safe); cell shows inflow + tax-free subline; taxable_now adds ordinary
income in arrival year; taxable_10yr spreads across EXACTLY 10 years; nominal stays as-entered while
today's-$ escalates; within-row reconciliation holds; off returns exactly to baseline. All 15 verified
passing in isolation in both apps. All column lookups use __hdrLabel (NOT innerText) per last session's
hidden-iframe lesson.

### Verified: baselines exact ($1,176,702 / $528,223), MC gate MATCH with inheritance active, engine
### parity, no page errors, all 15 guards pass in isolation. PENDING user's full-suite green run.

### PARKED (user agreed): charitable-vs-kids tax-DEDUCTION flag on GIFT line items. It's a tax-solver
### change (itemized deduction, AGI caps, std-vs-itemized interaction, affects MAGI/ACA/IRMAA), deserves
### its own focused task. Well-defined future item.

## ═══ INHERITANCE — completeness audit follow-ups (shipped) ═══
A post-build audit caught four gaps beyond the core feature; all fixed:
1. **Portfolio W/D help description** was incomplete — inheritance cash offsets the portfolio draw (a
   $200k inheritance can drop W/D to $0 in that year), just like RE/BI proceeds, but the formula text
   didn't mention inflow offsets. Updated in both apps to note RE/Biz + inheritance inflows reduce the
   draw (and can zero it).
2. **resetToDefaults()** didn't restore inheritance/gifting state — added DEFAULT_INHERITANCE_ITEMS /
   _ENABLED / DEFAULT_GIFTING_ENABLED restoration + re-render + toggle-sync in the reset path.
3. **exportConfig() / import** didn't round-trip inheritance — added inheritanceItems + inheritanceEnabled
   + giftingEnabled to the export snapshot and BOTH import restore paths. A saved profile now preserves
   inheritances.
4. **checkExportCoverage** (dev-only, MFJ) warned about giftingToggle/inheritanceToggle — added them to
   EXPORT_CHECK_IGNORE (they're saved via the snapshot enabled-flags, not inputIds). Single has no such
   guard, so no change there.
Verified: EOL and After-Tax Legacy both correctly include inheritance (it's in brokerage -> 100%
pass-through, no heir tax, which is right for money already received). Existing MAGI/ACA worked examples
unaffected (they use fixed hypothetical inputs, independent of inheritance). Test-suite gained a guard
that export saves inheritance/gifting state. Baselines still exact, MC MATCH, no errors.

## ═══ TOGGLE-BLANKS-TABLE BUG (fixed) — stale group-header colspan ═══
Symptom: toggling Gifting or Inheritance blanked the projection table until the user collapsed the left
panel (which forced a reflow and repainted it correctly).
Root cause: the "Household Summary" group-header cell (#combinedGroupHeader) has a colspan that must equal
the number of columns visually under it. It was hardcoded/adaptive as 14-or-13 back when the old "Life
Event" column lived INSIDE grpCombined. Moving Life Event -> Gifting (its own grpGifting group) and adding
the new grpInheritance column meant the columns under the banner became 13 (combined) + gifting-if-on +
inheritance-if-on, but the colspan still said 14. A header colspan that doesn't match the body column
count corrupts table column alignment until a layout reflow recomputes it (collapsing the sidebar sets
panel.style.display and forces exactly that reflow — which is why that "fixed" it).
Fix (both apps): the colspan is now computed dynamically as baseCombined (13 with MAGI / 12 without) +
(giftingEnabled?1:0) + (inheritanceEnabled?1:0), set on every recalc; and the STATIC default colspan in
the HTML was set per-app to match the initial toggle state (MFJ 14 = 13+gifting-on; Single 13 = 13+gifting
-off). Verified colspan == visible-column-count across all four toggle combinations in both apps; baselines
exact; toggling never empties the table; no reflow needed.
Lesson: when adding/removing/moving table columns, the group-header colspan(s) must be updated in lockstep
— a mismatch is invisible to logic tests (the data is all correct) but breaks the live layout until reflow.
Also kept: syncColumnGroups() now runs at the end of triggerRecalculate so feature-column visibility is
reapplied on every table rebuild (correct hygiene, though the colspan was the actual blanking cause).

## ═══ TWO REAL BUGS FROM USER TESTING (fixed) ═══
### Bug 1: gifting toggle didn't gate the gifts (logic bug)
Toggling Gifting OFF only hid the UI + column; the engine still applied childGiftingProfile, so EOL was
identical on/off. giftingEnabled was wired to column visibility but NOT to the engine. Fix (both apps):
`let childGiftAmt = giftingEnabled ? (childGiftingProfile[currentYear]||0)*infScale : 0;`. Now gifting OFF
truly stops gifts: MFJ EOL $1,176,702 (on) -> $4,481,638 (off, ~$900k of lifetime gifts retained); Single
unchanged (empty profile). Inheritance was already correctly gated (`if (inheritanceEnabled)` wraps its
whole block). Added a Tier-5 guard: gifting toggle gates the gifts (off stops them; asserted only when the
schedule has gifts).

### Bug 2: toggling Gifting/Inheritance blanked the table until the sidebar was collapsed (paint bug)
Symptom: toggle -> table blanks instantly (no console errors, <table> still in DOM); only collapsing the
left panel brought it back. Root cause: #sidebarPanel and #mainPanel are flex siblings in #appBodyRow.
Toggling a table COLUMN's visibility + rebuilding the body via innerHTML left the fixed-height
(calc(100vh-190px)), sticky-header, overflow scroll container in a stale paint state. Only a change that
forces the #appBodyRow FLEX ROW to recompute #mainPanel's width repaints it -- which is exactly what the
sidebar collapse (panel.style.display toggle) does. Earlier attempts toggled the wrong element (the table
wrapper), which doesn't cascade to the flex recompute. Fix: forceTableReflow() now does an invisible
same-frame round-trip on #sidebarPanel's display (off -> read #appBodyRow.offsetWidth -> on), forcing the
same flex recompute the manual collapse triggers. Called at the end of toggleGifting/toggleInheritance.
NOTE: this paint bug could not be reproduced in-sandbox because the Tailwind CDN is blocked here (layout
never renders headless), so it was diagnosed from the user's observation that only the sidebar collapse
fixes it. PENDING user's visual confirmation.

## ═══ "Children" -> "Education Planning" + master toggle (shipped) ═══
Renamed the top-level "Children" input container to "Education Planning" (icon fa-children -> fa-graduation
-cap) and added a master on/off toggle at that h2 level, mirroring the gifting toggle pattern.
- **educationEnabled** flag defaults ON when childrenProfiles is non-empty (MFJ: 2 kids -> on) and OFF when
  empty (Single: [] -> off). Defaults preserved exactly.
- **Engine gate**: the tuitionBurn loop and the 529-contribution lookahead (MFJ: `let total=0` remaining-
  tuition loop; Single: the `last529ContribYear` cutoff) are all gated on educationEnabled. When off,
  tuition -> $0 and 529 contributions stop. Verified: total tuition burn $544k -> $0 when toggled off.
- **Net-zero in default MFJ is CORRECT**: the default college is fully 529-funded (zero portfolio
  shortfall), so toggling education off removes both the cost and the matching 529 funding, leaving
  spendable EOL unchanged. Proven the gate DOES affect EOL when there's a portfolio shortfall (zeroed the
  529 -> education-on EOL $0 vs education-off $1,176,702).
- **UI**: child-profile rows wrapped in #educationBody (hidden when off); the nested Gifting Schedule
  stays OUTSIDE educationBody with its own independent toggle. toggleEducation() mirrors toggleGifting
  (hide body + recalc + forceTableReflow).
- **Wired into**: init (toggle reflects default state), resetToDefaults (restores DEFAULT_EDUCATION_ENABLED
  + re-syncs toggle), export snapshot + both import paths, and EXPORT_CHECK_IGNORE (MFJ). 
- **Tests**: tier-1 guards — education toggle default per app (MFJ on/Single off) + "Children"->"Education
  Planning" rename. Baselines exact ($1,176,702 / $528,223), no errors, both apps.

## ═══ "Total Taxable" column — preferential-income sub-line + header tooltip (shipped) ═══
User flagged that Total Taxable ($3,621 in 2042) looked misleading next to a much larger Taxes figure
($44k+). Not a bug: "Total Taxable" = totalTaxableGross = solvedResult.totalOrdinary (ORDINARY income
only), while Taxes also includes ltcgTax on preferentialGains (brokGain + rebiExitGainLtcg +
brokDivQualified) — long-term cap gains + qualified dividends taxed separately at preferential rates and
NOT shown in the column. In working years the brokerage throws off gains/divs (taxed) while ordinary
income is near zero, so tiny "Total Taxable" but real "Taxes". e.g. 2042: ordinary $3,621, preferential
$185,792, ltcgTax $22,595 of $56,273 total tax.
Fix chosen (option "E", user-approved): (1) CELL sub-line showing the preferential INCOME (not the tax),
labeled "cap gains & div", in muted orange, only when solvedResult.auditPrefGains > 0.5. Uses raw
solvedResult.auditPrefGains (c() applies dispScale). (2) HEADER tooltip on "Total Taxable" explaining it's
ordinary-only, that LTCG/qualified divs are taxed separately at preferential rates on the sub-line, and
why Taxes can exceed it. (3) Help-doc "Total Taxable" row expanded (it already noted LTCG taxed separately
— now points at the sub-line). 
IMPORTANT (hidden-iframe lesson): the header now has a tooltip, so the suite reads it via __hdrLabel (never
innerText). No test looks up "Total Taxable" by name via innerText, verified. Tier-1 guards added: header
resolves by name with tooltip present; cell shows the "cap gains & div" sub-line in a preferential-income
year. Both apps: baselines exact ($1,176,702 / $528,223), header label resolves clean, sub-line renders
(e.g. "$3,000 +$17,350 cap gains & div"), no errors.

## ═══ "Total Taxable" column clarity — preferential-income sub-line + header tooltip (shipped) ═══
User flagged that Total Taxable looked misleading: e.g. 2042 shows Total Taxable $3,621 but Taxes ~$44k.
NOT a bug -- the column shows ORDINARY taxable income only (solvedResult.totalOrdinary), while Taxes
includes ltcgTax on preferential income (long-term cap gains + qualified dividends: brokGain +
rebiExitGainLtcg + brokDivQualified). In working years the brokerage throws off gains/dividends taxed at
preferential rates while ordinary income is near zero, so tiny "Total Taxable" + real "Taxes" looks wrong
but is correct.
Fix (chosen: option E = sub-line + tooltip; user picked label "cap gains & div" and to show INCOME not tax):
- **Cell sub-line**: when solvedResult.auditPrefGains > 0.5, the Total Taxable cell shows the ordinary
  figure as the headline plus a muted sub-line `+$X cap gains & div` (the preferential INCOME, via
  solvedResult.auditPrefGains -> c() applies dispScale). Kept ordinary as headline; did NOT blend the two
  (they're taxed at different rates, blending would be its own confusion).
- **Header tooltip** on "Total Taxable": explains this is ordinary income; LTCG + qualified dividends are
  taxed separately at preferential rates and shown on the sub-line; that's why Taxes can exceed it.
- **Help doc**: the existing "Total Taxable" table row (which already noted LTCG taxed separately) was
  expanded to mention the sub-line and the working-years reason.
- **Test guard** (tier1): header still resolves by name via __hdrLabel WITH its new tooltip (iframe-safe,
  no innerText -- avoids the Healthcare-column-tooltip bug class); tooltip mentions preferential; a
  pref-income year shows the "cap gains & div" sub-line. Verified both apps.
Baselines exact ($1,176,702 / $528,223), MC MATCH, no errors. Cosmetic/display-only; engine untouched.

## ═══ RECONCILIATION EXPAND PANEL — Phase 1 SHIPPED (both apps) ═══
Click any ledger row in the combined "All Buckets Combined" table → a full-width expand row drops below it
showing the Portfolio-W/D reconciliation. This is PHASE 1 (additive, does NOT touch sticky headers or column
order). PHASE 2 (zone-band headers + column reorder + tinting) is the deferred, riskier sticky-header surgery
— NOT yet started; the mockup (reconciliation-mockup.html) is the approved target for it.

### What the panel shows (real per-year engine data, reconciles exactly):
- Two-column expenses table: each expense's full COST vs FROM-PORTFOLIO. Healthcare/Tuition show real cost
  but $0 from-portfolio with an "HSA paid $X"/"529 paid" tag when HSA/529 covered them (partial coverage
  shows the real split, e.g. HSA paid $33,206 / $13,566 to portfolio). from-portfolio column sums to the
  number that drives W/D.
- Cash-in subtotal: "− Cash In" with a blue sub-line listing nonzero sources (Income + Soc Sec + Inheritance).
- "= Withdrawn" (or "$0 net" + surplus→Brokerage note in surplus years where cash-in exceeds costs).
- "Came from" chips: Traditional / Roth / Brokerage (audElecTrad+forcedRmd / elecRoth / elecBrok).
- "Year reconciles": Starting + Contribs + Growth − W/D = Ending, real numbers, color-coded
  (contribs/growth teal, W/D magenta).

### Implementation (identical in mfj.html + single.html):
- **Data**: published reconCombStart/Cont/Grow, reconHsaDraw, reconSsPayout, reconInheritanceCashIn,
  reconIncome1099 to each row (× dispScale). But the panel actually builds from the in-scope LOCALS at
  render time (combStart, childGiftAmt, hsaDist, solvedResult.hcFromPortfolio, tuitionBurn, solvedTax,
  gross1099, currentSsPayout, inheritanceCashIn, portfolioWithdrawalActual, solvedResult.elecTrad/Roth/Brok,
  forcedRmd, spendableNetWorth) — the published fields are for tests/future use.
- **buildReconExpandRow(d)**: returns the hidden `<tr class="recon-exp" data-recon-for=YEAR>` HTML. Main row
  got `class="recon-row" data-recon-year=YEAR cursor-pointer`.
- **wireReconExpandRows()**: called right after ledgerTableBody.innerHTML=html. Sets
  window.__reconColspan = live #ledgerHeaderRow2 th count (DYNAMIC — toggle-safe, avoids the stale-colspan
  blank-table trap), and attaches one-at-a-time click handlers (ignores clicks on a/.info-tip-wrap children).
- **CSS**: recon-* classes, theme-aware (:root dark = luminous, [data-theme=light] = deeper), matching the
  mockup palette (adds teal #1da29b/#2dd4bf, cash blue #3b7bb0/#60a5fa, cost clay #d9825a/#fb923c,
  drain rose #be185d/#f472b6). Full-width straight rectangle (no rounded card).
- **Tests** (tier1): expand row exists per data row; colspan == live header col count (dynamic);
  sample row reconciles S+C+G−W=E. Verified both apps.
Baselines exact ($1,176,702 / $528,223), reconciles to the penny, no errors. Whole-row click, one open
at a time. NOTE: sandbox can't visually render the main app (Tailwind CDN blocked) but the expand panel's
DOM/math verify headless; user confirmed it renders correctly in-app.

## ═══ RECONCILIATION REDESIGN — PHASE 2 SHIPPED (both apps) ═══
The zone-band header redesign + column reorder is now LIVE in both mfj.html (index.html) and
single.html (p-zero-single.html). This completes the reconciliation redesign (Phase 1 = expand panel,
Phase 2 = zone bands/reorder). Baselines exact: MFJ $1,176,702, Single $528,223.

### Column reorder (both apps):
Combined-table columns physically reordered into zone order via index-map [0,1,2,3, 4,9,5,13, 6,8,10, 7,11,12, 14,15]
(0=Year). New order: Starting, Contribs, Growth | Planned Dist, Gifting, Healthcare, Taxes | Income, Soc Sec,
Inheritance | Roth Conv, Total Taxable, MAGI | Portfolio W/D | Ending. BOTH the header row-2 <th>s AND every
data-row <td> were reordered in lockstep (extracted by splitting on <td/<th boundaries — all 16 cells verified
balanced incl. the Inheritance IIFE and Total-Taxable sub-line cells — then re-emitted in new order). Header↔data
alignment verified by headless label=value pairing.

### Six zone bands (row 1, replaced the single "All Buckets Combined" banner):
zoneGrows (+ Grows Balance, teal --recon-adds) · zoneOutflows (Outflows ↑ W/D, clay --recon-cost) ·
zoneCashIn (Cash In ↓ W/D, blue --recon-cash) · zoneReference (Reference, #64748b slate) ·
zoneWithdrawal (Withdrawal, rose --recon-drain) · zoneEnding (Ending, #334155 mid-slate — NOT near-black,
that was black-on-black in dark theme). Band label text forced #ffffff !important (theme --text-primary was
overriding text-white → dark-on-dark on Reference/Ending). Old combinedGroupHeader id fully removed.

### ⚠️ CRITICAL — zone colspans are FLAG-BASED, not DOM-counted (learned the hard way):
The per-zone colspans are computed DIRECTLY from the authoritative flags giftingEnabled/inheritanceEnabled/
magiVisible — NOT by reading DOM visibility. DOM-reading caused a nasty header/data race (the MAGI/Inheritance
header th and data td toggle visibility at slightly different moments during the innerHTML rebuild, so counting
visible cols at colspan-time gave wrong numbers → bands desynced → CASH IN swallowed Roth Conv, REFERENCE
swallowed Portfolio W/D). Formula: zoneGrows=3, zoneOutflows=3+gifting, zoneCashIn=2+inheritance,
zoneReference=2+magiVisible, zoneWithdrawal=1, zoneEnding=1. MAGI now hides via a CONTAINER CLASS
(.magi-hidden .magi-col{display:none} toggled on the table) so header+data hide atomically — do NOT go back
to per-element inline display (it raced) or to DOM-counting (it raced). Verified: zone-sum == visible-cols
across all ACA/IRMAA/gifting/inheritance states, both apps.

### Surplus reconcile term (both apps):
In surplus years (cash-in > costs → W/D floors at $0, leftover banked to Brokerage), the expand panel's
"Year reconciles" line now shows an explicit "+ Surplus $X" term (blue, --recon-cash) so it's calculator-true:
Starting + Contribs + Growth − W/D + Surplus = Ending. No double-count: W/D and Surplus are the two sides of
one subtraction (only one is ever nonzero). Surplus amount = totalCash − totalFromP in buildReconExpandRow.
Kept the existing one-line surplus explanation above it.

### Subtle zone dividers:
1px low-opacity (rgba(148,163,184,0.18)) left border on the 5 zone-boundary columns only (Planned Dist,
Income, Roth Conv, Portfolio W/D, Ending) via a .zone-start class on both header th and data td. Not between
every column — just zone edges.

### Docs updated (both apps, sec-columns):
Column-definition table reordered into the 6 zones with colored zone subheadings; intro rewrote to name the
zones + ↑W/D/↓W/D logic; expand panel documented; reconcile formula fixed (added the previously-omitted
Contribs term AND the surplus term).

### Tests (test-suite.html, tier1):
Added Phase 2 guards (both apps pass): six zone bands present; zone colspans sum to visible columns in default
AND after ACA toggle; surplus year shows "+ Surplus" term and reconciles S+C+G−W+Su=E. Plus the existing
Phase 1 guards (expand row exists, colspan dynamic, reconciles).

### Gotchas confirmed this phase:
- Sandbox CANNOT fully render the app's Tailwind layout (CDN blocked) → pixel-alignment bugs may not show
  headless. Verify colspan/DOM math headless, but rely on USER screenshots for actual visual misalignment.
- User confirmed toggling Gifting/Inheritance works (no blank table) with the zone bands.
- EOL displays as "$1.18M" (abbreviated) — exact is $1,176,702; not a rounding bug, not engine drift.

---

## [DECISION LOG] Aug-2026 — The Single Catch-Up / Parity Session (redesign era ported MFJ → Single)

**Context.** MFJ (`index.html`) had received an entire redesign-era of work while Single (`p-zero-single.html`) sat at the redesign-tokens checkpoint. This session brought Single up to full feature parity with MFJ, then closed out with a parity audit, engine re-verification, help-doc updates (both apps), this CONTEXT update, and new UI-parity tests. Baselines held throughout: **MFJ $1,176,702 / Single $528,223** (today's $, all defaults). KPI tiles were re-checked for engine reconciliation after every ledger change.

**Method (the reliable pattern for this kind of port).** Block-port from MFJ → verify baseline + KPI reconciliation → checkpoint (ship) before the next risky step. Structures are near-identical across the two files (same anchors: `renderNetWorthChart`, `switchTab`, `buildReconExpandRow`, `kpiGrid`, `ledgerTableBody`, `sidebarPanel`, all modal handlers), so most subsystems port as whole blocks. Per-app differences that always need adapting: Single is Single/HoH (filing links to `index.html`, no Survivor section), Single's function indentation is often 12-space where MFJ is 14, and Single had a combined HSA/529 column that had to be split.

**What was ported to Single (all verified, baseline held):**
- **Chart polish** — Catmull-Rom `smoothLine`, per-bucket gradient fills, refined palette, taller SVG.
- **KPI heroes + status pill** — number-first 32px tiles; Secure/Shortfall pill in the 529 badge slot.
- **Dash/dollars hybrid** — `cf()` helper: flow cells render an em-dash when zero, balance cells keep `c()`. (Single-specific flow field `rebiToBrok`/`surplusCash` standardized.)
- **Executive Summary** — full workspace: `switchWorkspace`, `renderExecSummary`, es-hero + stat cards + advisor narrative + why-bullets + Upcoming Milestones. Default view = exec. Re-renders after each recalc.
- **Unified top nav** — brand + centered Exec/Details tabs + Analyze dropdown (Solve/MC/Compare) + utility icons (Import/Export, Reset, Theme, Help). `#analyzeMenu.hidden{display:none!important}` forced (Tailwind `.hidden` unreliable headless AND masks the inline-menu bug).
- **Input-panel collapsible reorg (7 groups)** + sidebar de-emphasis. Groups now MATCH MFJ logically: Household / Accounts & Contributions / Distribution & Tax Strategy / Income & Inflows (SS + Inheritance + Real Estate) / Care, Education & Gifting / **Estate & Legacy** (Single's name for MFJ's "Estate & Survivor" — no survivor) / Taxes & Global. Achieving this needed section **reordering** (surgical block-moves, NOT rebuild-from-scratch — see gotcha below).
- **ACA hide, panel defaults, expand-all/collapse-all.**
- **HSA/529 column split** — combined `grpHsa` (colspan 10) → `grpHsa` (HSA Detail, 5) + `grpF529` (529 Detail, 5); re-tagged 5 F529 headers + 5 F529 data cells; added `grpF529` to visibility + a "529" toggle.
- **Notables twin card** — replaced Single's `buildReconExpandRow` with MFJ's two-column version; added `notables:{…}` (8 fields: rothConv, inheritance, inheritanceTaxable, rebiSale, rmd, surplusBanked, ltc, tuitionShortfall) to the call; added recon-columns/tbl-notable CSS.
- **Column Details dropdown** — replaced Single's toggle-button row with MFJ's checkbox dropdown (`colDetailTrigger`/`colDetailMenu`/`toggleColDetailMenu`/`onColDetailToggle`), 7 groups.

**Ledger column fixes the user caught (my marker-diff missed them — see lesson):**
- **Roth Conv column** was missing from the Roth detail group. Added `rothConvAmt` header+cell between Growth and Dists; Roth zone colspan 5→6. Now matches MFJ.
- **Brokerage Inflows column** showed only `rebiToBrok` (RE proceeds subset). Changed to `surplusCash` (all external inflows) labeled "Inflows" — matches MFJ AND is the more-correct value (`rebiToBrok = min(surplusCash, rebiCashThisYear)`, so it understated brokerage inflow).

**Visibility-gating bugs (all the SAME bug class — a group not respecting its gate):**
- **grpCombined couldn't be hidden** (excluded from `applyColumnGroupVisibility`), so unchecking Household hid the headers but the rebuilt data cells stayed visible → header/cell desync. Fix: add `grpCombined` to the visibility loop.
- **Gifting showed when Household was off** — Single's `syncColumnGroups` gated Gifting/Inheritance on `giftingEnabled` alone, missing MFJ's `combinedOn && giftingEnabled`. Fixed.
- **Reference columns** — ported as a true dependent child of Household (MFJ's `applyReferenceVisibility`): `refOn = householdOn && checked`; uses a `.reference-hidden` class on the table + `ref-col` class on cells; **disables the Reference checkbox and greys its label when Household is off**; defaults OFF/unchecked (was wrongly defaulting visible).

**Control-styling parity (also user-caught):**
- **ACA/IRMAA** were plain checkboxes in Single vs sliders in MFJ → converted to the `.toggle-track` slider. (`acaPreserveSubsidy` + `stateExemptsSS` correctly STAY checkboxes — they're checkboxes in MFJ too; verified, not assumed.)
- **inheritance/education/gifting toggles** used hardcoded Tailwind tracks (`w-9 h-5`, green/amber) instead of `.toggle-track` → all 9 left-panel sliders now uniform size/color.
- **Filing + Dollars settings strip** — Single's filing toggle was pre-redesign inline markup; rebuilt to the `.settings-strip`/`.seg` structure, mirrored (Single active, Married links to index.html). **Dollars** toggle moved out of the Key Metrics bar into the settings strip (matching MFJ); `setDollarMode` rewired to toggle `.seg-btn.active`.
- **Key Metrics bar** was leaking onto the Exec Summary (sat OUTSIDE both view wrappers) → moved inside `planDetailsView` so it hides on the Exec tab, like MFJ.

**Intentionally NOT matched (correct divergences, do not "fix"):**
- Survivor scenario toggle + "Estate & Survivor" group → Single has "Estate & Legacy" (no survivor; single filer).
- Reference columns POSITION: Single keeps them before Ending; MFJ moved them after Ending. Functionally identical (same data, now same toggle/dependency). The physical reorder is the single highest-risk edit in the ledger (mid-table colspan/zone-band math) and was judged not worth the risk for a cosmetic position difference.

**⚠️ GOTCHA — do NOT rebuild the input panel from an enumerated section list.** First attempt at the group reorg rebuilt the sidebar from a hand-listed set of 14 sections; it silently **dropped the `RMD` sub-section (and hidden spouse-mirror blocks)**, which killed `triggerRecalculate` on missing `rmdAge`. Caught immediately by the baseline test, rolled back. The safe approach is **surgical block-moves** (extract one balanced `<div>` block, delete, re-insert at target; verify `<div>`==`</div>` count and baseline after each). There are interleaved non-obvious blocks (RMD, "Hidden spouse mirrors", a Survivor-Scenario *comment*) between the named sections.

**⚠️ GOTCHA — re-tagging mid-table columns corrupts easily.** The Reference re-tag (grpCombined → grpReference across zone band + 3 headers + 3 cells) failed twice via slice-reconstruction before succeeding with **targeted unique-string replacements** (each exact `<th…>`/`<td…>` string replaced once). Also note `visibleGroups = { grpCombined: true }` appears **twice** in Single (declaration + a reset inside resetToDefaults) — both need editing.

**LESSON (the user was right to push).** My automated feature-marker diff confirms a feature *exists* but does NOT catch (a) column-level fidelity (a missing column inside a present group), (b) control *styling* (checkbox vs slider, track size/color), (c) *placement/view-scoping* (which wrapper a block lives in / which tab it shows on), or (d) *visibility-gating* correctness. Every one of those classes had to be caught by the user. When "matching" an app, do the column-by-column / control-by-control / gate-by-gate sweep proactively — don't ship "~98%" off a marker diff.

**Docs / context / tests updated this session:**
- **Help (both apps):** added "1b. Interface: Views, Nav & Settings" (Executive Summary, workspace toggle, Analyze dropdown, settings strip, collapsible input groups) and "5c. Column Details Menu & Reference Columns" (the dropdown, Reference dependency, HSA/529 split, the two inflow columns, and the click-to-expand reconciliation panel + Notables). Per-app filing wording. TOC entries added. Verified rendering + baselines post-injection.
- **CONTEXT.md:** this entry + Section 8 header.
- **test-suite.html:** new UI-parity tier (see TESTING.md / suite).

**Final shipped md5s this session:** MFJ `index.html` = `e1265244…` (post-docs); Single `p-zero-single.html` = `3cf95e21…` (post-docs). Rollback backups staged in `/tmp/single.PRE-*.html` for each risky step.

---

## Timeline / gifting / Executive-Summary parity session — DONE (shipped, both apps)

The parity work continued past the interface-docs session into the Executive Summary and the visual chrome. Net result: **MFJ and Single are now at full parity across the Exec Summary, the Plan Timeline, gifting, and all header/panel chrome**, with the color layer reconciled to MFJ as source of truth.

**What was built (MFJ first, then transplanted into Single with engine differences respected):**
- **Multi-lane Plan Timeline** in the Executive Summary: a single proportional year-axis with a macro-milestone main line (Today, semi/full retirement, Medicare 65, SS claim, RMDs, and a "Plan Ends · $legacy" end-cap), plus — when dependents exist — one **education/gifting swimlane per child** (orange undergrad + purple grad duration bars anchored by labelled rings, a "Total Support" end-cap that breaks into Education/Gifts/Total on hover), colored cash-event dots (green inflows / red outflows), 5-year gridlines as a shared ruler, and zig-zag **compression breaks** over long quiet spans. Single shows **0 kid lanes by default** (children off); MFJ shows 2.
- **Gifting-recipient tagging** (`giftingRecipients` map): each gift row carries a recipient tag (Child 1…N / Donation / Other) that is **display-only** — it routes the gift's dot to a child lane vs the main line and rolls into that child's Total Support, but the engine never reads it (verified: retagging leaves EOL identical). Removing a child reverts their gifts to "Other" rather than deleting them.
- **8-card Executive Summary**: added Retirement Spending (+ withdrawal-rate sub-line), Lifetime Spending, and Effective Tax Rate to the existing five; replaced the flat bullet list with a **strong/watch callout pair**; embedded the Net-Worth chart in the Exec tab (cloned SVG with rewritten gradient IDs). Single's card *values* differ (smaller defaults) — structure identical.
- **Plan Details header block** ("Projection Analysis" + a populated context strip: Horizon / Peak / End / Legacy / Taxes / Brokerage), and **KPI cards hidden by default** on Plan Details (revealed only when a scenario is pinned for Compare).
- **Header chrome parity**: orange top-border signature (`#e49a62`), workspace-tab bottom-alignment + blue-underline styling, header height clamp (64px), and brand-block `min-width:333px` (the two together fix both the vertical *and* horizontal tab position).

**Color-variable reconciliation (MFJ = source of truth).** Root cause of a run of color/layout mismatches: Single's light-theme `--` variables had drifted. Aligned 10 of them to MFJ (`--accent`, `--accent-hover`, `--bg-base`, `--bg-panel`, `--border-color`, `--border-strong`, `--scrollbar-track`, `--text-muted`, `--text-primary`, `--text-secondary`), which fixed the tab-underline shade among others. Separately restored two missing *rules* (not variables): `aside.w-88 { background:#fff }` (left-panel white) and the `bg-slate-*` override inside the panel. **Lesson: when a color/layout differs between builds, check BOTH the variable values AND whether a CSS rule is simply absent from one build** — several of these were missing rules, not drifted variables.

**Single Help docs — reorganized to match MFJ AND validated against Single's engine.** Ported the MFJ reorg (new §1c Executive Summary with the full Plan Timeline writeup incl. child swimlanes documented fully despite being off by default; §1b shrunk to a pointer; §3 left-panel group map; §4 KPI dedup + hidden-by-default note; §15 gifting-recipient docs). Two-pass validation (docs→app, app→docs) caught **two real MFJ-leftover doc bugs in Single**: the children "Defaults" paragraph still described MFJ's two kids (2012/2015, grad×3) — rewritten to Single's actual "no children by default; added child defaults to 2018, grad off, grad×2 when on"; and the ACA worked-example table's `$100,000+` row showed `$18,000` net healthcare (MFJ leftover, also internally wrong) — fixed to `$20,000`. Confirmed correct without change: §3 balances/contributions, §12 std deduction ($16,100 Single / $24,150 HoH), §13 SS ("spousal/survivor not modeled in single-filer build"). **This is why Single docs can't be a blind copy — the engine differs, so every ported claim must be re-checked against Single's actual values.**

**Test suite — Tier 10 added (both builds).** New "Tier 10 — Recent Features" tier covering: Plan Timeline structure (nodes/gridlines/Plan-Ends), kid-lane behavior (MFJ ≥2 by default / Single 0), the 8 stat cards + spending/tax cards, callouts, chart-in-exec, KPI-hidden-default, the Plan Details header block + context strip, the **recon-header scoping regression guard** (row-expansion sub-table headers must not carry the colored zone-header background / white-on-light text — the bug was an over-broad `#planDetailsView thead tr:first-child` selector, fixed by scoping to `#ledgerHeaderRow1`), the **gift-routing display-only** invariant, and header chrome. Fixed two suite issues surfaced on first run: the pre-existing `tierUI` "renders milestones" check counted the retired `.es-mile` class (now counts `.es-timeline .tl-node`), and the Tier 10 gift test needed `giftingRecipients`/`childGiftingProfile` on `window` (added the exposure in both apps — inert, baselines held). TESTING.md updated with the Tier 10 section.

**Sandbox limitation (honest note).** The full iframe harness needs same-origin loading (serve over HTTP); this sandbox's headless browser can't reach localhost, and `file://` iframes are cross-origin-blocked, so the suite couldn't be run headless here. Tier 10 logic was validated by running its assertions directly against each app opened via `file://`. The suite runs green for the user via `python3 -m http.server` + `http://localhost:…/test-suite.html`. Pixel-level appearance still requires a real browser / user screenshot — DOM-measurable facts (geometry, computed styles, element counts) are reliable in-sandbox; final visual sign-off is the user's.

**Regression baselines held at every step:** MFJ `$1,176,702` / Single `$528,223` (today's $), 0 console errors.

**Final shipped md5s this session:** MFJ `index.html` = `e7c20ade…`; Single `p-zero-single.html` = `f3b09fa1…`; `test-suite.html` = `aabe69da…`; `TESTING.md` = `82a28f36…`. (Single went through several intermediate ships during the parity/doc work; these are the current heads.)
