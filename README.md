# 链家租房数据分析项目

作为北京邮电大学《Python程序设计》课程要求所设计的一个**完整的租房数据采集与分析系统**，涵盖**5个城市**（北京、上海、广州、深圳、杭州）的租房数据爬取、清洗、分析与可视化全流程。

---

## 快速开始

### 1. 环境要求

- **Python 3.8+**
- **uv** (推荐) 或 pip

### 2. 安装依赖

```bash
# 安装 uv（如果未安装）
pip install uv

# 安装所有依赖（包括分析模块）
uv sync --extra analysis
```

### 3. 配置 Cookie

⚠️ **关键步骤**：编辑 `settings.py`，填入链家网站的 Cookie

```python
# settings.py
Cookie = "lianjia_uuid=...; fng_nid=...; ..."  # 粘贴你的 Cookie
```

**获取方法**：
1. 访问 https://bj.lianjia.com
2. 按 F12 → Network → 找到任意请求 → 复制 Cookie 值
3. 粘贴到 `settings.py` 的 `Cookie` 变量中

### 4. 配置高德API Key（可选，用于地理分析）

```python
# settings.py
AMAP_API_KEY = "你的高德API密钥"  # 申请地址: https://lbs.amap.com/
```

### 5. 运行端到端示例

```bash
# 1. 爬取北京租房数据
uv run python -m src.cli --city bj --type rental

# 2. 数据清洗
uv run python scripts/preprocess_data.py --city bj

# 3. 添加地理坐标（需要高德API Key）
uv run python scripts/preprocess_data.py --city bj --add-coords --api-key "你的KEY"

# 4. 计算到就业中心的距离
uv run python scripts/calculate_distances.py --city bj

# 5. 采集周边配套设施（星巴克/麦当劳）
uv run python scripts/fetch_amenities.py --city bj

# 6. 运行各类分析（示例：城市对比）
uv run python scripts/analyze_cities.py

# 7. 查看结果
open output/analysis/city_comparison.png
```

---

## 1. 数据采集（爬虫）

### 基本用法

```bash
# 爬取北京租房数据
uv run python -m src.cli --city bj --type rental

# 爬取多个城市
uv run python -m src.cli --city bj sh gz --type rental

# 从断点恢复（中断后继续）
uv run python -m src.cli --city bj --type rental --resume

# 自定义延迟和重试
uv run python -m src.cli --city bj --type rental --delay 2.0 --retries 5
```

### 命令行参数

| 参数 | 可选值 | 说明 | 默认值 |
|------|--------|------|--------|
| `--city` | `bj` `sh` `sz` `gz` `hz` | 城市代码（可多个） | `bj` |
| `--type` | `rental` `secondhand` | 房产类型 | `rental` |
| `--strategy` | `http` `selenium` `drission` | 爬取策略 | `http` |
| `--delay` | 浮点数（秒） | 请求间隔 | `1.0` |
| `--retries` | 整数 | 重试次数 | `3` |
| `--resume` | - | 断点续传 | 禁用 |

### 输出文件

- `data/{city}_rental.csv` - 原始爬取数据（未清洗）
- `cache/{city}_rental_progress.json` - 进度文件（断点续传）

**字段**：城市、区域、板块、小区、户型、户型详情、租金、面积、单位租金、朝向、品牌、标题、链接

---

## 2. 数据预处理

### 2.1 数据清洗

**功能**：去重、异常值过滤、缺失值处理、单位租金计算

```bash
# 清洗单个城市
uv run python scripts/preprocess_data.py --city bj

# 批量清洗所有城市
uv run python scripts/preprocess_data.py --city bj sh sz gz hz

# 自定义输入输出路径
uv run python scripts/preprocess_data.py --input data/custom.csv --output data/clean.csv
```

### 2.2 地理坐标标注

**功能**：调用高德地图API获取房源经纬度（小区→板块→行政区三级降级策略）

```bash
# 添加坐标（需要高德API Key）
uv run python scripts/preprocess_data.py --city bj --add-coords --api-key "你的KEY"

# 批量处理
uv run python scripts/preprocess_data.py --city bj sh sz gz hz --add-coords --api-key "你的KEY"
```

**输出**：`data/{city}_rental_with_coordinate.csv`（新增字段：经度、纬度、坐标精度）

