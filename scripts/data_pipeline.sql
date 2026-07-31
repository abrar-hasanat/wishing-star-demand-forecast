-- ==============================================================================
-- File: data_pipeline.sql
-- Purpose: Enterprise Data Pipeline for "Wishing Star"
-- Description: Aggregates daily transactional order data with historical 
--              inventory logs and product metadata. Engineered to identify 
--              daily sales volume, revenue, and boolean stockout events.
-- Dialect: PostgreSQL
-- ==============================================================================

WITH daily_sales AS (
    -- Aggregate line-item transactions into daily product-level metrics
    SELECT 
        DATE(o."OrderDate") AS sale_date,
        oi."ProductID",
        SUM(oi."Quantity") AS daily_units_sold,
        SUM(oi."Quantity" * oi."UnitPrice" * (1 - o."DiscountApplied")) AS daily_revenue
    FROM "Orders" o
    JOIN "Order_Items" oi 
        ON o."OrderID" = oi."OrderID"
    GROUP BY 
        DATE(o."OrderDate"), 
        oi."ProductID"
)
SELECT 
    il."Date"::DATE AS log_date,
    il."ProductID",
    p."Category",
    p."BasePrice",
    p."SupplierLeadTime_Days",
    COALESCE(ds.daily_units_sold, 0) AS total_units_sold,
    COALESCE(ds.daily_revenue, 0) AS total_revenue,
    il."UnitsInStock",
    il."UnitsReceived",
    -- Identify days where inventory hits absolute zero (Stockout Anomaly)
    CASE 
        WHEN il."UnitsInStock" <= 0 THEN TRUE 
        ELSE FALSE 
    END AS is_stockout
FROM "Inventory_Log" il
-- Left join guarantees we keep days with 0 sales but active inventory tracking
LEFT JOIN daily_sales ds 
    ON il."Date"::DATE = ds.sale_date 
    AND il."ProductID" = ds."ProductID"
JOIN "Products" p 
    ON il."ProductID" = p."ProductID"
ORDER BY 
    il."Date"::DATE, 
    il."ProductID";