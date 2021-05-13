# Customer Churn Pipeline on AWS

*A production-ready churn prediction pipeline on AWS*



> An [AWS Professional Service](https://aws.amazon.com/professional-services/) open source initiative | aws-proserve-opensource@amazon.com

[![Python Version](https://img.shields.io/badge/python-3.9-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Table of contents

- [Quick Start](#quick-start)
- [Read The Docs](#read-the-docs)
- [Soution Architecture](#solution-architecture)

## Quick Start

    # Set up the resources
    ./standup.sh

    AWS_REGION=$(aws configure get region)

    # Trigger the training pipeline
    aws lambda --region ${AWS_REGION} invoke --function-name invokeTrainingStepFunction --payload '{ "": ""}' out

    # Trigger the inference pipeline
    aws lambda --region ${AWS_REGION} invoke --function-name invokeInferStepFunction --payload '{ "": ""}' out

    # Clean up
    ./delete_resources.sh

## [Read The Docs](https://aws-data-wrangler.readthedocs.io/)

[notebook](notebook/Sample_Churn_Data_ETL.ipynb)

## Solution Architecture

<img src="images/arch.png" width="480" height="480" frameBorder="0" class="giphy-embed" allowFullScreen>

