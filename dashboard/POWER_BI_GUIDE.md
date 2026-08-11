# Power BI Dashboard

Import `data/audit_findings.csv`.

## KPI cards
- Total Transactions
- Total Amount
- ML Anomalies
- High/Critical Findings
- Critical Findings

## Recommended visuals
1. Donut: Risk Level distribution
2. Bar chart: Risky transactions by Department
3. Bar chart: Top Vendors by Total Amount
4. Line chart: Transaction Amount by Date
5. Scatter: Amount vs ML Anomaly Score
6. Table: Transaction ID, Vendor, Amount, Risk Score, Risk Level, Risk Reasons
7. Slicers: Date, Department, Vendor, Risk Level

## Investigator interaction
Use the transaction table as the drill-through source. Selecting a transaction should expose
the evidence fields (`risk_reasons`, `ml_anomaly_score`, `vendor_amount_deviation`,
`vendor_age_days`) so an auditor can understand why it was flagged.
