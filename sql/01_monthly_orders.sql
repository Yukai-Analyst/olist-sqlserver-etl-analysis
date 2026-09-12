-- 图表1：月度已交付订单数量变化趋势
SELECT YEAR(o.order_purchase_timestamp) AS ord_year,
       MONTH(o.order_purchase_timestamp) AS ord_month,
       COUNT(DISTINCT o.order_id) AS order_cnt
FROM orders o
WHERE o.order_status = 'delivered'
GROUP BY YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp)
ORDER BY ord_year, ord_month;
