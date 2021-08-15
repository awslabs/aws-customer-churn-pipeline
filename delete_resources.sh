#!/bin/bash

source .env 

stack_name=$STACK_NAME
region_name=$REGION

# delete cloudformation stacks
aws cloudformation delete-stack --stack-name ${stack_name}-athena --region ${region_name} > /dev/null 
aws cloudformation delete-stack --stack-name ${stack_name}-glue --region ${region_name} > /dev/null
aws cloudformation delete-stack --stack-name ${stack_name}-pipeline --region ${region_name} > /dev/null
aws cloudformation delete-stack --stack-name ${stack_name}-CICD --region ${region_name} > /dev/null

# delete S3 bucket and all data
accountnum=$(aws sts get-caller-identity --query Account --output text)
aws s3 rb s3://${S3_BUCKET_NAME}-${accountnum}  --force

# github connection arn
#GITARN=$(aws codestar-connections list-connections --provider-type GitHub --output text | grep "churn_github_conn" | awk '{print $2}')
#aws codestar-connections delete-connection --connection-arn $GITARN

#git checkout delete_resources.sh
