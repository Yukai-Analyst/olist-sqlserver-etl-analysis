-- 创建Olist电商数据库
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'olist_db')
BEGIN
    CREATE DATABASE olist_db;
END
GO

USE olist_db;
GO

-- 1. customers 客户维度表【被orders表外键引用】
CREATE TABLE customers (
	customer_id VARCHAR(50) NOT NULL PRIMARY KEY,        -- 订单级客户ID，每一笔订单对应一个
	customer_unique_id VARCHAR(50) NOT NULL,             -- 用户唯一ID，同一个人多笔订单共用，用于复购/RFM分析
	customer_zip_code_prefix VARCHAR(10),                -- 客户邮编前缀，关联地理位置表
	customer_city VARCHAR(100),                          -- 客户所在城市
	customer_state VARCHAR(10)                           -- 客户所在州(巴西州缩写，SP圣保罗等)
);
GO

-- 2. geolocation 地理位置辅助表，邮编映射经纬度
CREATE TABLE geolocation (
	geolocation_zip_code_prefix VARCHAR(10),  -- 邮编前缀
	geolocation_lat FLOAT,                    -- 纬度
	geolocation_lng FLOAT,                   -- 经度
	geolocation_city VARCHAR(100),           -- 城市
	geolocation_state VARCHAR(10)            -- 州缩写
);
GO

--3. sellers卖家维度表【被order_items引用】
CREATE TABLE sellers (
	seller_id VARCHAR(50) NOT NULL PRIMARY KEY,     -- 卖家唯一ID
	seller_zip_code_prefix VARCHAR(10),            -- 卖家邮编前缀
	seller_city VARCHAR(100),                      -- 卖家城市
	seller_state VARCHAR(10)                       -- 卖家所在州
);
GO

--4. products商品维度表【被order_items引用】
CREATE TABLE products (
	product_id VARCHAR(50) NOT NULL PRIMARY KEY,        -- 商品唯一ID
	product_category_name VARCHAR(100),                 -- 商品品类(葡萄牙语，需要翻译表转英文)
	product_name_lenght INT,                            -- 商品名称字符长度
	product_description_lenght INT,                     -- 商品描述字符长度
	product_photos_qty INT,                             -- 商品图片数量
	product_weight_g INT,                               -- 商品重量，单位克
	product_length_cm INT,                              -- 商品长 cm
	product_height_cm INT,                              -- 商品高 cm
	product_width_cm INT                                -- 商品宽 cm
);
GO

--5. product_category_name_translation 品类翻译维度表
CREATE TABLE product_category_name_translation (
	product_category_name VARCHAR(100) PRIMARY KEY,  -- 葡语品类名，关联products表
	product_category_name_english VARCHAR(100)       -- 翻译成英文的品类名称，便于阅读分析
);
GO

--6. orders 订单主事实表，引用customers客户表
CREATE TABLE orders (
	order_id VARCHAR(50) NOT NULL PRIMARY KEY,                 -- 订单全局唯一ID
	customer_id VARCHAR(50) NOT NULL,                          -- 关联客户表customer_id
	order_status VARCHAR(20),                                  -- 订单状态 delivered已送达、canceled取消等
	order_purchase_timestamp DATETIME,                          -- 用户下单时间
	order_approved_at DATETIME,                                -- 订单审核/付款确认时间
	order_delivered_carrier_date DATETIME,                     -- 商品交给物流承运商时间
	order_delivered_customer_date DATETIME,                    -- 用户实际签收时间
	order_estimated_delivery_date DATETIME,                    -- 平台预计送达时间，计算准时率
	CONSTRAINT fk_orders_customer FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
GO

--7. order_items 订单明细表，一个订单多条商品记录；引用orders、products、sellers
CREATE TABLE order_items (
	order_id VARCHAR(50) NOT NULL,              -- 订单ID，关联orders
	order_item_id INT NOT NULL,                 -- 订单内商品序号，同一个订单多个商品序号递增
	product_id VARCHAR(50) NOT NULL,           -- 商品ID，关联products
	seller_id VARCHAR(50) NOT NULL,            -- 卖家ID，关联sellers
	shipping_limit_date DATETIME,              -- 卖家最晚发货时限
	price DECIMAL(10,2),                       -- 商品销售单价
	freight_value DECIMAL(10,2),               -- 该商品对应的运费
	PRIMARY KEY(order_id, order_item_id),
	CONSTRAINT fk_oi_order FOREIGN KEY(order_id) REFERENCES orders(order_id),
	CONSTRAINT fk_oi_product FOREIGN KEY(product_id) REFERENCES products(product_id),
	CONSTRAINT fk_oi_seller FOREIGN KEY(seller_id) REFERENCES sellers(seller_id)
);
GO

--8. order_payments订单支付事实表，一个订单可多条支付记录（分期）
CREATE TABLE order_payments (
	order_id VARCHAR(50) NOT NULL,             -- 订单ID，关联orders
	payment_sequential INT NOT NULL,           -- 同一订单多笔支付的序号
	payment_type VARCHAR(30),                  -- 支付类型：信用卡、boleto等
	payment_installments INT,                 -- 分期期数
	payment_value DECIMAL(10,2),              -- 该笔支付金额
	PRIMARY KEY(order_id,payment_sequential),
	CONSTRAINT fk_pay_order FOREIGN KEY(order_id) REFERENCES orders(order_id)
);
GO

--9. order_reviews订单评价事实表，引用orders订单表
CREATE TABLE order_reviews (
	review_id VARCHAR(50) NOT NULL PRIMARY KEY,    -- 评价记录唯一ID
	order_id VARCHAR(50) NOT NULL,                 -- 关联订单order_id
	review_score INT,                              -- 用户评分：1~5分
	review_comment_title NVARCHAR(200),            -- 评价标题
	review_comment_message NVARCHAR(MAX),          -- 评价正文文本
	review_creation_date DATETIME,                 -- 用户提交评价时间
	review_answer_timestamp DATETIME,              -- 商家回复评价时间
	CONSTRAINT fk_rev_order FOREIGN KEY(order_id) REFERENCES orders(order_id)
);
GO
