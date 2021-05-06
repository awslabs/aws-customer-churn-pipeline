#!/bin/bash

stack_name="your_stack_name"
region_name="your_region_name"

aws cloudformation delete-stack --stack-name ${stack_name}-athena --region ${region_name} > /dev/null 
 
aws cloudformation delete-stack --stack-name ${stack_name}-glue --region ${region_name} > /dev/null
 
aws cloudformation delete-stack --stack-name ${stack_name}-pipeline --region ${region_name} > /dev/null

git checkout delete_resources.sh
