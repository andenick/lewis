"""
FRED Data Loader
================

Module for loading Federal Reserve Economic Data (FRED) series.
Replicates the FRED API functionality from ClassFiles APE R project.

Supports:
- BEA International Investment Position (IIP)
- BEA International Transaction Accounts (ITA)
- Treasury Ownership Data (Z.1 L.210)
- Rest of World Accounts (Z.1 L.133)
- Corporate Equities (Z.1 L.223)

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
import warnings

# Try to import fredapi, provide fallback
try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    warnings.warn(
        "fredapi not available. Install with: pip install fredapi\n"
        "Will use cached data from data source instead."
    )

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
FLOW_OF_FUNDS_PATH = OUTPUT_ROOT / "FLOW_OF_FUNDS"


class FREDLoader:
    """
    Load FRED data for international economics analysis.

    Provides access to BEA international accounts data via FRED API,
    with fallback to cached data from data source.
    """

    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True):
        """
        Initialize FRED loader.

        Parameters
        ----------
        api_key : str, optional
            FRED API key. If None, the FRED_API_KEY environment variable is
            used when set.
        use_cache : bool, default True
            Whether to use cached data from the data store when available
        """
        self.use_cache = use_cache
        # Documented behaviour: fall back to the FRED_API_KEY environment
        # variable when no key is passed explicitly (see .env.example).
        self.api_key = api_key or os.environ.get("FRED_API_KEY") or None
        self.fred = None

        if FRED_AVAILABLE and self.api_key:
            self.fred = Fred(api_key=self.api_key)
        elif not FRED_AVAILABLE:
            print("[INFO] Using cached data from data source")

    # ========================================================================
    # BEA INTERNATIONAL INVESTMENT POSITION (IIP)
    # ========================================================================

    @staticmethod
    def get_bea_iip_series_list() -> List[str]:
        """
        Get list of BEA IIP series IDs.

        Returns 16 quarterly series covering:
        - US assets and liabilities
        - Direct investment
        - Portfolio investment
        - Other investment
        - Reserve assets
        - Net international investment position

        Returns
        -------
        list of str
            FRED series IDs for BEA IIP data
        """
        return [
            "IIPASSEA",      # US assets, total
            "IIPDIREAMVA",   # Direct investment at market value, assets
            "IIPDIRELMVA",   # Direct investment at market value, liabilities
            "IIPFINAAGA",    # Financial account, assets
            "IIPFINALGA",    # Financial account, liabilities
            "IIPFINANCNA",   # Financial account, net
            "IIPLIABA",      # US liabilities
            "IIPNETINA",     # Net international investment position
            "IIPOTHEAA",     # Other investment, assets
            "IIPOTHELA",     # Other investment, liabilities
            "IIPPORTAA",     # Portfolio investment, assets
            "IIPPORTLA",     # Portfolio investment, liabilities
            "IIPRESEA",      # Reserve assets
            "IIPUSASSA",     # US owned assets abroad
            "IIPUSLIAA",     # Foreign owned assets in US
            "IIPUSNETIA"     # Net position
        ]

    def load_bea_iip(self, from_cache: bool = None) -> pd.DataFrame:
        """
        Load BEA International Investment Position data.

        Parameters
        ----------
        from_cache : bool, optional
            Force use of cache (True) or API (False).
            If None, uses self.use_cache setting.

        Returns
        -------
        pd.DataFrame
            BEA IIP data with columns:
            - date: observation date
            - series_id: FRED series ID
            - value: observation value (millions of dollars)
            - title: series description
            - frequency: Q (quarterly)
            - units: typically "Millions of Dollars"
        """
        use_cache_now = from_cache if from_cache is not None else self.use_cache

        cache_path = FLOW_OF_FUNDS_PATH / "BEA_IIP" / "bea_iip_data.csv"

        if use_cache_now and cache_path.exists():
            print(f"[CACHE] Loading BEA IIP from {cache_path.relative_to(PROJECT_ROOT)}")
            df = pd.read_csv(cache_path)
            df['date'] = pd.to_datetime(df['date'])
            return df

        if self.fred is None:
            raise RuntimeError(
                "FRED API not available and cache not found. "
                f"Expected cache at: {cache_path}"
            )

        print("[FRED API] Fetching BEA IIP data...")
        series_ids = self.get_bea_iip_series_list()
        return self._fetch_fred_series(series_ids)

    # ========================================================================
    # BEA INTERNATIONAL TRANSACTION ACCOUNTS (ITA) TABLE 1.2
    # ========================================================================

    @staticmethod
    def get_bea_ita_series_list() -> List[str]:
        """
        Get list of BEA ITA Table 1.2 series IDs.

        Returns 100+ quarterly series covering detailed:
        - Exports and imports of goods
        - Services trade
        - Primary income
        - Secondary income
        - Financial account components

        Returns
        -------
        list of str
            FRED series IDs for BEA ITA Table 1.2
        """
        # This is a subset - full list has 100+ series
        return [
            # Current Account
            "IEAACDN", "IEAADIDIN", "IEAADIEN", "IEAADIN", "IEAADSLN", "IEAADSSN",
            "IEAAFDN", "IEAAN", "IEAAOICDN", "IEAAOILN", "IEAAOIN", "IEAAOITN",
            "IEAAORON", "IEAAPIDN", "IEAAPIEN", "IEAAPIN", "IEAARIMFN", "IEAARMN",
            "IEAARN", "IEAARON", "IEAARSDN", "IEAASN", "IEABCGN", "IEABCGSN",
            "IEABCN", "IEABCPIN", "IEABCPN", "IEABCSIN", "IEABCSN", "IEACTRN",

            # Financial Account
            "IEAFDN", "IEAIDIDIN", "IEAIDIEN", "IEAIDIN", "IEAIDSLN", "IEAIDSSN",
            "IEAIN", "IEAIOICDN", "IEAIOILN", "IEAIOIN", "IEAIOISDN", "IEAIOITN",
            "IEAIPIDN", "IEAIPIEN", "IEAIPIN",

            # Goods
            "IEAMGAVN", "IEAMGCGN", "IEAMGCN", "IEAMGFN", "IEAMGGN", "IEAMGIN",
            "IEAMGMN", "IEAMGN", "IEAMGON", "IEAMGSN",

            # Services
            "IEAMICN", "IEAMIDN", "IEAMIIN", "IEAMIN", "IEAMION", "IEAMIPN",
            "IEAMN", "IEAMSBN", "IEAMSFN", "IEAMSGN", "IEAMSIN", "IEAMSIPN",
            "IEAMSIRN", "IEAMSMN", "IEAMSN", "IEAMSTCN", "IEAMSTN", "IEAMSTVN",
            "IEANLCN", "IEANLFN", "IEASDN",

            # Exports
            "IEAXGAVN", "IEAXGCGN", "IEAXGCN", "IEAXGFN", "IEAXGGN", "IEAXGIN",
            "IEAXGMN", "IEAXGN", "IEAXGNXN", "IEAXGON", "IEAXGSN",
            "IEAXICN", "IEAXIDN", "IEAXIIN", "IEAXIN", "IEAXION", "IEAXIPN",
            "IEAXIRN", "IEAXN", "IEAXSBN", "IEAXSFN", "IEAXSGN", "IEAXSIN",
            "IEAXSIPN", "IEAXSIRN", "IEAXSMN", "IEAXSN", "IEAXSTCN", "IEAXSTN",
            "IEAXSTVN"
        ]

    def load_bea_ita(self, from_cache: bool = None) -> pd.DataFrame:
        """
        Load BEA International Transaction Accounts Table 1.2 data.

        Parameters
        ----------
        from_cache : bool, optional
            Force use of cache (True) or API (False)

        Returns
        -------
        pd.DataFrame
            BEA ITA data with date, series_id, value, metadata columns
        """
        use_cache_now = from_cache if from_cache is not None else self.use_cache

        cache_path = FLOW_OF_FUNDS_PATH / "BEA_ITA" / "bea_ita_table1_2_data.csv"

        if use_cache_now and cache_path.exists():
            print(f"[CACHE] Loading BEA ITA from {cache_path.relative_to(PROJECT_ROOT)}")
            df = pd.read_csv(cache_path)
            df['date'] = pd.to_datetime(df['date'])
            return df

        if self.fred is None:
            raise RuntimeError(
                "FRED API not available and cache not found. "
                f"Expected cache at: {cache_path}"
            )

        print("[FRED API] Fetching BEA ITA Table 1.2 data (100+ series)...")
        series_ids = self.get_bea_ita_series_list()
        return self._fetch_fred_series(series_ids)

    # ========================================================================
    # TREASURY OWNERSHIP DATA (Z.1 L.210)
    # ========================================================================

    @staticmethod
    def get_treasury_ownership_series_list() -> List[str]:
        """
        Get list of Treasury ownership series IDs from Z.1 L.210 table.

        Returns 50+ quarterly series covering holdings by:
        - Households
        - Nonfinancial business
        - State and local governments
        - Federal government
        - Monetary authority
        - Banks
        - Insurance
        - Pensions
        - Rest of world

        Returns
        -------
        list of str
            FRED series IDs for treasury ownership
        """
        return [
            "BOGZ1FL213061103Q", "BOGZ1FL213061120Q", "BOGZ1FL313161110Q",
            "BOGZ1FL313161205Q", "BOGZ1FL313161275Q", "BOGZ1FL313161283Q",
            "BOGZ1FL313161305Q", "BOGZ1FL313161375Q", "BOGZ1FL343061123Q",
            "BOGZ1FL343061145Q", "BOGZ1FL403061105Q", "BOGZ1FL633061105Q",
            "BOGZ1FL633061110Q", "BOGZ1FL633061120Q", "BOGZ1FL663061105Q",
            "BOGZ1FL673061103Q", "BOGZ1FL713061103Q", "BOGZ1FL713061113Q",
            "BOGZ1FL713061125Q", "BOGZ1FL893061105Q", "BOGZ1LM153061105Q",
            "BOGZ1LM153061185Q", "BOGZ1LM223061143Q", "BOGZ1LM263061105Q",
            "BOGZ1LM263061110Q", "BOGZ1LM263061120Q", "BOGZ1LM343061105Q",
            "BOGZ1LM343061155Q", "BOGZ1LM343061165Q", "BOGZ1LM473061105Q",
            "BOGZ1LM513061105Q", "BOGZ1LM513061115Q", "BOGZ1LM513061125Q",
            "BOGZ1LM543061105Q", "BOGZ1LM543061115Q", "BOGZ1LM543061125Q",
            "BOGZ1LM553061103Q", "BOGZ1LM563061103Q", "BOGZ1LM573061105Q",
            "BOGZ1LM573061133Q", "BOGZ1LM573061143Q", "BOGZ1LM653061105Q",
            "BOGZ1LM653061113Q", "BOGZ1LM653061125Q", "BOGZ1LM733061103Q",
            "BOGZ1LM743061103Q", "BOGZ1LM753061103Q", "BOGZ1LM763061100Q",
            "BOGZ1LM903061103Q", "FGSBLUQ027S", "FGTSL",
            "SLGTRSQ027S", "TSABSNNB", "TSABSNNCB"
        ]

    def load_treasury_ownership(self, from_cache: bool = None) -> pd.DataFrame:
        """Load Treasury ownership data from Z.1 L.210 table."""
        use_cache_now = from_cache if from_cache is not None else self.use_cache

        cache_path = FLOW_OF_FUNDS_PATH / "Treasury_Ownership" / "treasury_ownership_data.csv"

        if use_cache_now and cache_path.exists():
            print(f"[CACHE] Loading Treasury ownership from {cache_path.relative_to(PROJECT_ROOT)}")
            df = pd.read_csv(cache_path)
            df['date'] = pd.to_datetime(df['date'])
            return df

        if self.fred is None:
            raise RuntimeError(f"FRED API not available and cache not found at: {cache_path}")

        print("[FRED API] Fetching Treasury ownership data...")
        series_ids = self.get_treasury_ownership_series_list()
        return self._fetch_fred_series(series_ids)

    # ========================================================================
    # CORPORATE EQUITIES DATA
    # ========================================================================

    def load_corporate_equities(self, from_cache: bool = None) -> pd.DataFrame:
        """Load corporate equities holdings data."""
        use_cache_now = from_cache if from_cache is not None else self.use_cache

        cache_path = FLOW_OF_FUNDS_PATH / "Corporate_Equities" / "corp_equities_data.csv"

        if use_cache_now and cache_path.exists():
            print(f"[CACHE] Loading corporate equities from {cache_path.relative_to(PROJECT_ROOT)}")
            df = pd.read_csv(cache_path)
            df['date'] = pd.to_datetime(df['date'])
            return df

        raise NotImplementedError(
            "Corporate equities FRED series list not yet implemented. "
            f"Use cached data from: {cache_path}"
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _fetch_fred_series(self, series_ids: List[str]) -> pd.DataFrame:
        """
        Fetch multiple FRED series and combine into single DataFrame.

        Parameters
        ----------
        series_ids : list of str
            FRED series IDs to fetch

        Returns
        -------
        pd.DataFrame
            Combined data with series_id, date, value, and metadata columns
        """
        if self.fred is None:
            raise RuntimeError(
                "FRED API not initialized. Pass api_key=..., set the FRED_API_KEY "
                "environment variable, or run with use_cache=True."
            )

        all_data = []

        for i, series_id in enumerate(series_ids, 1):
            try:
                # Fetch observations
                series_data = self.fred.get_series(series_id, observation_start='1900-01-01')

                # Fetch metadata
                info = self.fred.get_series_info(series_id)

                # Combine
                df = pd.DataFrame({
                    'date': series_data.index,
                    'value': series_data.values,
                    'series_id': series_id,
                    'title': info.get('title', ''),
                    'frequency_short': info.get('frequency_short', ''),
                    'units_short': info.get('units_short', ''),
                    'seasonal_adjustment_short': info.get('seasonal_adjustment_short', ''),
                    'last_updated': info.get('last_updated', ''),
                    'observation_start': info.get('observation_start', ''),
                    'observation_end': info.get('observation_end', '')
                })

                all_data.append(df)
                print(f"  [{i}/{len(series_ids)}] {series_id}: {len(series_data)} observations")

            except Exception as e:
                print(f"  [ERROR] Failed to fetch {series_id}: {e}")

        if not all_data:
            raise ValueError("No data fetched successfully")

        combined = pd.concat(all_data, ignore_index=True)
        print(f"[OK] Fetched {len(all_data)} series, {len(combined):,} total observations")

        return combined

    def save_to_cache(self, df: pd.DataFrame, data_type: str):
        """
        Save fetched data to cache for future use.

        Parameters
        ----------
        df : pd.DataFrame
            Data to save
        data_type : str
            One of: 'bea_iip', 'bea_ita', 'treasury', 'corp_equities'
        """
        cache_paths = {
            'bea_iip': FLOW_OF_FUNDS_PATH / "BEA_IIP" / "bea_iip_data.csv",
            'bea_ita': FLOW_OF_FUNDS_PATH / "BEA_ITA" / "bea_ita_table1_2_data.csv",
            'treasury': FLOW_OF_FUNDS_PATH / "Treasury_Ownership" / "treasury_ownership_data.csv",
            'corp_equities': FLOW_OF_FUNDS_PATH / "Corporate_Equities" / "corp_equities_data.csv"
        }

        if data_type not in cache_paths:
            raise ValueError(f"Unknown data_type: {data_type}")

        cache_path = cache_paths[data_type]
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(cache_path, index=False)
        print(f"[SAVED] Cached to {cache_path.relative_to(PROJECT_ROOT)}")


def main():
    """Example usage of FREDLoader."""
    print("\n" + "=" * 80)
    print("FRED Data Loader - Example Usage")
    print("=" * 80)

    # Initialize loader (uses cache by default)
    loader = FREDLoader(use_cache=True)

    # Load BEA IIP data
    print("\n1. Loading BEA International Investment Position data...")
    iip = loader.load_bea_iip()
    print(f"   Shape: {iip.shape}")
    print(f"   Date range: {iip['date'].min()} to {iip['date'].max()}")
    print(f"   Series count: {iip['series_id'].nunique()}")

    # Load BEA ITA data
    print("\n2. Loading BEA International Transaction Accounts data...")
    ita = loader.load_bea_ita()
    print(f"   Shape: {ita.shape}")
    print(f"   Date range: {ita['date'].min()} to {ita['date'].max()}")
    print(f"   Series count: {ita['series_id'].nunique()}")

    # Load Treasury ownership
    print("\n3. Loading Treasury ownership data...")
    treasury = loader.load_treasury_ownership()
    print(f"   Shape: {treasury.shape}")
    print(f"   Date range: {treasury['date'].min()} to {treasury['date'].max()}")
    print(f"   Series count: {treasury['series_id'].nunique()}")

    print("\n" + "=" * 80)
    print("Example complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
