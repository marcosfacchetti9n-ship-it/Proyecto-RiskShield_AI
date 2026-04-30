from argparse import ArgumentParser
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ML_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET_PATH = ML_DIR / "data" / "synthetic_transactions.csv"
DEFAULT_MODEL_PATH = ML_DIR / "model.joblib"

NUMERIC_FEATURES = ["amount", "hour"]
CATEGORICAL_FEATURES = ["currency", "country", "device", "merchant_category"]
TARGET = "is_fraud"


def train_model(dataset_path: Path, model_path: Path) -> None:
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Run generate_dataset.py first."
        )

    dataset = pd.read_csv(dataset_path)
    features = dataset[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    target = dataset[TARGET]

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.20,
        random_state=42,
        stratify=target,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    model = LogisticRegression(max_iter=1_000, class_weight="balanced")
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    print("Model metrics")
    print(f"accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(f"precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
    print(f"recall: {recall_score(y_test, predictions, zero_division=0):.4f}")
    print(f"f1-score: {f1_score(y_test, predictions, zero_division=0):.4f}")
    print()
    print(classification_report(y_test, predictions, zero_division=0))

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Train the transaction fraud model.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_PATH)
    return parser


if __name__ == "__main__":
    args = parse_args().parse_args()
    train_model(dataset_path=args.dataset, model_path=args.model_output)
