"""
Olist电商项目：04_plot_result.py
功能：连接SQL Server读取分析结果，使用matplotlib绘制业务图表，图片保存本地
运行前提：数据库已经完整导入全部数据
⚠️账号密码从本地.env读取，禁止硬编码提交github
"""
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# 加载本地环境变量
load_dotenv()

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ==========从.env读取数据库配置==========
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")

conn_str = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;TrustServerCertificate=yes;"
)

if __name__ == "__main__":
    conn = pyodbc.connect(conn_str)

    # =========图表1：月度订单数量变化趋势 =========
    sql_month = """
    SELECT YEAR(o.order_purchase_timestamp) AS ord_year,
           MONTH(o.order_purchase_timestamp) AS ord_month,
           COUNT(DISTINCT o.order_id) AS order_cnt
    FROM orders o
    WHERE o.order_status = 'delivered'
    GROUP BY YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp)
    ORDER BY ord_year, ord_month;
    """
    df_month = pd.read_sql(sql_month, conn)
    # 拼接年月字符串，用于X轴标签
    df_month["ym"] = df_month["ord_year"].astype(str) + "-" + df_month["ord_month"].astype(str)

    plt.figure(figsize=(12,5))
    plt.plot(df_month["ym"], df_month["order_cnt"], marker='o')
    plt.title("月度订单数量变化")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./month_order.png")
    plt.show()

    # =========图表2：用户购买次数分布 =========
    sql_rpt = """
    SELECT buy_cnt, COUNT(customer_unique_id) AS user_count
    FROM (
        SELECT c.customer_unique_id, COUNT(o.order_id) AS buy_cnt
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
    ) t
    GROUP BY buy_cnt
    ORDER BY buy_cnt;
    """
    df_rpt = pd.read_sql(sql_rpt, conn)
    plt.figure(figsize=(8,4))
    plt.bar(df_rpt["buy_cnt"], df_rpt["user_count"])
    plt.title("用户购买次数分布")
    plt.xlabel("购买次数")
    plt.ylabel("用户数量")
    plt.tight_layout()
    plt.savefig("./user_buy_count.png")
    plt.show()

    conn.close()
    print("图表已经保存到项目根目录 month_order.png、user_buy_count.png")

