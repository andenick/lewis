# International Economics Analysis Platform

**Status**: Research showcase — reference implementation
**Type**: Comprehensive International Economics Research Platform

---

## Overview

A unified platform for international economics analysis combining Balance of Payments, Flow of Funds, and cross-border value transfer data. Integrates 116,000+ observations spanning 79 years (1945-2024) across multiple countries and economic indicators.

**Key Achievement**: Complete R-to-Python replication of two advanced data science projects (Advanced Political Economy and International Trade ClassFiles) with enhanced capabilities and unified platform architecture.

---

## Quick Start

> **Note on imports.** The modules live under `Technical/src/`, which is the import
> root. Either run a module directly as a script, or put `Technical/src` on the path
> first:
>
> ```python
> import sys; sys.path.insert(0, "Technical/src")
> from data.fred_loader import FREDLoader
> from analysis.bop_comparative_analysis import BoPComparativeAnalysis
> ```
>
> The examples below use that form.

### Prerequisites
- Python 3.8+
- pandas, numpy, matplotlib, seaborn
- Optional: fredapi (for fresh FRED data pulls)

### Installation
```bash
pip install -r requirements.txt
```

---

## Setup

The platform reads source data from `DATA_ROOT` and writes its outputs to
`OUTPUT_ROOT`. Both default to `data/` and `outputs/` under the repo if unset.

### Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATA_ROOT` | Directory the platform reads source/input data from | `data` |
| `OUTPUT_ROOT` | Directory the platform writes generated outputs to | `outputs` |
| `FRED_API_KEY` | FRED API key (Z.1 / capital-flows collectors) | — |
| `BANXICO_TOKEN` | Banco de Mexico SIE API token | — |
| `COMTRADE_API_KEY` | UN Comtrade API key | — |

Copy `.env.example` to `.env` and fill in your own values, or export them in
your shell:

```bash
export DATA_ROOT=/path/to/your/data
export OUTPUT_ROOT=/path/to/your/outputs
export FRED_API_KEY=your_fred_key
export BANXICO_TOKEN=your_banxico_token
export COMTRADE_API_KEY=your_comtrade_key
```

### API keys — bring your own (all free)

- **FRED** — free at <https://fred.stlouisfed.org/docs/api/api_key.html>; set `FRED_API_KEY`.
- **Banxico SIE** — free token at <https://www.banxico.org.mx/SieAPIRest/service/v1/token>; set `BANXICO_TOKEN`.
- **UN Comtrade** — free registration at <https://comtradeplus.un.org/>; set `COMTRADE_API_KEY`.

Many analyses run against cached/bundled data with no key. Keys are only needed
to pull fresh data from the respective providers. See `data/MANIFEST.md` for the
list of public data sources and download links.

---

## Platform Capabilities

### Data Coverage

**Balance of Payments** (BPM6-aligned):
- 🇺🇸 **United States**: 1960-2024 (258 quarterly observations → annual)
- 🇬🇧 **United Kingdom**: 1946-2023 (78 annual observations, longest history)
- 🇩🇪 **Germany**: 1971-2024 (645 monthly observations → annual)

**Flow of Funds** (US only):
- **BEA International Investment Position**: 16 series, 1976-2024 (28,755 obs)
- **BEA International Transactions**: 106 series, 1999-2024
- **Treasury Ownership**: 54 series by sector, 1945-2024
- **Corporate Equities**: Foreign holdings, 1945-2024

**FRED Economic Data**:
- 19 integrated series (trade balance, GDP, exchange rates, etc.)
- Automatic cache fallback (no API key required for basic use)

**Total**: 116,000+ observations

### Analytical Features

**Multi-Country Comparative Analysis**:
- Current Account vs Financial Account scatter plots
- BOP identity verification (CA + FA + Errors ≈ 0)
- Trade balance trends (% of GDP)
- Cross-country structural comparisons

**Historical Event Analysis**:
- Nixon Shock (August 1971) - End of Bretton Woods
- NAFTA Implementation (January 1994)
- China WTO Accession (December 2001)
- German Reunification (October 1990)
- Maastricht Treaty (1992) & Euro Introduction (1999)
- 2008 Financial Crisis

**US Deep Dive**:
- Net International Investment Position evolution
- Creditor→Debtor nation transition (1980s)
- Foreign holdings composition (direct vs portfolio)
- Treasury ownership by sector (domestic & foreign)
- Cross-border capital flow analysis

