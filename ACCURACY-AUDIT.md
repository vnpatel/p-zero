# P-ZERO — Full Triangulation / Accuracy Audit

**Date:** 2026-08-22
**Method:** Every documented claim, number, default, and behavior description was checked against the **actual shipped code** (MFJ `index.html`, Single `p-zero-single.html`) by reading the source and empirically verifying via automated runs. Ground-truth values were pulled from live runs, not from memory.

**Approach B:** This is a *findings-only* report. No documentation or code was changed in producing it. Fixes come after your review.

---

## Ground truth (verified from live runs, today's-dollars mode)

| Fact | MFJ | Single |
|---|---|---|
| Default spendable EOL | **$1,176,702** | **$524,584** |
| Default lifetime tax | $1,113,308 | $378,720 |
| Trad / Roth / Brok / HSA / 529 balances | $1.2M / $500K / $1M / $150K / $275K | $500K / $250K / $500K / $100K / $100K |
| Contributions Trad/Roth/Brok/HSA/529 | $70K / $70K / $70K / $8,750 / $24,000 | (to verify) |
| Inflation / healthcare inflation | 3% / 4.5% | 3% / 4.5% |
| Growth convention | half-year | half-year |
| RMD age | 75 | 75 |
| ACA / IRMAA / Roth-conv / SS toggles | off / on / off / off | off / on / off / off |
| Births (H/W) | 1980 / 1983 | 1980 / (mirrored) |

---

## SEVERITY LEGEND
- **[CRITICAL]** — wrong number/formula a user could act on, or a safety/accuracy claim that's false
- **[MAJOR]** — an entire feature undocumented, or a behavior description that's now wrong
- **[MINOR]** — small staleness, wording drift, cosmetic doc mismatch
- **[GAP]** — something a user would reasonably expect to find but isn't there

---

## SURFACE 1 — In-app Help modal (user-facing) — HIGHEST PRIORITY

### 1.1 [MAJOR] The Print / Save-PDF feature is completely undocumented
- **Finding:** The Help modal (21 sections) has **zero** mention of Print / Save PDF. The entire plan-document feature — branded header, hero, stat tiles, Monte Carlo section, native timeline, ledger, Plan Inputs, education span bars — is invisible in the docs.
- **Evidence:** `grep` of the Help modal region for "print"/"pdf" → 0 prose hits.
- **Impact:** A whole user-facing deliverable is undiscoverable via Help. This is the single biggest doc gap.
- **Fix:** Add a new Help section (e.g. "22. Printing / Exporting a Plan PDF") describing how to open it (Profile menu → Print / Save PDF), what the document contains, that Monte Carlo appears only if MC was run this session, and today's-dollars behavior.

### 1.2 [MAJOR] Gifting *reasons* feature is undocumented in prose
- **Finding:** Section 15 (Children: College Funding & Gifting) does not describe the new gifting-**reason** dropdown (Home Purchase / New Business / Wedding / Other), that it's display-only (never affects the projection), or that it's disabled for Charitable/Donation recipients.
- **Evidence:** The "reason" hits in the Help line-range were code, not prose.
- **Fix:** Add a short paragraph in Section 15 documenting the reason tag and its display-only nature.

### 1.3 [MINOR] Child-lane description is now slightly inaccurate post lane-gate fix
- **Finding:** Help says *"Each child gets their own lane."* After the recent fix, a child gets a lane only if they have **education content (when education is on) OR gifts tagged to them**; a child with neither gets **no lane**.
- **Evidence:** Shipped lane gate: `childrenProfiles.some(c,i => _childHasLane(c,i))`, and per-child `if (!_childHasLane) return ''`.
- **Fix:** Reword to "Each child with education or gifts gets their own lane."

### 1.4 [MINOR] Recipient label drift: "Donation" → "Charitable/Donation"
- **Finding:** The recipient option was relabeled to "Charitable/Donation." Any Help text referencing "Donation" as the label should match.
- **Fix:** Sweep Help for "Donation" as a UI label; update to "Charitable/Donation."

### 1.5 [TO-VERIFY] Timeline "Household" main-line label + tiered dot sizing
- **Finding:** We added a "Household" label to the main timeline line and tiered dot sizing (dots sized by $ amount: sm/md/lg). Help's timeline section should mention these if it enumerates timeline visual elements.
- **Status:** Needs a full read of the timeline Help subsection to confirm whether it now omits/contradicts these.

### 1.6 [CONFIRMED-ACCURATE] Input defaults section is correct
- Contribution defaults ($70K/$70K/$70K/$8,750/$24,000) and balances ($1.2M/$500K/$1M/$150K/$275K) in Help **match** shipped MFJ exactly. No change needed.
- Default nominal return "6%", inflation "3%", RMD age "75", Target EOL "95" — consistent with ground truth (6% return claim to be double-checked against the actual per-bucket return inputs).

