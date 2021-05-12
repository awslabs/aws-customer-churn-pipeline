# Hyperparameter Tuning

The Hyperparameter tuning step finds an optimal combination of hyperparmaters for your model. In this example, you use [XGBoost](https://en.wikipedia.org/wiki/XGBoost) to model churn as a binary outcome (will churn / will not churn). Specifically, you are going to try to achieve the highest accuracy possible through maximizing the [Area Under the Curve](https://en.wikipedia.org/wiki/Receiver_operating_characteristic), finding the best regularization terms, depth and tree splitting combinations in repeated parallel runs (defaulted at 2 total). This produces the most accurate model given the available data.

It’s worth noting that there is no script here. All configurations are passed as JSON directly to SageMaker in `pipeline.yaml`, using [SageMaker’s XGBoost container](https://github.com/aws/sagemaker-xgboost-container). As before, defaults are hardcoded. However, like all parts of the pipeline, these are updatable as needed. For a deeper look on HyperParameter Tuning with Amazon SageMaker and the the type of inputs possible see [here](https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning.html).

After this, a Lambda function is called to record the best performing model (and hyperparameter configurations) and then passes it on to the next step in the Step Functions workflow.