### Visualizations

**Balance of Payments Suite** (5 charts):
1. US BoP: Nixon Shock period (1960-1980)
2. US BoP: NAFTA period (1985-2015)
3. Germany BoP: Reunification period (1991-2000)
4. Germany BoP: Maastricht/Euro convergence (1991-2005)
5. Comparative current account vs financial account (all countries)

**Flow of Funds Suite** (4 charts):
6. Net International Investment Position (1976-2024)
7. IIP Components (assets & liabilities breakdown)
8. Foreign Holdings Analysis (direct, portfolio, total)
9. Treasury Ownership by Sector

**Global Dashboard** (1 multi-panel chart):
10. 5-panel global economics overview

All visualizations: 300 DPI, professional styling, written under `OUTPUT_ROOT` (default `outputs/`)

---

## Project Structure

```
lewis/
├── README.md                 # This file - master documentation
├── requirements.txt          # Python dependencies
├── .env.example              # Template for DATA_ROOT / OUTPUT_ROOT / API keys
│
├── data/                     # Input data root (DATA_ROOT)
│   └── MANIFEST.md           # Public data sources, download links, provenance
│
├── outputs/                  # Generated charts/reports (OUTPUT_ROOT; created at runtime)
│
└── Technical/                # Implementation
    └── src/
        ├── data/             # Data access layer (FRED/BEA/IMF/World Bank collectors)
        ├── analysis/         # Analysis layer (BoP, Flow of Funds, capital flows)
        ├── platform/         # Platform layer (orchestration)
        ├── dashboard/        # Interactive dashboard
        └── scripts/          # One-off extraction / utility scripts
```

**Note**: The project separates source code (`Technical/src/`) from input data
(`DATA_ROOT`) and generated outputs (`OUTPUT_ROOT`). Many module filenames carry a
dated prefix (see the Quick Start note). For the authoritative file list, run
`git ls-files`.

---

## Usage Examples

### Platform Interface

> **The two `platform/` modules are the exception.** `Technical/src/platform/`
> shadows Python's standard-library `platform` module, so it can never be imported
> as `platform.<module>`. Load those two by file instead (or run them as scripts):
>
> ```python
> import importlib.util, pathlib
> def load(path, name):
>     spec = importlib.util.spec_from_file_location(name, path)
>     mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
>     return mod
> P = pathlib.Path("Technical/src/platform")
> InternationalEconomicsPlatform = load(P / "international_economics_platform.py",
>                                       "iecon_platform").InternationalEconomicsPlatform
> ```

```python
# InternationalEconomicsPlatform loaded as shown above

# Initialize platform
platform = InternationalEconomicsPlatform()

# Quick start: load all data + generate all visualizations
platform.quick_start()

# Individual country analysis
us_results = platform.analyze_country('US')
uk_results = platform.analyze_country('UK')
germany_results = platform.analyze_country('Germany')

# Comparative analysis
comparison = platform.comparative_analysis()

# Platform summary
summary = platform.platform_summary()
print(summary)
```

### Individual Analysis Modules

```python
# Balance of Payments Analysis
from analysis.bop_comparative_analysis import BoPComparativeAnalysis

bop = BoPComparativeAnalysis()
bop.load_data()
bop.plot_us_nixon_shock()
bop.plot_us_nafta_period()
bop.plot_germany_reunification()
bop.plot_comparative_current_financial()

# Flow of Funds Analysis
from analysis.flow_of_funds_analysis import FlowOfFundsAnalysis

fof = FlowOfFundsAnalysis()
fof.load_all_data()
fof.plot_net_international_investment_position()
fof.plot_iip_components()
fof.plot_foreign_holdings()
fof.plot_treasury_ownership()
```

### Global Platform

```python
# Loaded the same way (see the note under Usage Examples):
#   GlobalEconomicsPlatform = load(P / "global_economics_platform.py",
#                                  "global_platform").GlobalEconomicsPlatform

# Initialize global platform
global_platform = GlobalEconomicsPlatform()

# Full execution
global_platform.execute_full_analysis()

# Individual components
global_platform.create_country_profile('US', save=True)
global_platform.generate_global_dashboard(save=True)
```

### Data Access

