"""
ClassFiles Cataloging System
=============================

Automatically catalogs and processes ClassFiles related to cross-border value transfers.

This script:
1. Scans ClassFiles directories
2. Identifies file types and extracts metadata
3. Categorizes by flow type (Flow of Funds, Capital Flows, Remittances, etc.)
4. Identifies data sources mentioned in documents
5. Generates comprehensive catalog report
6. Suggests data extraction opportunities

Author: Claude
Date: 2025-10-06
"""

import os
from pathlib import Path
from datetime import datetime
import csv
import json
from typing import Dict, List, Tuple
import re

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CLASSFILES = PROJECT_ROOT / "ClassFiles"
OUTPUT_DATA = PROJECT_ROOT / "Output" / "Data"
TECHNICAL_DATA = PROJECT_ROOT / "Technical" / "data"


class ClassFilesCatalog:
    """Catalog and process ClassFiles for cross-border value transfers."""

    def __init__(self):
        self.classfiles_path = CLASSFILES
        self.catalog = []
        self.data_sources = set()
        self.flow_types = {
            'Flow_of_Funds': [],
            'Capital_Flows': [],
            'Remittances': [],
            'Banking_Flows': [],
            'Other': []
        }

        # Known data source patterns to look for
        self.source_patterns = {
            'IMF': ['imf', 'international monetary fund', 'bpm6', 'bpm5'],
            'BIS': ['bis', 'bank for international settlements', 'banking statistics'],
            'OECD': ['oecd', 'organisation for economic'],
            'World Bank': ['world bank', 'wdi', 'wits'],
            'FRED': ['fred', 'federal reserve', 'alfred'],
            'BEA': ['bea', 'bureau of economic analysis'],
            'Eurostat': ['eurostat'],
            'UN': ['united nations', 'comtrade', 'unctad'],
            'WTO': ['wto', 'world trade organization'],
        }

    def scan_directory(self, directory: Path = None) -> List[Dict]:
        """Recursively scan ClassFiles directory and catalog all files."""
        if directory is None:
            directory = self.classfiles_path

        if not directory.exists():
            print(f"[WARNING] ClassFiles directory not found: {directory}")
            return []

        print(f"\n[SCANNING] {directory}")
        print("=" * 80)

        for item in directory.rglob('*'):
            if item.is_file():
                file_info = self._process_file(item)
                if file_info:
                    self.catalog.append(file_info)

                    # Categorize by directory
                    for flow_type in self.flow_types.keys():
                        if flow_type in str(item.parent):
                            self.flow_types[flow_type].append(file_info)
                            break

        return self.catalog

    def _process_file(self, file_path: Path) -> Dict:
        """Process individual file and extract metadata."""
        try:
            stat = file_path.stat()

            # Basic file info
            file_info = {
                'filename': file_path.name,
                'path': str(file_path.relative_to(PROJECT_ROOT)),
                'absolute_path': str(file_path),
                'extension': file_path.suffix.lower(),
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'category': self._categorize_file(file_path),
                'potential_sources': self._identify_sources(file_path),
                'is_data': self._is_data_file(file_path),
                'is_documentation': self._is_documentation(file_path),
            }

            # Additional processing based on file type
            if file_info['is_data']:
                file_info['data_info'] = self._extract_data_info(file_path)

            print(f"[OK] {file_path.name} ({file_info['size_mb']} MB) - {file_info['category']}")

            return file_info

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path.name}: {e}")
            return None

    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on name and location."""
        name_lower = file_path.name.lower()
        parent_lower = str(file_path.parent).lower()

        # Check parent directory first
        if 'flow_of_funds' in parent_lower or 'flow of funds' in parent_lower:
            return 'Flow of Funds'
        elif 'capital_flows' in parent_lower or 'capital flows' in parent_lower:
            return 'Capital Flows'
        elif 'remittance' in parent_lower:
            return 'Remittances'
        elif 'banking' in parent_lower:
            return 'Banking Flows'

        # Check filename for keywords
        keywords = {
            'FDI': 'Capital Flows - FDI',
            'portfolio': 'Capital Flows - Portfolio',
            'remittance': 'Remittances',
            'banking': 'Banking Flows',
            'reserves': 'Capital Flows - Reserves',
            'balance of payments': 'Balance of Payments',
            'bop': 'Balance of Payments',
            'current account': 'Current Account',
            'trade': 'Trade Flows',
            'oda': 'Official Development Assistance',
            'aid': 'Official Development Assistance',
        }

        for keyword, category in keywords.items():
            if keyword in name_lower:
                return category

        return 'Other'

    def _identify_sources(self, file_path: Path) -> List[str]:
        """Identify potential data sources mentioned in filename or path."""
        text = f"{file_path.name} {file_path.parent}".lower()
        sources = []

        for source_name, patterns in self.source_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    sources.append(source_name)
                    self.data_sources.add(source_name)
                    break

        return sources

    def _is_data_file(self, file_path: Path) -> bool:
        """Check if file is likely a data file."""
        data_extensions = {'.csv', '.xlsx', '.xls', '.dta', '.sas7bdat', '.rds', '.feather', '.parquet'}
        return file_path.suffix.lower() in data_extensions

    def _is_documentation(self, file_path: Path) -> bool:
        """Check if file is documentation."""
        doc_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.html'}
        return file_path.suffix.lower() in doc_extensions

    def _extract_data_info(self, file_path: Path) -> Dict:
        """Extract basic information from data files."""
        info = {'type': file_path.suffix.lower()}

        try:
            if file_path.suffix.lower() == '.csv':
                # Quick peek at CSV structure
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read first few lines
                    lines = [next(f) for _ in range(min(5, sum(1 for _ in f) + 5))]
                    if lines:
                        header = lines[0].strip().split(',')
                        info['columns'] = len(header)
                        info['sample_columns'] = header[:10]  # First 10 columns
                        info['estimated_rows'] = sum(1 for _ in open(file_path, 'r', encoding='utf-8', errors='ignore')) - 1

            elif file_path.suffix.lower() in {'.xlsx', '.xls'}:
                # Would need openpyxl or pandas to read
                info['note'] = 'Excel file - requires pandas/openpyxl to read'

        except Exception as e:
            info['error'] = str(e)

        return info

    def generate_report(self, output_file: Path = None) -> str:
        """Generate comprehensive catalog report."""
        if output_file is None:
            output_file = OUTPUT_DATA / "CLASSFILES_CATALOG.md"

        # Sort catalog by category and filename
        sorted_catalog = sorted(self.catalog, key=lambda x: (x['category'], x['filename']))

        report = []
        report.append("# ClassFiles Catalog Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal Files: {len(self.catalog)}")
        report.append(f"Total Size: {sum(f['size_mb'] for f in self.catalog):.2f} MB")
        report.append("\n" + "=" * 80)

        # Summary by category
        report.append("\n## Summary by Category\n")
        category_stats = {}
        for item in self.catalog:
            cat = item['category']
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'size_mb': 0, 'data_files': 0, 'docs': 0}
            category_stats[cat]['count'] += 1
            category_stats[cat]['size_mb'] += item['size_mb']
            if item['is_data']:
                category_stats[cat]['data_files'] += 1
            if item['is_documentation']:
                category_stats[cat]['docs'] += 1

        report.append("| Category | Files | Data Files | Docs | Size (MB) |")
        report.append("|----------|-------|------------|------|-----------|")
        for cat, stats in sorted(category_stats.items()):
            report.append(f"| {cat} | {stats['count']} | {stats['data_files']} | {stats['docs']} | {stats['size_mb']:.2f} |")

        # Data sources identified
        report.append(f"\n## Data Sources Identified\n")
        if self.data_sources:
            report.append("Files mention the following data sources:\n")
            for source in sorted(self.data_sources):
                count = sum(1 for f in self.catalog if source in f['potential_sources'])
                report.append(f"- **{source}**: {count} file(s)")
        else:
            report.append("No known data sources identified in filenames.")

        # Detailed file listing
        report.append("\n## Detailed File Listing\n")

        current_category = None
        for item in sorted_catalog:
            if item['category'] != current_category:
                current_category = item['category']
                report.append(f"\n### {current_category}\n")

            report.append(f"**{item['filename']}** ({item['size_mb']} MB)")
            report.append(f"- Path: `{item['path']}`")
            report.append(f"- Type: {item['extension']}")
            report.append(f"- Modified: {item['modified']}")

            if item['potential_sources']:
                report.append(f"- Sources: {', '.join(item['potential_sources'])}")

            if item['is_data'] and 'data_info' in item:
                data_info = item['data_info']
                if 'columns' in data_info:
                    report.append(f"- Data: {data_info['estimated_rows']:,} rows × {data_info['columns']} columns")
                    if 'sample_columns' in data_info:
                        report.append(f"- Sample columns: {', '.join(data_info['sample_columns'][:5])}")

            report.append("")

        # Recommendations
        report.append("\n## Recommendations\n")
        report.append("### Data Extraction Opportunities\n")

        data_files = [f for f in self.catalog if f['is_data']]
        if data_files:
            report.append(f"Found {len(data_files)} data files ready for processing:\n")
            for df in data_files[:10]:  # Show first 10
                report.append(f"- {df['filename']} ({df['category']})")
            if len(data_files) > 10:
                report.append(f"- ... and {len(data_files) - 10} more")

        report.append("\n### Next Steps\n")
        report.append("1. Review documentation files to understand data structure")
        report.append("2. Extract data from identified CSV/Excel files")
        report.append("3. Cross-reference with known data sources (IMF, BIS, OECD, etc.)")
        report.append("4. Integrate into data source following established patterns")
        report.append("5. Document data provenance and methodology alignment")

        # Write report
        report_text = '\n'.join(report)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"\n[OK] Catalog report written to: {output_file}")
        return report_text

    def export_json(self, output_file: Path = None):
        """Export catalog as JSON for programmatic access."""
        if output_file is None:
            output_file = OUTPUT_DATA / "classfiles_catalog.json"

        catalog_json = {
            'generated': datetime.now().isoformat(),
            'total_files': len(self.catalog),
            'total_size_mb': sum(f['size_mb'] for f in self.catalog),
            'data_sources': sorted(list(self.data_sources)),
            'files': self.catalog,
            'by_category': {k: len(v) for k, v in self.flow_types.items()}
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog_json, f, indent=2)

        print(f"[OK] JSON catalog written to: {output_file}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("ClassFiles Cataloging System")
    print("=" * 80)

    catalog = ClassFilesCatalog()

    # Scan all ClassFiles
    print("\nScanning ClassFiles directories...")
    files_found = catalog.scan_directory()

    if not files_found:
        print("\n[WARNING] No files found in ClassFiles directory.")
        print(f"Expected location: {catalog.classfiles_path}")
        print("\nPlease add ClassFiles to one of these directories:")
        for flow_type in catalog.flow_types.keys():
            print(f"  - ClassFiles/{flow_type}/")
        return

    # Generate reports
    print(f"\n[OK] Found {len(files_found)} files")
    print("\nGenerating reports...")

    catalog.generate_report()
    catalog.export_json()

    print("\n" + "=" * 80)
    print("Cataloging Complete!")
    print("=" * 80)
    print(f"Files processed: {len(files_found)}")
    print(f"Data sources identified: {len(catalog.data_sources)}")
    print("\nCheck Output/Data/ for:")
    print("  - CLASSFILES_CATALOG.md (human-readable report)")
    print("  - classfiles_catalog.json (machine-readable data)")


if __name__ == "__main__":
    main()
