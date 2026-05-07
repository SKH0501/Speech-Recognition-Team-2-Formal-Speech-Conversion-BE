from pathlib import Path
from typing import Dict, Any
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "models" / "formality_classifier.joblib"


class FormalityClassifier:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found: {MODEL_PATH}. "
                "Run train_classifier.py first."
            )
        self.model = joblib.load(MODEL_PATH)

    def predict(self, text: str, category: str, target_role: str) -> Dict[str, Any]:
        row = pd.DataFrame(
            [{
                "text": text,
                "category": category,
                "target_role": target_role,
            }]
        )

        pred = self.model.predict(row)[0]

        confidence = None
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(row)[0]
            classes = list(self.model.classes_)
            class_to_prob = dict(zip(classes, probs))
            confidence = float(class_to_prob.get(pred, max(probs)))
        else:
            confidence = 0.5

        return {
            "label": pred,  # appropriate / inappropriate
            "confidence": confidence,
        }


_classifier_instance: FormalityClassifier | None = None


def get_classifier() -> FormalityClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FormalityClassifier()
    return _classifier_instance