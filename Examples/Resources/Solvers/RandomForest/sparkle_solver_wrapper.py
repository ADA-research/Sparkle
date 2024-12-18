#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Solver wrapper for RandomForest implementation."""
from __future__ import annotations
import copy

from ConfigSpace import (
    Categorical,
    Configuration,
    ConfigurationSpace,
    EqualsCondition,
    Float,
    Integer,
)
import time
import sys
import re
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args


class DataSet():
    """Data set object class."""

    def __init__(self: DataSet) -> None:
        """Initialize data set wrapper."""
        self.data = None
        self.target = None

    def load_from_csv(self: DataSet, filepath: Path) -> DataSet:
        """Load data set from csv file."""
        df = pd.read_csv(filepath)
        attributes = list(df.columns)[:-1]
        target = list(df.columns)[-1]

        self.data = df[attributes].to_numpy()
        self.target = df[target].to_numpy()
        return self


class RandomForest:
    """Random forest classifier wrapper."""

    def __init__(self: RandomForest, dataset: DataSet) -> None:
        """Initialize random forest classifier."""
        self.dataset = dataset

    @property
    def configspace(self: RandomForest) -> ConfigurationSpace:
        """Get configuration space."""
        cs = ConfigurationSpace()

        n_estimators = Integer("n_estimators", (1, 500), default=100)
        criterion = Categorical("criterion", ["gini", "entropy", "log_loss"],
                                default="gini")
        max_depth_type = Categorical("max_depth_type", ["None", "int"],
                                     default="None")
        max_depth = Integer("max_depth", (1, 100), default=10)

        use_max_depth = EqualsCondition(child=max_depth,
                                        parent=max_depth_type, value="int")

        min_samples_split = Integer("min_samples_split", (1, 100), default=2)
        min_samples_leaf = Integer("min_samples_leaf", (1, 100), default=1)
        min_weight_fraction_leaf = Float("min_weight_fraction_leaf", (0.0, 0.5),
                                         default=0.0)

        max_features_type = Categorical("max_features_type",
                                        ["special", "float"], default="special")
        max_features_special = Categorical("max_features_special",
                                           ["sqrt", "log2", "None"], default="sqrt")
        # TODO max val to max features in dataset
        max_features_float = Float("max_features_float", (0.0, 1.0), default=0.5)

        use_max_features_special = EqualsCondition(child=max_features_special,
                                                   parent=max_features_type,
                                                   value="special")
        use_max_features_float = EqualsCondition(child=max_features_float,
                                                 parent=max_features_type, value="float")

        max_leaf_nodes_type = Categorical("max_leaf_nodes_type", ["None", "int"],
                                          default="None")
        max_leaf_nodes = Integer("max_leaf_nodes", (1, 1000), default=100)
        use_max_leaf_nodes = EqualsCondition(child=max_leaf_nodes,
                                             parent=max_leaf_nodes_type, value="int")

        min_impurity_decrease = Float("min_impurity_decrease", (0.0, 0.5), default=0.0)

        bootstrap = Categorical("bootstrap", [True, False], default=True)
        oob_score = Categorical("oob_score", [True, False], default=True)

        use_oob_score = EqualsCondition(child=oob_score, parent=bootstrap, value=True)

        max_samples_type = Categorical("max_samples_type", ["None", "float"],
                                       default="None")
        max_samples = Float("max_samples", (0.05, 0.95), default=0.8)

        use_max_samples = EqualsCondition(child=max_samples, parent=max_samples_type,
                                          value="float")
        use_max_samples2 = EqualsCondition(child=max_samples_type, parent=bootstrap,
                                           value=True)

        cs.add([n_estimators, criterion, max_depth_type, max_depth,
                min_samples_split, min_samples_leaf,
                min_weight_fraction_leaf, max_features_type,
                max_features_special, max_features_float,
                max_leaf_nodes_type, max_leaf_nodes,
                min_impurity_decrease, bootstrap, oob_score,
                max_samples_type, max_samples])

        cs.add([use_max_depth, use_max_features_float,
                use_max_features_special, use_max_leaf_nodes, use_oob_score,
                use_max_samples, use_max_samples2])

        return cs

    def train(self: RandomForest,
              config: Configuration,
              instance: str = "0",
              seed: int = 0,
              budget: int = 10) -> dict[str, float]:
        """Train a random forest classifier."""
        seed = int(seed)
        _ = np.random.RandomState(seed)

        max_depth = None if config["max_depth_type"] == "None" else config["max_depth"]
        if config["max_features_type"] == "float":
            max_features = config["max_features_float"]
        else:
            max_features = config["max_features_special"]
        if max_features == "None":
            max_features = None
        max_leaf_nodes =\
            None if config["max_leaf_nodes_type"] == "None" else config["max_leaf_nodes"]

        keys = ["n_estimators", "criterion", "min_samples_split", "min_samples_leaf",
                "min_weight_fraction_leaf", "min_impurity_decrease", "bootstrap"]
        kwargs = {k: config[k] for k in keys}
        if config["bootstrap"] is True:
            kwargs["oob_score"] = config["bootstrap"]
            max_samples =\
                None if config["max_samples_type"] == "None" else config["max_samples"]
            kwargs["max_samples"] = max_samples

        start_time = time.time()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

        classifier = RandomForestClassifier(
            max_depth=max_depth,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            **kwargs
        )

        instance = int(instance)
        dataset = self.dataset
        x_train, x_test, y_train, y_test = train_test_split(dataset.data, dataset.target,
                                                            test_size=0.2, shuffle=True,
                                                            random_state=seed)

        if instance == -1:
            # test
            pass
        else:
            # Returns the 10-fold cross validation accuracy
            x_train_base = copy.copy(x_train)
            y_train_base = copy.copy(y_train)
            # to make CV splits consistent
            cv = StratifiedKFold(n_splits=10, random_state=seed, shuffle=True)
            train_id, test_id = list(cv.split(x_train_base, y_train_base))[int(instance)]
            x_train = x_train_base[train_id, :]
            x_test = x_train_base[test_id, :]
            y_train = y_train_base[train_id]
            y_test = y_train_base[test_id]

        classifier.fit(x_train, y_train)
        y_pred = classifier.predict(x_test)

        model_size = 0
        for decision_tree in classifier.estimators_:
            model_size += decision_tree.tree_.node_count

        averaging = "binary" if len(np.unique(y_train)) == 2 else "micro"

        performances = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average=averaging),
            "recall": recall_score(y_test, y_pred, average=averaging),
            "f1": f1_score(y_test, y_pred, average=averaging),
            "time": time.time() - start_time,
            "size": model_size,
        }
        return performances


