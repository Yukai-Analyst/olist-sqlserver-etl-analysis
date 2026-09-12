# Olist 电商数据分析项目

基于巴西Olist电商平台公开数据集，完成从数据清洗、入库、业务分析到可视化呈现的完整ETL流程。

## 项目结构

```
├── raw/                    # 原始CSV数据（需手动从Kaggle下载）
├── clean/                  # 清洗后的CSV数据
├── sql/                    # 业务分析SQL脚本
├── output/                 # 生成的图表
├── config.py               # 统一配置模块
├── 01_clean_data.py        # 数据清洗脚本
├── 02_create_and_load.py   # 数据库建表与导入脚本
├── 03_analysis_sqlserver.sql # 业务指标分析SQL
├── 04_plot_result.py       # 图表生成脚本
├── schema_sqlserver.sql    # 数据库建表DDL
├── requirements.txt        # Python依赖
└── .env.example            # 环境变量模板
```

## 数据集说明

本项目使用 [Kaggle - Brazilian E-Commerce by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) 数据集，包含9张CSV文件：

| 文件 | 说明 |
|------|------|
| olist_customers_dataset.csv | 客户信息表 |
| olist_geolocation_dataset.csv | 地理位置表 |
| olist_sellers_dataset.csv | 卖家信息表 |
| olist_products_dataset.csv | 商品信息表 |
| product_category_name_translation.csv | 品类翻译表 |
| olist_orders_dataset.csv | 订单主表 |
| olist_order_items_dataset.csv | 订单商品明细表 |
| olist_order_payments_dataset.csv | 订单支付表 |
| olist_order_reviews_dataset.csv | 订单评价表 |

## 快速开始

### 1. 环境准备

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

复制 `.env.example` 为 `.env`，填入SQL Server连接信息：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=olist_db
DB_USER=sa
DB_PASSWORD=你的密码
DB_DRIVER={ODBC Driver 18 for SQL Server}
```

### 3. 下载数据

从Kaggle下载原始CSV文件，放入 `raw/` 目录。

### 4. 执行流程

```bash
# 步骤1：数据清洗（raw/ → clean/）
python 01_clean_data.py

# 步骤2：建表并导入数据库
python 02_create_and_load.py

# 步骤3：执行业务分析SQL（可选，直接在SSMS中运行）
# 03_analysis_sqlserver.sql

# 步骤4：生成可视化图表
python 04_plot_result.py
```

## 数据清洗说明

`01_clean_data.py` 执行以下清洗操作：

1. 空字符串、nan、NaN统一替换为NULL
2. 字符串字段去除首尾空格
3. 时间字段解析为datetime格式
4. 去除完全重复的数据行
5. order_reviews表按review_id去重
6. 数据质量校验（主键唯一性、空值率统计）

## 业务分析指标

| 指标 | 说明 |
|------|------|
| 总销售额 | 全部已交付订单的商品金额+运费 |
| 月度订单趋势 | 按年月统计已交付订单数量 |
| 用户复购统计 | 基于customer_unique_id统计购买次数分布 |
| 区域市场分析 | 各州订单量与销售额 |
| 品类销售排行 | 商品品类销售额TOP排名 |
| 配准时率 | 实际签收日期 vs 预计送达日期 |
| 用户评分分布 | 评价评分1-5分的分布情况 |
| 各州TOP3品类 | 使用窗口函数RANK()计算各州内部品类排名 |

## 可视化图表

运行 `04_plot_result.py` 后在 `output/` 目录生成：

- `01_monthly_orders.png` - 月度订单趋势
- `02_user_purchase_distribution.png` - 用户购买次数分布
- `03_state_sales.png` - 各州订单量与销售额
- `04_category_ranking.png` - 品类销售额TOP15
- `05_delivery_ontime_rate.png` - 配送准时率
- `06_review_score_distribution.png` - 评价评分分布
- `07_state_top3_categories.png` - 各州TOP3品类

## 技术栈

- Python 3.8+
- pandas - 数据处理
- pyodbc - SQL Server连接
- python-dotenv - 环境变量管理
- matplotlib - 数据可视化
- SQL Server - 关系型数据库