### 2.3 就业中心距离计算

**功能**：计算房源到核心就业中心（西二旗、望京、国贸等）的驾车距离

```bash
# 计算北京房源到就业中心的距离
uv run python scripts/calculate_distances.py --city bj

# 批量计算
uv run python scripts/calculate_distances.py --city bj sh sz gz hz

# 强制重新计算（忽略缓存）
uv run python scripts/calculate_distances.py --city bj --force
```

**就业中心配置**（每城市4个，共20个）：
- **北京**：西二旗、望京、国贸、金融街
- **上海**：陆家嘴、张江科学城、漕河泾、外滩
- **深圳**：南山科技园、深圳湾、福田CBD、坂田科技城
- **广州**：珠江新城、体育西路、天河软件园、广州科学城
- **杭州**：未来科技城、钱江新城、滨江区、湖滨商圈

**输出**：`data/{city}_rental_with_distances.csv`（新增字段：距离\_西二旗、距离\_望京、...、最近距离(km)）

### 2.4 周边配套设施采集

**功能**：统计房源1km范围内的星巴克和麦当劳数量

```bash
# 采集北京房源周边配套
uv run python scripts/fetch_amenities.py --city bj

# 自定义半径和并发数
uv run python scripts/fetch_amenities.py --city bj --radius 500 --workers 10

# 从头开始（忽略断点）
uv run python scripts/fetch_amenities.py --city bj --no-resume
```

**参数说明**：
- `--radius`：搜索半径（米），默认1000
- `--workers`：并发线程数，默认5，**建议不超过10**（避免封IP）

**输出**：`data/{city}_rental_with_amenities.csv`（新增字段：星巴克数量、麦当劳数量）

---

## 3. 数据分析（8个维度）

### 3.1 城市对比分析

**研究问题**：五城市租金水平差异、总租金 vs 单位租金梯队

```bash
# 运行分析
uv run python scripts/analyze_cities.py

# 仅分析部分城市
uv run python scripts/analyze_cities.py --city bj sh

# 不显示图表（仅保存文件）
uv run python scripts/analyze_cities.py --no-plot
```

**输出**：
- `output/analysis/city_statistics.csv` - 统计表格（9项指标 × 5城市）
- `output/analysis/city_comparison.png` - 可视化图表（2x2布局：箱线图+柱状图）

### 3.2 户型分析

**研究问题**：一居/两居/三居的价格差异、蜗居效应（小户型单位租金高）

```bash
# 运行分析
uv run python scripts/analyze_layouts.py

# 仅分析部分城市
uv run python scripts/analyze_layouts.py --city bj sh
```

**输出**：
- `output/analysis/layout_statistics.csv` - 统计表格
- `output/analysis/layout_pivot.csv` - 透视表（城市 × 户型）
- `output/analysis/layout_comparison.png` - 可视化图表（分组柱状图 + 热力图）

### 3.3 板块热度分析

**研究问题**：各城市内部哪些板块租金最高？哪些性价比高？

```bash
# 分析北京各板块
uv run python scripts/analyze_blocks.py --city bj

# 批量分析所有城市
uv run python scripts/analyze_blocks.py --city bj sh sz gz hz
```

**输出**（每城市）：
- `output/analysis/block_stats_{city}.csv` - 板块统计（TOP15）
- `output/analysis/block_comparison_{city}.png` - 双轴柱状图（租金 + 房源量）

### 3.4 朝向溢价分析

**研究问题**：南北通透 vs 纯南 vs 东西向的租金差异

```bash
# 运行分析
uv run python scripts/analyze_orientations.py

# 仅分析部分城市
uv run python scripts/analyze_orientations.py --city bj sh
```

**输出**：
- `output/analysis/orientation_statistics.csv` - 统计表格
- `output/analysis/orientation_pivot.csv` - 透视表（城市 × 朝向）
- `output/analysis/orientation_comparison.png` - 分组柱状图 + 热力图

### 3.5 品牌分布分析

**研究问题**：链家 vs 贝壳优选 vs 个人房源的市场占有率

```bash
# 运行分析
uv run python scripts/analyze_brands.py

# 仅分析部分城市
uv run python scripts/analyze_brands.py --city bj sh
```

