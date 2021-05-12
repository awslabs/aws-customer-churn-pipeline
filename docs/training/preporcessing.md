# Training Preprocessing Step

An Amazon SageMaker preprocessing job is run on data queried directly from the Amazon Athena table making use of [SageMaker’s Scikit Learn container.](https://github.com/aws/sagemaker-scikit-learn-container)

This step is run using `scripts/preporcessing.py` in the following order:

1. Data is read from the Athena table using [awswrangler](https://github.com/awslabs/aws-data-wrangler)
2. Data is split into training and validation datasets via a randomized split
3. Missing values are imputed and categorical values are one hot-encoded
4. The split and preprocessed datasets are then written back to S3 as csv files
5. The preprocessor is saved for use in the inference pipeline

The preprocessing scripts and Cloud Formation template `pipeline.yaml`’s Step Functions arguments are update-able.
For example, the entry point arguments for the container are set in the CloudFormation as:

```
"ContainerArguments": [
      "--database",
      "${AthenaDatabaseName}",
      "--region",
      "${AWS::Region}",
      "--table",
      "train",
      "--train-test-split-ratio",
      "0.2"],
```

The database name `{AthendaDatabaseName}` is passed in as the name of your stack with `-db` attached. Region is set from the variable you passed to `standup.sh`. The table name defaults to the training data name, in this case, “train”. Lastly, the random split between train and test is set here as a default, with 25% the data held out for testing.

For this blog post, you will leave `pipeline.yaml`’s settings as is. Keep in mind, it’s possible to change all of these configurations based on your data.
