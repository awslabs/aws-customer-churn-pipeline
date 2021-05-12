# Evaluate Model Performance

The final step runs a full evaluation on the training and testing data with a report of the results output to S3. The model evaluation step is here as a module because it allows for the customisation of metrics, plots, and hook for different churn use cases.

First, the trained model is loaded directly from its stored S3 URI. It then generates a classification report on the testing data and outputs the results as `evaluation.json` back to S3. Finally, SHAP values and a feature importance plot are output and saved back to S3. Please note, that unlike SageMaker Debugger step in **Training Pipeline** these outputs are sent directly to your named S3 bucket and not a SageMaker default bucket elsewhere.
