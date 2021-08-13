echo $S3_BUCKET_NAME
echo $AWS_REGION
echo $STACK_NAME

if [ $COXPH = true ]
then
    TEMPLATE="cfn/time_to_event_pipeline.yaml"   
else
    TEMPLATE="cfn/classification_pipeline.yaml"
fi 

echo "application template=${TEMPLATE}"

#aws glue --region ${AWS_REGION} start-crawler --name crawler-${STACK_NAME} 

echo "Deploying Training and Inference Pipeline..."


aws cloudformation deploy \
    --stack-name ${STACK_NAME}-pipeline \
    --template-file ${TEMPLATE} \
    --s3-bucket $S3_BUCKET_NAME\
    --s3-prefix "codepipeline/application" \
    --region ${AWS_REGION} \
    --parameter-overrides \
       AthenaDatabaseName=${DATABASE} \
       PipelineBucketName=${S3_BUCKET_NAME} \
    --capabilities CAPABILITY_NAMED_IAM \
    --no-fail-on-empty-changeset


