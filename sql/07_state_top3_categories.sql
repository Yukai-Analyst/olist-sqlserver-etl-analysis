-- 图表7：每个州销售额TOP3商品品类（RANK窗口函数）
;WITH state_cat_sales AS (
    SELECT
        c.customer_state,
        t.product_category_name_english,
        SUM(oi.price) AS cat_sales,
        RANK() OVER(PARTITION BY c.customer_state ORDER BY SUM(oi.price) DESC) AS rn
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state, t.product_category_name_english
)
SELECT * FROM state_cat_sales WHERE rn <= 3;
