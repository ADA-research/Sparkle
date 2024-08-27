#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""
import subprocess
import argparse
import shutil
import os
from pathlib import Path

from sparkle.platform import CommandName
from sparkle.CLI.help.argparse_custom import DownloadExamplesArgument
from sparkle.CLI.help import snapshot_help as snh
from sparkle.platform.settings_objects import Settings
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Parse CLI arguments for the initialise command."""
    parser = argparse.ArgumentParser(
        description=("Initialise the Sparkle platform in the current directory."))
    parser.add_argument(*DownloadExamplesArgument.names,
                        **DownloadExamplesArgument.kwargs)
    return parser


def detect_sparkle_platform_exists(check: callable = all) -> Path:
    """Return whether a Sparkle platform is currently active.

    The default working directories are checked for existence, for each directory in the
    CWD. If any of the parents of the CWD yield true, this path is returned

    Args:
        check: Method to check if the working directory exists. Defaults to all.

    Returns:
      Path to the Sparkle platform if it exists, None otherwise.
    """
    cwd = Path.cwd()
    while str(cwd) != cwd.root:
        if check([(cwd / wd).exists() for wd in gv.settings().DEFAULT_working_dirs]):
            return cwd
        cwd = cwd.parent
    return None


def check_for_initialise(requirements: list[CommandName] = None)\
        -> None:
    """Function to check if initialize command was executed and execute it otherwise.

    Args:
        argv: List of the arguments from the caller.
        requirements: The requirements that have to be executed before the calling
            function.
    """
    platform_path = detect_sparkle_platform_exists()
    if platform_path is None:
        print("-----------------------------------------------")
        print("No Sparkle platform found; "
              + "The platform will now be initialized automatically")
        if requirements is not None:
            if len(requirements) == 1:
                print(f"The command {requirements[0]} has \
                      to be executed before executing this command.")
            else:
                print(f"""The commands {", ".join(requirements)} \
                      have to be executed before executing this command.""")
        print("-----------------------------------------------")
        initialise_sparkle()
    elif platform_path != Path.cwd():
        print(f"[WARNING] Sparkle platform found in {platform_path} instead of "
              f"{Path.cwd()}. Switching to CWD to {platform_path}")
        os.chdir(platform_path)


def initialise_sparkle(download_examples: bool = False) -> None:
    """Initialize a new Sparkle platform.

    Args:
        download_examples: Downloads examples from the Sparkle Github.
            WARNING: May take a some time to complete due to the large amount of data.
    """
    print("Start initialising Sparkle platform ...")
    # Check if Settings file exists, otherwise initialise a default one
    if not Path(Settings.DEFAULT_settings_path).exists():
        print("Settings file does not exist, initializing default settings ...")
        gv.__settings = Settings(Settings.DEFAULT_example_settings_path)
        gv.settings().write_settings_ini(Path(Settings.DEFAULT_settings_path))

    gv.settings().DEFAULT_snapshot_dir.mkdir(exist_ok=True)
    if detect_sparkle_platform_exists(check=any):
        snh.save_current_sparkle_platform()
        snh.remove_current_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    for working_dir in gv.settings().DEFAULT_working_dirs:
        working_dir.mkdir(exist_ok=True)

    # Initialise the FeatureDataFrame
    FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    # Initialise the Performance DF with the static dimensions
    # TODO: We have many sparkle settings values regarding ``number of runs''
    # E.g. configurator, parallel portfolio, and here too. Should we unify this more, or
    # just make another setting that does this specifically for performance data?
    PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path,
                         objectives=gv.settings().get_general_sparkle_objectives(),
                         n_runs=1)

    # Check that Runsolver is compiled, otherwise, compile
    if not gv.settings().DEFAULT_runsolver_exec.exists():
        print("Runsolver does not exist, trying to compile...")
        if not (gv.settings().DEFAULT_runsolver_dir / "Makefile").exists():
            print("WARNING: Runsolver executable doesn't exist and cannot find makefile."
                  " Please verify the contents of the directory: "
                  f"{gv.settings().DEFAULT_runsolver_dir}")
        else:
            compile_runsolver =\
                subprocess.run(["make"],
                               cwd=gv.settings().DEFAULT_runsolver_dir,
                               capture_output=True)
            if compile_runsolver.returncode != 0:
                print("WARNING: Compilation of Runsolver failed with the following msg:"
                      f"[{compile_runsolver.returncode}] "
                      f"{compile_runsolver.stderr.decode()}")
            else:
                print("Runsolver compiled successfully!")
    # Check that java is available
    if shutil.which("java") is None:
        # NOTE: An automatic resolution of Java at this point would be good
        # However, loading modules from Python has thusfar not been successfull.
        print("Could not find Java as an executable!")

    if download_examples:
        # Download Sparkle examples from Github
        # NOTE: Needs to be thoroughly tested after Pip install is working
        print("Downloading examples ...")
        curl = subprocess.Popen(
            ["curl", "https://codeload.github.com/ADA-research/Sparkle/tar.gz/main"],
            stdout=subprocess.PIPE)
        outpath = Path("outfile.tar.gz")
        with curl.stdout, outpath.open("wb") as outfile:
            tar = subprocess.Popen(["tar", "-xz", "--strip=1", "Sparkle-main/Examples"],
                                   stdin=curl.stdout, stdout=outfile)
        curl.wait()  # Wait for the download to complete
        tar.wait()  # Wait for the extraction to complete
        outpath.unlink(missing_ok=True)

    print("New Sparkle platform initialised!")


if __name__ == "__main__":
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args()
    download = False if args.download_examples is None else args.download_examples
    initialise_sparkle(download_examples=download)
