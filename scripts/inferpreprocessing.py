import argparse
import logging
import os
import subprocess
import sys
import warnings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def install(package: str):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install("scikit-learn==0.24.1")
install("sklearn_pandas==2.1.0")
install("awswrangler==2.4.0")

import awswrangler as wr
import boto3
import joblib
from sklearn.exceptions import DataConversionWarning

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
}

columns = list(col_type.keys())


def main(args):
    """
    Runs preprocessing for the example data set
        1. Pulls data from the Athena database
        2. Transforms features using the saved preprocessor
        3. Writes preprocessed data to S3

    Args:
        database (str, required): Athena database to query data from
        table (str, required): Athena table name to query data from
        region (str, required): AWS Region for queries
    """

    logger.info(f"Received arguments {args}")
    DATABASE, TABLE, region = args.database, args.table, args.region

    boto3.setup_default_session(region_name=f"{region}")
    df = wr.athena.read_sql_query(
        f'SELECT * FROM "{TABLE}"', database=DATABASE, ctas_approach=False
    )
    df = df[columns]
    df = df.astype(col_type)
    logger.info(df.dtypes)
    df = df.dropna()

    logger.info("Load Preprocessing Model")
    preprocess = joblib.load("/opt/ml/processing/transformer/preprocessor.joblib")

    logger.info("Running feature engineering transformations")
    test_features = preprocess.transform(df)

    logger.info(f"Infer data shape after preprocessing: {test_features.shape}")

    test_features_output_path = os.path.join(
        "/opt/ml/processing/infer", "infer_features.csv"
    )

    logger.info(f"Saving test data to {test_features_output_path}")
    test_features.to_csv(test_features_output_path, header=False, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=str, required=True)
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--table", type=str, required=True)
    args = parser.parse_args()

    main(args)
