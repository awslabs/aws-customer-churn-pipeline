#!/usr/bin/env bash

###################################################################
# This script builds the long living infrastructure for the project.
# It creates S3 bucket and 3 cloudformation stacks related to- 
# 1) Athena, 2) Glue and 3) application CI/CD pipeline.
# It is created once at the initation of the churn application. 
###################################################################

#source environment variables
source .env 

#Create S3 bucket
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
S3_BUCKET_NAME=${S3_BUCKET_NAME}-${ACCOUNT_ID}-${REGION}

DATABASE=$S3_BUCKET_NAME

echo "stack name=${STACK_NAME}"
echo "bucket name=${S3_BUCKET_NAME}"
echo "region=${REGION}"
echo "database=${DATABASE}"

if aws s3 ls "s3://${S3_BUCKET_NAME}" 2>&1 | grep -q 'NoSuchBucket'
then
echo "S3 bucket does not exist. Creating..."
aws s3api create-bucket --bucket ${S3_BUCKET_NAME} --region ${REGION}
fi

# Create cfn stack 1 - Athena
echo "01) Building the Athena Workgroup..."

# will not run if primary workgroup already exists!
aws cloudformation --region ${REGION} create-change-set --stack-name ${STACK_NAME}-athena \
--change-set-name ImportChangeSet --change-set-type IMPORT \
--resources-to-import "[{\"ResourceType\":\"AWS::Athena::WorkGroup\",\"LogicalResourceId\":\"AthenaPrimaryWorkGroup\",\"ResourceIdentifier\":{\"Name\":\"primary\"}}]" \
--template-body file://cfn/01-athena.yaml --parameters ParameterKey="DataBucketName",ParameterValue=${S3_BUCKET_NAME} > /dev/null

sleep 30

aws cloudformation --region ${REGION} execute-change-set --change-set-name ImportChangeSet --stack-name ${STACK_NAME}-athena > /dev/null

# Create cfn stack 2 - Glue
echo "02) Building Glue resources..."

aws cloudformation --region ${REGION} create-stack \
--stack-name ${STACK_NAME}-glue \
--template-body file://./cfn/02-crawler.yaml \
--capabilities CAPABILITY_NAMED_IAM \
--parameters ParameterKey=RawDataBucketName,ParameterValue=${S3_BUCKET_NAME} \
ParameterKey=CrawlerName,ParameterValue=crawler-${STACK_NAME} > /dev/null

# need to wait for cloudformation to finish to kick off job
sleep 45

# sync demo data to s3
aws s3 sync ./data s3://${S3_BUCKET_NAME}/demo/ 
# start glue crawler
aws glue --region ${REGION} start-crawler --name crawler-${STACK_NAME} > /dev/null

# Create cfn stack 3 - CI/CD pipeline
echo "03) Building CI/CD pipeline..."

aws cloudformation deploy\
    --template-file "cfn/03-CICDpipeline.yaml"\
    --s3-bucket "$S3_BUCKET_NAME"\
    --s3-prefix "codepipeline/churn"\
    --region "$REGION"\
    --stack-name "${STACK_NAME}-CICD"\
    --parameter-overrides\
    pEnvironment="dev"\
    pSourceBucket="$S3_BUCKET_NAME" \
    pBranchName="main" \
    pRegion="$REGION" \
    pStackname="$STACK_NAME" \
    pCoxph="$COXPH" \
    --capabilities CAPABILITY_NAMED_IAM