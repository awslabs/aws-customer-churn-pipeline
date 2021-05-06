import json
import os
import pickle
import subprocess
import sys
import tarfile


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

if __name__ == "__main__":
    model_path = os.path.join("/opt/ml/processing/model", "model.tar.gz")
    print(f"Extracting model from path: {model_path}")
    with tarfile.open(model_path) as tar:
        tar.extractall(path=".")
    print("Loading model")
    with open("xgboost-model", "rb") as f:
        model = pickle.load(f)

    print("Loading test input data")
    test_features_data = os.path.join("/opt/ml/processing/test", "test_features.csv")

    X_test = pd.read_csv(test_features_data, header=0)
    y_test = X_test.iloc[:, 0]
    X_test.drop(X_test.columns[0], axis=1, inplace=True)
    predictions = model.predict(xgboost.DMatrix(X_test.values))

    print("Creating classification evaluation report")
    report_dict = classification_report(y_test, predictions > 0.5, output_dict=True)
    report_dict["accuracy"] = accuracy_score(y_test, predictions > 0.5)
    report_dict["roc_auc"] = roc_auc_score(y_test, predictions)

    print(f"Classification report:\n{report_dict}")

    evaluation_output_path = os.path.join(
        "/opt/ml/processing/evaluation", "evaluation.json"
    )
    print(f"Saving classification report to {evaluation_output_path}")

    with open(evaluation_output_path, "w") as f:
        f.write(json.dumps(report_dict))

    # SHAP
    train_features_data = os.path.join("/opt/ml/processing/train", "train_features.csv")
    X_train = pd.read_csv(train_features_data, header=0)
    y_train = X_train.iloc[:, 0]
    X_train.drop(X_train.columns[0], axis=1, inplace=True)

    latest_job_debugger_artifacts_path = "/opt/ml/processing/debug/debug-output"
    trial = create_trial(latest_job_debugger_artifacts_path)

    shap_values = trial.tensor("full_shap/f0").value(trial.last_complete_step)

    pd.DataFrame(shap_values).to_csv("/opt/ml/processing/evaluation/shap.csv")

    shap_no_base = shap_values[1:, :-1]
    shap_base_value = shap_values[0, -1]
    feature_names = X_train.columns
    os.makedirs("/opt/ml/processing/plot/", exist_ok=True)
    print(shap_values.shape, shap_no_base.shape, X_train.shape)
    shap.summary_plot(
        shap_no_base, features=X_train, feature_names=feature_names, show=False
    )
    plt.savefig("/opt/ml/processing/plot/feature_importance.png", bbox_inches="tight")
