# AuditLens — AI-Powered Continuous Audit Analytics

AuditLens is an MVP for continuous audit analytics. It ingests financial transactions,
applies audit rules, detects statistical/ML anomalies with Isolation Forest, combines
signals into a 0–100 risk score, and exposes findings through FastAPI.

## Architecture

CSV → validation/ETL → audit rules + Isolation Forest → risk engine → PostgreSQL/CSV → FastAPI → Power BI

## MVP features
- Duplicate invoice detection
- Weekend/out-of-hours detection
- Round-number detection
- New-vendor detection
- Vendor historical amount deviation
- Isolation Forest anomaly detection
- Explainable 0–100 audit risk score
- FastAPI investigation endpoints

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/pipeline.py
uvicorn api.main:app --reload
```

Open http://127.0.0.1:8000/docs

The generated `data/audit_findings.csv` can be imported into Power BI.
# AuditLens
