#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for LaTeX and bibTeX."""
from shutil import which
from pathlib import Path
import subprocess


def check_tex_commands_exist(latex_directory_path: Path) -> None:
    """Raise an exception if one of the latex commands is not present."""
    if which("bibtex") is None or which("pdflatex") is None:
        raise Exception("Error: It seems like latex is not available on your system.\n"
                        "You can install latex and run the command again, "
                        f"or copy the source files in {latex_directory_path} on your "
                        "local machine to generate the report.")


def compile_pdf(latex_files_path: Path, latex_report_filename: Path) -> Path:
    """Compile the given latex files to a PDF.

    Args:
        latex_files_path: Path to the directory with source files
            where the report will be generated.
        latex_report_filename: Name of the output files.

    Returns:
        Path to the newly generated report in PDF format.
    """
    pdf_process = subprocess.run(["pdflatex", "-interaction=nonstopmode",
                                 f"{latex_report_filename}.tex"],
                                 cwd=latex_files_path, capture_output=True)

    if pdf_process.returncode != 0:
        print(f"[{pdf_process.returncode}] ERROR generating with PDFLatex command:\n"
              f"{pdf_process.stdout.decode()}\n {pdf_process.stderr.decode()}\n")

    bibtex_process = subprocess.run(["bibtex", f"{latex_report_filename}.aux"],
                                    cwd=latex_files_path, capture_output=True)

    if bibtex_process.returncode != 0:
        print("ERROR whilst generating with Bibtex command:"
              f"{bibtex_process.stdout} {bibtex_process.stderr}")

    # TODO: Fix compilation for references
    # (~\ref[] yields [?] in pdf, re-running command fixes it)
    # We have to re-run the same pdf command to take in the updates bib files from bibtex
    # But Bibtex cannot function without .aux file produced by pdflatex. Hence run twice.
    pdf_process = subprocess.run(["pdflatex", "-interaction=nonstopmode",
                                 f"{latex_report_filename}.tex"],
                                 cwd=latex_files_path, capture_output=True)

    return Path(latex_files_path / latex_report_filename).with_suffix(".pdf")
