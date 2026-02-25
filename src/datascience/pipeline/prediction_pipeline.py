import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class PredictionPipeline:
    def __init__(
        self,
        model_path: Path = Path("artifacts/model_trainer/model.joblib")
    ):
        self.model_path = model_path
        self.model = self._load_model()
        
    def predict(self, data):
        prediction  = self.model.predict(data)
        return prediction

    