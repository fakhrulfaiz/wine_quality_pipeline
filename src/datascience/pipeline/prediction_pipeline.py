import joblib
import pandas as pd
from pathlib import Path


class PredictionPipeline:
    def __init__(
        self,
        model_path: Path = Path("artifacts/model_trainer/model.joblib"),
        preprocessor_path: Path = Path(
            "artifacts/data_transformation/preprocessor.joblib"
        ),
        feature_columns: list = None,
    ):
        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)

        if feature_columns is not None:
            self.feature_columns = feature_columns
        else:
            from src.datascience.config.configuration import ConfigurationManager
            dt_config = ConfigurationManager().get_data_transformation_config()
            self.feature_columns = dt_config.feature_columns

    def predict(self, data: pd.DataFrame) -> list:
        """
        Parameters
        ----------
        data : pd.DataFrame
            One or more rows with the feature columns defined in schema.yaml.

        Returns
        -------
        list of predictions (wine quality scores).
        """
        data = data[self.feature_columns]     # enforce schema-driven column order
        scaled = self.preprocessor.transform(data)
        predictions = self.model.predict(scaled)
        return predictions.tolist()
