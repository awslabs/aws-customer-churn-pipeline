# Customer Churn Pipeline on AWS

_A python package for deploying an end to end customer churn prediction pipeline on AWS_

For more details see the [documentation](https://awslabs.github.io/aws-customer-churn-pipeline/index.html)

## Getting Started

    # Set up the resources
    ./standup.sh

    AWS_REGION=$(aws configure get region)

    # Trigger the training pipeline
    aws lambda --region ${AWS_REGION} invoke --function-name invokeTrainingStepFunction --payload '{ "": ""}' out

    # Trigger the inference pipeline
    aws lambda --region ${AWS_REGION} invoke --function-name invokeInferStepFunction --payload '{ "": ""}' out

    # Clean up
    ./delete_resources.sh
    

## Notebook Tutorial

[notebook](notebook/Sample_Churn_Data_ETL.ipynb)
