"""
Olist电商项目：统一配置模块
集中管理路径、数据库连接、表名映射等常量，避免硬编码散落各脚本
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ======================== 路径配置 ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "clean")
SQL_DIR = os.path.join(BASE_DIR, "sql")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ======================== 数据库配置 ========================
DB_SERVER = os.getenv("DB_SERVER", "")
DB_DATABASE = os.getenv("DB_DATABASE", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "{ODBC Driver 18 for SQL Server}")


def get_conn_str():
    """组装数据库连接字符串"""
    if DB_USER and DB_PASSWORD:
        return (
            f"DRIVER={DB_DRIVER};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            f"Encrypt=yes;TrustServerCertificate=yes;"
        )
    else:
        return (
            f"DRIVER={DB_DRIVER};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"Trusted_Connection=yes;"
            f"Encrypt=yes;TrustServerCertificate=yes;"
        )


# ======================== ETL 文件映射 ========================
FILE_LIST = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "product_category_name_translation.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
]

# 每张表对应的时间字段
TIME_COLUMNS_MAP = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": ["shipping_limit_date"],
    "olist_order_reviews_dataset.csv": ["review_creation_date", "review_answer_timestamp"],
}

# 主键定义：用于清洗后校验主键唯一性
PRIMARY_KEY_MAP = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_geolocation_dataset.csv": [],
    "olist_sellers_dataset.csv": ["seller_id"],
    "olist_products_dataset.csv": ["product_id"],
    "product_category_name_translation.csv": ["product_category_name"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_order_reviews_dataset.csv": ["review_id"],
}

# ======================== 数据库导入顺序 ========================
# 维度表在前，事实表在后，满足外键依赖
TABLE_CSV_MAPPING = [
    ("customers", "olist_customers_dataset.csv"),
    ("geolocation", "olist_geolocation_dataset.csv"),
    ("sellers", "olist_sellers_dataset.csv"),
    ("products", "olist_products_dataset.csv"),
    ("product_category_name_translation", "product_category_name_translation.csv"),
    ("orders", "olist_orders_dataset.csv"),
    ("order_items", "olist_order_items_dataset.csv"),
    ("order_payments", "olist_order_payments_dataset.csv"),
    ("order_reviews", "olist_order_reviews_dataset.csv"),
]

# 表名 -> CSV文件名 快速查找
TABLE_NAME_TO_CSV = {table: csv for table, csv in TABLE_CSV_MAPPING}
CSV_TO_TABLE_NAME = {csv: table for table, csv in TABLE_CSV_MAPPING}
