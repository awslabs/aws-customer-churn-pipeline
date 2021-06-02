import argparse
import json
import logging
import os
import pickle
import subprocess
import sys
import tarfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


os.system("conda install -c sebp scikit-survival -y")
install("xgboost")
install("smdebug==1.0.5")
install("shap==0.39.0")
install("scikit-learn==0.24.1")
install("matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import xgboost
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MinMaxScaler
from sksurv.datasets import get_x_y
from sksurv.metrics import brier_score, concordance_index_ipcw
from smdebug.trials import create_trial


def main(args):
    """
    Runs evaluation for the data set
        1. Loads model from tar.gz
        2. Reads in test features
        3. Runs an accuracy report
        4. Generates feature importance with SHAP

    Args:
        model-name (str): Name of the trained model, default xgboost
        test-features (str): preprocessed test features for
         evaluation, default test_features.csv
        train-features (str): preproceed train features for SHAP,
        default train_features.csv
        test-features (str): preproceed test features for SHAP,
        default test_features.csv
        report-name (str): Name of the evaluation output
        , default evaluation.json
        shap-name (str): Name of the SHAP feature importance
        output file, default shap.csv
        threshold (float): Threshold to cut probablities at
        , default 0.5
        tau (int): time range for the c-index will be from 0 to tau
        , default 100
    """

    model_path = os.path.join("/opt/ml/processing/model", "model.tar.gz")

    logger.info(f"Extracting model from path: {model_path}")

    with tarfile.open(model_path) as tar:
        tar.extractall(path=".")
    logger.info("Loading model")
    with open(args.model_name, "rb") as f:
        model = pickle.load(f)

    logger.info("Loading train and test data")

    test_features_data = os.path.join("/opt/ml/processing/test", args.test_features)
    train_features_data = os.path.join("/opt/ml/processing/train", args.train_features)

    X_test = pd.read_csv(test_features_data, header=0)
    X_train = pd.read_csv(train_features_data, header=0)

    y_test = X_test.iloc[:, 0]
    y_train = X_train.iloc[:, 0]

    # Reverse transfrom to event and duration columns
    y_test_df = pd.DataFrame(
        np.vstack((np.where(y_test > 0, 1, 0), np.abs(y_test))).T,
        columns=["event", "duration"],
    )

    y_train_df = pd.DataFrame(
        np.vstack((np.where(y_train > 0, 1, 0), np.abs(y_train))).T,
        columns=["event", "duration"],
    )

    X_test.drop(X_test.columns[0], axis=1, inplace=True)
    X_train.drop(X_test.columns[0], axis=1, inplace=True)

    logger.info("Running inference")

    predictions = model.predict(
        xgboost.DMatrix(X_test.values[:, 1:]), output_margin=False
    )
    normed_predictions = MinMaxScaler().fit_transform(predictions.reshape(-1, 1))

    logger.info("Creating evaluation report")

    # NOTE: technical evaluation is really not as a classifier
    # TO DO: Normalize to 0 to 1 scale
    report_dict = classification_report(
        y_test_df["event"], normed_predictions > args.threshold, output_dict=True
    )
    report_dict["accuracy"] = accuracy_score(
        y_test_df["event"], normed_predictions > args.threshold
    )

    _, y_train_tuple = get_x_y(y_train_df, ["event", "duration"], pos_label=True)
    _, y_test_tuple = get_x_y(y_test_df, ["event", "duration"], pos_label=True)

    concordance_index = concordance_index_ipcw(
        y_train_tuple,
        y_test_tuple,
        predictions,
        tau=args.tau,  # default within 100 days
    )

    report_dict["concordance_index"] = {
        "cindex": float(concordance_index[0]),
        "concordant": int(concordance_index[1]),
        "discordant": int(concordance_index[2]),
        "tied_risk": int(concordance_index[3]),
        "tied_time": int(concordance_index[4]),
    }

    times, score = brier_score(
        y_train_tuple, y_test_tuple, predictions, y_test_df["duration"].max() - 1
    )

    report_dict["brier_score"] = {
        "times": times.astype(np.int32).tolist(),
        "score": score.astype(np.float32).tolist(),
    }

    logger.info(f"Classification report:\n{report_dict}")

    evaluation_output_path = os.path.join(
        "/opt/ml/processing/evaluation", args.report_name
    )
    logger.info(f"Saving classification report to {evaluation_output_path}")

    logger.debug(report_dict)

    with open(evaluation_output_path, "w") as f:
        f.write(json.dumps(report_dict))

    # SHAP
    latest_job_debugger_artifacts_path = "/opt/ml/processing/debug/debug-output"
    trial = create_trial(latest_job_debugger_artifacts_path)

    shap_values = trial.tensor("full_shap/f0").value(trial.last_complete_step)

    pd.DataFrame(shap_values).to_csv(
        os.path.join("/opt/ml/processing/evaluation", args.shap_name)
    )

    shap_no_base = shap_values[1:, :-1]
    feature_names = X_train.columns
    os.makedirs("/opt/ml/processing/plot/", exist_ok=True)
    logger.info(shap_values.shape, shap_no_base.shape, X_train.shape)
    shap.summary_plot(
        shap_no_base, features=X_train, feature_names=feature_names, show=False
    )
    plt.savefig("/opt/ml/processing/plot/feature_importance.png", bbox_inches="tight")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="xgboost-model")
    parser.add_argument("--test-features", type=str, default="test_features.csv")
    parser.add_argument("--train-features", type=str, default="train_features.csv")
    parser.add_argument("--report-name", type=str, default="evaluation.json")
    parser.add_argument("--shap-name", type=str, default="shap.csv")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--tau", type=int, default=100)
    args = parser.parse_args()

    main(args)
