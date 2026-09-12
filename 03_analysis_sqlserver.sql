USE olist_db;
GO

/*
Olist电商业务分析SQL脚本
说明：基于已导入完整数据表，做电商业务指标计算，包含多表JOIN，窗口函数RANK
*/

--1. 全部已交付订单总销售额（商品金额+运费）
SELECT SUM(oi.price + oi.freight_value) AS total_sales
FROM order_items oi;
GO

--2. 按年、月统计【已交付】订单数量，观察订单时间趋势
SELECT YEAR(o.order_purchase_timestamp) AS ord_year,
       MONTH(o.order_purchase_timestamp) AS ord_month,
       COUNT(DISTINCT o.order_id) AS order_cnt
FROM orders o
WHERE o.order_status = 'delivered'
GROUP BY YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp)
ORDER BY ord_year, ord_month;
GO

--3. 计算每一笔订单总金额，用于后续计算客单价
SELECT o.order_id, SUM(oi.price + oi.freight_value) AS order_total
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status='delivered'
GROUP BY o.order_id;
GO

--4. 用户复购统计：统计用户购买次数分布
--重点：使用customer_unique_id(真实用户ID)，不要用customer_id，customer_id是订单维度ID，每个订单不一样
SELECT buy_cnt, COUNT(customer_unique_id) AS user_count
FROM (
    SELECT c.customer_unique_id, COUNT(o.order_id) AS buy_cnt
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
) t
GROUP BY buy_cnt
ORDER BY buy_cnt;
GO

--5. 各个州：订单数量、总销售额，分析区域市场表现
SELECT c.customer_state,
       COUNT(DISTINCT o.order_id) AS order_count,
       SUM(oi.price + oi.freight_value) AS sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status='delivered'
GROUP BY c.customer_state
ORDER BY sales DESC;
GO

--6. 商品品类销售排行；关联翻译表，把葡萄牙语品类转为英文便于阅读
SELECT t.product_category_name_english,
       COUNT(DISTINCT oi.order_id) AS order_cnt,
       SUM(oi.price) AS sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t
ON p.product_category_name = t.product_category_name
GROUP BY t.product_category_name_english
ORDER BY sales DESC;
GO

--7. 订单配送准时率：实际签收日期 <=预计送达日期为准时
SELECT
    COUNT(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 END)*1.0 / COUNT(*) AS ontime_rate,
    COUNT(*) AS total_delivered
FROM orders
WHERE order_status = 'delivered';
GO

--8.【简历亮点】窗口函数RANK()：每个州内部，销售额排名TOP3的商品品类
--PARTITION BY customer_state，按州分组，组内按销售额排序
;WITH state_cat_sales AS (
SELECT
    c.customer_state,
    t.product_category_name_english,
    SUM(oi.price) AS cat_sales,
    RANK() OVER(PARTITION BY c.customer_state ORDER BY SUM(oi.price) DESC) AS rn
FROM customers c
JOIN orders o ON c.customer_id=o.customer_id
JOIN order_items oi ON o.order_id=oi.order_id
JOIN products p ON oi.product_id=p.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name=t.product_category_name
WHERE o.order_status='delivered'
GROUP BY c.customer_state, t.product_category_name_english
)
SELECT * FROM state_cat_sales WHERE rn <=3;
GO

--9. 用户评价评分分布（1~5分），观察用户满意度
SELECT review_score, COUNT(*) AS score_cnt
FROM order_reviews
GROUP BY review_score
ORDER BY review_score DESC;
GO
