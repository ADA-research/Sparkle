#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""
import subprocess
import argparse
import shutil
import os
import sys
import warnings
from pathlib import Path

from sparkle.platform import CommandName
from sparkle.CLI.help.argparse_custom import DownloadExamplesArgument
from sparkle.CLI.help import snapshot_help as snh
from sparkle.platform.settings_objects import Settings
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.CLI.help import global_variables as gv
from sparkle.configurator.implementations.irace import IRACE


def parser_function() -> argparse.ArgumentParser:
    """Parse CLI arguments for the initialise command."""
    parser = argparse.ArgumentParser(
        description="Initialise the Sparkle platform in the current directory.")
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


def initialise_irace() -> None:
    """Initialise IRACE."""
    if shutil.which("R") is None:
        warnings.warn("R is not installed, which is required for the IRACE"
                      "configurator. Make sure R is installed and try again.")
        return
    print("Initialising IRACE ...")
    r6_package_check = subprocess.run(["Rscript", "-e",
                                      'library("R6")'], capture_output=True)
    if r6_package_check.returncode != 0:  # R6 is not installed
        print("Installing R6 package (IRACE dependency) ...")
        r6_install = subprocess.run([
            "Rscript", "-e",
            f'install.packages("{IRACE.r6_dependency_package.absolute()}",'
            f'lib="{IRACE.configurator_path.absolute()}")'], capture_output=True)
        if r6_install.returncode != 0:
            print("An error occured during the installation of R6:\n",
                  r6_install.stdout.decode(), "\n",
                  r6_install.stderr.decode(), "\n"
                  "IRACE installation failed!")
            return
    else:
        print(f"[{r6_package_check.returncode}] "
              "R6 package (IRACE dependency) was already installed: "
              f"{r6_package_check.stdout.decode()}\n"
              f"{r6_package_check.stderr.decode()}")
    # Install IRACE from tarball
    irace_install = subprocess.run(
        ["Rscript", "-e",
         f'install.packages("{IRACE.configurator_package.absolute()}",'
         f'lib="{IRACE.configurator_path.absolute()}")'], capture_output=True)
    if irace_install.returncode != 0 or not IRACE.configurator_executable.exists():
        print("An error occured during the installation of IRACE:\n",
              irace_install.stdout.decode(), "\n",
              irace_install.stderr.decode())
    else:
        print("IRACE installed!")


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
    if detect_sparkle_platform_exists(check=all):
        print("Current Sparkle platform found! Saving as snapshot.")
        snh.save_current_platform()
        snh.remove_current_platform()

    for working_dir in gv.settings().DEFAULT_working_dirs:
        working_dir.mkdir(exist_ok=True)

    # Check if Settings file exists, otherwise initialise a default one
    if not Path(Settings.DEFAULT_settings_path).exists():
        print("Settings file does not exist, initializing default settings ...")
        gv.__settings = Settings(Settings.DEFAULT_example_settings_path)
        gv.settings().write_settings_ini(Path(Settings.DEFAULT_settings_path))

    # Initialise latest scenario file
    gv.ReportingScenario.DEFAULT_reporting_scenario_path.open("w+")

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
            warnings.warn("Runsolver executable doesn't exist and cannot find makefile."
                          " Please verify the contents of the directory: "
                          f"{gv.settings().DEFAULT_runsolver_dir}")
        else:
            compile_runsolver =\
                subprocess.run(["make"],
                               cwd=gv.settings().DEFAULT_runsolver_dir,
                               capture_output=True)
            if compile_runsolver.returncode != 0:
                warnings.warn("Compilation of Runsolver failed with the following msg:"
                              f"[{compile_runsolver.returncode}] "
                              f"{compile_runsolver.stderr.decode()}")
            else:
                print("Runsolver compiled successfully!")
    # Check that java is available for SMAC2
    if shutil.which("java") is None:
        # NOTE: An automatic resolution of Java at this point would be good
        # However, loading modules from Python has thusfar not been successfull.
        warnings.warn("Could not find Java as an executable! "
                      "Java 1.8.0_402 is required to use SMAC2 as a configurator.")

    # Check if IRACE is installed
    if not IRACE.configurator_executable.exists():
        initialise_irace()

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


def main(argv: list[str]) -> None:
    """Main function of the command."""
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args(argv)
    download = False if args.download_examples is None else args.download_examples
    initialise_sparkle(download_examples=download)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
