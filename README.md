# Olist 巴西电商ETL与多维度数据分析
> 数据集来源：Kaggle Olist Brazilian E-Commerce Public Dataset
> 项目简介：基于公开电商数据集，完成原始CSV数据清洗、SQL Server范式建库、ETL批量入库、SQL业务指标分析、可视化输出的完整数据分析项目。

## 技术栈
Python(Pandas) | SQL Server | pyodbc | python-dotenv | Matplotlib
1. ETL：原始CSV数据清洗，处理空值、字符串空格、时间格式、重复脏数据
2. 数据库建模：事实表+维度表设计，配置主键、物理外键约束保障参照完整性
3. SQL分析：多表JOIN、聚合统计、RANK窗口函数，计算电商业务指标
4. 工程化：`.env`管理数据库敏感凭据，`.gitignore`过滤大文件、缓存，保护密码安全

> 项目说明：
> 网上有不少同数据集的开源项目（如olist-ml-models）侧重于Databricks、特征工程、机器学习预测；
> **本项目核心侧重点为关系型数据库ETL范式建模与描述性业务数据分析，不做机器学习预测。**

## 项目目录
```
olist-etl/
├─ raw/                          # 原始 9 份 CSV 数据集，gitignore 忽略，自行下载放入
├─ clean/                        # pandas 清洗输出的 csv，gitignore 忽略
├─ sql/                          # 可视化所需的 SQL 查询文件（每个图表对应一个）
├─ output/                       # 可视化图表输出目录，gitignore 忽略
├─ config.py                     # 统一配置模块（路径、数据库连接、表映射）
├─ 01_clean_data.py              # Python 脚本：原始数据清洗 + 数据质量校验
├─ 02_create_and_load.py         # Python 脚本：批量导入清洗后数据进 SQL Server
├─ 03_analysis_sqlserver.sql     # SQL 脚本：【SSMS 执行】业务指标分析查询
├─ 04_plot_result.py             # Python 脚本：读取数据库结果，生成7张可视化图表
├─ schema_sqlserver.sql          # SQL 脚本：【SSMS 执行】建库、建表、主键外键
├─ requirements.txt              # Python 依赖清单
├─ .env                          # 本地私有，存放数据库账号密码，不上传 GitHub
├─ .env.example                  # 配置模板，提交 GitHub，用于项目复现
├─ .gitignore                    # git 忽略规则
└─ README.md                     # 项目说明文档
```

## 环境依赖

### 1. Python库安装
```bash
pip install -r requirements.txt
```

### 2. 额外必备

- **ODBC Driver 17/18 for SQL Server**，pyodbc 依赖该驱动，未安装会连接失败。

## 数据库凭据配置（防止密码泄露）

1. 复制`.env.example`，副本重命名为`.env`；
2. 在`.env`填入你本地 SQL Server 连接信息；
3. `.env`已经被`.gitignore`忽略，**不会提交到远程仓库**；

> 禁止把真实密码填写进`.env.example`，该文件会上传 GitHub。

`.env.example`内容参考：

```ini
# .env.example 配置模板
# 复制本文件另存为 .env，填入自己本地数据库信息
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=olist_db
DB_USER=sa
DB_PASSWORD=填写你的数据库密码
DB_DRIVER={ODBC Driver 18 for SQL Server}
```

> Windows 身份登录 SQL Server：不需要填写 DB_USER、DB_PASSWORD，连接串开启`Trusted_Connection=yes`。

## 完整运行顺序（严格执行）

1. **准备数据集**
将从 Kaggle 下载的 9 个原始 csv 全部放到项目下`raw`文件夹。

2. **执行数据清洗【Python 脚本】**
```bash
python 01_clean_data.py
```
> 读取 raw 原始文件，完成清洗，处理空值、空格、时间、重复行，输出至`clean`文件夹。
> 新增：清洗后自动执行数据质量校验（主键唯一性、空值率统计），输出质量报告。

3. **创建数据库与数据表【SSMS 执行】**
打开 SSMS，打开脚本`schema_sqlserver.sql`，点击执行。
> 创建`olist_db`数据库，9 张业务表，定义主键、物理外键约束。
> 如果导入报外键冲突，执行：
```sql
EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';
GO
-- 导入完成后恢复
EXEC sp_msforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL';
GO
```

4. **批量数据入库【Python 脚本】**
```bash
python 02_create_and_load.py
```
> 支持重复运行：导入前自动清空已有数据。
> 导入后自动校验数据库行数与CSV一致，防止静默丢数据。

5. **业务指标查询分析【SSMS 执行】**
SSMS 打开`03_analysis_sqlserver.sql`，执行脚本，查看各项业务分析结果。
> 可以全部一次性执行，也可以选中单条 SQL 片段单独调试运行。

6. **生成业务可视化图表【Python 脚本】**
```bash
python 04_plot_result.py
```
> 程序连接数据库读取查询结果，matplotlib 绘制7张图表，图片保存至`output`目录。

## 计算的业务指标

1. 总销售额、月度订单数量变化趋势
2. 用户购买次数分布（使用`customer_unique_id`真实用户ID，规避订单维度ID误区）
3. 巴西各个州订单量、销售额，区域市场表现
4. 商品品类销售排行，关联葡英翻译表
5. 订单配送准时履约率
6. 用户评价评分分布，评估客户满意度
7. RANK 窗口函数：每个州销售额 TOP3 商品品类

## ETL 清洗处理逻辑

1. 空值处理：空字符串、NaN 统一处理，入库映射数据库`NULL`；
2. 字符串字段去除首尾空格，避免多表 JOIN 匹配失败；
3. 时间字段解析转换为 datetime，非法时间置为空；
4. 删除完全重复数据行；
5. order_reviews 表按 review_id 去重（原始数据存在同一评价关联多订单的情况）；
6. **ETL 阶段不做业务过滤**：取消、异常状态订单完整保留；业务筛选逻辑在 SQL 分析层实现，区分数据清洗与业务过滤。
