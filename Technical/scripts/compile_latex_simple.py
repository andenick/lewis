"""
Simple LaTeX PDF Compiler for Lewis Platform Reports
===================================================

Simplified LaTeX compilation that handles cross-references properly.
Focuses on reliability and clear success/failure reporting.

Author: Lewis Platform
Date: October 14, 2025
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List
import time

class SimpleLatexCompiler:
    """Simple and reliable LaTeX PDF compilation."""

    def __init__(self, docs_dir: Path = None, output_dir: Path = None):
        """Initialize the LaTeX compiler."""
        if docs_dir is None:
            self.docs_dir = Path(__file__).parent.parent / "docs"
        else:
            self.docs_dir = Path(docs_dir)

        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent.parent / "Output" / "PDFs" / "Reports"
        else:
            self.output_dir = Path(output_dir)

        self.required_reports = [
            "methodology_report.tex",
            "executive_summary.tex",
            "analysis_report.tex",
            "reporting_strategy.tex"
        ]

    def ensure_output_directory(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {self.output_dir}")

    def compile_latex_simple(self, tex_file: Path) -> Dict:
        """Compile LaTeX file with simple approach."""
        result = {
            'file': tex_file.name,
            'success': False,
            'pdf_created': False,
            'error': None,
            'start_time': time.time()
        }

        try:
            # Change to docs directory
            original_cwd = os.getcwd()
            os.chdir(self.docs_dir)

            print(f"\nCompiling: {tex_file.name}")

            # Run pdflatex twice for cross-references
            for run_num in [1, 2]:
                print(f"  Run {run_num}/2...")

                process = subprocess.run([
                    'pdflatex', '-interaction=nonstopmode',
                    '-halt-on-error', tex_file.name
                ], capture_output=True, text=True, timeout=120)

                # Check if PDF was created after this run
                pdf_file = self.docs_dir / f"{tex_file.stem}.pdf"
                if pdf_file.exists():
                    result['pdf_created'] = True
                    print(f"    PDF created successfully")
                    break

            # Copy PDF to output directory if created
            if result['pdf_created']:
                pdf_source = self.docs_dir / f"{tex_file.stem}.pdf"
                pdf_dest = self.output_dir / f"{tex_file.stem}.pdf"

                import shutil
                shutil.copy2(pdf_source, pdf_dest)

                result['success'] = True
                print(f"  SUCCESS: PDF copied to {pdf_dest.name}")
            else:
                result['error'] = "PDF was not created after compilation attempts"
                print(f"  FAILED: PDF not created")

        except subprocess.TimeoutExpired:
            result['error'] = "Compilation timed out (120 seconds)"
            print(f"  TIMEOUT: Compilation too slow")
        except Exception as e:
            result['error'] = f"Compilation error: {str(e)}"
            print(f"  ERROR: {e}")
        finally:
            os.chdir(original_cwd)

        result['duration'] = time.time() - result['start_time']
        return result

    def compile_all_reports(self) -> Dict:
        """Compile all LaTeX reports."""
        print("SIMPLE LATEX PDF COMPILER - LEWIS PLATFORM")
        print("=" * 55)

        self.ensure_output_directory()

        # Find available LaTeX files
        available_files = []
        for report_name in self.required_reports:
            tex_file = self.docs_dir / report_name
            if tex_file.exists():
                available_files.append(tex_file)
                print(f"Found: {report_name}")
            else:
                print(f"Missing: {report_name}")

        if not available_files:
            print("\nERROR: No LaTeX files found!")
            return {'success': False, 'error': 'No files found'}

        print(f"\nCompiling {len(available_files)} files...")

        # Compile each file
        results = []
        successful = 0

        for tex_file in available_files:
            result = self.compile_latex_simple(tex_file)
            results.append(result)

            if result['success']:
                successful += 1

        # Summary
        print(f"\n" + "=" * 55)
        print("COMPILATION SUMMARY")
        print("=" * 55)
        print(f"Total files: {len(available_files)}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(available_files) - successful}")

        total_time = sum(r['duration'] for r in results)
        print(f"Total time: {total_time:.1f} seconds")

        # List generated PDFs
        pdf_files = list(self.output_dir.glob("*.pdf"))
        if pdf_files:
            print(f"\nGenerated PDF files:")
            for pdf_file in sorted(pdf_files):
                size_kb = pdf_file.stat().st_size / 1024
                print(f"  {pdf_file.name} ({size_kb:.0f} KB)")

        success_all = successful == len(available_files)
        if success_all:
            print(f"\nSUCCESS: All {len(available_files)} LaTeX files compiled to PDF!")
        else:
            print(f"\nPARTIAL: {successful}/{len(available_files)} files compiled successfully")

        return {
            'success': success_all,
            'compiled': successful,
            'total': len(available_files),
            'results': results
        }

    def clean_temp_files(self):
        """Clean up temporary LaTeX files."""
        temp_extensions = ['.aux', '.log', '.out', '.toc', '.bbl', '.blg', '.fdb_latexmk', '.fls', '.synctex.gz']

        cleaned = 0
        for ext in temp_extensions:
            for temp_file in self.docs_dir.glob(f"*{ext}"):
                try:
                    temp_file.unlink()
                    cleaned += 1
                except:
                    pass

        if cleaned > 0:
            print(f"Cleaned {cleaned} temporary files")


def main():
    """Main execution function."""
    compiler = SimpleLatexCompiler()

    try:
        results = compiler.compile_all_reports()

        # Clean up temporary files
        print(f"\nCleaning temporary files...")
        compiler.clean_temp_files()

        return results['success']

    except KeyboardInterrupt:
        print("\nCompilation interrupted by user")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)