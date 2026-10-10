ANALYTICS_QUERIES = {
    "price_anomalies": """
        SELECT d.calendar_date, p.product_name, p.source, a.current_price, a.previous_price,
               a.change_rate, a.anomaly_type
        FROM ads.price_anomaly a
        JOIN dim.dim_date d ON d.date_key=a.date_key
        JOIN dim.dim_product p ON p.product_key=a.product_key
        ORDER BY d.calendar_date DESC, ABS(a.change_rate) DESC
    """,
    "category_price_index": """
        SELECT c.category_name, d.calendar_date, ROUND(AVG(s.price), 4) AS avg_price
        FROM dwd.fact_price_snapshot s
        JOIN dim.dim_date d ON d.date_key=s.snapshot_date_key
        JOIN dim.dim_category c ON c.category_key=s.category_key
        GROUP BY c.category_name, d.calendar_date
        ORDER BY d.calendar_date DESC, c.category_name
    """,
    "out_of_stock_products": """
        SELECT d.calendar_date, p.source, p.product_name, s.availability
        FROM dwd.fact_price_snapshot s
        JOIN dim.dim_date d ON d.date_key=s.snapshot_date_key
        JOIN dim.dim_product p ON p.product_key=s.product_key
        WHERE s.availability='out_of_stock'
        ORDER BY d.calendar_date DESC
    """,
}