**输出**：
- `output/analysis/brand_statistics.csv` - 品牌统计
- `output/analysis/brand_pivot.csv` - 透视表
- `output/analysis/brand_pivot_pct.csv` - 市占率透视表
- `output/analysis/brand_comparison.png` - 堆叠柱状图

### 3.6 工资-租金关系分析

**研究问题**：租房负担能力，哪个城市租房压力最大？

```bash
# 运行分析
uv run python scripts/analyze_salary_rent.py

# 静默模式
uv run python scripts/analyze_salary_rent.py --quiet
```

**输出**：
- `output/analysis/salary_rent_statistics.csv` - 统计表格（6类衍生指标）
- `output/analysis/salary_rent_comparison.png` - 可视化图表（2x2布局）

### 3.7 距离衰减分析

**研究问题**：距离就业中心越远租金越低？衰减系数多少？哪里是价格洼地？

```bash
# 分析北京的距离衰减（全局最近距离）
uv run python scripts/analyze_distance_decay.py --city bj

# 分析特定就业中心
uv run python scripts/analyze_distance_decay.py --city bj --center 西二旗 --visualize

# 找出价格洼地（残差阈值-800）
uv run python scripts/analyze_distance_decay.py --city bj --find-value-zones --threshold -800

# 生成可视化（同心圆地图 + 散点图）
uv run python scripts/analyze_distance_decay.py --city bj --visualize

# 只分析单位租金（而非总租金）
uv run python scripts/analyze_distance_decay.py --city bj --metric 单位租金

# 限制最大距离（只分析20km以内）
uv run python scripts/analyze_distance_decay.py --city bj --max-distance 20
```

**输出**：
- `output/distance_analysis/{city}_distance_stats.csv` - 距离分组统计
- `output/distance_analysis/{city}_model_comparison.csv` - 回归模型对比
- `output/distance_analysis/{city}_min_distance_regression.png` - 回归散点图
- `output/distance_maps/{city}_{center}_circle_map.html` - 同心圆地图

### 3.8 配套设施溢价分析

**研究问题**：周边有星巴克/麦当劳的区域租金是否更高？溢价多少？

```bash
# 基本分析（不生成图表）
uv run python scripts/analyze_amenities.py --city bj

# 完整分析+可视化
uv run python scripts/analyze_amenities.py --city bj --visualize

# 只分析星巴克
uv run python scripts/analyze_amenities.py --city bj --amenity starbucks --visualize

# 自定义输出目录
uv run python scripts/analyze_amenities.py --city bj --visualize --output-dir results/bj_amenity
```

**输出**：
- `output/amenity_analysis/{city}_density_stats.csv` - 密度统计表
- `output/amenity_analysis/{city}_amenity_report.md` - Markdown格式分析报告
- `output/amenity_analysis/{city}_*_boxplot.png` - 箱线图（有/无配套对比）
- `output/amenity_analysis/{city}_*_scatter.png` - 散点图（配套数量 vs 租金）
- `output/amenity_analysis/{city}_density_barplot.png` - 密度分级柱状图
- `output/amenity_analysis/{city}_heatmap.png` - 星巴克×麦当劳交叉影响热力图

### 3.9 地图可视化

**功能**：生成交互式租金热力图（Folium地图）

```bash
# 生成北京租金热力图
uv run python scripts/visualize_map.py --city bj

# 批量生成所有城市
uv run python scripts/visualize_map.py --city bj sh sz gz hz

# 自定义输出路径
uv run python scripts/visualize_map.py --city bj --output output/custom_maps
```

**输出**：`output/maps/{city}_rental_heatmap.html`（可用浏览器打开）

---

## 配置说明

### settings.py 关键配置

```python
# ============ 链家 Cookie（必填）============
Cookie = "lianjia_uuid=...; fng_nid=...; ..."  # 从浏览器复制

# ============ 高德地图 API Key（地理分析必填）============
AMAP_API_KEY = "你的高德API密钥"  # 申请地址: https://lbs.amap.com/

# ============ 爬虫配置 ============
DOWNLOAD_DELAY = 1.0  # 请求间隔（秒）
MAX_RETRIES = 3  # 重试次数
USER_AGENT = "Mozilla/5.0 ..."  # User-Agent
PROXY = None  # 代理（可选）

# ============ 城市配置 ============
CITIES = {
    'bj': {'name': '北京', 'rental_url': '...'},
    'sh': {'name': '上海', 'rental_url': '...'},
    # ...
}

# ============ 就业中心配置 ============
EMPLOYMENT_CENTERS = {
    'bj': [
        {'name': '西二旗', 'lat': 40.0559, 'lon': 116.3076},
        {'name': '望京', 'lat': 40.0035, 'lon': 116.4777},
        # ...
    ],
    # ...
}

# ============ 工资数据配置（2024年）============
SALARY_DATA = {
    '北京': (224608, 106905, 92464),  # (非私营年薪, 私营年薪, 人均可支配收入)
    '上海': (229337, 111347, 93095),
    # ...
}
```

