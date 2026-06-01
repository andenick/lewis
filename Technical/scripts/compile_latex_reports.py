"""
LaTeX PDF Compiler for Lewis Platform Reports
=============================================

Automated compilation of LaTeX report templates into professional PDFs.
Ensures consistent formatting and handles compilation errors gracefully.

Author: Lewis Platform
Date: October 14, 2025
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import time
import shutil

class LatexPDFCompiler:
    """Automated LaTeX PDF compilation with error handling and validation."""

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

        self.compilation_results = []
        self.required_reports = [
            "methodology_report.tex",
            "executive_summary.tex",
            "analysis_report.tex",
            "reporting_strategy.tex"
        ]

    def check_latex_installation(self) -> Tuple[bool, str]:
        """Check if LaTeX (pdflatex) is installed and accessible."""
        try:
            result = subprocess.run(['pdflatex', '--version'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return True, f"LaTeX found: {version_line}"
            else:
                return False, "pdflatex command failed"
        except FileNotFoundError:
            return False, "pdflatex not found - LaTeX installation required"
        except subprocess.TimeoutExpired:
            return False, "LaTeX check timed out"
        except Exception as e:
            return False, f"Error checking LaTeX: {e}"

    def ensure_output_directory(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {self.output_dir}")

    def compile_single_latex(self, tex_file: Path, max_runs: int = 3) -> Dict:
        """Compile a single LaTeX file to PDF."""
        result = {
            'file': tex_file.name,
            'success': False,
            'pdf_path': None,
            'error': None,
            'warnings': [],
            'compilation_time': 0
        }

        start_time = time.time()

        if not tex_file.exists():
            result['error'] = f"LaTeX file not found: {tex_file}"
            return result

        # Create temporary working directory
        temp_dir = tex_file.parent / "temp_compilation"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Copy LaTeX file to temp directory
            temp_tex = temp_dir / tex_file.name
            shutil.copy2(tex_file, temp_tex)

            # Change to temp directory for compilation
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            print(f"\nCompiling: {tex_file.name}")

            for run in range(max_runs):
                print(f"  Run {run + 1}/{max_runs}...")

                # Run pdflatex with silent mode for cleaner output
                process = subprocess.run([
                    'pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                    '-file-line-error', temp_tex.name
                ], capture_output=True, text=True, timeout=60)

                # Check for fatal errors
                if process.returncode != 0:
                    error_output = process.stderr if process.stderr else process.stdout
                    if "Fatal error" in error_output or "Error:" in error_output:
                        result['error'] = f"LaTeX compilation failed: {error_output[:500]}"
                        break
                    else:
                        # Non-fatal errors might be warnings
                        result['warnings'].append(f"Run {run + 1}: {error_output[:200]}")

                # Check if PDF was created
                pdf_file = temp_dir / f"{tex_file.stem}.pdf"
                if pdf_file.exists():
                    result['success'] = True
                    result['pdf_path'] = pdf_file
                    break

            # Copy PDF to output directory if successful
            if result['success'] and result['pdf_path']:
                final_pdf = self.output_dir / f"{tex_file.stem}.pdf"
                shutil.copy2(result['pdf_path'], final_pdf)
                result['final_pdf_path'] = final_pdf
                print(f"  SUCCESS: PDF created: {final_pdf.name}")
            else:
                print(f"  FAILED: Could not create PDF")

        except subprocess.TimeoutExpired:
            result['error'] = "LaTeX compilation timed out (60 seconds)"
        except Exception as e:
            result['error'] = f"Compilation error: {e}"
        finally:
            os.chdir(original_cwd)
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        result['compilation_time'] = time.time() - start_time
        return result

    def compile_all_reports(self) -> Dict:
        """Compile all required LaTeX reports."""
        print("LATEX PDF COMPILATION FOR LEWIS PLATFORM")
        print("=" * 60)

        # Check LaTeX installation
        latex_ok, latex_msg = self.check_latex_installation()
        print(f"LaTeX Check: {latex_msg}")

        if not latex_ok:
            print(f"\nERROR: {latex_msg}")
            print("Please install a LaTeX distribution (MiKTeX, TeX Live, MacTeX)")
            return {'success': False, 'error': latex_msg}

        # Ensure output directory exists
        self.ensure_output_directory()

        # Find all LaTeX files
        available_files = []
        for report_name in self.required_reports:
            tex_file = self.docs_dir / report_name
            if tex_file.exists():
                available_files.append(tex_file)
            else:
                print(f"Warning: {report_name} not found in {self.docs_dir}")

        if not available_files:
            print("ERROR: No LaTeX files found to compile")
            return {'success': False, 'error': 'No LaTeX files found'}

        print(f"\nFound {len(available_files)} LaTeX files to compile")

        # Compile each file
        successful_compilations = 0
        total_compilation_time = 0

        for tex_file in available_files:
            result = self.compile_single_latex(tex_file)
            self.compilation_results.append(result)

            if result['success']:
                successful_compilations += 1
                print(f"SUCCESS: {tex_file.name} -> {result.get('final_pdf_path', 'Unknown')}")
                if result['warnings']:
                    print(f"  Warnings: {len(result['warnings'])}")
            else:
                print(f"FAILED: {tex_file.name} -> COMPILATION ERROR")
                if result['error']:
                    print(f"  Error: {result['error'][:100]}...")

            total_compilation_time += result['compilation_time']

        # Summary
        print(f"\n" + "=" * 60)
        print("COMPILATION SUMMARY")
        print("=" * 60)
        print(f"Total files processed: {len(available_files)}")
        print(f"Successful compilations: {successful_compilations}")
        print(f"Failed compilations: {len(available_files) - successful_compilations}")
        print(f"Total compilation time: {total_compilation_time:.1f} seconds")

        if successful_compilations == len(available_files):
            print(f"\nSUCCESS: All {len(available_files)} reports compiled to PDF!")
            print(f"PDFs saved to: {self.output_dir}")
            return {
                'success': True,
                'compiled': successful_compilations,
                'total': len(available_files),
                'output_dir': self.output_dir
            }
        else:
            print(f"\nPARTIAL SUCCESS: {successful_compilations}/{len(available_files)} files compiled")
            return {
                'success': False,
                'compiled': successful_compilations,
                'total': len(available_files),
                'failed_results': [r for r in self.compilation_results if not r['success']]
            }

    def list_output_pdfs(self) -> List[Path]:
        """List all PDF files in the output directory."""
        if not self.output_dir.exists():
            return []

        pdf_files = list(self.output_dir.glob("*.pdf"))
        return sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True)

    def generate_compilation_report(self) -> str:
        """Generate a detailed compilation report."""
        report = ["LATEX COMPILATION REPORT", "=" * 50]

        for result in self.compilation_results:
            report.append(f"\nFile: {result['file']}")
            report.append(f"Success: {result['success']}")

            if result['success']:
                if 'final_pdf_path' in result:
                    report.append(f"PDF: {result['final_pdf_path'].name}")
                report.append(f"Compilation time: {result['compilation_time']:.1f}s")
            else:
                report.append(f"Error: {result['error']}")

            if result['warnings']:
                report.append(f"Warnings: {len(result['warnings'])}")
                for warning in result['warnings'][:3]:  # Show first 3 warnings
                    report.append(f"  - {warning}")

        return "\n".join(report)


def main():
    """Main execution function."""
    print("Lewis Platform LaTeX PDF Compiler")
    print("Lewis Platform")
    print("=" * 60)

    compiler = LatexPDFCompiler()
    results = compiler.compile_all_reports()

    # List generated PDFs
    pdf_files = compiler.list_output_pdfs()
    if pdf_files:
        print(f"\nGenerated PDF files ({len(pdf_files)}):")
        for pdf_file in pdf_files:
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"  {pdf_file.name} ({size_mb:.1f} MB)")

    # Detailed report
    print(f"\n{compiler.generate_compilation_report()}")

    return results['success']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)