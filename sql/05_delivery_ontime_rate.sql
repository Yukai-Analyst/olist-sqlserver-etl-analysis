-- 图表5：订单配送准时率
SELECT
    COUNT(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 END) * 1.0
        / COUNT(*) AS ontime_rate,
    COUNT(*) AS total_delivered
FROM orders
WHERE order_status = 'delivered';
