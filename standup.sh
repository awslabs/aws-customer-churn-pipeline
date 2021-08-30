#!/bin/bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION_DEFAULT=$(aws configure get region)
STACK_NAME_DEFAULT=customer-churn-sagemaker-pipeline

STACK_NAME=${1:-${STACK_NAME_DEFAULT}}
S3_BUCKET_NAME=${2:-train-inference-pipeline-${ACCOUNT_ID}}
REGION=${3:-${REGION_DEFAULT}}
TIME_TO_EVENT=$4

DATABASE=$S3_BUCKET_NAME

case "$TIME_TO_EVENT" in 

    "time")
        TEMPLATE="https://${S3_BUCKET_NAME}.s3-${REGION}.amazonaws.com/cfn/time_to_event_pipeline.yaml"
        echo $TEMPLATE
    ;;
    *)
        TEMPLATE="https://${S3_BUCKET_NAME}.s3-${REGION}.amazonaws.com/cfn/classification_pipeline.yaml"
        echo $TEMPLATE 
    ;;
esac

echo "stack name=${STACK_NAME}"
echo "bucket name=${S3_BUCKET_NAME}"
echo "region=${REGION}"
echo "database=${DATABASE}"
echo "template=${TEMPLATE}"

echo "Uploading local data to S3..."

aws s3 sync ./data s3://${S3_BUCKET_NAME}/demo/ > /dev/null

echo "Building the Athena Workgroup..."

# will not run if primary workgroup already exists!
aws cloudformation --region ${REGION} create-change-set --stack-name ${STACK_NAME}-athena \
--change-set-name ImportChangeSet --change-set-type IMPORT \
--resources-to-import "[{\"ResourceType\":\"AWS::Athena::WorkGroup\",\"LogicalResourceId\":\"AthenaPrimaryWorkGroup\",\"ResourceIdentifier\":{\"Name\":\"primary\"}}]" \
--template-body file://cfn/01-athena.yaml --parameters ParameterKey="DataBucketName",ParameterValue=${S3_BUCKET_NAME} > /dev/null

sleep 15

aws cloudformation --region ${REGION} execute-change-set --change-set-name ImportChangeSet --stack-name ${STACK_NAME}-athena > /dev/null

echo "Building Glue resources..."

aws cloudformation --region ${REGION} create-stack \
--stack-name ${STACK_NAME}-glue \
--template-body file://./cfn/02-crawler.yaml \
--capabilities CAPABILITY_NAMED_IAM \
--parameters ParameterKey=RawDataBucketName,ParameterValue=${S3_BUCKET_NAME} \
ParameterKey=CrawlerName,ParameterValue=crawler-${STACK_NAME} > /dev/null

echo "Uploading Step Function Scripts to S3..."

aws s3 sync ./scripts s3://${S3_BUCKET_NAME}/script/ > /dev/null

aws s3 sync ./cfn/ s3://${S3_BUCKET_NAME}/cfn/ > /dev/null

# need to wait for cloudformation to finish to kick off job
sleep 45

aws glue --region ${REGION} start-crawler --name crawler-${STACK_NAME} > /dev/null

echo "Deploying Training and Inference Pipeline..."

aws cloudformation --region ${REGION}  create-stack \
--stack-name ${STACK_NAME}-pipeline \
--template-url ${TEMPLATE} \
--capabilities CAPABILITY_NAMED_IAM \
--parameters ParameterKey=AthenaDatabaseName,ParameterValue=${DATABASE} \
ParameterKey=PipelineBucketName,ParameterValue=${S3_BUCKET_NAME} \
--disable-rollback > /dev/null

echo "Writing environment variables to delete the resources file"

sed -i -e "s/your_region_name/${REGION}/g" delete_resources.sh
sed -i -e "s/your_stack_name/${STACK_NAME}/g" delete_resources.sh

rm -rf delete_resources.sh-e
