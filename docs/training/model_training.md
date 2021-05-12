# Model Training

Now with the best model identified, you will re-train one more time to obtain the fully trained model and output model explainability metrics.

Again, this step uses SageMaker configurations from `pipeline.yaml` to run SageMaker’s XGBoost container image. This time around, training is kicking off with optimized hyperparameters and [SageMaker Debugger](https://sagemaker.readthedocs.io/en/stable/amazon_sagemaker_debugger.html) settings. Running the training job with Debugger, allows for explainability metrics to be output to S3 in addition to a fully trained model.

Explainability metrics show how each feature affects customer churn. Incorporating techniques like [SHAP](https://github.com/slundberg/shap), enables the ability to explain the model as a whole and, more importantly, the ability to look at how scores are determined on an individual customer basis.
