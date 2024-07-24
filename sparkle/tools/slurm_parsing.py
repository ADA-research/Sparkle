"""This module helps to extract and structure information from Slurm I/O."""
from __future__ import annotations
import re
from pathlib import Path
import ast


def parse_commandline_dict(args: list[str]) -> dict:
    """Parses a commandline dictionary to the object."""
    dict_str = " ".join(args)
    # Remove white space
    dict_str = dict_str.replace(" ", "")
    # Remove all quotes to avoid double strings
    dict_str = dict_str.replace('"', "").replace("'", "")
    # Place the quotes only there where needed
    dict_str = dict_str.replace("{", "{'").replace(":", "':'")
    dict_str = dict_str.replace("[", "['").replace("]", "']")
    dict_str = dict_str.replace(",", "','").replace("}", "'}")
    # Undo quotes at the start and end of lists
    dict_str = dict_str.replace("':'[", "':[").replace("]','", "],'")
    return ast.literal_eval(dict_str)


class SlurmBatch:
    """Class to parse a Slurm batch file and get structured information.

    Attributes
    ----------
    sbatch_options: list[str]
        The SBATCH options. Ex.: ["--array=-22%250", "--mem-per-cpu=3000"]
    cmd_params: list[str]
        The parameters to pass to the command
    cmd: str
        The command to execute
    srun_options: list[str]
        A list of arguments to pass to srun. Ex.: ["-n1", "--nodes=1"]
    file: Path
        The loaded file Path
    """
    # Precompiled regex
    re_sbatch = re.compile("#SBATCH (.*)")
    re_params_all = re.compile(r"params=\( \\\n(?:(.*))\)", re.DOTALL)
    re_params_items = re.compile(r"'(.*)'")
    re_srun_all = re.compile(r"srun (.*)")
    re_srun_split = re.compile(r" (?!-)")

    def __init__(self: SlurmBatch, srcfile: Path) -> None:
        """Parse the data contained in srcfile and localy store the information."""
        self.file = Path(srcfile)

        with Path(self.file).open() as f:
            filestr = f.read()

        self.sbatch_options = SlurmBatch.re_sbatch.findall(filestr)

        # First find the cmd_params block ...
        cmd_block = ""
        if len(SlurmBatch.re_params_all.findall(filestr)) > 0:
            cmd_block = SlurmBatch.re_params_all.findall(filestr)[0]

        # ... then parse it
        self.cmd_params = SlurmBatch.re_params_items.findall(cmd_block)

        srun = SlurmBatch.re_srun_all.findall(filestr)[0]
        srun_args, cmd = SlurmBatch.re_srun_split.split(srun, maxsplit=1)

        self.srun_options = srun_args.split()

        self.cmd = cmd.replace("${params[$SLURM_ARRAY_TASK_ID]}", "").strip()
        self.cmd = self.cmd.replace("${output[$SLURM_ARRAY_TASK_ID]}", "").strip()
        self.cmd = self.cmd.replace(">", "").strip()
