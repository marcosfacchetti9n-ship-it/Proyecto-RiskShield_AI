from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "synthetic_transactions.csv"


def generate_synthetic_transactions(
    rows: int = 5_000,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    amounts = np.round(rng.lognormal(mean=9.5, sigma=1.0, size=rows), 2)
    currencies = rng.choice(["ARS", "USD", "BRL", "CLP"], size=rows, p=[0.72, 0.12, 0.08, 0.08])
    countries = rng.choice(
        ["Argentina", "Brazil", "Chile", "Uruguay", "United States"],
        size=rows,
        p=[0.70, 0.10, 0.08, 0.07, 0.05],
    )
    devices = rng.choice(["mobile", "desktop", "tablet", "unknown"], size=rows, p=[0.62, 0.25, 0.08, 0.05])
    hours = rng.integers(0, 24, size=rows)
    categories = rng.choice(
        ["groceries", "electronics", "travel", "fashion", "gambling", "services"],
        size=rows,
        p=[0.30, 0.18, 0.14, 0.18, 0.05, 0.15],
    )

    fraud_probability = np.full(rows, 0.03)
    fraud_probability += np.where(amounts >= 100_000, 0.23, 0.0)
    fraud_probability += np.where((hours >= 0) & (hours <= 5), 0.14, 0.0)
    fraud_probability += np.where(categories == "electronics", 0.08, 0.0)
    fraud_probability += np.where(categories == "gambling", 0.32, 0.0)
    fraud_probability += np.where(devices == "unknown", 0.18, 0.0)
    fraud_probability += np.where(countries != "Argentina", 0.08, 0.0)
    fraud_probability += np.where(currencies != "ARS", 0.04, 0.0)
    fraud_probability = np.clip(fraud_probability, 0.0, 0.95)

    is_fraud = rng.binomial(1, fraud_probability)

    return pd.DataFrame(
        {
            "amount": amounts,
            "currency": currencies,
            "country": countries,
            "device": devices,
            "hour": hours,
            "merchant_category": categories,
            "is_fraud": is_fraud,
        }
    )


def save_dataset(output_path: Path, rows: int, seed: int) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = generate_synthetic_transactions(rows=rows, seed=seed)
    dataset.to_csv(output_path, index=False)
    return output_path


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Generate synthetic transactions for ML training.")
    parser.add_argument("--rows", type=int, default=5_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser


if __name__ == "__main__":
    args = parse_args().parse_args()
    path = save_dataset(output_path=args.output, rows=args.rows, seed=args.seed)
    print(f"Synthetic dataset saved to {path}")
