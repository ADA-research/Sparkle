#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper classes/method for LaTeX and bibTeX."""
from shutil import which
from pathlib import Path
import subprocess
from enum import Enum

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.kaleido.scope.mathjax = None  # Bug fix for kaleido


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


def list_to_latex(content: list | list[tuple]) -> str:
    """Convert a list to LaTeX.

    Args:
        content: The list to convert. If a tuple, first item will be boldface.

    Returns:
        The list as LaTeX str.
    """
    if len(content) == 0:
        return "\\item"
    if isinstance(content[0], tuple):
        return "".join(f"\\item \\textbf{{{item[0]}}}{item[1]}" for item in content)
    return "".join(f"\\item {item}\n" for item in content)


def generate_comparison_plot(points: list,
                             figure_filename: str,
                             xlabel: str = "default",
                             ylabel: str = "optimised",
                             title: str = "",
                             scale: str = "log",
                             limit: str = "magnitude",
                             limit_min: float = 0.2,
                             limit_max: float = 0.2,
                             replace_zeros: bool = True,
                             magnitude_lines: int = 2147483647,
                             output_dir: Path = None) -> None:
    """Create comparison plots between two different solvers/portfolios.

    Args:
        points: list of points which represents with the performance results of
        (solverA, solverB)
        figure_filename: filename without filetype (e.g., .jpg) to save the figure to.
        xlabel: Name of solverA (default: default)
        ylabel: Name of solverB (default: optimised)
        title: Display title in the image (default: None)
        scale: [linear, log] (default: linear)
        limit: The method to compute the axis limits in the figure
            [absolute, relative, magnitude] (default: relative)
            absolute: Uses the limit_min/max values as absolute values
            relative: Decreases/increases relatively to the min/max values found in the
            points. E.g., min/limit_min and max*limit_max
            magnitude: Increases the order of magnitude(10) of the min/max values in the
            points. E.g., 10**floor(log10(min)-limit_min)
            and 10**ceil(log10(max)+limit_max)
        limit_min: Value used to compute the minimum limit
        limit_max: Value used to compute the maximum limit
        computing the figure limits. This is only relevant for runtime objectives
        replace_zeros: Replaces zeros valued performances to a very small value to make
        plotting on log-scale possible
        magnitude_lines: Draw magnitude lines (only supported for log scale)
        output_dir: directory path to place the figure and its intermediate files in
            (default: current working directory)
    """
    output_dir = Path() if output_dir is None else Path(output_dir)

    df = pd.DataFrame(points, columns=[xlabel, ylabel])
    if replace_zeros and (df < 0).any(axis=None):
        # Log scale cannot deal with negative and zero values, set to smallest non zero
        df[df < 0] = np.nextafter(0, 1)

    # process range values
    min_point_value = df.min(numeric_only=True).min()
    max_point_value = df.max(numeric_only=True).max()

    if limit == "absolute":
        min_value = limit_min
        max_value = limit_max
    elif limit == "relative":
        min_value = (min_point_value * (1 / limit_min) if min_point_value > 0
                     else min_point_value * limit_min)
        max_value = (max_point_value * limit_max if max_point_value > 0
                     else max_point_value * (1 / limit_max))
    elif limit == "magnitude":
        min_value = 10 ** (np.floor(np.log10(min_point_value)) - limit_min)
        max_value = 10 ** (np.ceil(np.log10(max_point_value)) + limit_max)

    if scale == "log" and np.min(points) <= 0:
        raise Exception("Cannot plot negative and zero values on a log scales")

    output_plot = output_dir / f"{figure_filename}.pdf"
    log_scale = scale == "log"
    fig = px.scatter(data_frame=df, x=xlabel, y=ylabel,
                     range_x=[min_value, max_value], range_y=[min_value, max_value],
                     title=title, log_x=log_scale, log_y=log_scale,
                     width=500, height=500)
    # Add in the seperation line
    fig.add_shape(type="line", x0=0, y0=0, x1=max_value, y1=max_value,
                  line=dict(color="lightgrey", width=1))
    fig.update_traces(marker=dict(color="RoyalBlue", symbol="x"))
    fig.update_layout(
        plot_bgcolor="white"
    )
    fig.update_xaxes(
        type="linear" if not log_scale else "log",
        mirror=True,
        tickmode="linear",
        ticks="outside",
        tick0=0,
        dtick=100 if not log_scale else 1,
        showline=True,
        linecolor="black",
        gridcolor="lightgrey"
    )
    fig.update_yaxes(
        type="linear" if not log_scale else "log",
        mirror=True,
        tickmode="linear",
        ticks="outside",
        tick0=0,
        dtick=100 if not log_scale else 1,
        showline=True,
        linecolor="black",
        gridcolor="lightgrey"
    )
    fig.write_image(output_plot)


def fill_template_tex(template_tex: str, variables: dict) -> str:
    """Given a latex template, replaces all the @@ variables using the dict.

    Args:
        template_tex: The template to be populated
        variables: Variable names (key) with their target (value)

    Returns:
        The populated latex string.
    """
    for variable_key, target_value in variables.items():
        variable = f"@@{variable_key}@@"
        target_value = str(target_value)
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
