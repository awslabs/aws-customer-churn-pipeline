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

    # Step 1 - Verify default parameters are in .env file. To run with Cox proportional hazard modeling instead of binary logloss set COXPH to 'positive'. 

    # Step 2 - Deploy infrastructure. 
    ./standup.sh

    # Step 3 - Update the pending Github connection manually in the console and release change in churn pipeline. This is a one time approval. 
  <p align="center">
  <img src="images/UpdateConn.png" width="480" height="480" class="centerImage">
  </p>

  <p align="center">
  <img src="images/ReleaseChange.png" width="480" height="480" class="centerImage">
  </p>

    # Step 4 - Once the build succeeds, navigate to Step Functions to verify completion

    # Step 5 - Trigger Inference pipeline. This can be further scheduled based on cron jobs or S3 triggers as required. 
    
    AWS_REGION=$(aws configure get region)

    aws lambda --region ${AWS_REGION} invoke --function-name invokeInferStepFunction --payload '{ "": ""}' out

    # Clean up
    ./delete_resources.sh

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
