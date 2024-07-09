#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Compute features for an instance, only for internal calls from Sparkle."""
import argparse
from pathlib import Path
from filelock import FileLock

import global_variables as gv
from sparkle.structures import FeatureDataFrame
from sparkle.instance import InstanceSet
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
    args = parser.parse_args()

    # Process command line arguments
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        instance_set = InstanceSet(instance_path.parent)
        instance_path = instance_set.get_path_by_name(instance_name)

    extractor_path = Path(args.extractor)
    feature_data_csv_path = Path(args.feature_csv)
    cutoff_extractor = args.cutoff

    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        instance_list = [str(filepath) for filepath in instance_path]
    else:
        instance_list = [instance_path]

    extractor = Extractor(extractor_path, gv.runsolver_path, gv.sparkle_tmp_path)
    # We are not interested in the runsolver log, but create the file to filter it 
    # from the extractor call output
    runsolver_watch_path = gv.sparkle_tmp_path / f"{instance_path}_{extractor_path}.wlog"
    features = extractor.run(instance_list,
                             runsolver_args=["--cpu-limit", cutoff_extractor,
                                             "-w", runsolver_watch_path])

    # Now that we have our result, we write it to the FeatureDataCSV with a FileLock
    lock = FileLock(f"{feature_data_csv_path}.lock")
    if features is not None:
        with lock.acquire(timeout=60):
            feature_data = FeatureDataFrame(feature_data_csv_path)
            for feature_group, feature_name, value in features:
                feature_data.set_value(str(instance_path), str(extractor_path),
                                       feature_group, feature_name, float(value))
            feature_data.save_csv()
        lock.release()
    else:
        print("EXCEPTION during retrieving extractor results.\n"
              f"****** WARNING: Feature vector computation on instance {instance_path}"
              " failed! ******")
    runsolver_watch_path.unlink(missing_ok=True)
