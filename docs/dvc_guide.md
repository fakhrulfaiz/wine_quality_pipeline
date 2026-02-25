# DVC Guide — Wine Quality MLOps Pipeline

This guide walks you through setting up and using DVC with this project,
using DagsHub as the remote storage for both data and pipeline tracking.

---

## Prerequisites

```bash
pip install dvc dvc-s3   # or: pip install "dvc[s3]"
# DagsHub uses an S3-compatible endpoint, so dvc-s3 is required
```

---

## 1. Initialise DVC (one-time)

```bash
# Inside your project root (already a git repo)
dvc init
git add .dvc .dvcignore
git commit -m "initialise dvc"
```

---

## 2. Connect DagsHub as the DVC remote (one-time)

Your DagsHub repo is `https://dagshub.com/fakhrulfaiz/wine_quality_pipeline`.

```bash
dvc remote add origin s3://wine_quality_pipeline
dvc remote modify origin endpointurl https://dagshub.com/fakhrulfaiz/wine_quality_pipeline.s3
dvc remote modify origin --local access_key_id     YOUR_DAGSHUB_TOKEN
dvc remote modify origin --local secret_access_key YOUR_DAGSHUB_TOKEN

dvc remote default origin
```

> **Where to find your token**: DagsHub → profile avatar → Settings → Access Tokens.
> The `--local` flag writes credentials to `.dvc/config.local` which is git-ignored — never commit credentials.

Commit the (non-secret) remote config:

```bash
git add .dvc/config
git commit -m "add dagshub dvc remote"
```

---

## 3. Track raw data with DVC

Instead of committing the CSV to git, let DVC manage it:

```bash
dvc add artifacts/data_ingestion/winequality-red.csv
git add artifacts/data_ingestion/winequality-red.csv.dvc .gitignore
git commit -m "track raw data with dvc"

dvc push   # uploads the file to DagsHub storage
```

> From now on git tracks the `.dvc` pointer file; DagsHub stores the actual bytes.

---

## 4. Define the pipeline in `dvc.yaml`

Create `dvc.yaml` at the project root. Each `stage` maps directly to a step in `main.py`.

```yaml
stages:

  data_ingestion:
    cmd: python -c "
      from src.datascience.pipeline.data_ingestion_pipeline import DataIngestionPipeline;
      DataIngestionPipeline().initiate_data_ingestion()"
    deps:
      - src/datascience/components/data_ingestion.py
      - config/config.yaml
    outs:
      - artifacts/data_ingestion/winequality-red.csv

  data_validation:
    cmd: python -c "
      from src.datascience.pipeline.data_validation_pipeline import DataValidationPipeline;
      DataValidationPipeline().initiate_data_validation()"
    deps:
      - src/datascience/components/data_validation.py
      - artifacts/data_ingestion/winequality-red.csv
      - config/config.yaml
      - schema.yaml
    outs:
      - artifacts/data_validation/status.txt

  data_transformation:
    cmd: python -c "
      from src.datascience.pipeline.data_transformation_pipeline import DataTransformationPipeline;
      DataTransformationPipeline().initiate_data_transformation()"
    deps:
      - src/datascience/components/data_transformation.py
      - artifacts/data_ingestion/winequality-red.csv
      - artifacts/data_validation/status.txt
      - config/config.yaml
      - schema.yaml
    outs:
      - artifacts/data_transformation/train.csv
      - artifacts/data_transformation/test.csv
      - artifacts/data_transformation/preprocessor.joblib

  model_trainer:
    cmd: python -c "
      from src.datascience.pipeline.model_trainer_pipeline import ModelTrainerTrainingPipeline;
      ModelTrainerTrainingPipeline().initiate_model_training()"
    deps:
      - src/datascience/components/model_trainer.py
      - artifacts/data_transformation/train.csv
      - artifacts/data_transformation/test.csv
      - config/config.yaml
      - params.yaml
    params:
      - ElasticNet.alpha
      - ElasticNet.l1_ratio
    outs:
      - artifacts/model_trainer/model.joblib

  model_evaluation:
    cmd: python -c "
      from src.datascience.pipeline.model_evaluation_pipeline import ModelEvaluationPipeline;
      ModelEvaluationPipeline().initiate_model_evaluation()"
    deps:
      - src/datascience/components/model_evaluation.py
      - artifacts/data_transformation/test.csv
      - artifacts/data_transformation/preprocessor.joblib
      - artifacts/model_trainer/model.joblib
      - config/config.yaml
      - params.yaml
    metrics:
      - artifacts/model_evaluation/metrics.json:
          cache: false
```

