from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "formality_train.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "formality_classifier.joblib"


FEATURE_COLUMNS = ["text", "category", "target_role", "turn_type"]
TARGET_COLUMNS = ["contextMatch", "politenessLevel", "naturalness"]


def main():
    df = pd.read_csv(DATA_PATH, encoding="utf-8")

    required_cols = set(FEATURE_COLUMNS + TARGET_COLUMNS)
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # 혹시 True/False가 bool로 읽혀도 문자열 라벨로 통일
    df["contextMatch"] = df["contextMatch"].astype(str)
    df["politenessLevel"] = df["politenessLevel"].astype(str).str.upper()
    df["naturalness"] = df["naturalness"].astype(str).str.upper()

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMNS]

    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(ngram_range=(1, 2)), "text"),
            (
                "meta",
                OneHotEncoder(handle_unknown="ignore"),
                ["category", "target_role", "turn_type"],
            ),
        ]
    )

    base_classifier = LogisticRegression(max_iter=1000)

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", MultiOutputClassifier(base_classifier)),
        ]
    )

    model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Saved model to {MODEL_PATH}")
    print(f"Features: {FEATURE_COLUMNS}")
    print(f"Targets: {TARGET_COLUMNS}")


if __name__ == "__main__":
    main()