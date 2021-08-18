#!/bin/bash

source .env 

stack_name=$STACK_NAME
region_name=$REGION

# delete cloudformation stacks
aws cloudformation delete-stack --stack-name ${stack_name}-athena --region ${region_name}  
aws cloudformation delete-stack --stack-name ${stack_name}-glue --region ${region_name} 
aws cloudformation delete-stack --stack-name ${stack_name}-pipeline --region ${region_name} 
# ensure application stack is deleted before CICD stack
# since by default it assumes the last used role which is associated with CICD stack
sleep 30
aws cloudformation delete-stack --stack-name ${stack_name}-CICD --region ${region_name} 

# delete S3 bucket and all data
accountnum=$(aws sts get-caller-identity --query Account --output text)
aws s3 rb s3://${S3_BUCKET_NAME}-${accountnum}  --force

