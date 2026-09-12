-- 图表6：用户评价评分分布（1~5分）
SELECT review_score, COUNT(*) AS score_cnt
FROM order_reviews
GROUP BY review_score
ORDER BY review_score DESC;
