# Olist 巴西电商ETL与多维度数据分析

> 数据集：[Kaggle Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
>
> 完成原始CSV数据清洗、SQL Server范式建库、ETL批量入库、SQL业务指标分析、可视化输出的完整数据分析项目。
> 本项目侧重点为关系型数据库ETL范式建模与描述性业务数据分析，不做机器学习预测。

## 技术栈

Python(Pandas) | SQL Server | pyodbc | python-dotenv | Matplotlib

## 项目结构

```
olist-etl/
├─ raw/                          # 原始 CSV 数据集（gitignore，自行下载放入）
├─ clean/                        # 清洗后 CSV（gitignore）
├─ sql/                          # 可视化所需 SQL 查询（每个图表一个文件）
├─ output/                       # 可视化图表输出（gitignore）
├─ config.py                     # 统一配置（路径、DB连接、表映射）
├─ 01_clean_data.py              # 数据清洗 + 质量校验
├─ 02_create_and_load.py         # 批量导入 SQL Server
├─ 03_analysis_sqlserver.sql     # 【SSMS执行】业务指标分析
├─ 04_plot_result.py             # 生成7张可视化图表
├─ schema_sqlserver.sql          # 【SSMS执行】建库建表
├─ requirements.txt              # Python 依赖
├─ .env.example                  # 数据库凭据模板
└─ README.md
```

## 环境依赖

```bash
pip install -r requirements.txt
```

另外需要安装 **ODBC Driver 17/18 for SQL Server**，pyodbc 依赖该驱动。

## 数据库凭据配置

1. 复制 `.env.example` 为 `.env`，填入本地 SQL Server 连接信息
2. `.env` 已被 gitignore 忽略，不会提交到远程仓库
3. Windows 身份登录：不填 `DB_USER`/`DB_PASSWORD`，连接串自动使用 `Trusted_Connection=yes`

## 运行顺序

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 准备数据 | — | 将 Kaggle 下载的 9 个 CSV 放入 `raw/` |
| 2. 数据清洗 | `python 01_clean_data.py` | 输出至 `clean/`，含质量校验报告 |
| 3. 建库建表 | SSMS 执行 `schema_sqlserver.sql` | |
| 4. 批量入库 | `python 02_create_and_load.py` | 支持重复运行，自动清空+行数校验 |
| 5. SQL分析 | SSMS 执行 `03_analysis_sqlserver.sql` | |
| 6. 可视化 | `python 04_plot_result.py` | 图表输出至 `output/` |

> 如导入报外键冲突，先执行：
> ```sql
> EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';
> -- 导入完成后恢复
> EXEC sp_msforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL';
> ```

## 业务指标

1. 月度订单数量变化趋势
2. 用户购买次数分布（基于 `customer_unique_id`）
3. 各州订单量与销售额
4. 商品品类销售排行
5. 订单配送准时率
6. 用户评价评分分布
7. RANK 窗口函数：每州销售额 TOP3 品类

## ETL 清洗逻辑

- 空字符串/NaN → `NULL`；字符串去除首尾空格
- 时间字段解析，非法值置空；删除完全重复行
- `order_reviews` 按 `review_id` 去重（原始数据存在同一评价关联多订单）
- ETL 阶段不做业务过滤，取消/异常状态订单完整保留，业务筛选在 SQL 分析层实现
