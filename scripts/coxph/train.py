import argparse
import logging
import os
import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install("xgboost")

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def survival_y_cox(dframe):
    """Returns array of outcome encoded for XGB"""
    y_survival = []

    for idx, row in dframe[["duration", "event"]].iterrows():
        if row["event"]:
            # uncensored
            y_survival.append(int(row["duration"]))
        else:
            # right censored
            y_survival.append(-int(row["duration"]))
    return np.array(y_survival)


def main(args):
    """
    Runs preprocessing for the example data set
        1. Pulls data from the Athena database
        2. Splits data into training and testing
        3. Preprocess categorical and numerical test_features
        4. Writes preprocessed data to S3

    Args:
        database (str, required): Athena database to query data from
        table (str, required): Athena table name to query data from
        region (str, required): AWS Region for queries
        train-test-split-ratio (float): Percentage to split the data into
        , default is 25%
        random-state (float): Random seed used for train and test split
        , default is 123

    """
    logger.debug(f"Received arguments {args}")

    train_data_path = os.path.join("/opt/ml/input/data/train", args.train_data)
    test_data_path = os.path.join("/opt/ml/input/data/test", args.test_data)

    train = pd.read_csv(train_data_path, header=0)
    test = pd.read_csv(test_data_path, header=0)

    train = train.rename(columns={"91": "event", "90": "duration"})
    test = test.rename(columns={"91": "event", "90": "duration"})

    logger.info(train.shape)
    logger.info(test.shape)

    y_train = train[["duration", "event"]]
    y_test = test[["duration", "event"]]

    train = train.drop(["duration", "event"], 1)
    test = test.drop(["duration", "event"], 1)

    logger.info(train.shape, y_train.shape)
    logger.info(test.shape, y_test.shape)

    xgb_train = xgb.DMatrix(train, label=survival_y_cox(y_train))
    xgb_test = xgb.DMatrix(test, label=survival_y_cox(y_test))

    callbacks = [xgb.callback.EvaluationMonitor(period=20)]

    params = {
        "eta": args.eta,
        "max_depth": args.max_depth,
        "objective": args.objective,
        "tree_method": args.tree_method,
        "min_child_weight": args.min_child_weight,
        "gamma": args.gamma,
        "alpha": args.alpha,
        "subsample": args.subsample,
        "seed": args.seed,
    }

    logger.info(f"pramas set to {params}")

    model = xgb.train(
        params,
        xgb_train,
        num_boost_round=args.num_boost_round,
        evals=[(xgb_train, "train"), (xgb_test, "val")],
        early_stopping_rounds=10,
        callbacks=callbacks,
        verbose_eval=0,
    )

    logger.info(f"Best score of model is {model.best_score}")

    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="xgboost-model")
    parser.add_argument("--test-data", type=str, default="test_features.csv")
    parser.add_argument("--train-data", type=str, default="train_features.csv")
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--seed", type=int, default=123)

    # HYPERPARAMETERS
    parser.add_argument("--objective", type=str, default="survival:cox")
    parser.add_argument("--eta", type=float, default=0.1)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--subsample", type=float, default=0.8)
    parser.add_argument("--gamma", type=float, default=0.0)
    parser.add_argument("--min-child-weight", type=int, default=1)
    parser.add_argument("--tree-method", type=str, default="hist")
    parser.add_argument("--alpha", type=float, default=0.0)

    args = parser.parse_args()

    main(args)
