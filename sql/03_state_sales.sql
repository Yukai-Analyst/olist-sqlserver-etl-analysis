-- 图表3：各州订单量与销售额
SELECT c.customer_state,
       COUNT(DISTINCT o.order_id) AS order_count,
       SUM(oi.price + oi.freight_value) AS sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY sales DESC;
