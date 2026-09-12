"""
Olist电商项目：04_plot_result.py
功能：连接SQL Server读取分析结果，使用matplotlib绘制业务图表，图片保存至output目录
运行前提：数据库已经完整导入全部数据
"""
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyodbc
from config import SQL_DIR, OUTPUT_DIR, get_conn_str

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# 中文字体设置
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def load_sql(filename):
    """从sql目录读取SQL文件内容"""
    sql_path = os.path.join(SQL_DIR, filename)
    with open(sql_path, "r", encoding="utf-8") as f:
        return f.read()


def get_conn():
    """获取数据库连接"""
    try:
        return pyodbc.connect(get_conn_str())
    except Exception as e:
        print("❌ 数据库连接失败！")
        print("   请检查：1. .env配置是否正确；2. SQL Server是否运行")
        raise e


def plot_monthly_orders(conn):
    """图表1：月度订单数量变化趋势"""
    sql = load_sql("01_monthly_orders.sql")
    df = pd.read_sql(sql, conn)
    df["ym"] = df["ord_year"].astype(str) + "-" + df["ord_month"].astype(str)

    plt.figure(figsize=(14, 5))
    plt.plot(df["ym"], df["order_cnt"], marker="o", linewidth=2, markersize=5)
    plt.title("月度已交付订单数量变化趋势", fontsize=14)
    plt.xlabel("年月")
    plt.ylabel("订单数量")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_monthly_orders.png"), dpi=150)
    plt.close()
    print("  ✅ 01_monthly_orders.png")


def plot_user_purchase_distribution(conn):
    """图表2：用户购买次数分布"""
    sql = load_sql("02_user_purchase_distribution.sql")
    df = pd.read_sql(sql, conn)

    plt.figure(figsize=(10, 5))
    plt.bar(df["buy_cnt"], df["user_count"])
    plt.title("用户购买次数分布", fontsize=14)
    plt.xlabel("购买次数")
    plt.ylabel("用户数量")
    plt.xlim(0, 15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_user_purchase_distribution.png"), dpi=150)
    plt.close()
    print("  ✅ 02_user_purchase_distribution.png")


def plot_state_sales(conn):
    """图表3：各州订单量与销售额"""
    sql = load_sql("03_state_sales.sql")
    df = pd.read_sql(sql, conn)

    fig, ax1 = plt.subplots(figsize=(14, 6))
    color = "tab:blue"
    ax1.bar(df["customer_state"], df["order_count"], color=color, alpha=0.7)
    ax1.set_xlabel("州")
    ax1.set_ylabel("订单数量", color=color)
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.plot(df["customer_state"], df["sales"], color=color, marker="o", linewidth=2)
    ax2.set_ylabel("销售额 (BRL)", color=color)
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title("巴西各州订单量与销售额", fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_state_sales.png"), dpi=150)
    plt.close()
    print("  ✅ 03_state_sales.png")


def plot_category_ranking(conn):
    """图表4：商品品类销售排行TOP15"""
    sql = load_sql("04_category_ranking.sql")
    df = pd.read_sql(sql, conn)
    df_top = df.head(15)

    plt.figure(figsize=(12, 7))
    plt.barh(df_top["product_category_name_english"][::-1], df_top["sales"][::-1])
    plt.title("商品品类销售额排行 TOP15", fontsize=14)
    plt.xlabel("销售额 (BRL)")
    plt.ylabel("品类")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_category_ranking.png"), dpi=150)
    plt.close()
    print("  ✅ 04_category_ranking.png")


def plot_delivery_ontime_rate(conn):
    """图表5：订单配送准时率"""
    sql = load_sql("05_delivery_ontime_rate.sql")
    df = pd.read_sql(sql, conn)

    ontime = df["ontime_rate"].iloc[0]
    late = 1 - ontime

    plt.figure(figsize=(6, 6))
    plt.pie(
        [ontime, late],
        labels=["准时配送", "延迟配送"],
        autopct="%1.1f%%",
        colors=["#2ecc71", "#e74c3c"],
        startangle=90,
    )
    plt.title(f"订单配送准时率 ({df['total_delivered'].iloc[0]:,}单)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_delivery_ontime_rate.png"), dpi=150)
    plt.close()
    print("  ✅ 05_delivery_ontime_rate.png")


def plot_review_score_distribution(conn):
    """图表6：用户评价评分分布"""
    sql = load_sql("06_review_score_distribution.sql")
    df = pd.read_sql(sql, conn)
    df = df.sort_values("review_score")

    plt.figure(figsize=(8, 5))
    colors = ["#e74c3c", "#e67e22", "#f1c40f", "#3498db", "#2ecc71"]
    bars = plt.bar(df["review_score"], df["score_cnt"], color=colors)
    plt.title("用户评价评分分布", fontsize=14)
    plt.xlabel("评分 (1-5)")
    plt.ylabel("评价数量")
    plt.xticks(df["review_score"])

    for bar, cnt in zip(bars, df["score_cnt"]):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                 f"{cnt:,}", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_review_score_distribution.png"), dpi=150)
    plt.close()
    print("  ✅ 06_review_score_distribution.png")


def plot_state_top3_categories(conn):
    """图表7：每个州销售额TOP3商品品类"""
    sql = load_sql("07_state_top3_categories.sql")
    df = pd.read_sql(sql, conn)

    states = df["customer_state"].unique()
    n_states = len(states)
    ncols = 4
    nrows = (n_states + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(20, nrows * 4))
    axes = axes.flatten()

    for idx, state in enumerate(states):
        ax = axes[idx]
        state_df = df[df["customer_state"] == state].sort_values("rn")
        y_pos = range(len(state_df))
        ax.barh(y_pos, state_df["cat_sales"].values, color="#3498db")
        ax.set_yticks(y_pos)
        labels = state_df["product_category_name_english"].fillna("N/A").values
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_title(f"{state} (TOP3)", fontsize=10)
        ax.ticklabel_format(axis="x", style="scientific", scilimits=(0, 0))

    for idx in range(n_states, len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle("巴西各州销售额 TOP3 商品品类", fontsize=16, y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_state_top3_categories.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✅ 07_state_top3_categories.png")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = get_conn()
    print("开始生成业务分析图表...\n")

    try:
        plot_monthly_orders(conn)
        plot_user_purchase_distribution(conn)
        plot_state_sales(conn)
        plot_category_ranking(conn)
        plot_delivery_ontime_rate(conn)
        plot_review_score_distribution(conn)
        plot_state_top3_categories(conn)
        print(f"\n全部 7 张图表已保存至 {OUTPUT_DIR} 目录")
    except Exception as e:
        print(f"\n❌ 图表生成过程中发生错误: {e}")
        sys.exit(1)
    finally:
        conn.close()
