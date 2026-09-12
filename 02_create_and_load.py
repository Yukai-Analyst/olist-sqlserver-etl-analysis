"""
Olist电商项目：02_create_and_load.py
功能：读取clean目录下清洗完成的csv，批量插入SQL Server数据库
⚠️重要：账号密码从.env读取，禁止硬编码提交github
注意：
1. 数据表有外键依赖，table_csv_mapping顺序不能修改！
2. 先运行01_clean_data.py生成clean目录下csv，再运行本脚本
3. 支持重复运行：导入前自动清空已有数据（关闭外键约束→清空→恢复约束）
4. 导入后校验数据库行数与CSV一致，防止静默丢数据
"""
import os
import sys
import pandas as pd
import pyodbc
from config import (
    CLEAN_DIR, TABLE_CSV_MAPPING, get_conn_str
)

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def get_db_conn():
    """获取数据库连接对象"""
    try:
        conn = pyodbc.connect(get_conn_str())
        return conn
    except Exception as e:
        print("❌ 数据库连接失败！")
        print("   请检查：1. .env配置是否正确；2. ODBC Driver是否安装；3. SQL Server是否运行")
        raise e


def clear_all_tables(conn):
    """关闭外键约束 → 清空所有表 → 恢复约束"""
    cursor = conn.cursor()
    cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
    conn.commit()

    for table, _ in reversed(TABLE_CSV_MAPPING):
        try:
            cursor.execute(f"DELETE FROM [{table}]")
            conn.commit()
        except Exception as e:
            print(f"⚠️ 清空表 {table} 失败: {e}")
            conn.rollback()
            raise

    cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL'")
    conn.commit()
    cursor.close()


def batch_insert_table(table_name, df, conn):
    """批量插入数据到SQL Server"""
    cursor = conn.cursor()
    columns = list(df.columns)
    col_bracket = ",".join([f"[{c}]" for c in columns])
    place_holder = ",".join(["?"] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({col_bracket}) VALUES ({place_holder})"

    # NaN/NaT → None，pyodbc把None映射为SQL NULL
    row_data = df.values.tolist()
    for row in row_data:
        for i, val in enumerate(row):
            if isinstance(val, float) and val != val:
                row[i] = None

    cursor.executemany(insert_sql, row_data)
    conn.commit()
    cursor.close()


def validate_row_count(conn, table_name, expected_count):
    """校验导入后行数是否一致"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
    actual_count = cursor.fetchone()[0]
    cursor.close()
    if actual_count != expected_count:
        print(f"  ❌ 行数校验失败: 预期 {expected_count}, 实际 {actual_count}")
        return False
    return True


if __name__ == "__main__":
    if not os.path.isdir(CLEAN_DIR):
        print(f"❌ clean目录不存在: {CLEAN_DIR}")
        print("   请先运行 python 01_clean_data.py")
        sys.exit(1)

    conn = get_db_conn()

    try:
        print("正在清空已有数据...")
        clear_all_tables(conn)
        print("数据清空完成\n")

        success_count = 0
        fail_count = 0
        for table, csv_name in TABLE_CSV_MAPPING:
            csv_path = os.path.join(CLEAN_DIR, csv_name)
            if not os.path.exists(csv_path):
                print(f"❌ 文件不存在: {csv_path}")
                fail_count += 1
                continue

            df = pd.read_csv(csv_path)
            csv_rows = len(df)
            print(f"正在导入 {table}，行数 {csv_rows}")

            try:
                batch_insert_table(table, df, conn)
                if validate_row_count(conn, table, csv_rows):
                    print(f"  ✅ {table} 导入完成，行数校验通过")
                    success_count += 1
                else:
                    print(f"  ⚠️ {table} 导入完成，但行数不一致")
                    fail_count += 1
            except Exception as e:
                print(f"  ❌ {table} 导入失败: {e}")
                conn.rollback()
                fail_count += 1
                continue

        print(f"\n{'=' * 50}")
        print(f"导入完成: {success_count} 成功, {fail_count} 失败")
        if fail_count == 0:
            print("========= 全部数据表导入SQL Server完成 =========")
        else:
            print("⚠️ 部分表导入失败，请检查上方错误信息")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
