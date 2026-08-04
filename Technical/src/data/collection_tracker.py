"""
Data Collection Tracker
=======================

Intelligent tracker to avoid re-polling APIs and track collection history.

Maintains metadata on:
- What has been collected
- When it was collected
- Collection status
- Data freshness
- Source coverage

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
TRACKER_FILE = OUTPUT_ROOT / "COLLECTION_METADATA" / "collection_tracker.json"
TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)


class CollectionTracker:
    """
    Track data collection history to avoid redundant API calls.

    Maintains JSON metadata file tracking:
    - Collections by source, country, indicator, time period
    - Last collection date
    - Number of observations
    - File locations
    """

    def __init__(self):
        """Initialize collection tracker."""
        self.tracker_file = TRACKER_FILE
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load existing metadata or create new."""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'collections': {}
            }

    def _save_metadata(self):
        """Save metadata to JSON file."""
        self.metadata['last_updated'] = datetime.now().isoformat()
        with open(self.tracker_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def get_collection_key(self, source: str, country: str, indicator: str,
                          start_year: int, end_year: int) -> str:
        """
        Generate unique key for collection.

        Parameters
        ----------
        source : str
            Data source (e.g., 'WorldBank', 'Banxico', 'OECD')
        country : str
            Country code
        indicator : str
            Indicator code
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        str
            Unique collection key
        """
        return f"{source}_{country}_{indicator}_{start_year}_{end_year}"

    def is_collected(self, source: str, country: str, indicator: str,
                    start_year: int, end_year: int) -> bool:
        """
        Check if data has already been collected.

        Parameters
        ----------
        source : str
            Data source
        country : str
            Country code
        indicator : str
            Indicator code
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        bool
            True if already collected
        """
        key = self.get_collection_key(source, country, indicator, start_year, end_year)
        return key in self.metadata['collections']

    def record_collection(self, source: str, country: str, indicator: str,
                         start_year: int, end_year: int,
                         observations: int, file_path: str,
                         success: bool = True, error: Optional[str] = None):
        """
        Record a data collection.

        Parameters
        ----------
        source : str
            Data source
        country : str
            Country code
        indicator : str
            Indicator code
        start_year : int
            Start year
        end_year : int
            End year
        observations : int
            Number of observations collected
        file_path : str
            Path to saved file
        success : bool
            Whether collection succeeded
        error : str, optional
            Error message if failed
        """
        key = self.get_collection_key(source, country, indicator, start_year, end_year)

        self.metadata['collections'][key] = {
            'source': source,
            'country': country,
            'indicator': indicator,
            'start_year': start_year,
            'end_year': end_year,
            'observations': observations,
            'file_path': file_path,
            'success': success,
            'error': error,
            'collected_at': datetime.now().isoformat()
        }

        self._save_metadata()

    def get_missing_indicators(self, source: str, country: str,
                              all_indicators: List[str],
                              start_year: int, end_year: int) -> List[str]:
        """
        Get list of indicators not yet collected for a country.

        Parameters
        ----------
        source : str
            Data source
        country : str
            Country code
        all_indicators : list
            List of all possible indicators
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        list
            List of indicators not yet collected
        """
        missing = []
        for indicator in all_indicators:
            if not self.is_collected(source, country, indicator, start_year, end_year):
                missing.append(indicator)
        return missing

    def get_missing_countries(self, source: str, indicator: str,
                             all_countries: List[str],
                             start_year: int, end_year: int) -> List[str]:
        """
        Get list of countries not yet collected for an indicator.

        Parameters
        ----------
        source : str
            Data source
        indicator : str
            Indicator code
        all_countries : list
            List of all possible countries
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        list
            List of countries not yet collected
        """
        missing = []
        for country in all_countries:
            if not self.is_collected(source, country, indicator, start_year, end_year):
                missing.append(country)
        return missing

    def get_collection_summary(self, source: Optional[str] = None) -> pd.DataFrame:
        """
        Get summary of all collections.

        Parameters
        ----------
        source : str, optional
            Filter by source

        Returns
        -------
        pd.DataFrame
            Summary of collections
        """
        collections = []

        for key, data in self.metadata['collections'].items():
            if source is None or data['source'] == source:
                collections.append(data)

        if collections:
            return pd.DataFrame(collections)
        else:
            return pd.DataFrame()

    def get_data_freshness(self, days_threshold: int = 30) -> Dict[str, List[str]]:
        """
        Identify stale data that needs updating.

        Parameters
        ----------
        days_threshold : int
            Number of days before data considered stale

        Returns
        -------
        dict
            Dictionary with 'fresh' and 'stale' lists
        """
        from datetime import timedelta

        now = datetime.now()
        fresh = []
        stale = []

        for key, data in self.metadata['collections'].items():
            collected_at = datetime.fromisoformat(data['collected_at'])
            age_days = (now - collected_at).days

            if age_days <= days_threshold:
                fresh.append(key)
            else:
                stale.append(key)

        return {
            'fresh': fresh,
            'stale': stale,
            'fresh_count': len(fresh),
            'stale_count': len(stale),
            'total_count': len(fresh) + len(stale)
        }

    def suggest_updates(self, max_age_days: int = 30) -> List[Dict]:
        """
        Suggest which data sources should be updated.

        Parameters
        ----------
        max_age_days : int
            Maximum age before suggesting update

        Returns
        -------
        list
            List of suggested updates
        """
        from datetime import timedelta

        now = datetime.now()
        suggestions = []

        for key, data in self.metadata['collections'].items():
            collected_at = datetime.fromisoformat(data['collected_at'])
            age_days = (now - collected_at).days

            if age_days > max_age_days and data['success']:
                suggestions.append({
                    'source': data['source'],
                    'country': data['country'],
                    'indicator': data['indicator'],
                    'last_collected': data['collected_at'],
                    'age_days': age_days,
                    'priority': 'High' if age_days > 60 else 'Medium'
                })

        # Sort by age (oldest first)
        suggestions.sort(key=lambda x: x['age_days'], reverse=True)

        return suggestions

    def export_summary_report(self, output_path: Optional[Path] = None):
        """
        Export summary report to markdown.

        Parameters
        ----------
        output_path : Path, optional
            Output file path
        """
        if output_path is None:
            output_path = OUTPUT_ROOT / "COLLECTION_METADATA" / "collection_summary.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get summary stats
        summary = self.get_collection_summary()
        freshness = self.get_data_freshness()

        report = f"""# Data Collection Tracker - Summary Report

**Generated**: {datetime.now().strftime('%B %d, %Y at %H:%M')}
**Tracker Version**: {self.metadata['version']}
**Last Updated**: {self.metadata['last_updated']}

---

## Overall Statistics

- **Total Collections**: {len(self.metadata['collections'])}
- **Successful**: {len(summary[summary['success'] == True]) if len(summary) > 0 else 0}
- **Failed**: {len(summary[summary['success'] == False]) if len(summary) > 0 else 0}
- **Fresh Data (<30 days)**: {freshness['fresh_count']}
- **Stale Data (>30 days)**: {freshness['stale_count']}

---

## Collections by Source

"""

        if len(summary) > 0:
            by_source = summary.groupby('source').agg({
                'observations': 'sum',
                'country': 'nunique',
                'indicator': 'nunique'
            }).reset_index()

            by_source.columns = ['Source', 'Total Observations', 'Countries', 'Indicators']

            report += by_source.to_markdown(index=False)
        else:
            report += "No collections recorded yet.\n"

        report += """

---

## Recent Collections

"""

        if len(summary) > 0:
            # Sort by collected_at (as string timestamps sort correctly in ISO format)
            recent = summary.sort_values('collected_at', ascending=False).head(10)[['source', 'country', 'indicator', 'observations', 'collected_at', 'success']]
            report += recent.to_markdown(index=False)
        else:
            report += "No collections recorded yet.\n"

        # Save report
        with open(output_path, 'w') as f:
            f.write(report)

        print(f"Collection summary exported to: {output_path.relative_to(PROJECT_ROOT)}")


def main():
    """Test collection tracker."""
    tracker = CollectionTracker()

    print("\n" + "="*80)
    print("COLLECTION TRACKER - TEST")
    print("="*80)

    # Show summary
    summary = tracker.get_collection_summary()
    print(f"\nTotal collections tracked: {len(summary)}")

    if len(summary) > 0:
        print(f"\nCollections by source:")
        print(summary.groupby('source')['observations'].sum())

    # Export summary report
    tracker.export_summary_report()


if __name__ == "__main__":
    main()