if __name__ == "__main__":
    # Wrapper for RandomForest to run from command line
    args = parse_solver_wrapper_args(sys.argv)
    dataset = Path(args["instance"])
    solver_dir = Path(args["solver_dir"])
    seed = args["seed"]
    cutoff = float(args["cutoff_time"])
    objectives = args["objectives"]  # Fix me: stale?
    instance = "-1"  # Place holder

    del args["solver_dir"]
    del args["instance"]
    del args["cutoff_time"]
    del args["seed"]
    del args["objectives"]
    config = args

    dataset = DataSet().load_from_csv(dataset)
    rf = RandomForest(dataset)

    for k, v in config.items():
        if v == "True":
            config[k] = True
        elif v == "False":
            config[k] = False
        elif re.fullmatch(r"-?\d+", v):
            config[k] = int(v)
        elif re.fullmatch(r"-?[\d\.]+", v):
            config[k] = float(v)

    # Fix constraints
    if "max_depth_type" in config:
        if config["max_depth_type"] != "int" and "max_depth" in config:
            del config["max_depth"]
    else:
        config["max_depth_type"] = "None"

    if "max_features_type" in config:
        if config["max_features_type"] == "float" and "max_features_special" in config:
            del config["max_features_special"]
        elif config["max_features_type"] == "special" and "max_features_float" in config:
            del config["max_features_float"]
    else:
        config["max_features_type"] = "special"

    if "max_leaf_nodes_type" in config:
        if config["max_leaf_nodes_type"] != "int" and "max_leaf_nodes" in config:
            del config["max_leaf_nodes"]
    else:
        config["max_leaf_nodes_type"] = "None"

    if "bootstrap" in config:
        if config["bootstrap"] is False:
            if "oob_score" in config:
                del config["oob_score"]
            if "max_samples_type" in config:
                del config["max_samples_type"]
            if "max_samples" in config:
                del config["max_samples"]
    else:
        config["bootstrap"] = True
        config["oob_score"] = True

    if "max_samples_type" in config:
        if config["max_samples_type"] != "float" and "max_samples" in config:
            del config["max_samples"]

    # Fill missing mappings with default
    if "criterion" not in config:
        config["criterion"] = "gini"
    if "min_impurity_decrease" not in config:
        config["min_impurity_decrease"] = 0.0
    if "min_samples_leaf" not in config:
        config["min_samples_leaf"] = 1
    if "min_samples_split" not in config:
        config["min_samples_split"] = 2
    if "min_weight_fraction_leaf" not in config:
        config["min_weight_fraction_leaf"] = 0.0
    if "n_estimators" not in config:
        config["n_estimators"] = 100
    if "max_features_special" not in config:
        config["max_features_special"] = "sqrt"
    if "max_samples_type" not in config:
        config["max_samples_type"] = "None"

    config = Configuration(rf.configspace, config)
    status = "SUCCESS"
    try:
        result = rf.train(config, instance, seed)
    except Exception as e:
        print(e)
        status = "CRASHED"
        result = {k: 0 for k in objectives}

    result["status"] = status
    print(result)
