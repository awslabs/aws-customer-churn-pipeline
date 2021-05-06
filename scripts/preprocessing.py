import argparse
import os
import subprocess
import sys
import warnings


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install("scikit-learn==0.24.1")
install("sklearn_pandas==2.1.0")
install("awswrangler==2.4.0")

import awswrangler as wr
import boto3
import joblib
import pandas as pd
from sklearn.exceptions import DataConversionWarning
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn_pandas import DataFrameMapper

warnings.filterwarnings(action="ignore", category=DataConversionWarning)

col_type = {
    "state": "category",
    "account length": "int64",
    "area code": "str",
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


def split_col_dtype(col_type, target_label):
    cat, num = [], []
    for k, v in col_type.items():
        if k == target_label:
            continue
        if v != "category":
            num.append(k)
        else:
            cat.append(k)
    return cat, num


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=str, required=True)
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--table", type=str, required=True)
    parser.add_argument("--train-test-split-ratio", type=float, default=0.25)
    args = parser.parse_args()

    print(f"Received arguments {args}")
    DATABASE, TABLE, region = args.database, args.table, args.region

    boto3.setup_default_session(region_name=f"{args.region}")
    df = wr.athena.read_sql_query(
        f'SELECT * FROM "{TABLE}"', database=DATABASE, ctas_approach=False
    )
    df = df[columns]
    df = df.astype(col_type)
    print(df.dtypes)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df[target_col] = df[target_col].replace(class_labels, [1, 0])

    negative_examples, positive_examples = df[target_col].value_counts().values
    print(
        """Data after cleaning: {}
        , {} positive examples, {} negative examples""".format(
            df.shape, positive_examples, negative_examples
        )
    )

    split_ratio = args.train_test_split_ratio
    print(f"Splitting data into train and test sets with ratio {split_ratio}")
    X_train, X_test, y_train, y_test = train_test_split(
        df.drop(target_col, axis=1),
        df[target_col],
        test_size=split_ratio,
        random_state=0,
    )
    print(X_train.dtypes)

    cat, num = split_col_dtype(col_type, target_col)
    preprocess = DataFrameMapper(
        [([col], [SimpleImputer(strategy="median"), StandardScaler()]) for col in num]
        + [
            (
                [col],
                [
                    SimpleImputer(strategy="constant", fill_value="missing"),
                    OneHotEncoder(handle_unknown="ignore"),
                ],
            )
            for col in cat
        ]
        + [],
        df_out=True,
    )
    print("Running preprocessing and feature engineering transformations")
    train_features = preprocess.fit_transform(X_train)
    test_features = preprocess.transform(X_test)

    preprocessor_output_path = os.path.join(
        "/opt/ml/processing/transformer", "preprocessor.joblib"
    )
    joblib.dump(preprocess, preprocessor_output_path)

    print(f"Train data shape after preprocessing: {train_features.shape}")
    print(f"Test data shape after preprocessing: {test_features.shape}")

    train_features_output_path = os.path.join(
        "/opt/ml/processing/train", "train_features.csv"
    )

    test_features_output_path = os.path.join(
        "/opt/ml/processing/test", "test_features.csv"
    )

    print(f"Saving training data to {train_features_output_path}")
    pd.concat([y_train, train_features], axis=1).to_csv(
        train_features_output_path, header=True, index=False
    )

    print(f"Saving test data to {test_features_output_path}")
    pd.concat([y_test, test_features], axis=1).to_csv(
        test_features_output_path, header=True, index=False
    )
