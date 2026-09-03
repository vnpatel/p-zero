#!/usr/bin/env python3
"""
qa_independent_model.py  —  INDEPENDENT VALIDATION ORACLE for the P-ZERO retirement simulator
================================================================================================

PURPOSE
-------
This is a from-scratch, engine-blind reimplementation of the retirement projection. It computes
what each QA scenario's outputs (EOL net worth, lifetime tax, legacy) SHOULD be, using ONLY:
  (a) the scenario's raw inputs,
  (b) authoritative 2026 IRS/CMS constants (see AUTHORITATIVE CONSTANTS below, each sourced), and
  (c) the engine's documented modeling assumptions (each identified, judged professionally sound,
      and re-implemented here independently).

It is the "third witness" in a THREE-WAY check:
    A = frozen benchmark (QA-SCENARIOS.md)
    B = engine output    (run the app — see QA-RUNBOOK.md)
    C = this model's output
Validation passes only when  A == B == C  (to within floating-point rounding, ~$50 on ~$15M).

WHY THIS FILE EXISTS
--------------------
Reproducing the engine to the dollar required capturing ~15 non-obvious assumptions (RMD
reinvestment, state-SS exemption, Roth-conversion growth timing, healthcare-inflation taper, ...).
Without this file, a future reviewer would have to rediscover them all and would likely stop at
"a few % off, close enough" — which is exactly the circular trap this QA system exists to prevent.
Every assumption below was verified to the dollar against the engine on 2026-08-29.

*** ANTI-CIRCULARITY RULE ***
The benchmark numbers in QA-SCENARIOS.md are FROZEN. If this model or the engine disagrees with a
benchmark, that is a FINDING to investigate — NOT a number to overwrite. Do not "fix" a mismatch by
editing the benchmark. Investigate whether the engine changed, an assumption changed, or a constant
went stale. Only update a benchmark when the underlying scenario definition is deliberately changed.

--------------------------------------------------------------------------------------------------
AUTHORITATIVE 2026 CONSTANTS  (external truth — verify annually against the cited sources)
--------------------------------------------------------------------------------------------------
  MFJ standard deduction .......... 32,200   (IRS Rev. Proc. 2025-32)
  MFJ ordinary brackets ........... 10% to 24,800 | 12% to 100,800 | 22% to 211,400 |
                                     24% to 403,550 | 32% to 512,450 | 35% to 768,700 | 37% above
  MFJ LTCG brackets ............... 0% to 98,900 | 15% to 613,700 | 20% above
  RMD Uniform Lifetime divisors ... age 75 = 24.6, 76 = 23.7, ... (IRS Pub 590-B / Treas. Reg.
                                     1.401(a)(9)-9) — full table below
  RMD start age ................... 75 (SECURE 2.0, for anyone born 1960 or later)
  IRMAA MFJ tiers (per-person, base, inflation-indexed) ...
                                     >218k=1,148 | >274k=2,885 | >342k=4,620 | >410k=6,355 | >750k=6,936
                                     (CMS 2026; 2-year MAGI lookback)
NOTE: NIIT (3.8%) and AMT are NOT modeled — the engine discloses this; immaterial at low MAGI,
      understates tax only in high-MAGI years (e.g. S7's large-conversion years, MAGI > 250k).

--------------------------------------------------------------------------------------------------
ENGINE MODELING ASSUMPTIONS re-implemented here (all verified to the dollar; each judged defensible)
--------------------------------------------------------------------------------------------------
 1. Inflation-indexed brackets + standard deduction (avoids bracket creep). [correct]
 2. First-year contributions prorated by remaining months of the calendar year (currentMonth). [ok]
 3. Contributions inflate 3%/yr.
 4. Growth convention 'halfyear': growth = (start + contrib*0.5 - withdrawals*0.5) * roi. [ok]
 5. Brokerage: 2% dividend yield, 85% qualified (taxed at LTCG), 15% nonqualified (ordinary);
    dividends taxed every year; reinvested dividends add to basis. Basis ratio snapshotted BEFORE
    withdrawals on (brokStart + brokContribution).
 6. Drawdown order: Brokerage -> Traditional -> Roth; HSA reserved for healthcare.
 7. RMD = prior-year-Dec-31 Traditional / IRS divisor, from age 75; included in Traditional growth
    withdrawal base at half-year.
 8. RMD REINVESTMENT: spending is funded from the drawdown order; the full RMD is forced out as
    ordinary income and its surplus cash is banked to Brokerage as after-tax basis. [internally
    consistent; NOTE: realizes brokerage gains that a tax-optimizing person might avoid — a
    professional observation, not an arithmetic error.]
 9. State + county tax (default 2.90% + 1.5% = 4.4%) on ordinary income with NO standard deduction
    against the state base, and on LTCG. Taxable Social Security is EXEMPT from the state base
    (stateExemptsSS default ON — matches many states incl. Colorado).
10. Roth conversion timing: leaves Traditional BEFORE growth (in the withdrawal base, half-year),
    enters Roth AFTER growth (earns nothing the conversion year). Fully taxable ordinary income.
11. Healthcare inflation TAPER: Medicare cost inflates at 4.5% (hotter than 3% CPI); the 1.5%
    excess over CPI tapers linearly to zero over 25 years. NOT a flat rate.
12. Cash sources (SS, RE/BI distributions, inheritance) fund spending first (reduce the portfolio
    draw); surplus banked to Brokerage.
13. Social Security taxation: FLAT 85% of the benefit (engine's DISCLOSED simplification — NOT the
    statutory IRC 86 provisional-income phase-in). Accurate when provisional income is high
    (> ~108k); OVERSTATES taxable SS for lower-income retirees. Flagged as a professional finding.
14. RE/BI: distributions (taxable per distTaxablePct) bank to Brokerage -> affect EOL; the illiquid
    appreciating value affects LEGACY only (not liquid EOL net worth).
15. Legacy = Roth + Brokerage + HSA*(1-heirTax) + Traditional*(1-heirTax) + illiquid RE/BI value.

RUN:  python3 qa_independent_model.py            # runs all scenarios, prints A/C comparison
      python3 qa_independent_model.py s3          # run one scenario
"""