---

## 项目结构

```
Lianjia-Housing-Analysis/
├── pyproject.toml              # 项目依赖配置(uv管理)
├── uv.lock                     # 依赖锁定文件
├── settings.py                 # 全局配置文件
├── README.md                   # 本文档
│
├── src/                        # 源代码目录
│   ├── cli.py                  # 命令行入口
│   ├── spider/                 # 爬虫模块
│   │   ├── core/               # 核心功能(调度器、解析器、策略)
│   │   ├── items/              # 数据模型
│   │   ├── storage/            # CSV写入器
│   │   └── config/             # 配置常量
│   ├── preprocess/             # 数据预处理模块
│   │   ├── data_cleaner.py     # 数据清洗
│   │   ├── coordinates.py      # 坐标转换
│   │   └── constants.py        # 预处理常量
│   ├── analysis/               # 数据分析模块(8个维度)
│   │   ├── city_comparison.py
│   │   ├── layout_analysis.py
│   │   ├── block_comparison.py
│   │   ├── orientation_visualizer.py
│   │   ├── brand_visualizer.py
│   │   ├── salary_rent_comparison.py
│   │   ├── distance_decay.py
│   │   ├── amenity_analyzer.py
│   │   └── map_visualizer.py
│   └── crawler/                # 外部数据爬取
│       └── amenity_crawler.py  # POI采集
│
├── data/                       # 数据文件目录
│   ├── xxx_rental.csv          # 原始爬取数据
│   ├── xxx_rental_clean.csv    # 清洗后数据
│   ├── xxx_rental_with_coordinate.csv    # 带坐标数据
│   ├── xxx_rental_with_distances.csv     # 带通勤距离数据
│   └── xxx_rental_with_amenities.csv     # 带配套设施数据
│
├── output/                     # 分析结果输出
│   ├── analysis/               # 统计分析结果(CSV + PNG)
│   ├── maps/                   # 地图可视化结果(HTML)
│   ├── distance_analysis/      # 通勤距离分析结果
│   └── amenity_analysis/       # 配套设施分析结果
│
├── scripts/                    # 快捷执行脚本
│   ├── preprocess_data.py
│   ├── calculate_distances.py
│   ├── fetch_amenities.py
│   ├── analyze_cities.py
│   ├── analyze_layouts.py
│   ├── analyze_blocks.py
│   ├── analyze_orientations.py
│   ├── analyze_brands.py
│   ├── analyze_salary_rent.py
│   ├── analyze_distance_decay.py
│   ├── analyze_amenities.py
│   └── visualize_map.py
│
└── cache/                      # 临时缓存文件
    └── xxx_progress.json       # 爬取进度记录

注: xxx 代表城市代码(bj/sh/gz/sz/hz)
```

---

## 数据集说明

### 原始数据

爬取自链家网站（2025年12月数据），涵盖5个城市：

| 城市 | 原始记录 | 清洗后 | 保留率 |
|------|---------|--------|--------|
| 北京 | 43,433 | 28,926 | 66.6% |
| 上海 | 21,796 | 15,136 | 69.5% |
| 深圳 | 15,893 | 11,028 | 69.4% |
| 广州 | 19,637 | 13,556 | 69.0% |
| 杭州 | 21,234 | 14,722 | 69.3% |

### 最终数据集字段

**基础字段**（13个）：城市、区域、板块、小区、户型、户型详情、租金、面积、单位租金、朝向、品牌、标题、链接

**扩展字段**（可选）：
- **地理标注**：经度、纬度、坐标精度
- **距离分析**：距离\_西二旗、距离\_望京、...、最近距离(km)
- **配套设施**：星巴克数量、麦当劳数量

---