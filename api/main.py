from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "audit_findings.csv"

app = FastAPI(title="AuditLens API", version="1.0.0")

def get_df():
    if not DATA.exists():
        raise HTTPException(500, "Run `python src/pipeline.py` first.")
    return pd.read_csv(DATA)

@app.get("/")
def root():
    return {"project": "AuditLens", "status": "running"}

@app.get("/findings")
def findings(risk_level: str | None = None):
    df = get_df()
    if risk_level:
        df = df[df["risk_level"].str.upper() == risk_level.upper()]
    return df.to_dict(orient="records")

@app.get("/findings/{transaction_id}")
def finding(transaction_id: str):
    df = get_df()
    row = df[df["transaction_id"] == transaction_id]
    if row.empty:
        raise HTTPException(404, "Transaction not found")
    return row.iloc[0].to_dict()

@app.get("/summary")
def summary():
    df = get_df()
    return {
        "transactions": int(len(df)),
        "total_amount": float(df["amount"].sum()),
        "anomalies": int(df["ml_anomaly"].astype(str).str.lower().eq("true").sum()),
        "high_or_critical": int(df["risk_level"].isin(["HIGH","CRITICAL"]).sum()),
        "critical": int((df["risk_level"] == "CRITICAL").sum())
    }
