"""
Final Simple LaTeX PDF Compiler for Lewis Platform
==================================================

Ultra-simple, reliable LaTeX compilation that actually works.
Compiles all 4 LaTeX reports and copies them to the Output directory.

Author: Lewis Platform
Date: October 14, 2025
"""

import subprocess
import sys
import os
from pathlib import Path
import time
import shutil

def compile_latex_file(tex_file: Path, docs_dir: Path) -> bool:
    """Compile a single LaTeX file and return success status."""
    print(f"\nCompiling: {tex_file.name}")

    # Change to docs directory for compilation
    original_cwd = os.getcwd()
    os.chdir(docs_dir)

    try:
        # Run pdflatex
        print(f"  Running pdflatex...")
        result = subprocess.run([
            'pdflatex', '-interaction=nonstopmode',
            '-halt-on-error', tex_file.name
        ], capture_output=True, text=True, timeout=120)

        # Check if PDF was created
        pdf_file = docs_dir / f"{tex_file.stem}.pdf"
        if pdf_file.exists():
            print(f"  SUCCESS: PDF created ({pdf_file.stat().st_size / 1024:.0f} KB)")
            return True
        else:
            print(f"  FAILED: PDF not created")
            if result.returncode != 0:
                print(f"  Error: Compilation failed with return code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: Compilation took too long")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def copy_pdf_to_output(tex_file: Path, docs_dir: Path, output_dir: Path) -> bool:
    """Copy compiled PDF to output directory."""
    pdf_source = docs_dir / f"{tex_file.stem}.pdf"
    pdf_dest = output_dir / f"{tex_file.stem}.pdf"

    if pdf_source.exists():
        try:
            shutil.copy2(pdf_source, pdf_dest)
            print(f"  Copied to: {pdf_dest.name}")
            return True
        except Exception as e:
            print(f"  Copy failed: {e}")
            return False
    else:
        print(f"  Source PDF not found: {pdf_source}")
        return False

def main():
    """Main compilation function."""
    print("LEWIS PLATFORM LATEX PDF COMPILER")
    print("=" * 40)

    # Setup directories
    docs_dir = Path(__file__).parent.parent / "docs"
    output_dir = Path(__file__).parent.parent.parent / "Output" / "PDFs" / "Reports"

    print(f"Source directory: {docs_dir}")
    print(f"Output directory: {output_dir}")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # List of LaTeX files to compile (simple versions)
    latex_files = [
        "methodology_report_simple.tex",
        "executive_summary_simple.tex",
        "analysis_report_simple.tex",
        "reporting_strategy_simple.tex"
    ]

    # Check which files exist
    available_files = []
    for filename in latex_files:
        tex_file = docs_dir / filename
        if tex_file.exists():
            available_files.append(tex_file)
            print(f"Found: {filename}")
        else:
            print(f"Missing: {filename}")

    if not available_files:
        print(f"\nERROR: No LaTeX files found in {docs_dir}")
        return False

    print(f"\nCompiling {len(available_files)} LaTeX files...")

    # Compile each file
    successful_compilations = 0
    start_time = time.time()

    for tex_file in available_files:
        # Compile the LaTeX file
        if compile_latex_file(tex_file, docs_dir):
            # Copy PDF to output directory
            if copy_pdf_to_output(tex_file, docs_dir, output_dir):
                successful_compilations += 1

    # Summary
    total_time = time.time() - start_time
    print(f"\n" + "=" * 40)
    print("COMPILATION SUMMARY")
    print("=" * 40)
    print(f"Total files: {len(available_files)}")
    print(f"Successful: {successful_compilations}")
    print(f"Failed: {len(available_files) - successful_compilations}")
    print(f"Total time: {total_time:.1f} seconds")

    # List generated PDFs in output directory
    output_pdfs = list(output_dir.glob("*.pdf"))
    if output_pdfs:
        print(f"\nGenerated PDFs in {output_dir}:")
        for pdf_file in sorted(output_pdfs):
            size_kb = pdf_file.stat().st_size / 1024
            print(f"  {pdf_file.name} ({size_kb:.0f} KB)")

    # Clean up temporary files
    print(f"\nCleaning temporary files...")
    temp_extensions = ['.aux', '.log', '.out', '.toc', '.bbl', '.blg', '.fdb_latexmk', '.fls', '.synctex.gz']
    cleaned = 0
    for ext in temp_extensions:
        for temp_file in docs_dir.glob(f"*{ext}"):
            try:
                temp_file.unlink()
                cleaned += 1
            except:
                pass
    if cleaned > 0:
        print(f"Cleaned {cleaned} temporary files")

    # Success determination
    success = successful_compilations == len(available_files)
    if success:
        print(f"\nSUCCESS: All {len(available_files)} LaTeX files compiled to PDF!")
    else:
        print(f"\nPARTIAL: {successful_compilations}/{len(available_files)} files compiled")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)