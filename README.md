# Customer Churn Pipeline on AWS

*A production-focused End to End churn prediction pipeline on AWS*

<img src="images/logo.png" width="321" height="145">

It provides:

- One-click Training and Inference Pipelines for churn prediction
- Preprocessing, Validation, Hyperparameter tuning, and model Explainability all backed into the pipelines
- Amazon Athena and AWS Glue backend that allows for the pipeline to scale on demand and with new data
- End to End Implementation for your own custom churn pipeline

> An [AWS Professional Service](https://aws.amazon.com/professional-services/) open source initiative | aws-proserve-opensource@amazon.com

[![Python Version](https://img.shields.io/badge/python-3.9-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![ActionBuild](https://github.com/awslabs/aws-customer-churn-pipeline/actions/workflows/testing.yaml/badge.svg)
![Release Version](https://img.shields.io/github/v/release/awslabs/aws-customer-churn-pipeline.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Table of contents

- [Customer Churn Pipeline on AWS](#customer-churn-pipeline-on-aws)
  - [Table of contents](#table-of-contents)
  - [Quick Start](#quick-start)
  - [Read The Docs](#read-the-docs)
  - [Solution Architecture](#solution-architecture)
  - [Contributing](#contributing)

## Quick Start

    # Default parameters are in .env file. To run with Cox proportional hazard modeling instead of binary logloss set COXPH to true. 
    Deploy CICD pipeline.
    sh CICD/deploy_infrastructure.sh

    # This creates a code Pipeline that will automatically deploy the application. For the first time, update the pending Github connection manually in the console and release change in churn pipeline. This is a one time approval. 
    https://console.aws.amazon.com/codesuite/settings/connections

    AWS_REGION=$(aws configure get region)

    # Trigger the training pipeline
    aws lambda --region ${AWS_REGION} invoke --function-name invokeTrainingStepFunction --payload '{ "": ""}' out

    # Trigger the inference pipeline
    aws lambda --region ${AWS_REGION} invoke --function-name invokeInferStepFunction --payload '{ "": ""}' out

    # Clean up
    ./delete_resources.sh

To run with Cox proportional hazard modeling instead of binary logloss pass a 4th argument:

`./standup.sh <stack-name> <bucket-name> <region> time`

Clustering or customer segmentation is enabled by default in each Cloud Formation cfn template.

To disable it - go to cnf template and update the `ContainerArguments` under `SageMaker Training Step Preprocessing`, by setting '--cluster' to "False".


## [Read The Docs](https://awslabs.github.io/aws-customer-churn-pipeline/)

[Documentation](https://awslabs.github.io/aws-customer-churn-pipeline/)

In addition, check out the blog posts:

* [Deploying a Scalable End to End Customer Churn Prediction Solution with AWS](https://towardsdatascience.com/deploying-a-scalable-end-to-end-customer-churn-prediction-solution-with-aws-cbf3536be996)!
* [Retain Customers with Time to Event Modeling-Driven Intervention](https://towardsdatascience.com/retain-customers-with-time-to-event-modeling-driven-intervention-de517a39c6e3)

## Solution Architecture

<p align="center">
<img src="images/arch.png" width="480" height="480" class="centerImage">
</p>

## Contributing

For how to Contribute [see here.](https://github.com/awslabs/aws-customer-churn-pipeline/blob/main/CONTRIBUTING.md)
