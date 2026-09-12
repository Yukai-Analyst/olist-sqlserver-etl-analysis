"""
Olist电商项目：01_clean_data.py
功能：读取raw文件夹原始CSV，执行完整ETL清洗，输出clean文件夹清洗后csv
清洗处理内容：
1. 空字符串、nan、NaN统一替换为None，数据库识别为NULL
2. 字符串字段去除首尾空格，避免关联匹配失败
3. 时间字段解析转换为datetime时间格式
4. 去除完全重复的数据行
5. order_reviews表按review_id去重（原始数据存在同一评价关联多订单）
6. 清洗后执行数据质量校验（主键唯一性、空值率统计）
运行前置：raw文件夹放入全部9份原始数据集
"""
import os
import sys
import pandas as pd
from config import (
    RAW_DIR, CLEAN_DIR, FILE_LIST, TIME_COLUMNS_MAP, PRIMARY_KEY_MAP
)

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def validate_raw_files():
    """校验原始数据文件是否存在"""
    missing = []
    for f in FILE_LIST:
        if not os.path.exists(os.path.join(RAW_DIR, f)):
            missing.append(f)
    if missing:
        print(f"❌ raw目录缺少以下文件: {missing}")
        print(f"   请将Kaggle下载的原始CSV放入 {RAW_DIR} 目录")
        sys.exit(1)


def clean_dataframe(filename, df):
    """
    增强版清洗函数
    :param filename: 当前处理的文件名，用来识别时间列
    :param df: 原始DataFrame
    :return: 清洗后DataFrame
    """
    # 1. 删除完全重复行
    before = len(df)
    df = df.drop_duplicates(keep="first")
    dup_removed = before - len(df)

    # 2. object字符串列处理：空值替换 + strip首尾空格
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].replace(["", "nan", "NaN"], None)
            df.loc[df[col].notna(), col] = df.loc[df[col].notna(), col].apply(lambda x: x.strip())

    # 3. 时间字段解析，转为datetime
    if filename in TIME_COLUMNS_MAP:
        for time_col in TIME_COLUMNS_MAP[filename]:
            if time_col in df.columns:
                df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

    # 4. order_reviews表：review_id作为主键在原始数据中存在重复，需按review_id去重
    review_dedup = 0
    if filename == "olist_order_reviews_dataset.csv":
        before_count = len(df)
        df = df.drop_duplicates(subset=["review_id"], keep="first")
        review_dedup = before_count - len(df)

    return df, dup_removed, review_dedup


def validate_clean_data(filename, df):
    """
    数据质量校验：主键唯一性、空值率统计
    :return: 校验报告字典
    """
    report = {"filename": filename, "rows": len(df), "pk_violations": 0, "high_null_cols": []}

    # 主键唯一性校验
    pk_cols = PRIMARY_KEY_MAP.get(filename, [])
    if pk_cols:
        valid_pk = [c for c in pk_cols if c in df.columns]
        if valid_pk:
            dup_mask = df.duplicated(subset=valid_pk, keep=False)
            report["pk_violations"] = int(dup_mask.sum())
            if report["pk_violations"] > 0:
                dup_ids = df.loc[dup_mask, valid_pk].head(5).to_dict("records")
                report["pk_dup_examples"] = dup_ids

    # 空值率统计（>30%标记为高风险）
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_rate = null_count / len(df) if len(df) > 0 else 0
        if null_rate > 0.3:
            report["high_null_cols"].append({
                "column": col,
                "null_count": null_count,
                "null_rate": f"{null_rate:.1%}",
            })

    return report


def print_quality_report(all_reports):
    """打印汇总质量报告"""
    print("\n" + "=" * 70)
    print("                     数据清洗质量报告")
    print("=" * 70)

    total_rows = 0
    total_pk_issues = 0
    has_issue = False

    for r in all_reports:
        total_rows += r["rows"]
        flag = ""
        if r["pk_violations"] > 0:
            flag = " ⚠️ 主键重复"
            total_pk_issues += r["pk_violations"]
            has_issue = True
        if r["high_null_cols"]:
            flag += " ⚠️ 高空值率"
            has_issue = True
        print(f"  {r['filename']:45s} | {r['rows']:>8,} 行{flag}")

        if r["high_null_cols"]:
            for nc in r["high_null_cols"]:
                print(f"    └─ {nc['column']}: {nc['null_count']:,} 空值 ({nc['null_rate']})")

    print("-" * 70)
    print(f"  合计: {total_rows:,} 行")
    if total_pk_issues > 0:
        print(f"  ⚠️ 发现 {total_pk_issues} 条主键重复记录，请检查数据源")
    if not has_issue:
        print("  ✅ 全部校验通过，数据质量良好")
    print("=" * 70)


if __name__ == "__main__":
    # 前置校验
    validate_raw_files()
    os.makedirs(CLEAN_DIR, exist_ok=True)

    all_reports = []

    for filename in FILE_LIST:
        full_raw_file = os.path.join(RAW_DIR, filename)
        try:
            df = pd.read_csv(full_raw_file)
        except Exception as e:
            print(f"❌ 读取 {filename} 失败: {e}")
            continue

        original_count = len(df)
        df_clean, dup_removed, review_dedup = clean_dataframe(filename, df)

        # 数据质量校验
        report = validate_clean_data(filename, df_clean)
        all_reports.append(report)

        # 写出清洗后的csv
        output_file = os.path.join(CLEAN_DIR, filename)
        df_clean.to_csv(output_file, index=False)

        # 清洗摘要
        parts = [f"原始:{original_count}"]
        if dup_removed > 0:
            parts.append(f"完全重复去重:-{dup_removed}")
        if review_dedup > 0:
            parts.append(f"review_id去重:-{review_dedup}")
        parts.append(f"清洗后:{len(df_clean)}")
        print(f"✅ {filename} | {' → '.join(parts)}")

    print_quality_report(all_reports)
    print(f"\n清洗结果输出至 {CLEAN_DIR} 目录")
