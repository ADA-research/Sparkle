"""Methods to deal with Parameter Configuration Space files."""

from pathlib import Path

def get_pcs_file_from_solver_directory(solver_directory: Path) -> Path:
    """Return the name of the PCS file in a solver directory.

    If not found, return an empty str.

    Args:
        solver_directory: Directory of solver

    Returns:
        Returns string containing the name of pcs file if found
    """
    for file_path in Path(solver_directory).iterdir():
        file_extension = "".join(file_path.suffixes)

        if file_extension == ".pcs":
            return file_path.name

    return ""
