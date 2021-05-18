from sagemaker.local import LocalSession
from sagemaker.sklearn.estimator import SKLearn

sagemaker_session = LocalSession()
sagemaker_session.config = {"local": {"local_code": True}}

# For local training a dummy role will be sufficient
role = "arn:aws:iam::111111111111:role/service-role/"
role = role + "AmazonSageMaker-ExecutionRole-20200101T000001"

sklearn = SKLearn(
    entry_point="/home/ec2-user/SageMaker/surv/train.py",
    framework_version="0.23-1",
    instance_type="local",
    role=role,
    base_job_name="training_job",
    sagemaker_session=sagemaker_session,
)

# sklearn.fit({"train": train_data_location, "test": test_data_location})

training_job_description = sklearn.jobs[-1].describe()
training_output_config = training_job_description["ModelArtifacts"]

print(training_output_config)
