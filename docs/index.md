# **Churn Prediction on AWS**

**An End to End customer churn prediction pipeline on AWS.**

## Features

- One-click Training and Inference Pipelines for churn prediction
- Preprocessing, Validation, Hyperparameter tuning, and model Explainability all backed into the pipelines
- Amazon Athena and AWS Glue backend that allows for the pipeline to scale on demand and with new data
- Reference implementation for your own custom churn pipeline
- MIT License

![](../images/arch.png)

## Getting Started

```
# Set up the resources
./stand_up.sh

AWS_REGION=$(aws configure get region)

# Trigger the training pipeline
aws lambda --region ${AWS_REGION} invoke --function-name invokeTrainingStepFunction --payload '{ "": ""}' out

# Trigger the inference pipeline
aws lambda --region ${AWS_REGION} invoke --function-name invokeInferStepFunction --payload '{ "": ""}' out

# Clean up
./delete_resources.sh
```

## Dependencies

Before you get started, you will first need an AWS account setup with credentials configured, as explained in this [documentation](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html). In addition, make sure the [AWS Command Line Interface](https://aws.amazon.com/cli/) AWS CLI is already installed. This tutorial assumes that you have an environment with the necessary [Identity Access Management IAM permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started.html).

For MAC users the easiest way is to Brew install the AWS CLI:

```
brew install awscli
```

The you can configure credentials with:

```
aws configure
```

For OSes and more info please see the links above.

## Contributing

New features should be discussed first and we also want to prevent
that two people are working on the same thing. To get started locally, you can clone
the repo and quickly get started using the `Makefile`.

### Bugs

If you encounter a bug, we'd love to hear about it!
We would appreciate though if you could add a reproducible
example when you [submit an issue on github](https://github.com/awslabs/amazon-sagemaker-customer-churn-pipeline/issues/new/choose).

We've included some methods to our library to make this
relatively easy. Here's an example of a reproducible code-block.

## FAQ

### Why this solution?

We've seen customers struggling at getting churn setup and running smoothly into production.
This framework serves as a good starting point on the technical side.
