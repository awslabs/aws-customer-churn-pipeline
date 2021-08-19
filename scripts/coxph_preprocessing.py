import argparse
import logging
import os
import subprocess
import sys
import warnings


def install(package):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package]
        # quietly
        ,
        stdout=open(os.devnull, "wb"),
    )


install("scikit-learn==0.24.1")
install("awswrangler==2.4.0")
os.system("conda install -c conda-forge hdbscan -y")
install("Amazon-DenseClus==0.0.7")

import awswrangler as wr
import boto3
import joblib
import numpy as np
import pandas as pd
from denseclus import DenseClus
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import DataConversionWarning
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

warnings.filterwarnings(action="ignore", category=DataConversionWarning)

col_type = {
    "state": "category",
    "account length": "int64",
    "area code": "str",
    "phone": "str",
    "int'l plan": "category",
    "vmail plan": "category",
    "vmail message": "int64",
    "day mins": "float64",
    "day calls": "int64",
    "day charge": "float64",
    "eve mins": "float64",
    "eve calls": "int64",
    "eve charge": "float64",
    "night mins": "float64",
    "night calls": "int64",
    "night charge": "float64",
    "intl mins": "float64",
    "intl calls": "int64",
    "intl charge": "float64",
    "custserv calls": "int64",
    "churn?": "category",
}

columns = list(col_type.keys())
target_col = "churn?"
class_labels = ["True.", "False."]


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
    DATABASE, TABLE, REGION = args.database, args.table, args.region

    logger.info("Querying Athena...")
    boto3.setup_default_session(region_name=f"{REGION}")
    df = wr.athena.read_sql_query(
        f'SELECT * FROM "{TABLE}"', database=DATABASE, ctas_approach=False
    )
    df = df[columns]
    df = df.astype(col_type)
    logger.info(df.dtypes)

    df["event"] = np.where(df["churn?"] == "False.", 0, 1)
    del df["churn?"]
    df = df.rename(columns={"account length": "duration"})

    df = df.drop(["area code", "phone"], 1)
    df = df.dropna()
    df = df.drop_duplicates()

    negative_examples, positive_examples = df["event"].value_counts().values
    print(
        """Data after cleaning: {}
            , {} positive examples, {} negative examples""".format(
            df.shape, positive_examples, negative_examples
        )
    )
    # no fit predict method currently supported for DenseClus
    # See: https://github.com/awslabs/amazon-denseclus/issues/4
    if args.cluster:

        logger.info("Clustering data")
        clf = DenseClus()
        clf.fit(df)
        logger.info("Clusters fit")

        df["segments"] = clf.score()
        df["segments"] = df["segments"].astype(str)

    y = survival_y_cox(df)
    X = df.drop(["event", "duration"], 1)

    logger.info(f"Splitting training and validation by{args.train_test_split_ratio}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.train_test_split_ratio, random_state=args.random_state
    )

    logger.info(X_train.dtypes)

    numerical_idx = X_train.select_dtypes(
        exclude=["object", "category"]
    ).columns.tolist()

    categorical_idx = X_train.select_dtypes(exclude=["float", "int"]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(sparse=False, handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("numerical", numeric_transformer, numerical_idx),
            ("categorical", categorical_transformer, categorical_idx),
        ],
        remainder="passthrough",
    )

    logger.info("Running preprocessing and feature engineering transformations")
    train_features = preprocessor.fit_transform(X_train)
    test_features = preprocessor.transform(X_test)

    logger.info(f"train features size {train_features.shape}")
    logger.info(f"test features size {test_features.shape}")

    # adding back the target as the first columan for XGB
    train_features = np.hstack((y_train.reshape(-1, 1), train_features))
    test_features = np.hstack((y_test.reshape(-1, 1), test_features))

    # getting the feature names
    feature_names = (
        numerical_idx
        + preprocessor.transformers_[1][1]["onehot"].get_feature_names().tolist()
    )

    feature_names = ["target"] + feature_names

    preprocessor_output_path = os.path.join(
        "/opt/ml/processing/transformer", "preprocessor.joblib"
    )
    joblib.dump(preprocessor, preprocessor_output_path)

    train_features_output_path = os.path.join(
        "/opt/ml/processing/train", "train_features.csv"
    )

    test_features_output_path = os.path.join(
        "/opt/ml/processing/test", "test_features.csv"
    )

    logger.info(f"Saving training data to {train_features_output_path}")

    pd.DataFrame(train_features, columns=feature_names).to_csv(
        train_features_output_path, header=True, index=False
    )

    logger.info(f"Saving test data to {test_features_output_path}")
    pd.DataFrame(test_features, columns=feature_names).to_csv(
        test_features_output_path, header=True, index=False
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=str, required=True)
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--table", type=str, required=True)
    parser.add_argument("--train-test-split-ratio", type=float, default=0.20)
    parser.add_argument("--random-state", type=float, default=123)
    parser.add_argument(
        "--cluster",
        default=True,
        type=bool,
        help="Run clusters as part of preprocessing",
    )
    args = parser.parse_args()

    main(args)
