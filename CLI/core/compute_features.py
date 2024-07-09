#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Compute features for an instance, only for internal calls from Sparkle."""
import argparse
from pathlib import Path, PurePath
from filelock import FileLock

import global_variables as gv
import tools.general as tg
from sparkle.platform import file_help as sfh, settings_help
from sparkle.structures import FeatureDataFrame
from sparkle.instance import InstanceSet
from sparkle.solver import Extractor


if __name__ == "__main__":
    # Initialise settings
    global settings
    settings_dir = Path("Settings")
    file_path_latest = PurePath(settings_dir / "latest.ini")
    gv.settings = settings_help.Settings(file_path_latest)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance file(s) to run on")
    parser.add_argument("--extractor", required=True, type=str,
                        help="path to feature extractor")
    parser.add_argument("--feature-csv", required=True, type=str,
                        help="path to feature data CSV file")
    args = parser.parse_args()

    # Process command line arguments
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    has_instance_set = False
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        instance_set = InstanceSet(instance_path.parent)
        instance_path = instance_set.get_path_by_name(instance_name)
        has_instance_set = True

    extractor_path = Path(args.extractor)
    feature_data_csv_path = Path(args.feature_csv)
    cutoff_extractor = gv.settings.get_general_extractor_cutoff_time()

    key_str = (f"{extractor_path.name}_"
               f"{instance_name}_"
               f"{tg.get_time_pid_random_string()}")
    result_path = Path(f"Feature_Data/{key_str}.csv")
    runsolver_watch_data_path = f"{result_path}.log"
    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        instance_list = [str(filepath) for filepath in instance_path]
    else:
        instance_list = [instance_path]
    extractor = Extractor(extractor_path, gv.runsolver_path, gv.sparkle_tmp_path)
    
    features = extractor.run(instance_list,
                             runsolver_args=["--cpu-limit", str(cutoff_extractor),
                                             "-w", runsolver_watch_data_path])

    # Now that we have our result, we write it to the FeatureDataCSV with a FileLock
    lock = FileLock(f"{feature_data_csv_path}.lock")
    if features is not None:
        with lock.acquire(timeout=60):
            feature_data = FeatureDataFrame(feature_data_csv_path)
            for feature_group, feature_name, value in features:
                feature_data.set_value(str(instance_path), str(extractor_path),
                                       feature_group, feature_name, float(value))
            feature_data.save_csv()
        result_string = "Successful"
    else:
        print("EXCEPTION during retrieving extractor results.\n"
              f"****** WARNING: Feature vector computation on instance {instance_path}"
              " failed! ******")
        result_string = "Failed"
    lock.release()
    result_path.unlink(missing_ok=True)

    sfh.rmfiles(runsolver_watch_data_path)
