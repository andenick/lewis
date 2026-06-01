"""
Excel Compliance Validator and Fixer - Simple Version
====================================================

Fixes multi-sheet Excel files to comply with the one-sheet standard.

Author: Lewis Platform
Date: October 14, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

class ExcelComplianceFixer:
    """Validate and fix Excel one-sheet compliance violations."""

    def __init__(self, data_directory: Path = None):
        """Initialize the compliance fixer."""
        if data_directory is None:
            self.data_dir = Path(__file__).parent.parent.parent / "Output" / "Data"
        else:
            self.data_dir = Path(data_directory)

        self.violations = []
        self.fixes_applied = []

    def validate_all_excel_files(self) -> Dict[str, List[str]]:
        """Validate all Excel files for one-sheet compliance."""
        print("VALIDATING EXCEL ONE-SHEET COMPLIANCE")
        print("=" * 60)

        excel_files = list(self.data_dir.rglob("*.xlsx"))
        compliant_files = []
        violating_files = []

        for file_path in excel_files:
            try:
                xl = pd.ExcelFile(file_path)
                sheet_count = len(xl.sheet_names)

                if sheet_count == 1:
                    compliant_files.append(str(file_path))
                    print(f"COMPLIANT: {file_path.name} (1 sheet)")
                else:
                    violating_files.append(str(file_path))
                    self.violations.append({
                        'file': str(file_path),
                        'sheets': xl.sheet_names,
                        'count': sheet_count
                    })
                    print(f"VIOLATION: {file_path.name} ({sheet_count} sheets: {xl.sheet_names})")

            except Exception as e:
                print(f"ERROR reading {file_path.name}: {e}")
                violating_files.append(str(file_path))

        print("\n" + "=" * 60)
        print(f"SUMMARY: {len(compliant_files)} compliant, {len(violating_files)} violations")

        return {
            'compliant': compliant_files,
            'violations': violating_files
        }

    def fix_world_bank_gdp_file(self) -> bool:
        """Fix BoP_WBankGDP_NA.xlsx by splitting into 2 single-sheet files."""
        print("\nFIXING: BoP_WBankGDP_NA.xlsx")

        gdp_file = None
        for violation in self.violations:
            if 'BoP_WBankGDP_NA.xlsx' in violation['file']:
                gdp_file = Path(violation['file'])
                break

        if not gdp_file:
            print("BoP_WBankGDP_NA.xlsx not found in violations")
            return False

        try:
            xl = pd.ExcelFile(gdp_file)
            print(f"Found sheets: {xl.sheet_names}")

            for sheet_name in xl.sheet_names:
                df = pd.read_excel(gdp_file, sheet_name=sheet_name)

                if sheet_name.lower() in ['81000-0001', 'data', 'gdp_data']:
                    output_file = gdp_file.parent / "world_bank_gdp_data.xlsx"
                elif sheet_name.lower() in ['note', 'notes', 'metadata']:
                    output_file = gdp_file.parent / "world_bank_gdp_notes.xlsx"
                else:
                    safe_name = sheet_name.replace(' ', '_').replace('-', '_').lower()
                    output_file = gdp_file.parent / f"world_bank_gdp_{safe_name}.xlsx"

                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)

                print(f"Created: {output_file.name}")
                self.fixes_applied.append(f"Split {gdp_file.name} sheet '{sheet_name}' -> {output_file.name}")

            gdp_file.unlink()
            print(f"Removed original: {gdp_file.name}")
            self.fixes_applied.append(f"Removed original multi-sheet file: {gdp_file.name}")

            return True

        except Exception as e:
            print(f"Error fixing {gdp_file.name}: {e}")
            return False

    def fix_trade_analysis_file(self) -> bool:
        """Fix trade_analysis_results.xlsx by splitting into 4 themed files."""
        print("\nFIXING: trade_analysis_results.xlsx")

        trade_file = None
        for violation in self.violations:
            if 'trade_analysis_results.xlsx' in violation['file']:
                trade_file = Path(violation['file'])
                break

        if not trade_file:
            print("trade_analysis_results.xlsx not found in violations")
            return False

        try:
            xl = pd.ExcelFile(trade_file)
            print(f"Found sheets: {xl.sheet_names}")

            sheet_mappings = {
                'Data_Summary': 'trade_summary_statistics.xlsx',
                'US_Current_Account': 'us_current_account_analysis.xlsx',
                'US_Period_Stats': 'us_period_statistics.xlsx',
                'Cross_Country_Comparison': 'cross_country_comparison.xlsx'
            }

            for sheet_name in xl.sheet_names:
                df = pd.read_excel(trade_file, sheet_name=sheet_name)
                output_name = sheet_mappings.get(sheet_name, f"trade_analysis_{sheet_name.lower().replace(' ', '_')}.xlsx")
                output_file = trade_file.parent / output_name

                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)

                print(f"Created: {output_file.name}")
                self.fixes_applied.append(f"Split {trade_file.name} sheet '{sheet_name}' -> {output_file.name}")

            trade_file.unlink()
            print(f"Removed original: {trade_file.name}")
            self.fixes_applied.append(f"Removed original multi-sheet file: {trade_file.name}")

            return True

        except Exception as e:
            print(f"Error fixing {trade_file.name}: {e}")
            return False

    def run_full_fix(self) -> bool:
        """Run complete validation and fix process."""
        print("STARTING EXCEL COMPLIANCE FIX PROCESS")
        print("=" * 60)

        validation_results = self.validate_all_excel_files()

        if not validation_results['violations']:
            print("ALL FILES COMPLIANT - No fixes needed!")
            return True

        fixes_success = True

        if any('BoP_WBankGDP_NA.xlsx' in v for v in validation_results['violations']):
            success = self.fix_world_bank_gdp_file()
            fixes_success = fixes_success and success

        if any('trade_analysis_results.xlsx' in v for v in validation_results['violations']):
            success = self.fix_trade_analysis_file()
            fixes_success = fixes_success and success

        print("\nRE-VALIDATING AFTER FIXES...")
        print("=" * 60)

        self.violations.clear()
        final_results = self.validate_all_excel_files()

        print("\n" + "=" * 60)
        print("FIX SUMMARY")
        print("=" * 60)

        for fix in self.fixes_applied:
            print(f"* {fix}")

        if not final_results['violations']:
            print(f"\nSUCCESS: All {len(validation_results['violations'])} violations fixed!")
            print(f"{len(final_results['compliant']) + len(validation_results['violations'])} files now compliant")
            return True
        else:
            print(f"\nPARTIAL SUCCESS: {len(final_results['violations'])} violations remain")
            return False


def main():
    """Main execution function."""
    print("Excel Compliance Validator and Fixer")
    print("Lewis International Economics Platform Enhancement")
    print("=" * 60)

    fixer = ExcelComplianceFixer()
    success = fixer.run_full_fix()

    if success:
        print("\nALL EXCEL FILES NOW COMPLY WITH DRUCK STANDARDS!")
    else:
        print("\nSome issues remain - manual intervention may be needed")

    return success


if __name__ == "__main__":
    main()