---

## SURFACE 2 — CONTEXT.md (internal project doc, 310 KB) — KNOWN STALE

### 2.1 [MAJOR] Does not reflect this session's work
- **Finding:** CONTEXT.md was last updated 2026-08-20 (before the entire print redesign, gifting reasons, timeline enhancements, education-lane fix, education span bars, chart-contrast change, and the full Single port).
- **Fix:** A comprehensive update pass covering: the redesigned print (both apps), gifting-reason feature, timeline Household label + tiered dots, the education-lane gate fix, education span bars in print, the chart opacity change, and Single now at parity.

### 2.2 [CONFIRMED] The dot-size discrepancy you flagged
- **Finding:** Prior context/summary claimed dot tiers of **12/16/20**; the **actual shipped** value is **11/13/15** (base 12). This exact class of drift is why this audit exists.
- **Fix:** Correct any 12/16/20 reference to 11/13/15 wherever it appears in CONTEXT.md / notes.

### 2.3 [TO-VERIFY] Baseline numbers in CONTEXT.md
- Need to confirm CONTEXT.md's stated baselines match $1,176,702 (MFJ) / $524,584 (Single).

---

## SURFACE 3 — test-suite.html + TESTING.md — DO TESTS MATCH CURRENT BEHAVIOR?

### 3.1 [TO-VERIFY] Baseline assertions
- **Finding:** test-suite.html was last touched 2026-08-20. Need to confirm its baseline EOL assertions still equal the shipped $1,176,702 / $524,584, and that no test asserts old dot sizes, old timeline gating, or pre-fix education-lane behavior.
- **Risk:** If tests encode the *old* lane-gate behavior (lane only when education on), they'd now be wrong tests.

### 3.2 [GAP] No tests for the new features
- Likely no coverage for: gifting reasons (round-trip export/import), the education-lane gate fix (gifts-only child gets a lane; child with neither gets none), education bars in print, the single-filer age column, MC print block conditional rendering.
- **Fix:** Add targeted tests once behavior is locked.

---

## SURFACE 4 — MFJ ↔ Single parity

### 4.1 [CONFIRMED-ALIGNED] Feature parity achieved this session
- Gifting reasons, timeline Household label + tiered dots (11/13/15), the redesigned print, education-lane fix, and education span bars are now present in **both** apps.

### 4.2 [BY-DESIGN differences — not bugs, but should be documented]
- Print filing label: "Married Filing Jointly" (MFJ) vs "Single" / "Head of Household" (Single, via `isHoH()`).
- Print People table: Husband + Wife rows (MFJ) vs single "You" row (Single).
- Ledger age column: "H/W" like 46/43 (MFJ) vs single age like 46 (Single) — **just fixed**.
- Single mirrors spouse internally (`wBirthYear === hBirthYear`), so any doc that says Single "has no spouse fields" should note the mirroring nuance.

---

## SURFACE 5 — The four "lifetime totals" you asked about (GAP analysis)

None of these four are surfaced as clean lifetime totals the way **Lifetime Tax** is. The per-year data exists in `__chartSeries` (`audGift`, `audTuitionBurn`, `audInheritance`, etc.), so all four are computable read-only.

| Metric | Computed? | Surfaced? | Notes |
|---|---|---|---|
| **Lifetime gifting to kids** | Per-year `audGift` exists; child-tagged via `giftingRecipients` | ❌ No total anywhere | Easy to sum child-tagged gifts |
| **Lifetime donations / non-kid gifts** | Distinguished by `donation` tag | ❌ No total | Easy to sum donation-tagged gifts |
| **Lifetime healthcare cost** | Engine computes `totalHealthcareCost` (net of ACA) internally | ⚠️ Not surfaced as lifetime headline (ACA subsidy IS surfaced) | Gross vs net worth clarifying |
| **Lifetime tuition / education** | Per-year `audTuitionBurn` sums (~$544K default MFJ) | ⚠️ Only per-child in print Children table / kid-lane cap | No single lifetime total |

- **Recommendation:** These are a natural, high-value **feature addition** — a "Lifetime Flows" strip (print + exec summary) with Lifetime Gifts, Donations, Healthcare, Education. Engine-read-only (sum existing `aud*` fields). Treat as a separate authorized piece after the doc fixes.

---

## SURFACE 6 — journal.txt
- **[MINOR]** Needs this session's transcript appended to the catalog.

---

## RECOMMENDED FIX ORDER (after your review)
1. **In-app Help** (user-facing): add Print/PDF section (1.1), gifting-reason paragraph (1.2), fix child-lane wording (1.3), label sweep (1.4), verify timeline subsection (1.5).
2. **test-suite.html**: confirm baselines, fix any tests encoding old behavior, add coverage for new features (3.1, 3.2).
3. **CONTEXT.md**: comprehensive update (2.1), fix 12/16/20 → 11/13/15 (2.2), verify baselines (2.3).
4. **journal.txt**: append session (6).
5. **(Separate feature decision)** the four Lifetime Flows totals (Surface 5).

