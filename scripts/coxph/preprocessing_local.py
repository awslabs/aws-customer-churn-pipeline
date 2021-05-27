from sagemaker.local import LocalSession
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor

sagemaker_session = LocalSession()
sagemaker_session.config = {"local": {"local_code": True}}

# For local training a dummy role will be sufficient
role = "arn:aws:iam::111111111111:role/service-role/"
role = role + "AmazonSageMaker-ExecutionRole-20200101T000001"

processor = SKLearnProcessor(
    framework_version="0.23-1",
    instance_count=1,
    base_job_name="TrainingPreprocessing",
    instance_type="local",
    role=role,
)

# TO DO: possible to write locally instead of to S3? Mock bucket?
print("Starting processing job.")
print(
    """Note: if launching for the first time in local mode,
     container image download might take a few minutes to complete."""
)
processor.run(
    code="preprocessing.py",
    inputs=[
        ProcessingInput(source="data/", destination="/opt/ml/processing/input_data/")
    ],
    outputs=[
        ProcessingOutput(output_name="train_data", source="/opt/ml/processing/train"),
        ProcessingOutput(output_name="test_data", source="/opt/ml/processing/test"),
        ProcessingOutput(
            output_name="preprocessor", source="/opt/ml/processing/transformer"
        ),
    ],
    arguments=[
        "--database",
        #        DATABASE,
        "--region",
        sagemaker_session.boto_region_name,
        "--table",
        #       TABLE,
        "--train-test-split-ratio",
        "0.2",
    ],
)

preprocessing_job_description = processor.jobs[-1].describe()
output_config = preprocessing_job_description["ProcessingOutputConfig"]
print(output_config)
