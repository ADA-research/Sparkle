#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Compute features for an instance, only for internal calls from Sparkle."""
import argparse
from pathlib import Path
from filelock import FileLock

from sparkle.CLI.help import global_variables as gv
from sparkle.structures import FeatureDataFrame
from sparkle.instance import Instance_Set
from sparkle.solver import Extractor


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance file(s) to run on")
    parser.add_argument("--extractor", required=True, type=str,
                        help="path to feature extractor")
    parser.add_argument("--feature-csv", required=True, type=str,
                        help="path to feature data CSV file")
    parser.add_argument("--cutoff", required=True, type=str,
                        help="the maximum CPU time for the extractor.")
    parser.add_argument("--feature-group", required=False, type=str,
                        help="the group of features to compute, if available for the "
                             "extractor. If not available or provided, all groups will"
                             " be computed.")
    parser.add_argument("--log-dir", type=Path, required=False,
                        help="path to the log directory")
    args = parser.parse_args()

    # Process command line arguments
    log_dir =\
        args.log_dir if args.log_dir is not None else gv.settings().DEFAULT_tmp_output
    instance_path = Path(args.instance)
    instance_name = instance_path
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        data_set = Instance_Set(instance_path.parent)
        instance_path = data_set.get_path_by_name(Path(instance_name).name)

    extractor_path = Path(args.extractor)
    feature_data_csv_path = Path(args.feature_csv)
    cutoff_extractor = args.cutoff

    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        instance_list = [str(filepath) for filepath in instance_path]
    else:
        instance_list = [instance_path]

    extractor = Extractor(extractor_path,
                          gv.settings().DEFAULT_runsolver_exec,
                          log_dir)
    features = extractor.run(instance_list,
                             feature_group=args.feature_group,
                             cutoff_time=cutoff_extractor,
                             log_dir=log_dir)

    # Now that we have our result, we write it to the FeatureDataCSV with a FileLock
    lock = FileLock(f"{feature_data_csv_path}.lock")
    if features is not None:
        print(f"Writing features to CSV: {instance_name}, {extractor_path.name}")
        with lock.acquire(timeout=60):
            feature_data = FeatureDataFrame(feature_data_csv_path)
            for feature_group, feature_name, value in features:
                feature_data.set_value(str(instance_name), extractor_path.name,
                                       feature_group, feature_name, float(value))
            feature_data.save_csv()
        lock.release()
    else:
        print("EXCEPTION during retrieving extractor results.\n"
              f"****** WARNING: Feature vector computation on instance {instance_path}"
              " failed! ******")
