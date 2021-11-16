""" This module contains a tool to parse a Slurm sbatch file to get the information
contained in the file in structured way."""

# standard libs
import re
from typing import Union
from pathlib import Path

# precompiled regex
re_sbatch = re.compile("#SBATCH (.*)")
re_params_all = re.compile(r"params=\( \\\n(?:(.*))\)", re.DOTALL)
re_params_items = re.compile(r"'(.*)'")
re_srun_all = re.compile(r"srun (.*)")
re_srun_split = re.compile(r" (?!-)")


class SlurmBatch:
    """ Simple class to parse a Slurm batch file and get the info


    Attributes
    ----------
    sbatch: list[str]
        The #SBATCH options. Ex.: ['--array=-22%250', '--mem-per-cpu=3000']
    params: list[str]
        The parameters to pass to the command
    cmd: str
        The command to execute
    srun_args: list[str]
        A list of arguments to pass to srun. Ex.: ['-n1', '-N1']
    """

    def __init__(self, srcfile: Union[str, Path]):
        """ Parse the data contained in srcfile and localy store the information. """
        self.file = Path(srcfile)

        with open(self.file) as f:
            filestr = f.read()

        self.sbatch = re_sbatch.findall(filestr)
        self.params = re_params_items.findall(re_params_all.findall(filestr)[0])

        srun = re_srun_all.findall(filestr)[0]
        srun_args, cmd = re_srun_split.split(srun, maxsplit=1)

        self.srun_args = srun_args.split()
        self.cmd = cmd.replace("${params[$SLURM_ARRAY_TASK_ID]}", "").strip()
