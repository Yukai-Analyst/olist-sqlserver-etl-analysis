-- 图表4：商品品类销售排行（关联翻译表转英文）
SELECT t.product_category_name_english,
       COUNT(DISTINCT oi.order_id) AS order_cnt,
       SUM(oi.price) AS sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t
ON p.product_category_name = t.product_category_name
GROUP BY t.product_category_name_english
ORDER BY sales DESC;
