## Inference: Batch Transform

Now that the inference dataset is in the proper format you can get churn predictions.
This next step make use of [Amazon SageMaker’s Batch Transform](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html) feature to directly run the inference as a batch job and then writes the data results to S3 into the prefix `/data/inference_result`.