```python
from data.fred_loader import FREDLoader

# Initialize (works without API key using cache)
loader = FREDLoader(use_cache=True)

# Load specific datasets
iip_data = loader.load_bea_iip()
ita_data = loader.load_bea_ita()
treasury_data = loader.load_treasury_ownership()

# Or with a FRED API key for fresh data. If FRED_API_KEY is set in the
# environment it is picked up automatically and api_key can be omitted.
loader = FREDLoader(api_key='<your FRED API key>', use_cache=False)
fresh_data = loader.load_bea_iip()
```

---

## Data Sources & Attribution

### Primary Sources

**United States**:
- Bureau of Economic Analysis (BEA) - International Transactions & IIP
- Federal Reserve Economic Data (FRED) - St. Louis Fed
- U.S. Treasury - TIC (Treasury International Capital) System

**United Kingdom**:
- Office for National Statistics (ONS) - Balance of Payments

**Germany**:
- Deutsche Bundesbank - Balance of Payments Statistics

**International Organizations**:
- International Monetary Fund (IMF) - BOP, DOTS, IIP databases
- World Bank - GDP and development indicators
- OECD - International trade statistics

### Methodology Standards

- **IMF Balance of Payments Manual 6th Edition (BPM6)**: Current standard (2009-present)
- **Complete BPM History**: All 6 editions referenced (1948-2009)
- **UN System of National Accounts (SNA 2008)**: National accounting framework

### Data Provenance

See `data/MANIFEST.md` for the list of public data sources, download links, and
provenance notes.

---

## Technical Implementation

### R-to-Python Translation

**Original R Projects**:
- `Trade_Visualization_NA.Rmd` (183 KB): Multi-country BoP, 25+ visualizations —
  **shipped** at `Technical/src/analysis/Trade_Visualization_NA.Rmd`.
- A second R notebook covering the Flow-of-Funds analysis (100+ FRED series) was the
  other source for this translation. It is coursework and is **not redistributed
  here**, so that half of the provenance cannot be verified from this repository.

**Python Equivalents Created**:

| R Functionality | Python Implementation | Status |
|-----------------|----------------------|--------|
| `fredr` package | `fredapi` + cache fallback | ✅ Complete |
| `tidyverse` data manipulation | `pandas` | ✅ Complete |
| `ggplot2` visualizations | `matplotlib` + `seaborn` | ✅ Complete |
| Quarterly→Annual aggregation | `groupby().sum()` | ✅ Complete |
| GDP normalization | Pandas merge + calculation | ✅ Complete |
| Historical period filtering | Boolean indexing | ✅ Complete |

**Enhancements Over R**:
- Unified platform (R had separate projects)
- Cached data access (no API key required)
- Cross-project integration (BoP + FoF combined)
- Enhanced error handling and logging
- Windows encoding compatibility

### Code Statistics

- **Total Python code**: ~61,600 lines across 125 tracked modules
- **Countries with dedicated collectors**: 7 (Japan, Canada, France, Italy, China,
  India, Brazil) on top of the US / UK / Germany BoP core
- **Charts**: generated into `OUTPUT_ROOT` at run time; none are committed

### Performance

- **Full Platform Execution**: ~20 seconds
- **Data Loading**: ~5 seconds
- **Visualization Suite**: ~10 seconds
- **Individual Country Analysis**: ~2 seconds
- **Memory Usage**: ~200 MB peak

---

## Documentation Guide

- **This file (README.md)**: Platform overview, setup, and usage
- **`data/MANIFEST.md`**: Data catalog — public sources, download links, provenance
- **`Technical/` README and module docstrings**: Implementation details and the
  conceptual public API for the analysis/platform/data layers
- **Inline code comments**: Throughout the source under `Technical/src/`

---

## Project History

### Phase 1: Initial Setup (Complete)
- Project structure established
- Data store integration
- FRED data collection (19 series)
- Methodology documentation (6 BPM editions)

### Phase 2: ClassFiles Integration (Complete)
- APE R project analysis and replication
- Trade R project analysis and replication
- Data extraction into the data store
- Python module creation (bop_comparative_analysis.py, flow_of_funds_analysis.py)

### Phase 3: Platform Development (Complete ✅)
- Base platform integration (international_economics_platform.py)
- FRED data loader with cache fallback (fred_loader.py)
- Multi-country analysis framework
- Comprehensive visualization suite

### Phase 4: Global Expansion (Complete ✅)
- Global economics platform (global_economics_platform.py)
- Country profile generation (JSON exports)
- Global dashboard creation
- IMF data collector framework (imf_data_collector.py)

