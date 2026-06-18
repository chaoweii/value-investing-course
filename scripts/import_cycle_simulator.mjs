#!/usr/bin/env node
import { writeFile, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import XLSX from 'xlsx';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUTPUT = join(ROOT, 'src/data/cycle-simulator.json');
const SHILLER_URL = 'https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/ie_data.xls?ver=1755225921953';
const FRED_URL = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS,GS10';

const pct = (value) => Number.isFinite(value) ? value / 100 : null;

async function fetchBuffer(url) {
  const response = await fetch(url, { headers: { 'User-Agent': 'OwnerMindsetCourse/0.1' } });
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return Buffer.from(await response.arrayBuffer());
}

async function fetchText(url) {
  const response = await fetch(url, { headers: { 'User-Agent': 'OwnerMindsetCourse/0.1' } });
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.text();
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = lines.shift().split(',');
  return lines.map((line) => {
    const cells = line.split(',');
    return Object.fromEntries(header.map((key, index) => [key, cells[index] ?? '']));
  });
}

function monthKeyFromShillerFraction(dateFraction) {
  const year = Math.floor(Number(dateFraction));
  const month = Math.round((Number(dateFraction) - year) * 12 + 0.5);
  return `${year}-${String(Math.max(1, Math.min(12, month))).padStart(2, '0')}`;
}

function parseShillerWorkbook(buffer) {
  const workbook = XLSX.read(buffer, { type: 'buffer' });
  const sheet = workbook.Sheets.Data ?? workbook.Sheets[workbook.SheetNames.at(-1)];
  const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: true, blankrows: false });
  return rows.slice(7).map((row) => {
    const dateFraction = Number(row[5]);
    const year = Math.floor(dateFraction);
    const month = Math.round((dateFraction - year) * 12 + 0.5);
    const price = Number(row[1]);
    const dividend = Number(row[2]);
    const earnings = Number(row[3]);
    const cape = Number(row[12]);
    return {
      key: monthKeyFromShillerFraction(dateFraction),
      year,
      month,
      price,
      dividend,
      earnings,
      pe: earnings > 0 ? price / earnings : null,
      cape: Number.isFinite(cape) ? cape : null,
    };
  }).filter((row) => row.year && row.month && row.price > 0);
}

function parseFred(text) {
  const observations = new Map();
  for (const row of parseCsv(text)) {
    const key = row.observation_date?.slice(0, 7);
    if (!key) continue;
    observations.set(key, {
      tbill: row.TB3MS && row.TB3MS !== '.' ? pct(Number(row.TB3MS)) : null,
      gs10: row.GS10 && row.GS10 !== '.' ? pct(Number(row.GS10)) : null,
    });
  }
  return observations;
}

function average(values) {
  const usable = values.filter((value) => Number.isFinite(value));
  return usable.length ? usable.reduce((sum, value) => sum + value, 0) / usable.length : null;
}

function annualize(shillerRows, fredByMonth) {
  const rows = [];
  for (let i = 1; i < shillerRows.length; i += 1) {
    const current = shillerRows[i];
    const previous = shillerRows[i - 1];
    const fred = fredByMonth.get(current.key) ?? {};
    const dividendCash = (current.dividend || 0) / 12;
    const spReturn = previous.price > 0 ? (current.price + dividendCash) / previous.price - 1 : null;
    rows.push({
      ...current,
      spReturn,
      tbillReturn: fred.tbill != null ? fred.tbill / 12 : null,
      tbillYield: fred.tbill,
      gs10: fred.gs10,
    });
  }

  const byYear = new Map();
  for (const row of rows) {
    if (!Number.isFinite(row.spReturn) || row.tbillReturn == null) continue;
    if (!byYear.has(row.year)) byYear.set(row.year, []);
    byYear.get(row.year).push(row);
  }

  return [...byYear.entries()]
    .filter(([, months]) => months.length >= 10)
    .map(([year, months]) => {
      const spTotalReturn = months.reduce((wealth, month) => wealth * (1 + month.spReturn), 1) - 1;
      const tbillReturn = months.reduce((wealth, month) => wealth * (1 + month.tbillReturn), 1) - 1;
      return {
        year,
        spTotalReturn,
        tbillReturn,
        avgCape: average(months.map((month) => month.cape)),
        avgPe: average(months.map((month) => month.pe)),
        avgTbillYield: average(months.map((month) => month.tbillYield)),
        avgGs10Yield: average(months.map((month) => month.gs10)),
      };
    })
    .filter((row) => row.year >= 1934);
}