import sys

# ==================================================================================================
# AUTHORITATIVE CONSTANTS  (MFJ)  — see sources in the header
# ==================================================================================================
MFJ = {
    "std_ded": 32_200,
    "ordinary": [(0, .10), (24_800, .12), (100_800, .22), (211_400, .24),
                 (403_550, .32), (512_450, .35), (768_700, .37)],
    "ltcg": [(0, 0.0), (98_900, .15), (613_700, .20)],
    "irmaa_tiers": [(218_000, 1_148), (274_000, 2_885), (342_000, 4_620),
                    (410_000, 6_355), (750_000, 6_936)],
}
RMD_DIVISOR = {75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5,
               83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2,
               91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9}

# ---- Single-app constants (p-zero-single.html) — verified vs IRS Rev. Proc. 2025-32 / CMS ----
# The Single app files as SINGLE when there are no dependents, and HEAD-OF-HOUSEHOLD when
# childrenProfiles.length > 0. IRMAA tiers are the single-filer thresholds, counted for ONE person.
SINGLE = {
    "std_ded": 16_100,
    "ordinary": [(0, .10), (12_400, .12), (50_400, .22), (105_700, .24),
                 (201_775, .32), (256_225, .35), (640_600, .37)],
    "ltcg": [(0, 0.0), (49_450, .15), (545_500, .20)],
    "irmaa_tiers": [(109_000, 1_148), (137_000, 2_885), (171_000, 4_620),
                    (205_000, 6_355), (500_000, 6_936)],
    "irmaa_persons": 1,
}
HOH = {
    "std_ded": 24_150,
    "ordinary": [(0, .10), (17_700, .12), (67_450, .22), (105_700, .24),
                 (201_775, .32), (256_225, .35), (640_600, .37)],
    "ltcg": [(0, 0.0), (66_200, .15), (579_600, .20)],
    "irmaa_tiers": [(109_000, 1_148), (137_000, 2_885), (171_000, 4_620),
                    (205_000, 6_355), (500_000, 6_936)],
    "irmaa_persons": 1,
}
# MFJ counts IRMAA for two people; give it the key too so project() is filing-status agnostic.
MFJ["irmaa_persons"] = 2

