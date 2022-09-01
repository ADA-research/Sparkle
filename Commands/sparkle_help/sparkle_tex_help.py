from shutil import which
import os

def check_tex_commands_exist():
    if which('bibtex') is None or which('pdflatex') is None:
        return False
    else:
        return True

def compile_pdf(latex_directory_path, latex_report_filename):
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