### Phase 5: Documentation (Complete)
- Platform documentation (this README + module docstrings)
- Data catalog (`data/MANIFEST.md`)
- Master README update (this file)

---

## Known Limitations

1. **FRED API**: Optional (platform works with cache), fresh pulls require API key
2. **Country Coverage**: Currently limited to US, UK, Germany (by design from ClassFiles)
3. **IMF API**: Framework created, network access issue prevents live collection
4. **Frequency Harmonization**: All analysis uses annual data (monthly/quarterly aggregated)

---

## Future Enhancement Framework

### Phase 6: Additional Countries (Planned)
- Japan, France, Italy, Canada (G7 completion)
- China, South Korea, Mexico (major trading partners)
- Framework ready, requires data collection

### Phase 7: API Automation (Planned)
- Full IMF API integration (BOP, DOTS, IIP, CPIS, CDIS, COFER)
- OECD API integration
- Eurostat API integration
- Real-time data updates

### Phase 8: Advanced Analytics (Planned)
- Bilateral flow matrices (who-to-whom capital flows)
- Sectoral decomposition (financial account by sector)
- Implied profit rate analysis (complete APE replication)
- Forecasting models

### Phase 9: Interactive Features (Planned)
- Web dashboard (Plotly/Dash)
- Interactive country comparisons
- Custom period selection
- Export functionality (Excel, PDF reports)

---

## Validation & Testing

### Data Quality Checks ✅
- **US Data**: BOP identity verified (CA + FA ≈ -Errors)
- **UK Data**: Complete 1946-2023 coverage, no gaps
- **Germany Data**: Monthly→Annual aggregation correct
- **Flow of Funds**: IIP net position matches public data (-$26.3T)
- **GDP Normalization**: Produces reasonable percentages

### Code Quality ✅
- Every tracked module parses and its first-party imports resolve
- Graceful degradation (cache fallback when API unavailable)
- Type hints throughout
- Comprehensive docstrings
- Error handling for missing data
- Windows encoding compatibility (cp1252 issues resolved)

### Visualization Quality ✅
- Proper axis labels and titles
- Historical event markers
- Zero reference lines
- Professional styling (seaborn whitegrid)
- High resolution (300 DPI)
- Consistent color schemes

---

## Best Practices Applied

1. **Data Provenance**: Complete documentation in `data/MANIFEST.md`
2. **Read-Only Originals**: ClassFiles never modified
3. **Modular Design**: Separate data/analysis/platform layers
4. **Cache-First**: Reduce API dependency
5. **Comprehensive Logging**: Track all operations
6. **Error Handling**: Graceful degradation
7. **Type Safety**: Type hints throughout
8. **Documentation**: Extensive inline and external docs
9. **Testing**: the `test_*.py` files under `Technical/src/` are runnable
   demonstration scripts, not a `pytest` suite — several perform live network
   calls, so run them individually rather than collecting them
10. **Standards Compliance**: IMF BPM6

---

## Citation

If using this platform for research or publication:

```
International Economics Analysis Platform (2025)
Integrated data from BEA, ONS, Deutsche Bundesbank, FRED, World Bank, and IMF
```

For data sources and download links, see `data/MANIFEST.md`.

---

## Contact & Support

- **Project**: Lewis — International Economics Analysis Platform
- **Standards**: IMF BPM6 (2009)

**For questions about**:
- **Data sources & provenance**: See `data/MANIFEST.md`
- **Platform usage & APIs**: See the module docstrings under `Technical/src/`

---

## License

This project is dual-licensed — see [`LICENSE`](LICENSE) and [`LICENSES.md`](LICENSES.md):

- **Code** (everything under `Technical/`, scripts, tooling): **MIT**.
- **Data & documentation** produced by this project: **CC BY 4.0**.

Upstream data sources keep their own terms:
- **US Government Data** (BEA, FRED): Public domain
- **UK ONS Data**: Open Government License
- **Bundesbank Data**: Available for non-commercial research
- **IMF/World Bank**: Open data with attribution

---

**Platform status**: Research showcase — reference implementation
**Time span**: 79 years (1945-2024)
**Core BoP countries**: 3 (US, UK, Germany), plus 7 further country collectors
**Python code**: ~61,600 lines across 125 tracked modules

---

*International Economics Analysis Platform - Comprehensive research infrastructure for international trade, balance of payments, and flow of funds analysis*
