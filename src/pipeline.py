from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "transactions.csv"
OUTPUT = ROOT / "data" / "audit_findings.csv"

def load_data():
    df = pd.read_csv(INPUT, parse_dates=["date", "vendor_created_date"])
    required = ["transaction_id","invoice_id","date","vendor_id","amount"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df

def engineer_features(df):
    x = df.copy()
    x["hour"] = x["date"].dt.hour
    x["day_of_week"] = x["date"].dt.dayofweek
    x["is_weekend"] = x["day_of_week"] >= 5
    x["is_out_of_hours"] = (x["hour"] < 7) | (x["hour"] > 20)

    vendor_mean = x.groupby("vendor_id")["amount"].transform("mean")
    x["vendor_amount_deviation"] = x["amount"] / vendor_mean.replace(0, np.nan)
    x["vendor_amount_deviation"] = x["vendor_amount_deviation"].fillna(1)

    x["vendor_age_days"] = (x["date"] - x["vendor_created_date"]).dt.days
    x["is_new_vendor"] = x["vendor_age_days"] <= 7

    x["is_round_amount"] = (x["amount"] % 10000 == 0)
    x["duplicate_invoice"] = x.duplicated("invoice_id", keep=False)

    # Detect multiple payments close to an approval threshold.
    x["threshold_splitting"] = (
        x.groupby(["vendor_id", "employee_id"])["amount"]
         .transform(lambda s: ((s >= 90000) & (s < 100000)).astype(int).sum() >= 2)
    )
    return x

def run_ml(x):
    features = [
        "amount","hour","day_of_week","vendor_amount_deviation",
        "vendor_age_days"
    ]
    matrix = x[features].replace([np.inf, -np.inf], np.nan).fillna(0)
    model = IsolationForest(
        n_estimators=200, contamination=0.20, random_state=42
    )
    model.fit(matrix)
    raw = -model.decision_function(matrix)
    # Normalize to a readable 0–100 anomaly score.
    score = 100 * (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)
    x["ml_anomaly_score"] = score.round(1)
    x["ml_anomaly"] = model.predict(matrix) == -1
    return x

def risk_engine(x):
    rules = []
    scores = []
    levels = []

    for _, r in x.iterrows():
        reasons, score = [], 0
        if r["duplicate_invoice"]:
            reasons.append("Duplicate invoice detected"); score += 30
        if r["is_weekend"]:
            reasons.append("Weekend transaction"); score += 10
        if r["is_out_of_hours"]:
            reasons.append("Outside normal business hours"); score += 15
        if r["threshold_splitting"]:
            reasons.append("Potential threshold splitting"); score += 20
        if r["is_new_vendor"]:
            reasons.append("Vendor recently created"); score += 10
        if r["is_round_amount"]:
            reasons.append("Round-number transaction"); score += 5
        if r["vendor_amount_deviation"] >= 3:
            reasons.append("Amount is unusually high for vendor"); score += 20
        if r["ml_anomaly"]:
            reasons.append("Isolation Forest anomaly"); score += 25

        score = min(100, score)
        level = "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
        rules.append("; ".join(reasons) if reasons else "No significant rule triggered")
        scores.append(score)
        levels.append(level)

    x["risk_reasons"] = rules
    x["risk_score"] = scores
    x["risk_level"] = levels
    x["audit_action"] = np.where(
        x["risk_score"] >= 60,
        "Request invoice, verify vendor and approval chain, compare purchase order",
        "Routine review"
    )
    return x

def main():
    df = load_data()
    df = engineer_features(df)
    df = run_ml(df)
    df = risk_engine(df)
    df.to_csv(OUTPUT, index=False)
    print(f"Created {OUTPUT}")
    print(df[["transaction_id","amount","risk_score","risk_level","risk_reasons"]].sort_values("risk_score", ascending=False).to_string(index=False))

if __name__ == "__main__":
    main()
