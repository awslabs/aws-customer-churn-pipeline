#!/bin/bash

conda create -n churn python=3.8 -y
source activate churn

conda install -c conda-forge shap -y
conda install -c sebp scikit-survival -y
conda install -c conda-forge xgboost -y
python3 -m pip install matplotlib graphviz lifelines seaborn
conda install ipykernel -y

echo "packages installed"

# create the kernel
python3 -m ipykernel install --user --name churn --display-name "churn-kernel"

echo "kernel installed"
# deactivete
conda deactivate churn

# to save this enviroment you can:
#conda env export > environment.yml