# Engine default modeling parameters (from the app's input panel defaults)
DEFAULTS = {
    "roi": 0.06, "infl": 0.03,
    "state": 0.029, "county": 0.015,          # state + county tax
    "brok_basis_pct": 0.60, "div_yield": 0.02, "div_qualified": 0.85,
    "heir_tax": 0.28,
    "current_month": 8,                        # first-year contribution proration (12-month)/12
    "hc_inflation": 0.045, "hc_converge_years": 25,   # healthcare taper
}

# ==================================================================================================
# SHARED PROJECTION ENGINE (engine-blind reimplementation)
# ==================================================================================================
def _tax_brackets(x, brackets, sc):
    if x <= 0:
        return 0.0
    t = 0.0
    for k in range(len(brackets)):
        lo = brackets[k][0] * sc
        hi = brackets[k + 1][0] * sc if k + 1 < len(brackets) else float("inf")
        r = brackets[k][1]
        if x > lo:
            t += (min(x, hi) - lo) * r
    return t

def _ltcg_tax(ordinary_taxable, gains, brackets, sc):
    if gains <= 0:
        return 0.0
    pos = max(0, ordinary_taxable)
    rem = gains
    t = 0.0
    for k in range(len(brackets)):
        lo = brackets[k][0] * sc
        hi = brackets[k + 1][0] * sc if k + 1 < len(brackets) else float("inf")
        r = brackets[k][1]
        if pos >= hi:
            continue
        take = min(rem, hi - pos)
        if take > 0:
            t += take * r
            rem -= take
            pos += take
        if rem <= 0:
            break
    return t

def _hc_inf_scale(i, cfg):
    """Healthcare inflation taper: excess over CPI tapers linearly to zero over converge_years."""
    excess = cfg["hc_inflation"] - cfg["infl"]
    window = cfg["hc_converge_years"]
    factor = 1.0
    for y in range(1, i + 1):
        frac = max(0, 1 - (y - 1) / window)
        rate = cfg["infl"] + excess * frac
        factor *= (1 + rate)
    return factor