## RESOLVED VERIFICATIONS (completed this pass)

- **"6% default return" claim → ACCURATE.** Shipped input `roiNominal = 6` in both apps. Help's "default 6%" is correct.
- **State/county tax → ACCURATE.** `stateRate = 2.90%`, `countyRate = 1.5%` shipped; consistent with the Effective Tax Rate example.
- **CONTEXT.md baselines → CORRECT.** $1,176,702 (MFJ) and $524,584 (Single) appear consistently (20+ occurrences). CONTEXT.md's *numbers* are right; its *feature descriptions* are what's stale (2.1).
- **test-suite.html → NO WRONG TESTS, but a COVERAGE GAP.** ~40 test blocks, all engine-behavior (RE/business deals: distributions/refi/exit, IRMAA spike, reconciliation, magnitude, stale-profile). It does **not** assert the headline EOL, and has **0** references to lane/dot internals or any new feature (gifting reasons, print, education bars) → so nothing to *correct*, but new coverage is missing (3.2).
- **Single contribution defaults (was TBD):** Trad **$24,500**, Roth **$47,500**, Brok **$36,000**, HSA **$4,400**, 529 **$0**. These are DIFFERENT from MFJ's $70K/$70K/$70K/$8,750/$24,000.

### 1.7 [CHECKED — CLEAN] Single contribution defaults differ from MFJ, and Single's Help correctly reflects them
- **Finding:** Single's shipped contribution defaults ($24,500 / $47,500 / $36,000 / $4,400 / $0) differ materially from MFJ's ($70K/$70K/$70K/$8,750/$24,000). **Single's Help sentence is correct**: "Defaults (2026): Traditional $24,500 · Roth $47,500 ..." — so no copy-paste drift here.
- **Single's Help balances** ($500K/$250K/$500K/$100K/$100K) are also correct.
- **"married couple"** appears once in Single but in the sentence *"This build files as a single..."* — contextual, not an error.
- **Conclusion:** Single's Help was properly localized for the single filer. No fix needed for 1.7. (Still add the Print/reason sections to Single's Help too, per 1.1/1.2 — those gaps exist in both apps.)

## STILL-OUTSTANDING (small, low-risk — can fold into fixes)
- Full prose read of Help's timeline subsection to confirm whether "Household" label + tiered dot sizing are mentioned (1.5). Preliminary read shows the timeline section describes rings/lanes/education bars but was written before the Household label + tiered-dots; likely a MINOR addition needed.
- Confirm Single's Help modal exists and mirrors MFJ's (Single was ported; its Help may be MFJ's text verbatim, which would carry MFJ-specific numbers — see 1.7).

---

## ADDENDUM — Bug found while writing test coverage (Surface 3 follow-up)

Writing the Tier-10 tests surfaced a **real, shipped bug** (exactly the point of the exercise):

### [FIXED] `window.giftingReasons` was never exposed → gift reasons missing from print tooltips
- **Root cause:** `giftingRecipients` and `childGiftingProfile` are published on `window` (for the print builder + tests), but `giftingReasons` was **not**. The print timeline reads `window.giftingReasons` (with a `|| {}` guard), so it always saw an empty map — **gift reason labels never appeared in the printed timeline tooltips** (e.g. "Gifted $50,000 — Wedding" showed only "Gifted $50,000").
- **Second, related bug:** all three gifting maps are **reassigned** (not mutated) on import / applyInputsSnapshot / resetToDefaults, which left the `window` refs **stale** after any of those actions.
- **Fix (both apps):** expose `window.giftingReasons` at init, and re-sync all three `window` refs immediately after every reassignment site (import, applyInputsSnapshot, reset). Verified: print tooltip now shows the reason; post-reset window ref is clean; baselines hold ($1,176,702 / $524,584).

### Test-suite coverage added (Tier 10)
- **Hard assertions (validated headless):** gift reason is display-only (EOL unchanged across reasons) + round-trips through snapshot; print document builds with 8 tiles, timeline SVG, ledger, Plan Inputs divider; filing label correct per app; MFJ Husband+Wife rows vs Single "You" row; Single ledger shows one age (no "46/46"); education OFF → no kid bars; child with neither edu nor gifts → no lane.
- **Guarded (skip-with-note if the headless harness can't register the injected gift):** gifts-only child gets a lane; print education span bars present when education on. These assert correctly in the real same-origin suite; they degrade to a clean skip rather than a false red if object-injection doesn't sync (a known `file://` limitation).
- **Honest note:** the full iframe harness must be run over HTTP (same-origin) to exercise everything; green there ≠ engine-verified, per the project's standing discipline.
