# End-to-End Data Science Project

This repository contains a production-ready, modular Machine Learning project.

## 🏗️ ML Pipeline Architecture

The automated pipeline follows these sequential stages:

1. **Data Ingestion:** Fetching data from the source (databases, APIs, or local storage).
2. **Data Validation:** Checking data quality, schema, and identifying anomalies.
3. **Data Transformation:** Feature engineering, scaling, and data preprocessing.
4. **Model Trainer:** Training the machine learning algorithm.
5. **Model Evaluation:** Tracking metrics, experimenting, and registering models using **MLflow** and **DagsHub**.
6. **Deployment:** Serving the model via an API or Web Application (Flask/FastAPI).

## 🛠️ Development Workflow

When building a new component or adding a feature, follow these exact steps to maintain the modular architecture:

1. Update `config/config.yaml` (Define file paths and directory structures)
2. Update `schema.yaml` (Define data columns and data types)
3. Update `params.yaml` (Define model hyperparameters)
4. Update the **Entity** (`src/project_name/entity/config_entity.py` - Define data classes for the configs)
5. Update the **Configuration Manager** (`src/project_name/config/configuration.py` - Read the yaml files)
6. Update the **Components** (`src/project_name/components/` - Write the actual processing/training logic)
7. Update the **Pipeline** (`src/project_name/pipeline/` - Chain the components together)
8. Update `main.py` (Trigger the pipeline execution)
9. Update `app.py` (Integrate the pipeline with the web interface/API)