---

## 5. Run the pipeline

```bash
dvc repro          # runs only stages whose deps/params have changed
dvc repro --force  # forces all stages to re-run regardless
```

**What "change-aware" means in practice:**

| You change | DVC reruns |
|---|---|
| `params.yaml` (alpha / l1_ratio) | `model_trainer` + `model_evaluation` |
| `data_transformation.py` | `data_transformation` + downstream |
| Raw CSV (new data) | All stages from `data_ingestion` down |
| Nothing | Nothing — all stages skipped |

---

## 6. Push artifacts to DagsHub after a run

```bash
dvc push           # pushes all new/changed cached artifacts
git add dvc.lock
git commit -m "update pipeline lock after repro"
git push
```

`dvc.lock` records the exact input/output hashes for the run — commit it so
teammates can reproduce the exact same pipeline state with `dvc repro`.

---

## 7. Reproduce on a new machine / teammate

```bash
git clone https://dagshub.com/fakhrulfaiz/wine_quality_pipeline.git
cd wine_quality_pipeline

dvc remote modify origin --local access_key_id     THEIR_DAGSHUB_TOKEN
dvc remote modify origin --local secret_access_key THEIR_DAGSHUB_TOKEN

dvc pull           # downloads all tracked artifacts from DagsHub
dvc repro          # reruns only stages that are stale
```

---

## 8. Useful day-to-day commands

| Command | Purpose |
|---|---|
| `dvc status` | Show which stages are stale (inputs changed) |
| `dvc dag` | Print the pipeline DAG in the terminal |
| `dvc params diff` | Show parameter changes vs last run |
| `dvc metrics show` | Print `metrics.json` values |
| `dvc metrics diff` | Compare metrics between git commits |
| `dvc push` | Upload new artifacts to DagsHub |
| `dvc pull` | Download artifacts from DagsHub |
| `dvc gc -w` | Remove cached artifacts not used by current workspace |

---

## 9. What to add to `.gitignore`

DVC manages the actual artifact files; Git should only track the pointers:

```
# DVC-managed artifact files (tracked via .dvc files or dvc.lock)
artifacts/data_ingestion/winequality-red.csv
artifacts/data_transformation/train.csv
artifacts/data_transformation/test.csv
artifacts/data_transformation/preprocessor.joblib
artifacts/model_trainer/model.joblib
artifacts/model_evaluation/metrics.json

# DVC cache
.dvc/cache/
.dvc/tmp/
```

---

## 10. How DVC + MLflow (DagsHub) work together

This project already logs to MLflow via DagsHub. DVC and MLflow are complementary:

| Tool | Tracks |
|---|---|
| **DVC** | Pipeline stages, data files, model artifacts, parameters → reproducibility |
| **MLflow** | Experiment runs, metrics per run, model registry → comparison & deployment |

Typical workflow:

```
dvc repro              ← runs the pipeline, skipping unchanged stages
                       ← model_evaluation logs run to MLflow automatically
dvc push               ← pushes artifacts to DagsHub storage
git add dvc.lock && git commit && git push
```

You can then view both the DVC pipeline graph and the MLflow experiment runs
side-by-side on your DagsHub project page.
