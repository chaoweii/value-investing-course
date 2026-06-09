# Owner Mindset

A private, case-first value-investing apprenticeship.

The site is deliberately separate from the valuation workbench:

- durable lessons live here;
- live valuation snapshots are imported read-only;
- personal investment decisions live as Markdown journals;
- the original `tost_googl_sotp_dcf/tutorials/` folder remains untouched.

## Run locally

```bash
npm install
npm run import:live
npm run dev
```

## Refresh live companions

```bash
npm run import:live
```

The importer reads:

`/Users/chao86/Documents/Investment 2/tost_googl_sotp_dcf/outputs/data/master_portfolio_valuation.csv`

It never writes to the valuation workbench.
