ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

S3_BUCKET_NAME=${S3_BUCKET_NAME}-${ACCOUNT_ID}

TEMPLATE="https://${S3_BUCKET_NAME}.s3.amazonaws.com/cfn/classification_pipeline.yaml"

echo "application template=${TEMPLATE}"

aws glue --region ${REGION} start-crawler --name crawler-${STACK_NAME} > /dev/null

echo "Deploying Training and Inference Pipeline..."

aws cloudformation --region ${REGION}  create-stack \
--stack-name ${STACK_NAME}-pipeline \
--template-url "${TEMPLATE}" \
--capabilities CAPABILITY_NAMED_IAM \
--parameters ParameterKey=AthenaDatabaseName,ParameterValue=${DATABASE} \
ParameterKey=PipelineBucketName,ParameterValue=${S3_BUCKET_NAME} \
--disable-rollback > /dev/null
