-- 看訂單表前10筆
SELECT * 
FROM orders 
LIMIT 10;


-- 熱銷商品類別 Top 10
SELECT 
    ct.product_category_name_english AS 商品類別,
    COUNT(oi.order_id) AS 銷售數量,
    ROUND(SUM(oi.price), 2) AS 總營收
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 商品類別
ORDER BY 總營收 DESC
LIMIT 10;

-- 物流效率：實際 vs 預期送達時間
SELECT 
    ROUND(AVG(JULIANDAY(order_delivered_customer_date) - 
              JULIANDAY(order_purchase_timestamp)), 1) AS 平均實際天數,
    ROUND(AVG(JULIANDAY(order_estimated_delivery_date) - 
              JULIANDAY(order_purchase_timestamp)), 1) AS 平均預期天數,
    COUNT(*) AS 訂單數
FROM orders
WHERE order_status = 'delivered'
AND order_delivered_customer_date IS NOT NULL;


-- 各州平均送達天數
SELECT 
    c.customer_state AS 州,
    COUNT(*) AS 訂單數,
    ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - 
              JULIANDAY(o.order_purchase_timestamp)), 1) AS 平均送達天數
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 州
ORDER BY 平均送達天數 ASC;

-- 客戶評分分布
SELECT 
    review_score AS 評分,
    COUNT(*) AS 數量,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS 百分比
FROM order_reviews
GROUP BY review_score
ORDER BY review_score DESC;

-- 各州總營收排名
SELECT 
    c.customer_state AS 州,
    COUNT(DISTINCT o.order_id) AS 訂單數,
    ROUND(SUM(oi.price), 2) AS 總營收
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 州
ORDER BY 總營收 DESC;