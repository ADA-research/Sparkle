#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Execute Feature Extractor for an instance, write features to FeatureDataFrame."""

import argparse
from pathlib import Path
from filelock import FileLock

from sparkle.structures import FeatureDataFrame
from sparkle.selector import Extractor
from sparkle.instance import Instance_Set


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--extractor", required=True, type=Path, help="path to feature extractor"
    )
    parser.add_argument(
        "--instance",
        required=True,
        type=Path,
        nargs="+",
        help="path to instance file(s) to run on",
    )
    parser.add_argument(
        "--feature-csv", required=True, type=Path, help="path to feature data CSV file"
    )
    parser.add_argument(
        "--cutoff",
        required=True,
        type=str,
        help="the maximum CPU time for the extractor.",
    )
    parser.add_argument(
        "--feature-group",
        required=False,
        type=str,
        help="the group of features to compute, if available for the "
        "extractor. If not available or provided, all groups will"
        " be computed.",
    )
    parser.add_argument(
        "--log-dir", type=Path, required=True, help="path to the log directory"
    )
    args = parser.parse_args()

    # Process command line arguments
    log_dir = args.log_dir

    # Instance agument is a list to allow for multifile instances
    instance_path: list[Path] = args.instance
    # We only receive the instance path on the CLI, but the FeatureDataFrame is keyed by
    # the canonical (set_name, instance_name) pair. Rather than guess the name (file sets
    # store the .stem, iterable sets store the full name with suffix), reconstruct the
    # owning InstanceSet from the instance's parent directory and look the pair up by path.
    target = instance_path[0].resolve()
    # Instance_Set() picks the same subclass (file / iterable / multi-file) that was used
    # originally, so its instance_pairs carry the exact stored naming convention.
    instance_set = Instance_Set(instance_path[0].parent)
    # Walk the set's pairs alongside their paths and return the pair whose path(s) include
    # our target file. ipath may be a list (multi-file instance), so normalise to a list.
    instance_pair = next(
        (
            pair
            for pair, ipath in zip(
                instance_set.instance_pairs, instance_set.instance_paths
            )
            if target
            in [
                path.resolve()
                for path in (ipath if isinstance(ipath, list) else [ipath])
            ]
        ),
        # Fallback (no match found): keep prior behaviour of (parent dir name, stem).
        (instance_path[0].parent.name, instance_path[0].stem),
    )
    instance_name = instance_pair[1]
    extractor_path = args.extractor
    feature_data_csv_path = args.feature_csv
    cutoff_extractor = args.cutoff

    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        instance_list = [str(filepath) for filepath in instance_path]
    else:
        instance_list = [str(instance_path)]

    extractor = Extractor(extractor_path)
    if args.feature_group:
        print(
            f"Calling {extractor.name} with feature group {args.feature_group} for instance {instance_list} with cutoff {cutoff_extractor}"
        )
    else:
        print(
            f"Calling {extractor.name} for instance {instance_list} with cutoff {cutoff_extractor}"
        )

    features = extractor.run(
        instance_list,
        feature_group=args.feature_group,
        cutoff_time=cutoff_extractor,
        log_dir=log_dir,
    )

    if features is None or len(features) == 0:
        raise ValueError(
            "No features found! This may be due to a timeout. Check extractor logs."
        )

    feature_data_per_group = {}
    for feature_group, feature_name, value in features:
        if feature_group not in feature_data_per_group:
            feature_data_per_group[feature_group] = [[], []]
        print(
            f"{extractor_path.name} {instance_name} {feature_group} {feature_name} | {value}"
        )  # For logging purposes
        feature_data_per_group[feature_group][0] += [feature_name]
        feature_data_per_group[feature_group][1] += [float(value)]

    # Now that we have our result, we write it to the FeatureDataCSV with a FileLock
    lock = FileLock(f"{feature_data_csv_path}.lock")
    if features is not None:
        print("Writing features to file...")
        with lock.acquire(timeout=600):
            feature_data = FeatureDataFrame(feature_data_csv_path)
            for feature_group, (
                feature_names,
                feature_values,
            ) in feature_data_per_group.items():
                # for feature_group, feature_name, value in features:
                feature_data.set_value(
                    instance_pair,
                    extractor_path.name,
                    feature_group,
                    feature_names,
                    feature_values,
                    append_write_csv=True,
                )
        lock.release()
        print("Writing successful!")
    else:
        print(
            "EXCEPTION during retrieving extractor results.\n"
            f"****** WARNING: Feature vector computation on instance {instance_path}"
            " failed! ******"
        )
