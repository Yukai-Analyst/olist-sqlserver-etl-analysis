"""
Olist电商项目：01_clean_data.py
功能：读取raw文件夹原始CSV，执行完整ETL清洗，输出clean文件夹清洗后csv
清洗处理内容：
1. 空字符串、nan、NaN统一替换为None，数据库识别为NULL
2. 字符串字段去除首尾空格，避免关联匹配失败
3. 时间字段解析转换为datetime时间格式
4. 去除完全重复的数据行
⚠️注意：不做业务层面过滤，取消/异常状态订单全部保留；业务筛选交给后续SQL分析
运行前置：raw文件夹放入全部9份原始数据集
"""
import os
import pandas as pd

# 原始csv存放路径
raw_path = "./raw"
# 清洗完成后输出路径，不存在自动创建
clean_path = "./clean"
os.makedirs(clean_path, exist_ok=True)

# Olist全部9张业务csv文件列表
file_list = [
    "olist_customers_dataset.csv",          # 客户表
    "olist_geolocation_dataset.csv",         # 地理位置表
    "olist_sellers_dataset.csv",            # 卖家表
    "olist_products_dataset.csv",           # 商品表
    "product_category_name_translation.csv", # 品类翻译表
    "olist_orders_dataset.csv",             # 订单主表
    "olist_order_items_dataset.csv",        # 订单商品明细表
    "olist_order_payments_dataset.csv",     # 订单支付表
    "olist_order_reviews_dataset.csv"       # 订单评价表
]

# 每张表对应的时间字段，用于时间解析
time_columns_map = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],
    "olist_order_items_dataset.csv": ["shipping_limit_date"],
    "olist_order_reviews_dataset.csv": ["review_creation_date", "review_answer_timestamp"]
}


def clean_dataframe(filename, df):
    """
    增强版清洗函数
    :param filename: 当前处理的文件名，用来识别时间列
    :param df: 原始DataFrame
    :return: 清洗后DataFrame
    """
    # 1. 删除完全重复行
    df = df.drop_duplicates(keep="first")

    # 2. object字符串列处理：空值替换 + strip首尾空格
    for col in df.columns:
        if df[col].dtype == "object":
            # 空字符串、nan、NaN 统一替换为None
            df[col] = df[col].replace(["", "nan", "NaN"], None)
            # 去除字符串首尾空格，非None才执行
            df.loc[df[col].notna(), col] = df.loc[df[col].notna(), col].apply(lambda x: x.strip())

    # 3. 时间字段解析，转为datetime
    if filename in time_columns_map:
        for time_col in time_columns_map[filename]:
            if time_col in df.columns:
                df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
                # coerce：无法解析时间置为NaT，写出csv会变成空，入库识别NULL

    return df


if __name__ == "__main__":
    for filename in file_list:
        full_raw_file = os.path.join(raw_path, filename)
        # 读取原始csv
        df = pd.read_csv(full_raw_file)
        df_clean = clean_dataframe(filename, df)
        # 写出清洗后的csv，na_rep=""：空值输出为空字符串
        output_file = os.path.join(clean_path, filename)
        df_clean.to_csv(output_file, index=False, na_rep="")
        print(f"✅ {filename} | 原始行数:{len(df)} → 清洗后行数:{len(df_clean)}")

    print("\n==== 全部文件清洗完毕，结果输出至 ./clean 目录 ====")