def project(scn, C=MFJ, cfg=DEFAULTS):
    """
    Run the full projection for a scenario dict `scn`. Returns dict with eol, tax, legacy, and the
    per-year series. `scn` provides raw inputs and OPTIONAL levers (see scenario builders below).
    """
    SY = scn["start_year"]; AGE0 = scn["age0"]; END_AGE = scn["end_age"]
    roi = cfg["roi"]; infl = cfg["infl"]
    STL = cfg["state"] + cfg["county"]
    heir = cfg["heir_tax"]
    y0frac = (12 - cfg["current_month"]) / 12

    trad = scn["trad0"]; roth = scn["roth0"]; brok = scn["brok0"]; hsa = scn["hsa0"]
    basis = brok * cfg["brok_basis_pct"]
    prev_trad = trad
    lifetax = 0.0
    magi_hist = {}
    series = {}

    for i in range(END_AGE - AGE0 + 1):
        year = SY + i; age = AGE0 + i; sc = (1 + infl) ** i
        retired = age >= scn["retire_age"]
        yf = y0frac if i == 0 else 1.0

        # ----- contributions (full during saving phase) -----
        tc = (scn["cont_trad"] * sc) * yf if not retired else 0.0
        bc = (scn["cont_brok"] * sc) * yf if not retired else 0.0

        trad_start, roth_start, brok_start, hsa_start = trad, roth, brok, hsa
        basis += bc

        # ----- brokerage dividends (taxed yearly); basis-add deferred to after draws -----
        div = max(0, brok) * cfg["div_yield"]
        qd = div * cfg["div_qualified"]; nqd = div * (1 - cfg["div_qualified"])
        pre_withdraw_brok = max(1, brok_start + bc)
        basis_ratio = min(1.0, basis / pre_withdraw_brok)

        # ----- RMD (forced ordinary income; prior-year balance / divisor) -----
        rmd = 0.0
        if age >= 75:
            rmd = min(prev_trad / RMD_DIVISOR[age], trad)
        trad -= rmd

        # ----- Roth conversion lever -----
        roth_conv = 0.0
        cv = scn.get("roth_conv")
        if cv and age >= cv["start_age"]:
            roth_conv = min(cv["amount"] * sc, trad)
            trad -= roth_conv                     # leaves Traditional (before growth)

        # ----- spending need -----
        need = scn["net_dist"] * sc if retired else 0.0

        # education lever (tuition as extra after-tax need)
        tuition = 0.0
        for child in scn.get("children", []):
            ug_start = child["birth_year"] + 18
            if ug_start <= year < ug_start + child["ug_years"]:
                tuition += child["ug_cost"] * sc
        need += tuition

        # cash-source levers (fund spending first): SS, RE/BI distribution, inheritance
        ss = 0.0; ss_taxable = 0.0
        s = scn.get("ss")
        if s and age >= s["claim_age"]:
            ss = s["annual_combined"] * (1 + s["cola"]) ** i
            ss_taxable = s["taxable_pct"] * ss

        rebi_dist = 0.0; rebi_dist_taxable = 0.0
        rb = scn.get("rebi")
        if rb:
            # dist_cola is a boolean flag; when True the distribution inflates at CPI (3%)
            cola_rate = infl if rb.get("dist_cola") else 0.0
            rebi_dist = rb["annual_dist"] * (1 + cola_rate) ** i
            rebi_dist_taxable = rb["dist_taxable_pct"] * rebi_dist

        inheritance = 0.0
        inh = scn.get("inheritance")
        if inh and year == inh["arrival_year"]:
            inheritance = inh["amount"] * (sc if not inh.get("is_nominal") else 1.0)
            # (type 'taxfree' -> not taxable; only taxfree is modeled in these scenarios)

        # ----- healthcare (Medicare base + IRMAA), post-65; HSA-first funding -----
        gross_hc = 0.0; irmaa = 0.0
        hc = scn.get("healthcare")
        if hc and age >= 65:
            hc_scale = _hc_inf_scale(i, cfg)
            medicare = hc["medicare"] * hc_scale
            # IRMAA: 2-year MAGI lookback, per-person, inflation-indexed
            if scn.get("irmaa") and (year - 2) in magi_hist:
                persons65 = C.get("irmaa_persons", 2) if age >= 65 else 0
                look = magi_hist[year - 2]
                per = 0.0
                for frm, ann in reversed(C["irmaa_tiers"]):
                    if look > frm * sc:
                        per = ann * sc
                        break
                irmaa = per * persons65
            gross_hc = medicare + irmaa
        hsa_cover = min(hsa, gross_hc)
        hsa -= hsa_cover
        need += gross_hc - hsa_cover

        # ----- solve elective withdrawal to cover need + tax, net of cash sources -----
        std = C["std_ded"] * sc

        def compute(elec):
            rem = elec
            eb = min(brok, rem); rem -= eb
            et = min(max(0, trad), rem); rem -= et
            er = min(roth, rem); rem -= er
            bg = eb * (1 - basis_ratio)
            ordinary = rmd + nqd + et + roth_conv + ss_taxable + rebi_dist_taxable
            gains = bg + qd
            ord_base = max(0, ordinary - std)
            fed = _tax_brackets(ord_base, C["ordinary"], sc)
            lt = _ltcg_tax(ord_base, gains, C["ltcg"], sc)
            # state: full ordinary (no std ded), SS-exempt; plus gains
            st = max(0, ordinary - ss_taxable) * STL
            st_g = gains * STL
            return fed + lt + st + st_g, eb, et, er, bg

        # In RMD years the RMD cash funds spending FIRST (before selling brokerage), reducing
        # realized capital gains. This is the engine's behavior as of 2026-08-30 (the "spend RMD
        # first" change). A scenario may set rmd_spend_first=False to model the older behavior
        # (RMD banked to brokerage as surplus while spending is funded from the drawdown order).
        spend_cash = ss + rebi_dist + inheritance
        if scn.get("rmd_spend_first", True):
            spend_cash += rmd
        elec = max(0, need)
        for _ in range(30):
            tax, eb, et, er, bg = compute(elec)
            new_elec = max(0, need + tax - spend_cash)
            if abs(new_elec - elec) < 0.5:
                elec = new_elec
                break
            elec = new_elec
        tax, eb, et, er, bg = compute(elec)
        lifetax += tax
        magi_hist[year] = (rmd + nqd + et + roth_conv + ss_taxable + rebi_dist_taxable) + (bg + qd)

        # ----- apply withdrawals -----
        trad_drawn = et; roth_drawn = er; brok_drawn = eb
        basis = max(0, basis - brok_drawn * basis_ratio)   # basis reduced by drawn * snapshot
        trad -= trad_drawn; roth -= roth_drawn; brok -= brok_drawn
        basis = min(max(1, brok), basis + div)             # dividends to basis AFTER draws

        # ----- surplus (incl forced RMD + cash sources) banked to Brokerage -----
        cash_in = rmd + trad_drawn + roth_drawn + brok_drawn + ss + rebi_dist + inheritance
        cash_out = need + tax
        surplus = max(0, cash_in - cash_out)
        if surplus > 0:
            brok += surplus; basis += surplus

        # ----- growth (halfyear convention) -----
        def grow(start, cont, wd):
            return max(0, start + cont * 0.5 - wd * 0.5) * roi
        tg = grow(trad_start, tc, trad_drawn + rmd + roth_conv)
        rg = grow(roth_start, 0, roth_drawn)
        bg2 = grow(brok_start, bc, brok_drawn)
        hg = grow(hsa_start, 0, hsa_cover)
        trad += tc + tg
        roth += rg + roth_conv                              # conversion added AFTER growth
        brok += bc + bg2
        hsa += hg

        prev_trad = trad
        series[year] = {"age": age, "trad": trad, "roth": roth, "brok": max(0, brok),
                        "hsa": hsa, "rmd": rmd, "tax": tax}

    last = series[SY + (END_AGE - AGE0)]
    eol = last["trad"] + last["roth"] + last["brok"] + last["hsa"]

    # illiquid RE/BI value -> legacy only
    rebi_end = 0.0
    if scn.get("rebi"):
        rb = scn["rebi"]
        rebi_end = rb["value"] * (1 + rb["appr_pct"]) ** (END_AGE - AGE0) * (1 + rb["appr_pct"])
    legacy = (last["roth"] + last["brok"] + last["hsa"] * (1 - heir)
              + last["trad"] * (1 - heir) + rebi_end)

    return {"eol": eol, "tax": lifetax, "legacy": legacy, "rebi_end": rebi_end,
            "rmd75": series.get(SY + (75 - AGE0), {}).get("rmd", 0), "series": series}


