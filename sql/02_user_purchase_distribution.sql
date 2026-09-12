-- 图表2：用户购买次数分布（使用customer_unique_id真实用户ID）
SELECT buy_cnt, COUNT(customer_unique_id) AS user_count
FROM (
    SELECT c.customer_unique_id, COUNT(o.order_id) AS buy_cnt
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
) t
GROUP BY buy_cnt
ORDER BY buy_cnt;
