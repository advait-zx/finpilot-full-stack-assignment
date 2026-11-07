-- 1. Top 10 customers by current snapshot AUM
SELECT c.customer_id, c.full_name, ROUND(SUM(v.market_value), 2) AS aum
FROM portfolio_positions_v v
JOIN customers c ON c.customer_id = v.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY aum DESC
LIMIT 10;

-- 2. Asset allocation for one customer
SELECT asset_class, ROUND(SUM(market_value), 2) AS market_value
FROM portfolio_positions_v
WHERE customer_id = 'C0001'
GROUP BY asset_class
ORDER BY market_value DESC;

-- 3. Monthly settled BUY/SELL net cash flow for the last 12 months.
-- BUY is treated as an outflow and SELL as an inflow.
SELECT date_trunc('month', trade_date) AS month,
       ROUND(SUM(CASE WHEN transaction_type = 'SELL' THEN amount
                      WHEN transaction_type = 'BUY' THEN -amount ELSE 0 END), 2) AS net_cash_flow
FROM transactions
WHERE status = 'SETTLED'
  AND transaction_type IN ('BUY','SELL')
  AND trade_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;

-- 4. Instruments with the most distinct holders
SELECT i.instrument_id, i.symbol, i.instrument_name,
       COUNT(DISTINCT a.customer_id) AS distinct_holders
FROM holdings_snapshot h
JOIN accounts a ON a.account_id = h.account_id
JOIN instruments i ON i.instrument_id = h.instrument_id
GROUP BY i.instrument_id, i.symbol, i.instrument_name
ORDER BY distinct_holders DESC, i.instrument_id
LIMIT 10;

-- 5. High-priority goals below 25% funded
SELECT c.customer_id, c.full_name, g.goal_id, g.goal_name,
       ROUND((g.current_funded_amount / NULLIF(g.target_amount,0) * 100), 2) AS funded_pct
FROM goals g
JOIN customers c ON c.customer_id = g.customer_id
WHERE g.priority = 'HIGH'
  AND g.current_funded_amount / NULLIF(g.target_amount,0) < 0.25
ORDER BY funded_pct;

-- 6. Reconciliation / data-quality exceptions retained by importer
SELECT b.id AS batch_id, b.file_name, r.row_number, r.reason, r.raw_payload
FROM import_rejects r
JOIN import_batches b ON b.id = r.batch_id
ORDER BY b.id DESC, r.row_number;

-- Example performance demonstration
EXPLAIN (ANALYZE, BUFFERS)
SELECT t.*
FROM transactions t
WHERE t.account_id = 'A00001'
  AND t.trade_date BETWEEN DATE '2026-01-01' AND DATE '2026-12-31'
ORDER BY t.trade_date DESC
LIMIT 25;
