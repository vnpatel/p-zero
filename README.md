# P-ZERO Financial Engine

A single-file, fully client-side retirement and Roth-conversion planning
sandbox. It projects a married couple's finances year by year across
accumulation, semi-retirement, and full retirement — modeling taxes, RMDs,
ACA subsidies, IRMAA, Social Security, dividends, survivor scenarios, and
after-tax legacy — then stress-tests the plan with Monte Carlo simulation.

No server, no database, no build step. Open the HTML file and it runs.

> ⚠️ **For illustration and educational purposes only — not financial, tax,
> or legal advice.** This is a personal planning sandbox built on simplified
> assumptions; real outcomes will differ. Consult a qualified financial
> advisor, CPA, or attorney about your individual situation. See the full
> disclaimer in the app's Help section.

## Features

- **Year-by-year projection** across four life phases with a full ledger
  (contributions, growth, withdrawals, taxes, RMDs, MAGI, and more).
- **Tax modeling** — MFJ ordinary + LTCG brackets, state/local tax, the
  standard deduction, and editable bracket tables.
- **Roth conversion optimizer** — spending-aware, bracket-capped conversions
  with an auto or manual start.
- **Healthcare** — ACA premium subsidies (with the 400% FPL cliff) and IRMAA
  surcharges on a two-year lookback.
- **Monte Carlo** — historical block-bootstrap (1972–2025, with an optional
  stress mode back to 1928) and a parametric mode. Reports success rate, a
  fan chart, outcome percentiles, and an "anatomy of a typical failure" view.
- **Analysis tools** — A/B compare, a solve-for engine (max spend, earliest
  retirement, required portfolio), and after-tax legacy estimation.
- **Import / Export** — save and reload a complete profile as a JSON file.

## Running it

Download `Patel Retirement Simulation - Only.html` and open it in any modern
browser. That's it — everything (including the Monte Carlo data) is embedded
in the file, and it works offline. No installation, no dependencies to fetch.

## Methodology & data

The historical Monte Carlo uses a 5-year block bootstrap over hand-entered
approximations of annual S&P 500 total return, 10-year Treasury return, and
CPI inflation. The figures are *shape-accurate* (real crashes, recoveries,
and inflation spikes are present in roughly the right magnitudes) but **not
basis-point exact**, and the data is frozen in the file — the app makes no
network calls. Tax tables, IRMAA tiers, and ACA parameters reflect a
specific point in time and should be verified against current law before
relying on any result. See the in-app Help for full details.

## Limitations

- Uses JavaScript floating-point math, so figures carry sub-dollar rounding
  (irrelevant for multi-decade planning, but not penny-exact).
- A single fixed return drives the deterministic projection; volatility is
  modeled only in the Monte Carlo tool.
- Defaults are tuned to one household's situation; adjust all inputs to yours.
- Tax/benefit rules are simplified and U.S.- (and partly Indiana-) specific.

## Tech

Vanilla HTML/CSS/JavaScript in one file. Tailwind (browser build) and Font
Awesome are loaded via CDN for styling/icons; all logic and data are inline.

## Disclaimer

This software is provided "as is," without warranty of any kind. It is not
financial, tax, investment, or legal advice. The author is not responsible
for decisions made based on its output. Always consult qualified
professionals.

## License

Copyright (c) 2026 V Patel. All rights reserved. This project is proprietary
— see [LICENSE](LICENSE). You may view the source for personal reference, but
any redistribution, modification, or reuse requires prior written permission.
Please contact the author with any such request.
