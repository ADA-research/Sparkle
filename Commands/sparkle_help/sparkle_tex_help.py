#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from shutil import which
from pathlib import Path
import os


def check_tex_commands_exist(latex_directory_path: Path):
    '''Raise an exception if one of the latex commands is not present.'''
    if which('bibtex') is None or which('pdflatex') is None:
        raise Exception('Error: It seems like latex is not available on your system.\n'
                        'You can install latex and run the command again, '
                        f'or copy the source files in {latex_directory_path} on your '
                        'local machine to generate the report.')


def compile_pdf(latex_directory_path: Path, latex_report_filename: Path):
    '''Compile the given latex files to a PDF.'''
    pdflatex_command = (f'cd {latex_directory_path}; pdflatex -interaction=nonstopmode '
                        f'{latex_report_filename}.tex 1> /dev/null 2>&1')
    bibtex_command = f'cd {latex_directory_path}; bibtex {latex_report_filename}.aux'

    os.system(pdflatex_command)
    os.system(pdflatex_command)

    os.system(bibtex_command)
    os.system(bibtex_command)

    os.system(pdflatex_command)
    os.system(pdflatex_command)

    report_path = f'{latex_directory_path}{latex_report_filename}.pdf'

    return report_path
