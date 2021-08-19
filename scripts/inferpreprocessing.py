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
install("awswrangler==2.4.0")
os.system("conda install -c conda-forge hdbscan -y")
install("Amazon-DenseClus==0.0.7")

import awswrangler as wr
import boto3
import joblib
import pandas as pd
from denseclus import DenseClus
from sklearn.exceptions import DataConversionWarning

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
        coxph (bool): Flag indicating that it's a cox proportional hazard model,
        default False
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

    df = df.drop(["area code", "phone"], 1)
    df = df.dropna()

    if args.coxph:
        del df["account length"]

    # no fit predict method currently supported for DenseClus
    # See: https://github.com/awslabs/amazon-denseclus/issues/4
    if args.cluster:

        logger.info("Clustering data")
        clf = DenseClus()
        clf.fit(df)
        logger.info("Clusters fit")

        df["segments"] = clf.score()
        df["segments"] = df["segments"].astype(str)

    logger.info("Load Preprocessing Model")
    preprocess = joblib.load("/opt/ml/processing/transformer/preprocessor.joblib")

    logger.info("Running feature engineering transformations")
    test_features = preprocess.transform(df)

    logger.info(f"Infer data shape after preprocessing: {test_features.shape}")

    test_features_output_path = os.path.join(
        "/opt/ml/processing/infer", "infer_features.csv"
    )
    if isinstance(test_features, pd.DataFrame):
        test_features.to_csv(test_features_output_path, header=False, index=False)
    else:
        pd.DataFrame(test_features).to_csv(
            test_features_output_path, header=False, index=False
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=str, required=True)
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--table", type=str, required=True)
    parser.add_argument("--coxph", type=bool, default=False)
    parser.add_argument(
        "--cluster",
        default=True,
        type=bool,
        help="Run clusters as part of preprocessing",
    )
    args = parser.parse_args()

    main(args)