# ==================================================================================================
# SCENARIO DEFINITIONS (MFJ)  — raw inputs + one lever each vs the S1 anchor
# ==================================================================================================
def _base():
    return {"start_year": 2026, "age0": 55, "end_age": 95,
            "trad0": 1_000_000, "roth0": 500_000, "brok0": 1_000_000, "hsa0": 50_000,
            "cont_trad": 24_500, "cont_brok": 50_000,
            "retire_age": 60, "net_dist": 70_000}

def s1():
    return _base()

def s2():
    s = _base()
    s["children"] = [{"birth_year": 2018, "ug_cost": 30_500, "ug_years": 4}]
    return s

def s3():
    s = _base()
    s["ss"] = {"claim_age": 67, "annual_combined": 50_000, "cola": 0.03, "taxable_pct": 0.85}
    return s

def s4():
    s = _base()
    s["rebi"] = {"value": 100_000, "appr_pct": 0.04, "annual_dist": 4_000,
                 "dist_taxable_pct": 0.25, "dist_cola": True}
    return s

def s5():
    s = _base()
    s["inheritance"] = {"amount": 500_000, "is_nominal": False, "arrival_year": 2040, "type": "taxfree"}
    return s

def s6():
    s = _base()
    s["roth_conv"] = {"start_age": 60, "amount": 50_000}
    return s

