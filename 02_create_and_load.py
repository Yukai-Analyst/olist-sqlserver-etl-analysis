"""
Olist电商项目：02_create_and_load.py
功能：读取clean目录下清洗完成的csv，批量插入SQL Server数据库
⚠️重要：数据库账号密码存放于本地.env文件，不要硬编码写在代码中，避免上传github泄密
注意：
1. 数据表有外键依赖，table_csv_mapping列表顺序不能修改！
2. 先运行01_clean_data.py生成clean目录下csv，再运行本脚本
3. 原始数据集存在少量脏外键ID，导入报错可在SSMS执行关闭外键约束语句
"""
import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv

# 加载本地 .env 环境变量文件（只读取本地，不会上传github）
load_dotenv()

# ======================== 从本地.env读取数据库配置，不再写死密码 ========================
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")
# ==================================================================================

# 组装数据库连接字符串
conn_str = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;TrustServerCertificate=yes;"
)

# Windows身份验证连接字符串示例（.env就不要填DB_USER、DB_PASSWORD）
# conn_str = (
#     f"DRIVER={driver};"
#     f"SERVER={server};"
#     f"DATABASE={database};"
#     f"Trusted_Connection=yes;"
#     f"Encrypt=yes;TrustServerCertificate=yes;"
# )


def get_db_conn():
    """获取数据库连接对象"""
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print("数据库连接失败！")
        print("请检查：1.本地.env配置是否正确；2.ODBC Driver17驱动是否安装")
        raise e


# 【表名 - 清洗后csv文件】映射
# ⚠️顺序不能改动！维度表（被外键引用）必须在前，事实表在后，满足外键依赖
table_csv_mapping = [
    ("customers", "olist_customers_dataset.csv"),        # 客户维度表，被orders依赖
    ("geolocation", "olist_geolocation_dataset.csv"),   # 地理位置，无依赖
    ("sellers", "olist_sellers_dataset.csv"),            # 卖家维度表，被order_items依赖
    ("products", "olist_products_dataset.csv"),           # 商品维度表，被order_items依赖
    ("product_category_name_translation", "product_category_name_translation.csv"), #品类翻译
    ("orders", "olist_orders_dataset.csv"),              # 订单主表，被items/payments/reviews依赖
    ("order_items", "olist_order_items_dataset.csv"),     # 订单明细，依赖orders/products/sellers
    ("order_payments", "olist_order_payments_dataset.csv"), #支付表，依赖orders
    ("order_reviews", "olist_order_reviews_dataset.csv")    #评价表，依赖orders
]

clean_folder = "./clean"


def batch_insert_table(table_name, df, conn):
    """
    批量插入数据到SQL Server
    :param table_name: 目标数据表名
    :param df: 需要写入的DataFrame（已经清洗完毕）
    :param conn: 数据库连接
    """
    cursor = conn.cursor()
    columns = list(df.columns)
    col_bracket = ",".join([f"[{c}]" for c in columns]) #字段名加中括号，防止字段名冲突
    place_holder = ",".join(["?"] * len(columns))       #pyodbc占位符
    insert_sql = f"INSERT INTO {table_name} ({col_bracket}) VALUES ({place_holder})"
    row_data = df.values.tolist()
    cursor.executemany(insert_sql, row_data)
    conn.commit() #提交事务
    cursor.close()


if __name__ == "__main__":
    conn = get_db_conn()
    for table, csv_name in table_csv_mapping:
        csv_path = os.path.join(clean_folder, csv_name)
        df = pd.read_csv(csv_path)
        print(f"正在导入表 {table}，行数 {len(df)}")
        batch_insert_table(table, df, conn)
        print(f"✅ {table} 导入完成\n")

    conn.close()
    print("========= 全部数据表导入SQL Server完成 =========")

