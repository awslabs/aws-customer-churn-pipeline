#!/bin/bash

source .env 

stack_name=$STACK_NAME
region_name=$REGION

aws cloudformation delete-stack --stack-name ${stack_name}-athena --region ${region_name} > /dev/null 
 
aws cloudformation delete-stack --stack-name ${stack_name}-glue --region ${region_name} > /dev/null
 
aws cloudformation delete-stack --stack-name ${stack_name}-pipeline --region ${region_name} > /dev/null

aws cloudformation delete-stack --stack-name ${stack_name}-CICD --region ${region_name} > /dev/null

#git checkout delete_resources.sh
