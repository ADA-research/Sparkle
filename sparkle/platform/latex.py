#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper classes/method for LaTeX and bibTeX."""
from shutil import which
from pathlib import Path
import subprocess
from enum import Enum


class ReportType(str, Enum):
    """enum for separating different types of reports."""
    ALGORITHM_SELECTION = "algorithm_selection"
    ALGORITHM_CONFIGURATION = "algorithm_configuration"
    PARALLEL_PORTFOLIO = "parallel_portfolio"


def check_tex_commands_exist(latex_directory_path: Path) -> None:
    """Raise an exception if one of the latex commands is not present."""
    if which("bibtex") is None or which("pdflatex") is None:
        raise Exception("Error: It seems like latex is not available on your system.\n"
                        "You can install latex and run the command again, "
                        f"or copy the source files in {latex_directory_path} on your "
                        "local machine to generate the report.")


def underscore_for_latex(string: str) -> str:
    """Return the input str with the underscores escaped for use in LaTeX.

    Args:
        string: A given str with underscores.

    Returns:
        The corresponding str with underscores escaped.
    """
    return string.replace("_", "\\_")


def get_directory_list(source: Path | list[Path]) -> str:
    """Get the Path names in a list for use in a LaTeX document.

    Args:
        source: The source directory or list of Paths

    Returns:
        The list of directory names as LaTeX str.
    """
    if isinstance(source, Path):
        source = [p for p in source.iterdir()]
    # Patching with Path(path) in case a list of str is given
    return "".join(f"\\item \\textbf{{{Path(path).name}}}\n"
                   for path in source)


def fill_template_tex(template_tex: str, variables: dict) -> str:
    """Given a latex template, replaces all the @@ variables using the dict.

    Args:
        template_tex: The template to be populated
        variables: Variable names (key) with their target (value)

    Returns:
        The populated latex string.
    """
    for variable_key, target_value in variables.items():
        variable = "@@" + variable_key + "@@"
        # We don't modify variable names in the Latex file
        if "\\includegraphics" not in target_value and "\\label" not in target_value:
            # Rectify underscores in target_value
            target_value = target_value.replace("_", r"\textunderscore ")
        template_tex = template_tex.replace(variable, target_value)
    return template_tex


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


def generate_report(latex_source_path: Path,
                    latex_template_name: str,
                    target_path: Path,
                    report_name: str,
                    variable_dict: dict) -> None:
    """General steps to generate a report.

    Args:
        latex_source_path: The path to the template
        latex_template_name: The template name
        target_path: The directory where the result should be placed
        report_name: The name of the pdf (without suffix)
        variable_dict: TBD
    """
    latex_template_filepath = latex_source_path / latex_template_name

    report_content = latex_template_filepath.open("r").read()
    report_content = fill_template_tex(report_content, variable_dict)

    target_path.mkdir(parents=True, exist_ok=True)
    latex_report_filepath = target_path / report_name
    latex_report_filepath = latex_report_filepath.with_suffix(".tex")
    Path(latex_report_filepath).open("w+").write(report_content)

    check_tex_commands_exist(target_path)
    report_path = compile_pdf(target_path, report_name)

    print(f"Report is placed at: {report_path}")