function simulate(records, strategy, options = {}) {
  const {
    startYear = records[1]?.year,
    endYear = records.at(-1)?.year,
    lowCape = 15,
    highCape = 25,
    minEquity = 0.3,
    normalEquity = 0.6,
    maxEquity = 0.9,
    hurdleSpread = 0.02,
    drawdownTrigger = -0.2,
  } = options;
  const selected = records.filter((record) => record.year >= startYear - 1 && record.year <= endYear);
  let wealth = 10000;
  let spWealth = 10000;
  let priorWeight = null;
  let turnover = 0;
  let peak = wealth;
  let maxDrawdown = 0;
  const series = [];
  const weights = [];

  for (let i = 1; i < selected.length; i += 1) {
    const previous = selected[i - 1];
    const current = selected[i];
    if (current.year < startYear) continue;
    const spDrawdown = spWealth / Math.max(...[10000, ...series.map((point) => point.spWealth)]) - 1;
    let equityWeight;
    if (strategy === 'sp500') equityWeight = 1;
    else if (strategy === 'tbills') equityWeight = 0;
    else if (strategy === 'balanced') equityWeight = 0.7;
    else if (strategy === 'spread') {
      const earningsYield = previous.avgPe ? 1 / previous.avgPe : 0;
      const spread = earningsYield - (previous.avgTbillYield ?? 0);
      equityWeight = spread >= hurdleSpread ? maxEquity : spread <= 0 ? minEquity : normalEquity;
    } else {
      equityWeight = previous.avgCape <= lowCape ? maxEquity : previous.avgCape >= highCape ? minEquity : normalEquity;
      if (strategy === 'fear' && spDrawdown <= drawdownTrigger && previous.avgCape < highCape) {
        equityWeight = Math.min(maxEquity, equityWeight + 0.2);
      }
    }
    if (priorWeight != null) turnover += Math.abs(equityWeight - priorWeight);
    priorWeight = equityWeight;
    const annualReturn = equityWeight * current.spTotalReturn + (1 - equityWeight) * current.tbillReturn;
    wealth *= 1 + annualReturn;
    spWealth *= 1 + current.spTotalReturn;
    peak = Math.max(peak, wealth);
    maxDrawdown = Math.min(maxDrawdown, wealth / peak - 1);
    weights.push(equityWeight);
    series.push({ year: current.year, wealth, spWealth, annualReturn, equityWeight, cape: previous.avgCape });
  }
  const years = Math.max(1, series.length);
  return {
    endingWealth: wealth,
    cagr: (wealth / 10000) ** (1 / years) - 1,
    maxDrawdown,
    averageEquityWeight: average(weights),
    turnover,
    years,
    series,
  };
}

async function main() {
  const warnings = [];
  let existing = {};
  if (existsSync(OUTPUT)) {
    existing = JSON.parse(await readFile(OUTPUT, 'utf8'));
  }

  let annualRecords = existing.annualRecords ?? [];
  try {
    const [shillerBuffer, fredText] = await Promise.all([
      fetchBuffer(SHILLER_URL),
      fetchText(FRED_URL),
    ]);
    annualRecords = annualize(parseShillerWorkbook(shillerBuffer), parseFred(fredText));
  } catch (error) {
    warnings.push(`Cycle simulator refresh failed; retained prior snapshot. ${error.message}`);
    if (!annualRecords.length) throw error;
  }

  const defaultOptions = {
    startYear: Math.max(1935, annualRecords[1]?.year ?? 1935),
    endYear: annualRecords.at(-1)?.year,
    lowCape: 15,
    highCape: 25,
    minEquity: 0.3,
    normalEquity: 0.6,
    maxEquity: 0.9,
    hurdleSpread: 0.02,
    drawdownTrigger: -0.2,
  };
  const strategies = {
    sp500: simulate(annualRecords, 'sp500', defaultOptions),
    tbills: simulate(annualRecords, 'tbills', defaultOptions),
    balanced: simulate(annualRecords, 'balanced', defaultOptions),
    valuation: simulate(annualRecords, 'valuation', defaultOptions),
    spread: simulate(annualRecords, 'spread', defaultOptions),
    fear: simulate(annualRecords, 'fear', defaultOptions),
  };

  const payload = {
    generatedAt: new Date().toISOString(),
    warnings,
    assumptions: {
      initialWealth: 10000,
      taxFreeAccount: true,
      annualRebalancing: true,
      dividendsReinvested: true,
      tbillYieldReinvested: true,
      noLeverage: true,
      noShorting: true,
      transactionCosts: 'Ignored in v1 for teaching simplicity',
      lookAheadGuard: 'Each annual allocation uses the prior year valuation and yield regime.',
    },
    sources: {
      shiller: 'https://shillerdata.com/ and its ie_data.xls download',
      fred: FRED_URL,
    },
    defaultOptions,
    annualRecords,
    defaultStrategies: Object.fromEntries(Object.entries(strategies).map(([key, value]) => [key, {
      endingWealth: value.endingWealth,
      cagr: value.cagr,
      maxDrawdown: value.maxDrawdown,
      averageEquityWeight: value.averageEquityWeight,
      turnover: value.turnover,
      years: value.years,
    }])),
  };
  await writeFile(OUTPUT, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  console.log(`Wrote ${OUTPUT} with ${annualRecords.length} annual records`);
  warnings.forEach((warning) => console.warn(`Warning: ${warning}`));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
