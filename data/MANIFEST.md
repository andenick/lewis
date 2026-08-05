# Data Manifest

The platform reads its source data from the directory named by the `DATA_ROOT`
environment variable (default: `./data`) and writes derived outputs to
`OUTPUT_ROOT` (default: `./outputs`). No source data is committed to this
repository — fetch it from the public sources below and place it under
`DATA_ROOT`.

## Public data sources

| Source | Coverage | Access | Env var / key |
|--------|----------|--------|---------------|
| **FRED** (Federal Reserve Economic Data) | US macro series, Z.1 Flow of Funds, exchange rates | <https://fred.stlouisfed.org/> · API: <https://fred.stlouisfed.org/docs/api/fred/> | `FRED_API_KEY` (free) |
| **BEA** (Bureau of Economic Analysis) | US Balance of Payments, International Investment Position, International Transactions | <https://apps.bea.gov/iTable/> · API: <https://apps.bea.gov/API/> | — |
| **Banco de México (SIE)** | Mexico BoP, trade, exchange rates | <https://www.banxico.org.mx/SieAPIRest/> | `BANXICO_TOKEN` (free) |
| **UN Comtrade** | Bilateral merchandise trade flows | <https://comtradeplus.un.org/> | `COMTRADE_API_KEY` (free) |
| **World Bank** | GDP, development indicators (200+ economies) | <https://data.worldbank.org/> · API: <https://datahelpdesk.worldbank.org/knowledgebase/articles/889392> | — |
| **IMF** | BOP, CDIS, CPIS, COFER | <https://data.imf.org/> · SDMX API | — |
| **OECD** | BoP and macro indicators | <https://data.oecd.org/> · SDMX API | — |
| **Eurostat** | EU balance of payments | <https://ec.europa.eu/eurostat> · SDMX API | — |
| **BIS** | International banking statistics | <https://www.bis.org/statistics/> | — |
| **ONS** (UK) | UK Balance of Payments (Pink Book) | <https://www.ons.gov.uk/> | — |
| **Deutsche Bundesbank** | Germany Balance of Payments | <https://www.bundesbank.de/en/statistics> | — |

## Expected layout under `DATA_ROOT`

Collectors write/read under subdirectories of `DATA_ROOT`, e.g.:

```
$DATA_ROOT/
  FRED/                 # FRED CSV exports
  FRED_Z1/              # Z.1 Flow of Funds
  ALFRED/               # ALFRED historical vintages
  CENSUS/               # Census data
  ALPHA_VANTAGE/        # financial-market data
  international/        # bilateral / cross-border series
  ...
```

The R Markdown analysis (`Technical/src/analysis/Trade_Visualization_NA.Rmd`)
reads four Balance-of-Payments workbooks from `DATA_ROOT`:
`BoP_USRData_NA.xlsx`, `BoP_UKRData_NA.xlsx`, `BoP_GermanyRData_NA.xlsx` and
`BoP_WBankGDP_NA.xlsx`.

**These four workbooks are not redistributed with this repository**, and no
sample data ships. They were assembled by hand from coursework extracts, so
there is no single download URL for them. To reproduce that analysis you have
to rebuild them from the primary sources below, each of which is free and
public:

| Workbook | Rebuild from | Source |
|---|---|---|
| `BoP_USRData_NA.xlsx` | US balance of payments (ITA), annual | BEA International Transactions — https://apps.bea.gov/iTable/?reqid=62 |
| `BoP_UKRData_NA.xlsx` | UK balance of payments (Pink Book), annual | ONS — https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments |
| `BoP_GermanyRData_NA.xlsx` | German balance of payments, monthly → annual | Deutsche Bundesbank time-series database — https://www.bundesbank.de/en/statistics/time-series-databases-745582 |
| `BoP_WBankGDP_NA.xlsx` | Nominal GDP, current US$ (`NY.GDP.MKTP.CD`) | World Bank Open Data — https://data.worldbank.org/indicator/NY.GDP.MKTP.CD |

Each workbook is a single sheet of years × BoP components (current account,
capital account, financial account and their major sub-balances) in current US
dollars, with the World Bank workbook supplying the GDP denominator used for
the "% of GDP" normalisation. The Python BoP modules read the same four files.

The remaining series listed above are pulled directly from their providers'
APIs by the collectors under `Technical/src/data/`; those need only the free
API keys named in `.env.example`.
