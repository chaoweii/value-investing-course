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
npm run import:portfolio
npm run import:dcf-learning
npm run refresh:macro
npm run import:cycles
npm run dev
```

## Publish with GitHub + Vercel

This course is designed to publish as a static Astro site. Use GitHub as the source of truth and
Vercel as the automatic publisher.

Recommended Vercel settings:

- Framework preset: `Astro`
- Build command: `npm run build:deploy`
- Output directory: `dist`
- Production branch: `main`

The deploy command intentionally skips the local workbench importers. Vercel should build only from
the website-local snapshots already committed under `src/data/`, so it never needs access to:

`/Users/chao86/Documents/Investment 2/tost_googl_sotp_dcf`

### Update workflow

For content-only updates:

```bash
npm run check:deploy
git add .
git commit -m "Update course"
git push
```

For valuation, portfolio, DCF, or macro snapshot updates:

```bash
npm run import:live
npm run import:portfolio
npm run import:dcf-learning
npm run refresh:macro
npm run import:cycles
npm run check:deploy
git add src/data
git add .
git commit -m "Refresh course snapshots"
git push
```

Vercel will publish every push to `main`. Branch pushes can be used for preview deployments before
merging larger lesson changes.

## Refresh live companions

```bash
npm run import:live
```

The importer reads:

`/Users/chao86/Documents/Investment 2/tost_googl_sotp_dcf/outputs/data/master_portfolio_valuation.csv`

It never writes to the valuation workbench.

The portfolio importer also reads the workbench's probability-weighted scenarios and writes only
`src/data/portfolio-candidates.json` inside the course repository.

The DCF learning importer reads TOST, ADYEY, and BRK.B operating-model, yearly-DCF, target-price,
and master-valuation outputs and writes only `src/data/dcf-learning.json`.

## Refresh the dated macro companion

```bash
npm run refresh:macro
```

This reads official U.S. Treasury and Federal Reserve/FRED sources and writes only
`src/data/macro-snapshot.json` inside this course repository. Normal builds use the last stored
snapshot and never require network access.

## Refresh the cycle simulator snapshot

```bash
npm run import:cycles
```

This reads Robert Shiller's public historical market workbook and FRED Treasury series, then writes
only `src/data/cycle-simulator.json`. The published simulator uses the committed snapshot, so Vercel
does not need network access for historical data.

Validate the stored snapshot without a network call:

```bash
npm run verify:macro
npm run verify:dcf-learning
```
