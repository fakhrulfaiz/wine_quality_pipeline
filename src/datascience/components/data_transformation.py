import os
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.datascience import logger
from src.datascience.entity.config_entity import DataTransformationConfig


def build_preprocessor() -> Pipeline:
    """
    Returns a fitted-ready sklearn Pipeline.

    StandardScaler is essential for ElasticNet (and any L1/L2 regularised
    model) because regularisation penalises coefficient magnitude; unscaled
    features skew those penalties dramatically.
    """
    return Pipeline(steps=[("scaler", StandardScaler())])


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def train_test_spliting(self):
        data = pd.read_csv(self.config.data_path)
        feature_cols = self.config.feature_columns
        target_col = [c for c in data.columns if c not in feature_cols][0]

        train, test = train_test_split(data, test_size=0.25, random_state=42)
        logger.info(f"Train shape: {train.shape} | Test shape: {test.shape}")

        # ── Fit preprocessor on train features only ──────────────────────────
        preprocessor = build_preprocessor()
        preprocessor.fit(train[feature_cols])

        # ── Transform both splits ─────────────────────────────────────────────
        train_scaled = pd.DataFrame(
            preprocessor.transform(train[feature_cols]),
            columns=feature_cols,
        )
        train_scaled[target_col] = train[target_col].values

        test_scaled = pd.DataFrame(
            preprocessor.transform(test[feature_cols]),
            columns=feature_cols,
        )
        test_scaled[target_col] = test[target_col].values

        # ── Persist preprocessor ──────────────────────────────────────────────
        os.makedirs(os.path.dirname(self.config.preprocessor_path), exist_ok=True)
        joblib.dump(preprocessor, self.config.preprocessor_path)
        logger.info(f"Preprocessor saved to: {self.config.preprocessor_path}")

        # ── Persist split data ────────────────────────────────────────────────
        train_scaled.to_csv(
            os.path.join(self.config.root_dir, "train.csv"), index=False
        )
        test_scaled.to_csv(
            os.path.join(self.config.root_dir, "test.csv"), index=False
        )
        logger.info("Scaled train/test CSVs written to artifacts/data_transformation/")

        return Path(self.config.preprocessor_path)
