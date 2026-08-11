-- High-risk transactions
SELECT transaction_id, vendor_id, amount, risk_score, risk_level, risk_reasons
FROM audit_findings
WHERE risk_level IN ('HIGH', 'CRITICAL')
ORDER BY risk_score DESC;

-- Risk by vendor
SELECT vendor_id,
       COUNT(*) AS transactions,
       SUM(amount) AS total_amount,
       AVG(risk_score) AS avg_risk
FROM audit_findings
GROUP BY vendor_id
ORDER BY avg_risk DESC;

-- Risk by department
SELECT department,
       COUNT(*) AS transactions,
       SUM(amount) AS total_amount,
       SUM(CASE WHEN risk_level IN ('HIGH','CRITICAL') THEN 1 ELSE 0 END) AS risky_transactions
FROM audit_findings
GROUP BY department
ORDER BY risky_transactions DESC;
