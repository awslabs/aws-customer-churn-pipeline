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


install("xgboost")
install("smdebug==1.0.5")
install("shap==0.39.0")
install("matplotlib")

import matplotlib.pyplot as plt
import pandas as pd
import shap
import xgboost
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from smdebug.trials import create_trial


def main(args):
    """
    Runs evaluation for the data set
        1. Loads model from tar.gz
        2. Reads in test features
        3. Runs classification accuracy report
        4. Generates feature importance with SHAP

    Args:
        model-name (str, required): Name of the trained model, default xgboost
        test-features (str, required): preprocessed test features for
         evaluation, default test_features.csv
        train-features (str, required): preproceed train features for SHAP,
        default train_features.csv
        report-name (str, required): Name of the evaluation output
        , default evaluation.json
        shap-name (str, required): Name of the SHAP feature importance
        output file, default shap.csv
        threshold (float, required): Threshold to cut probablities at
        , default 0.5


    """

    model_path = os.path.join("/opt/ml/processing/model", "model.tar.gz")
    
    logger.info(f"Extracting model from path: {model_path}")
    
    with tarfile.open(model_path) as tar:
        tar.extractall(path=".")
    logger.info("Loading model")
    with open(args.model_name, "rb") as f:
        model = pickle.load(f)

    logger.info("Loading test input data")
    test_features_data = os.path.join("/opt/ml/processing/test", args.test_features)

    X_test = pd.read_csv(test_features_data, header=0)
    y_test = X_test.iloc[:, 0]
    X_test.drop(X_test.columns[0], axis=1, inplace=True)
    predictions = model.predict(xgboost.DMatrix(X_test.values))

    logger.info("Creating classification evaluation report")
    report_dict = classification_report(
        y_test, predictions > args.threshold, output_dict=True
    )
    report_dict["accuracy"] = accuracy_score(y_test, predictions > args.threshold)
    report_dict["roc_auc"] = roc_auc_score(y_test, predictions)

    logger.info(f"Classification report:\n{report_dict}")

    evaluation_output_path = os.path.join(
        "/opt/ml/processing/evaluation", args.report_name
    )
    logger.info(f"Saving classification report to {evaluation_output_path}")

    with open(evaluation_output_path, "w") as f:
        f.write(json.dumps(report_dict))

    # SHAP
    train_features_data = os.path.join("/opt/ml/processing/train", args.train_features)
    X_train = pd.read_csv(train_features_data, header=0)
    X_train.drop(X_train.columns[0], axis=1, inplace=True)

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
    parser.add_argument(
        "--model-name", type=str, default="xgboost-model", required=True
    )
    parser.add_argument(
        "--test-features", type=str, default="test_features.csv", required=True
    )
    parser.add_argument(
        "--train-features", type=str, default="train_features.csv", required=True
    )
    parser.add_argument(
        "--report-name", type=str, default="evaluation.json", required=True
    )
    parser.add_argument("--shap-name", type=str, default="shap.csv", required=True)
    parser.add_argument("--threshold", type=float, default=0.5, required=True)
    args = parser.parse_args()

    main(args)
