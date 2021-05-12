### Inference Preprocessing

In this step, you load the saved preprocesser and transform the data so that it’s in the proper format to run churn inference on.

Same as the training pipeline this is triggered by the invocation of an Amazon Lambda.

```
aws lambda --region ${REGION} invoke --function-name invokeInferStepFunction --payload "{ '': ''}" out
```

Same as before, job kickoff success is indicated by the 200 code and the inference pipeline starts to run.

```
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```

A look in the `pipeline.yaml `shows that inference data is assumed to be under the table name `infer`.

```
"ContainerArguments": [
        "--database",
        "${AthenaDatabaseName}",
         "--region",
         "${AWS::Region}",
         "--table",
          "infer"],
```

Same as before, the database name `{AthendaDatabaseName}` is passed in as the name of your stack with `-db` attached. Region set as the region passed to `standup.sh`. Likewise, SageMaker configurations are almost completely the same, with the container image still using SageMaker’s Scikit Learn container.

The exception here is that instead of `scripts/preprocessing.py `you will use `scripts/inferpreprocessing.py`. This script loads the saved training preprocessor from **Training Preprocessor** to use on the new data. Transformed features are then output back to S3 under the prefix `data/intermediate` into your designated S3 bucket.