def s7():
    s = _base()
    s["roth_conv"] = {"start_age": 65, "amount": 200_000}
    s["healthcare"] = {"medicare": 5_000}
    s["irmaa"] = True
    return s

# Frozen benchmarks (A) — MFJ. MUST match QA-SCENARIOS.md. Do NOT edit to silence a mismatch.
BENCHMARKS = {
    # --- Scenario 0 ("Customer Zero"): the app's SHIPPED DEFAULT state (2 kids b.2012/2015 w/ grad,
    #     gifting 2038-2043, education ON, IRMAA ON, Trad 1.2M/Roth 500k/Brok 1M/HSA 150k/529 275k,
    #     contribs 70k/70k/70k/8,750/24k, dist 150k, hc 40k, medi 18k, semi-inc 25k/100k).
    #     This is the baseline every user sees on load. Frozen from the engine (B leg).
    #     NOTE: benchmark EOL is NOMINAL (parity with s1-s7). Today's-$ EOL (the "memorized
    #     baseline") = 1,215,092 / tax 1,110,383 / legacy 1,215,092.
    "s0": {"eol": 5_651_255, "tax": 2_185_631, "legacy": 5_651_255,
           "eol_today": 1_215_092, "tax_today": 1_110_383, "legacy_today": 1_215_092},
    "s1": {"eol": 14_782_906, "tax": 763_541, "legacy": 13_828_491},
    "s2": {"eol": 13_876_900, "tax": 739_530, "legacy": 12_922_485},
    "s3": {"eol": 20_951_035, "tax": 1_473_810, "legacy": 19_996_620},
    "s4": {"eol": 15_741_870, "tax": 805_009, "legacy": 15_286_761},
    "s5": {"eol": 18_072_034, "tax": 882_995, "legacy": 17_117_619},
    "s6": {"eol": 14_429_627, "tax": 533_604, "legacy": 14_276_987},
    "s7": {"eol": 11_729_122, "tax": 660_839, "legacy": 11_729_122},
}
SCENARIOS = {"s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5, "s6": s6, "s7": s7}


# ==================================================================================================
# SCENARIO DEFINITIONS (SINGLE app, p-zero-single.html)
# ==================================================================================================
# Single person, age 55, retire 60. Balances/contributions are the Single app's scale (~half MFJ).
# Filing status: SINGLE when childless; HEAD-OF-HOUSEHOLD when a dependent is present (s2_single).
# All benchmarks captured in NOMINAL dollar mode against the corrected engine (post constants fix).
def _base_single():
    return {"start_year": 2026, "age0": 55, "end_age": 95,
            "trad0": 500_000, "roth0": 250_000, "brok0": 500_000, "hsa0": 50_000,
            "cont_trad": 24_500, "cont_brok": 36_000,
            "retire_age": 60, "net_dist": 50_000}

def s1_single():   # anchor — Single filing
    return _base_single()

def s2_single():   # dependent present -> HEAD-OF-HOUSEHOLD filing (run with C=HOH). No tuition here;
    return _base_single()          # this isolates the Single->HoH filing switch (the key Single mechanic).

def s3_single():   # Social Security, single claim
    s = _base_single()
    s["ss"] = {"claim_age": 67, "annual_combined": 25_000, "cola": 0.03, "taxable_pct": 0.85}
    return s

def s4_single():   # RE/BI deal
    s = _base_single()
    s["rebi"] = {"value": 100_000, "appr_pct": 0.04, "annual_dist": 4_000,
                 "dist_taxable_pct": 0.25, "dist_cola": True}
    return s

def s5_single():   # inheritance, tax-free
    s = _base_single()
    s["inheritance"] = {"amount": 500_000, "is_nominal": False, "arrival_year": 2040, "type": "taxfree"}
    return s

def s6_single():   # Roth conversions
    s = _base_single()
    s["roth_conv"] = {"start_age": 60, "amount": 50_000}
    return s

def s7_single():   # IRMAA (single tiers, one person) + large conversions
    s = _base_single()
    s["roth_conv"] = {"start_age": 65, "amount": 100_000}
    s["healthcare"] = {"medicare": 5_000}
    s["irmaa"] = True
    return s

# Frozen benchmarks (A) — SINGLE app. Each captured from the corrected engine and reproduced to the
# dollar by this model (2026-08-29). Do NOT edit to silence a mismatch.
BENCHMARKS_SINGLE = {
    # --- Scenario 0 ("Customer Zero"): Single app SHIPPED DEFAULT (childless; Trad 500k/Roth 250k/
    #     Brok 500k/HSA 100k, contribs 24,500/47,500/36,000/4,400, dist 90k). Frozen from engine.
    #     NOTE: benchmark EOL is NOMINAL. Today's-$ EOL ("memorized baseline") = 540,113 /
    #     tax 375,366 / legacy 540,113.
    "s0": {"eol": 2_298_841, "tax": 793_417, "legacy": 2_298_841,
           "eol_today": 540_113, "tax_today": 375_366, "legacy_today": 540_113},
    "s1": {"eol": 5_497_272, "tax": 391_983, "legacy": 4_908_427},
    "s2": {"eol": 5_599_410, "tax": 336_514, "legacy": 5_010_564},
    "s3": {"eol": 8_658_552, "tax": 710_740, "legacy": 8_069_707},
    "s4": {"eol": 6_485_140, "tax": 416_526, "legacy": 6_395_600},
    "s5": {"eol": 8_765_223, "tax": 514_124, "legacy": 8_176_377},
    "s6": {"eol": 4_725_267, "tax": 283_111, "legacy": 4_572_627},
    "s7": {"eol": 3_274_654, "tax": 371_586, "legacy": 3_274_654},
}
# Each single scenario runs with its filing-status constants: s2 uses HOH, the rest use SINGLE.
SCENARIOS_SINGLE = {"s1": (s1_single, SINGLE), "s2": (s2_single, HOH), "s3": (s3_single, SINGLE),
                    "s4": (s4_single, SINGLE), "s5": (s5_single, SINGLE), "s6": (s6_single, SINGLE),
                    "s7": (s7_single, SINGLE)}
TOL = 100  # dollars; floating-point residual across 40 years compounding is ~$20-50


def run(which=None, app="mfj"):
    if app == "single":
        scen_map = SCENARIOS_SINGLE
        bench = BENCHMARKS_SINGLE
        label = "SINGLE"
    else:
        scen_map = {k: (v, MFJ) for k, v in SCENARIOS.items()}
        bench = BENCHMARKS
        label = "MFJ"
    names = [which] if which else list(scen_map.keys())
    print(f"=== {label} app ===")
    print(f"{'scn':<5}{'metric':<8}{'benchmark(A)':>16}{'model(C)':>16}{'A-C':>10}  status")
    print("-" * 62)
    all_ok = True
    for name in names:
        fn, C = scen_map[name]
        r = project(fn(), C=C)
        b = bench[name]
        for metric in ("eol", "tax", "legacy"):
            if b[metric] is None:
                continue
            c = r[metric]; a = b[metric]; d = a - c
            ok = abs(d) <= TOL
            all_ok = all_ok and ok
            print(f"{name:<5}{metric:<8}{a:>16,}{round(c):>16,}{round(d):>10,}  {'OK' if ok else 'FAIL <<<'}")
    print("-" * 62)
    print(f"ALL {label} MODEL(C) vs BENCHMARK(A):", "PASS" if all_ok else "FAIL")
    print("\nReminder: this is only the C-vs-A leg. Full QA also requires B (engine) vs A —")
    print("see QA-RUNBOOK.md. A mismatch is a finding to investigate, never a benchmark to overwrite.")
    return all_ok


if __name__ == "__main__":
    # usage: python3 qa_independent_model.py [scenario] [app]
    #   python3 qa_independent_model.py            # all MFJ
    #   python3 qa_independent_model.py s3          # MFJ s3
    #   python3 qa_independent_model.py all single  # all Single
    #   python3 qa_independent_model.py s7 single   # Single s7
    args = [a.lower() for a in sys.argv[1:]]
    app = "single" if "single" in args else "mfj"
    scen = next((a for a in args if a.startswith("s") and a != "single"), None)
    if scen == "all":
        scen = None
    run(scen, app)
