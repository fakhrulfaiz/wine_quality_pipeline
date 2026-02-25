# Wine Quality Prediction — MLOps Pipeline

End-to-end ML pipeline for predicting red wine quality scores, built with a modular MLOps architecture.

## Stack

- **Preprocessing** — scikit-learn `Pipeline` + `StandardScaler`
- **Model** — ElasticNet (scikit-learn)
- **Experiment Tracking** — MLflow + DagsHub
- **Pipeline Orchestration** — DVC
- **Serving** — Flask

## Pipeline Stages

| Stage | Component | Output Artifact |
|---|---|---|
| Data Ingestion | `data_ingestion.py` | `artifacts/data_ingestion/winequality-red.csv` |
| Data Validation | `data_validation.py` | `artifacts/data_validation/status.txt` |
| Data Transformation | `data_transformation.py` | `train.csv`, `test.csv`, `preprocessor.joblib` |
| Model Training | `model_trainer.py` | `artifacts/model_trainer/model.joblib` |
| Model Evaluation | `model_evaluation.py` | `metrics.json` + MLflow run on DagsHub |

## Quickstart

```bash
pip install -r requirements.txt

# Run full pipeline
python main.py

# Start web app
python app.py
```

## Development Workflow

When adding a new feature or stage, update in this order:

1. `config/config.yaml` — file paths and directories
2. `schema.yaml` — column names and types
3. `params.yaml` — model hyperparameters
4. `entity/config_entity.py` — dataclass for the new config
5. `config/configuration.py` — read and return the new config
6. `components/` — processing or training logic
7. `pipeline/` — wire the component into a pipeline stage
8. `main.py` — add the stage to the full run
9. `app.py` — expose via the web interface if needed

## MLflow & DagsHub

Metrics and model artifacts (including `preprocessor.joblib`) are logged to DagsHub on every evaluation run.

```
https://dagshub.com/fakhrulfaiz/wine_quality_pipeline
```

## DVC

See [`docs/dvc_guide.md`](docs/dvc_guide.md) for setup and usage with DagsHub remote storage.
