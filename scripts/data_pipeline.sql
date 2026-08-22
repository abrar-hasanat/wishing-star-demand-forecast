/*
File: data_pipeline.sql
Purpose: Aggregate daily demand and inventory status for Wishing Star.
Dialect: PostgreSQL
*/

WITH daily_sales AS (
    /* Aggregate line item transactions into daily product metrics. */
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
    /* Identify days where inventory reaches zero. */
    CASE 
        WHEN il."UnitsInStock" <= 0 THEN TRUE 
        ELSE FALSE 
    END AS is_stockout
FROM "Inventory_Log" il
/* Keep days with zero sales and active inventory tracking. */
LEFT JOIN daily_sales ds 
    ON il."Date"::DATE = ds.sale_date 
    AND il."ProductID" = ds."ProductID"
JOIN "Products" p 
    ON il."ProductID" = p."ProductID"
ORDER BY 
    il."Date"::DATE, 
    il."ProductID";
