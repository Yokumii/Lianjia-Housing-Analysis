#import "../lib.typ": *

#let (
  doctype,
  date,
  twoside,
  anonymous,
  info,
  doc,
  preface,
  mainmatter,
  appendix,
  cover,
  cover-en,
  declare,
  abstract,
  abstract-en,
  outline,
  image-outline,
  table-outline,
  algorithm-outline,
  nomenclature,
  bib,
  acknowledgement,
  achievement,
  summary-en,
) = documentclass(
  doctype: "report", // 文档类型: "master" | "doctor" | "bachelor"
  date: datetime.today(), // 日期
  twoside: false, // 双面模式
  print: false, // 打印模式, 设置为 true 时，根据奇偶页调整页边距
  anonymous: false, // 盲审模式
  info: (
    course_name: "Python程序设计",
    experiment_name: "五大城市租房市场多维度特征差异与职住适配度全景分析",
    student_id: "2023212539",
    name: "张珂铭",
    name_en: "Zhang San",
    class: "2023211305",
    degree: "课程报告",
    supervisor: "李炜",
    supervisor_en: "Prof. Li Si",
    title: "课程名称",
    title_en: "DISSERTATION TEMPLATE FOR MASTER DEGREE OF ENGINEERING IN SHANGHAI JIAO TONG UNIVERSITY",
    school: "计算机学院（国家示范性软件学院）",
    school_en: "School of XXXXXXX",
    major: "计算机科学与技术",
  ),
)

#show: doc

#cover()

#if doctype != "report" [
  #cover-en()
]

#declare(
  confidentialty-level: "internal", // 保密级别: "public" | "internal" | "secret" | "confidential"
  confidentialty-year: 2, // 保密年份数，请根据保密级别的要求填写
  date: datetime.today(),
  original-statement-sign: place(dx: 13cm, dy: -1.3cm, image("figures/student-sign.png", height: 2em)), // 请根据签名图片的大小，自行调整图片的高度和位置
  authorization-author-sign: place(dx: 5cm, dy: -1.3cm, image("figures/student-sign.png", height: 2em)),
  supervisor-sign: place(dx: 4cm, dy: -1.2cm, image("figures/supervisor-sign.png", height: 2em)),
) // 不需要显示日期和签名，可直接注释

#show: preface

#if doctype != "report" [
  #abstract(keywords: (
    "学位论文",
    "论文格式",
    "规范化",
    "模板",
  ))[
    学位论文是研究生从事科研工作的成果的主要表现，集中表明了作者在研究工作中获得的新的发明、理论或见解，是研究生申请硕士或博士学位的重要依据，也是科研领域中的重要文献资料和社会的宝贵财富。
  
    为了提高研究生学位论文的质量，做到学位论文在内容和格式上的规范化与统一化，特制作本模板。
  ]

  #abstract-en(keywords: ("dissertation", "dissertation format", "standardization", "template"))[
    As a primary means of demonstrating research findings for postgraduate students, dissertation is a systematic and standardized record of the new inventions, theories or insights obtained by the author in the research work. It can not only function as an important reference when students pursue further studies, but also contribute to scientific research and social development.
  
    This template is therefore made to improve the quality of postgraduates' dissertations and to further standardize it both in content and in format.
  ]
]

#outline()

#if doctype != "report" [
  #image-outline() // 插图目录

  #table-outline() // 表格目录

  #algorithm-outline() // 算法目录

  #nomenclature(
    width: 50%,
    columns: (1fr, 1.5fr),
  )[
    / $epsilon$: 介电常数
    / $mu$: 磁导率
    / $epsilon$: 介电常数
    / $mu$: 磁导率
    / $epsilon$: 介电常数
    / $mu$: 磁导率
  ]
]

#show: mainmatter
// #show: mainmatter.with(enable-avoid-orphan-headings: true) // 避免孤行标题，此为实验性功能，会对页面顶部距离造成影响
#show: word-count-cjk // 正文字数统计

#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#show: codly-init.with()
#codly(languages: codly-languages)

= 项目简介 <chp:intro>

== 任务目标和意义

本项目旨在利用 Python 数据采集与分析技术，深入探究中国主要城市的租赁市场特征。以*北京、上海、广州、深圳*四个一线城市及*杭州*（新一线城市的代表）为研究对象，构建多维度的数据分析框架。本项目具体将达成以下四个核心层面的任务目标：
 
+ 数据爬取与清洗工程；
+ 租赁市场多维统计分析，包括*总体价格特征画像*、*户型与供给结构分析*和*市场主体格局分析*；
+ 房源属性与空间价值挖掘，包括*空间板块价值分层*和*朝向溢价与归因分析*；
+ 经济关联与深度拓展研究，包括*租房负担能力评估*、*互联网核心区的通勤半径与租金衰减*和*周边配套与租金溢价的关系*#footnote[有研究表明，周围有星巴克、麦当劳等配套设施的区域，通常代表了更高的社区活力和年轻人聚集度。]；

== 报告结构说明

本报告共分为六个章节#footnote[*本文的正文+附录总页数为30页*，但由于排版原因，实际页数还包含封面和目录，整体符合要求，希望老师理解。由于篇幅限制省略的内容可查看网页https://yokumii.github.io/Lianjia-Housing-Analysis/]，除本章外具体安排如下：

*第二章*（数据获取与清洗工程）详细阐述数据来源、爬虫技术方案和数据清洗流程；

*第三章*（租赁市场多维统计分析）从宏观层面，对比五城市的总体房租水平、不同户型房源结构与价格差异、市场主体与中介品牌分布，揭示城市间的租赁市场格局差异；

*第四章*（房源属性与空间价值挖掘）聚焦城市内部的空间异质性，分析板块均价热度分布以及房屋朝向对租金的影响，挖掘房源属性中的隐含价值规律；

*第五章*（经济关联与深度拓展研究）置于更广阔的经济社会背景中考察，探讨租房负担能力与收入关系、通勤半径与租金衰减规律、周边配套设施对租金的溢价效应；

*第六章*（总结与展望）系统回顾项目核心成果、技术学习收获与心得体会；

= 数据获取与清洗工程

== 数据来源说明

本项目数据来源于*链家网*（ https://www.lianjia.com ），这是中国最大的房地产中介服务平台之一，覆盖全国主要城市，拥有海量真实房源数据。租房数据获取范围如下：
- *目标城市*：北京、上海、广州、深圳、杭州共5个城市
- *采集时间*：2025年12月
- *数据规模*：原始数据约17万条，清洗后有效数据11.4万余条，其中有效房源数量最少的深圳有 14405 条，占深圳实际房源总量的 28%，满足要求。

== 爬虫技术方案

=== 反爬策略与应对

通过对链家反爬机制的简单逆向，不难发现其主要通过*IceManSDK* 劫持前端网络请求来监控服务器返回的状态。当服务器判定当前用户可能是爬虫时，该 SDK 会拦截响应，中断正常的业务流程，并弹出验证码/阻断页面（通过CaptchaSDK生成验证码#footnote[通过分析 *CaptchaSDK* 可以找到获取/提交验证的API：`GET /captcha/resource?sceneId=...&token=...`和`GET /captcha/pre-validate?sceneId=...&token=...&challenger=...`，可以用来接入自动过码平台，不过成本太高，本项目不采用。]）。其作为“哨兵”，实际执行逻辑在后端，难以进行逆向或伪造指纹。故本项目采用以下策略：

#tablex(
  [验证码拦截],
  [策略切换],
  [HTTP 策略失败时切换到 DrissionPage 浏览器模拟],

  [请求频率限制],
  [延迟与随机化],
  [每次请求间隔 1–2 秒，随机化延迟时间],

  [Cookie 过期],
  [配置化管理],
  [从 `settings.py` 读取 Cookie，支持热更新],

  [IP 封禁],
  [低频爬取],
  [顺序遍历区域，避免并发请求触发封禁],

  [User-Agent 检测],
  [真实浏览器头],
  [HTTP 策略使用 Chrome User-Agent，模拟真实浏览器],

  header: (
    [*反爬机制*],
    [*应对策略*],
    table.hline(end: 3, stroke: 0.25pt),
    [*实现方式*],
  ),
  columns: 3,
  caption: [爬虫反爬策略对照表],
  label-name: "anti-scraping-strategies",
)

=== 核心技术架构设计

本项目在前期作业的基础上，优化了并设计了*策略模式爬虫框架*，通过抽象基类 `CrawlStrategy` + 具体策略实现（`HttpStrategy`, `DrissionPageStrategy`），支持灵活切换爬取策略，针对链家网的反爬机制进行针对性设计。具体爬虫模块在 `src/spider` 下实现，核心技术栈包括：

#tablex(
  [requests],
  [>=2.28.0],
  [轻量级 HTTP 请求库],

  [DrissionPage],
  [>=4.0.0],
  [现代浏览器自动化工具，自动化特征较少],

  [lxml],
  [>=4.9.0],
  [高性能 HTML 解析库，支持 CSS 选择器提取],

  [Pandas],
  [>=1.5.0],
  [数据处理与 CSV 导出],

  header: (
    [*名称*],
    [*版本*],
    table.hline(end: 3, stroke: 0.25pt),
    [*说明*]
  ),
  columns: 3,
  caption: [主要技术与依赖库],
  label-name: "tech-stack-table",
)

本项目采用*模块化分层架构*，各组件职责清晰：

#tablex(
  [协调层],
  [`SpiderOrchestrator`],
  [任务调度、区域遍历、进度管理],

  [策略层],
  [`HttpStrategy`],
  [requests 实现的 HTTP 爬取],

  [],
  [`DrissionPageStrategy`],
  [浏览器自动化爬取（备用）],

  [解析层],
  [`Parser`],
  [CSS 选择器提取房源字段],

  [存储层],
  [`CsvWriter`],
  [CSV 追加写入],

  [状态层],
  [`StateManager`],
  [进度保存、断点续传],

  header: (
    [*模块*],
    [*核心类*],
    table.hline(end: 3, stroke: 0.25pt),
    [*职责*],
  ),
  columns: 3,
  caption: [爬虫架构分层],
  label-name: "spider-architecture",
)

核心工作流程：

+ *初始化*：从 `settings.py` 加载城市配置、Cookie、选择器
+ *生成任务*：`UrlGenerator` 遍历城市的所有行政区，动态获取总页数
+ *顺序爬取*：`SpiderOrchestrator` 按区域→页码顺序执行
+ *HTML 解析*：`Parser` 使用 CSS 选择器提取房源数据
+ *原始存储*：`CsvWriter` 追加到 CSV（保留所有采集数据，去重在预处理阶段进行）
+ *进度持久化*：`StateManager` 保存 `{city}|{district}: page` 状态

=== 核心代码实现

==== SpiderOrchestrator 协调器

爬虫的核心调度逻辑，负责任务管理、页面获取、数据解析和存储：

```python
class SpiderOrchestrator:
    """爬虫协调器"""
    def crawl(self, delay: float = 1.0, resume: bool = True):
        # 1. 生成所有任务键（{city}|{district} 格式）
        task_keys = UrlGenerator.get_all_task_keys([self.city])
        self.state_manager.init_tasks(task_keys, self.csv_path)
        # 2. 获取待处理任务（跳过已完成的）
        pending_tasks = self.state_manager.get_pending_tasks()
        # 3. 遍历每个任务
        for task_key, page_num in pending_tasks:
            city_code, district = task_key.split('|')
            # 3.1 构建 URL
            url = UrlGenerator.build_url(
                city_code, district, page_num, self.property_type
            )
            # 3.2 获取页面 HTML（通过策略模式）
            html = self.strategy.fetch_page(url)
            # 3.3 解析总页数（动态判断是否继续）
            max_page = self.parser.get_max_page(html)
            if page_num > max_page:
                self.state_manager.mark_done(task_key)  # 标记完成
                continue
            # 3.4 提取房源数据
            items = self.parser.parse(html, city_name, district, city_code)
            # 3.5 追加到 CSV（原始数据，不去重）
            self.writer.append(items)
            # 3.6 更新进度状态
            if page_num >= max_page:
                self.state_manager.mark_done(task_key)  # 完成
            else:
                self.state_manager.update_page(task_key, page_num + 1)
            # 3.7 延迟（反爬）
            time.sleep(delay)
```

首次爬取某区域时，从 HTML 中提取 `total_count` 并自动确定最大页码。每完成一页立即保存进度，异常中断后可从上次位置继续。

==== HttpStrategy 请求策略

基于 `requests` 的 HTTP 请求实现，保持 Cookie 和连接池，*复用Session*，并采用*指数退避*，避免触发频率限制，以及*User-Agent 伪装*，降低被识别概率，核心代码如下：

```python
class HttpStrategy(CrawlStrategy):
    """HTTP 请求策略"""
    def fetch_page(self, url: str) -> str:
        # 获取页面 HTML
        for attempt in range(self.retries):
            try:
                response = self.session.get(
                    url, timeout=self.timeout,
                    headers=self.session.headers,
                    verify=self.verify_ssl
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == self.retries - 1:
                    raise  # 最后一次重试失败，抛出异常
                time.sleep(2 ** attempt)  # 指数退避
```

=== 断点续传机制

为防止爬虫中断导致数据丢失，我实现了基于 `StateManager` 的状态管理：

+ *进度格式*：`{city_code}|{district}: page_number` 或 `-1`（表示完成）
+ *状态文件*：`cache/{city}_{property_type}_state.json`
+ *保存时机*：每完成一页或遇到异常时立即保存
+ *恢复机制*：启动时 → 加载状态文件 → 按 `{city}|{district}` 键检查进度 → 跳过已完成（page=-1）或从中断页继续。

```python
class StateManager:
    def get_current_page(self, city: str, district: str) -> int:
        """获取当前区域的爬取进度"""
        key = f"{city}|{district}"
        return self.state_data.get(key, 1)

    def save_progress(self, city: str, district: str, page: int):
        """保存进度（-1 表示完成）"""
        key = f"{city}|{district}"
        self.state_data[key] = page
        # 原子写入 JSON 文件
        self._atomic_write()
```

=== 运行方法与结果

采用*顺序爬取*模式，避免并发封禁：

1. 每个城市独立运行：`python main.py --city bj --type rental`
2. `SpiderOrchestrator` 遍历该城市所有行政区
3. 每个行政区首先请求第一页，解析总页数
4. 顺序爬取该区域的所有分页（`pg1` → `pg2` → ...）
5. 输出到独立 CSV：`data/{city}_rental.csv`
6. 状态保存：`cache/{city}_rental_state.json`

这种方式可以避免并发请求触发 IP 封禁，支持随时中断和恢复。实际测试过程中，初期能爬取 6000 条左右的数据不触发人机验证。后期由于可能存在的 IP/账号被标记，导致会定期触发风控，具体表现为爬取几百条数据后需要手动过一次验证码，同时链家容易在页码为 10 的倍数的页面进行人机验证。

== 数据清洗与规整

原始爬取数据存在*重复、缺失、异常值、格式不一致*等问题，需要系统化清洗。本项目实现了 *7 步清洗流程*（`src/preprocess/data_cleaner.py`）。

=== 清洗流程设计

#import "@preview/fletcher:0.5.8" as fletcher: diagram, edge, node
#import fletcher.shapes: parallelogram

#imagex(
  diagram(
    node-stroke: 0.5pt,
    node-inset: 0.7em,
    spacing: 1.4em,
    edge-corner-radius: 5pt,

    // 起点
    node((0, 0), "原始CSV", shape: parallelogram),

    // 第 1 列：向下
    edge("-|>"),
    node((0, 1), "Step 1:数据标准化"),
    edge("-|>"),
    node((0, 2), "Step 2:智能去重"),
    
    // 转到第 2 列（向上）
    edge("-|>"),
    node((1, 2), "Step 3:户型过滤"),
    edge("-|>"),
    node((1, 1), "Step 4:业务规则清洗"),
    edge("-|>"),
    node((1, 0), "Step 5:缺失值处理"),

    // 转到第 3 列（向下）
    edge("-|>"),
    node((2, 0), "Step 6:计算单位租金"),
    edge("-|>"),
    node((2, 1), "Step 7:列顺序整理"),
    edge("-|>"),
    node((2, 2), "Clean CSV", shape: parallelogram, corner-radius: 5pt),
  ),
  caption: [数据清洗流程图],
  label-name: "cleaning-flowchart",
)

=== 详细清洗步骤

*Step 1: 数据标准化* 将"未知"、空字符串统一转为 `NaN`，数值字段自动类型转换

```python
df = df.replace(['未知', '', 'null', 'None'], np.nan)
df['租金'] = pd.to_numeric(df['租金'], errors='coerce')
df['面积'] = pd.to_numeric(df['面积'], errors='coerce')
```

*Step 2: 智能去重* 按"链接"字段分组，合并相同房源的不同采集记录#footnote[以北京为例，从 43,433 条 → 31,751 条（去除 26.9% 重复）。
]

#tablex(
  [最新值],
  [租金、面积、朝向],
  [保留最后一次爬取的值（可能有价格更新）],

  [众数],
  [品牌],
  [多次爬取的品牌取出现最多的],

  [非空优先],
  [小区、板块],
  [如果某次缺失，取其他记录的值],

  header: (
    [*去重策略*],
    [*字段*],
    table.hline(end: 3, stroke: 0.25pt),
    [*选择逻辑*],
  ),
  columns: 3,
  caption: [去重合并规则],
  label-name: "dedup-rules",
)


*Step 3: 户型过滤* 删除"四居+"房源#footnote[考虑到四居房源数量少，且一般需求用户与一～三居房不符合，因此进行过滤。]

```python
df = df[~df['户型'].str.contains('四居', na=False)]
```

*Step 4: 业务规则异常值清洗* 基于租房市场常识，我设定了的区间如@tbl:outlier-thresholds 所示

#tablex(
  [面积],
  [5 ㎡],
  [500 ㎡],
  [正常租房面积范围],

  [租金],
  [100 元],
  [100,000 元],
  [排除假房源和豪宅],

  [单位租金],
  [1 元/㎡],
  [1,200 元/㎡],
  [排除价格录入错误],

  header: (
    [*字段*],
    [*下限*],
    [*上限*],
    table.hline(end: 4, stroke: 0.25pt),
    [*清洗理由*],
  ),
  columns: 4,
  caption: [业务规则异常值阈值],
  label-name: "outlier-thresholds",
)

```python
df = df[
    (df['面积'] >= 5) & (df['面积'] <= 500) &
    (df['租金'] >= 100) & (df['租金'] <= 100000) &
    (df['单位租金'] >= 1) & (df['单位租金'] <= 1200)
]
```

*Step 5: 缺失值处理*

+ *品牌缺失*：默认填充"链家"（数据来源）
+ *关键字段缺失*（租金/面积/朝向/板块）：直接删除记录

*Step 6: 单位面积租金计算* 核心评价指标，用于后续分析

```python
df['单位租金'] = (df['租金'] / df['面积']).round(2)
```

*Step 7: 列顺序整理* 按标准顺序输出 13 个字段，代码实现略。

=== 地理坐标增强

为支持空间分析（距离衰减、地图可视化），使用 *高德地图 API* 为每条房源添加经纬度坐标（`src/preprocess/coordinates.py`）。

由于部分小区名称无法精确匹配，采用多级降级，智能地址降级策略如@tbl:address-fallback 所示。

#tablex(
  [A：小区级],
  [`{城市}{区域}{小区}`],
  [★★★★★],
  ["北京市朝阳区美岸栖庭"],

  [B：板块级],
  [`{城市}{区域}{板块}商圈`],
  [★★★],
  ["北京市朝阳区望京商圈"],

  [C：行政区级],
  [`{城市}{区域}`],
  [★★],
  ["北京市朝阳区"],

  header: (
    [*策略*],
    [*地址格式*],
    [*精度*],
    table.hline(end: 4, stroke: 0.25pt),
    [*示例*],
  ),
  columns: 4,
  caption: [地址降级策略],
  label-name: "address-fallback",
)

高德地理编码API调用逻辑以及核心代码如下：

```python
class CoordinateProvider:
    """地理坐标提供者"""
    def get_coordinates(self, address: str, city: str):
        """调用高德API获取经纬度"""
        params = {
            'address': address, 'city': city,
            'key': self.api_key, 'output': 'JSON'
        }
        response = requests.get(
            "https://restapi.amap.com/v3/geocode/geo",
            params=params, timeout=5
        )
        data = response.json()
        # 解析返回的经纬度，代码略
```

=== 周边配套设施获取

对于房源周边的 POI 信息，初次尝试时仍利用高德 API 进行获取，但发现时效性不强且返回结果有限，因此选择星巴克和麦当劳#footnote[这两类品牌具有严格的选址标准（人流量、消费能力、交通便利性），其密度可作为区域商业成熟度的代理变量]的网页端并抓取到对应的搜索请求，使用该 API 获取周边门店数量（`src/crawler/amenity_crawler.py`）：

```python
def fetch_starbucks(self, lat: float, lon: float) -> int:
    """查询周边星巴克数量"""
    params = {'lat': lat, 'lon': lon, 'radius': 1000}
    response = requests.get(
        "https://www.starbucks.com.cn/api/stores/nearby",
        params=params
    )
    data = response.json()
    return data.get('meta', {}).get('total', 0)
def fetch_mcdonalds(self, lat: float, lon: float) -> int:
    """查询周边麦当劳数量"""
    point = f"{lat},{lon}" # 构造POST参数
    data = {'point': point, 'type': ''}
    response = requests.post(
        self.MCDONALDS_API, data=data,
        headers=self.headers, timeout=10
    )
    result = response.json()
    stores = result.get('data', [])
    # 过滤距离在radius_m内的门店
    count = sum(1 for store in stores if store.get('_distance', float('inf')) <= self.radius_m)
    return count
```

搜索半径默认为 1000米（1公里），平衡覆盖范围与准确性，并使用`ThreadPoolExecutor`并发请求，加速爬取，同样支持断点续爬。

== 数据集概览与存储

清洗后的最终数据集#footnote[清洗后有效数据 *114,635 条*，平均保留率 *67.1%*。]：

#tablex(

  [北京 (BJ)],
  [43,433],
  [28,927],
  [66.6%],
  [6,107 元],
  [81.2 ㎡],
  [77.79 元/㎡],

  [上海 (SH)],
  [32,156],
  [21,797],
  [67.8%],
  [5,832 元],
  [68.3 ㎡],
  [87.42 元/㎡],

  [广州 (GZ)],
  [35,842],
  [24,100],
  [67.2%],
  [4,215 元],
  [75.6 ㎡],
  [58.13 元/㎡],

  [深圳 (SZ)],
  [21,504],
  [14,405],
  [67.0%],
  [5,943 元],
  [62.4 ㎡],
  [97.26 元/㎡],

  [杭州 (HZ)],
  [37,872],
  [25,406],
  [67.1%],
  [4,568 元],
  [70.8 ㎡],
  [67.39 元/㎡],

  header: (
    table.hline(stroke: 0.5pt),
    [*城市*], [*原始数据*], [*清洗后*], [*保留率*], [*平均租金*], [*平均面积*], [*平均单价*],
  ),
  columns: 7,
  caption: "五城市租房数据汇总表",
  label-name: "dataset-summary",
)

最终数据集包含：城市、区域、板块、小区、户型、户型详情、租金、面积、单位租金、朝向、品牌、标题、链接、经度、纬度、坐标精度、距离\_就业中心、最近距离(km)、星巴克数量、麦当劳数量。

北京某真实房源如@img:数据样例 所示。

#imagex(
  image(
    "figures/shujuyangli.png",
    width: 90%,
  ),
  caption: [数据样例],
  label-name: "数据样例",
)

数据以 *CSV 格式* 存储，编码为 `UTF-8-SIG`（兼容Excel），每个城市独立文件，便于增量更新和分城市分析，命名规则见附录A。

= 租赁市场多维统计分析

== 五城市总体房租水平对比

=== 程序实现

`CityComparator` 模块用于城市间租金统计计算，使用 `groupby().agg()` 一次性计算5个指标，避免多次遍历数据，提高效率。核心代码如下：

```python
# 按城市分组，计算多指标统计
stats = df_all.groupby('城市').agg({
    '租金': ['mean', 'max', 'min', 'median', 'count'],
    '单位租金': ['mean', 'max', 'min', 'median'] }).round(1)
```

`CityVisualizer` 类专门负责统计结果的可视化，箱线图展示分布离散度，柱状图量化统计差异。核心代码如下：

```python
# 箱线图：展示租金分布和离群值
sns.boxplot(x='城市', y='租金', data=df, ax=axes[0, 0], palette="Set2")
sns.boxplot(x='城市', y='单位租金', data=df, ax=axes[0, 1], palette="Set2")
# 柱状图：对比多个统计指标
sns.barplot(x='城市', y='值', hue='指标',
           data=stats_melted, ax=axes[1, 0], palette="Blues_d")
sns.barplot(x='城市', y='值', hue='指标',
           data=stats_melted, ax=axes[1, 1], palette="Greens_d")
```

=== 结果分析

五城市租金对比的可视化结果如@img:city-comparison 所示，呈现以下关键特征：

#imagex(
  image(
    "../../output/analysis/city_comparison.png",
    width: 90%,
  ),
  caption: [五城市租金对比分析图],
  label-name: "city-comparison",
)

+ *总租金梯队分化明显*：*第一梯队*：上海和北京领跑全国，两城均价接近，均显著高于其他城市，深圳紧随其后，与京沪差距约200-300元；*第二梯队*：杭州和广州租金水平相近，约为京沪的55%

+ *单位租金呈现不同格局*：
   - *高单价城市*：上海、深圳和北京单位租金领先
   - *性价比城市*：杭州和广州单位租金“*亲民*”，这对于应届生或工薪阶层来说，生存压力明显较小
   - *深圳特征*：总租金略低于京沪，但单位租金逼近上海，这暗示了深圳的房源户型普遍偏小，在深圳租房，花的每一分钱买到的空间是最少的

+ *价格离散程度*：箱线图显示所有城市均存在大量高租金离群值，这些高端房源（长尾）同时拉高了整体平均值，导致中位数普遍低于均价，租金分布呈*右偏*。其中，深圳最低租金门槛最高（1200元），反映其*租房市场准入成本较高*

== 不同户型房源结构与价格差异

=== 程序实现

`LayoutComparator` 类使用 `pd.Categorical` 确保图表按面积递增排序，同时使用二级分组 `groupby(['城市', '户型'])` ，刻画双维度差异。核心代码如下：

```python
# 转换为有序分类类型（确保图表按一居→两居→三居排序）
df_filtered['户型'] = pd.Categorical(
    df_filtered['户型'], categories=TARGET_LAYOUTS, ordered=True)
# 按城市和户型二级分组聚合
stats = df_filtered.groupby(['城市', '户型']).agg({
    '租金': ['mean', 'max', 'min', 'median', 'count'],
    '单位租金': ['mean', 'max', 'min', 'median']}).round(1)
```

`LayoutVisualizer` 类用于可视化分组柱状图（同城对比）+ 热力图（全局定位），核心代码如下：

```python
# 分组柱状图：城市内按户型并列对比
sns.barplot(x='城市', y='租金', hue='户型', data=df, ax=ax1, palette="Set2")
ax1.bar_label(container, fmt='%.0f')
sns.barplot(x='城市', y='单位租金', hue='户型', data=df, ax=ax2, palette="Set2")
# 热力图：城市 x 户型透视表
sns.heatmap(pivot_rent, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax3)
sns.heatmap(pivot_unit, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax4)
```

=== 结果分析

户型对比的可视化结果如@img:layout-comparison 所示，可以得出以下核心发现：

#imagex(
  image(
    "../../output/analysis/layout_comparison.png",
    width: 90%,
  ),
  caption: [五城市户型租金对比分析图],
  label-name: "layout-comparison",
)

1. *总租金单调递增规律*：所有城市均呈现*一居 < 两居 < 三居*的总租金阶梯。其中，北京、上海三居室租金突破8600元大关，接近一居室的1.8-1.9倍；广州、杭州户型间价差相对较小（三居约为一居的1.5倍），市场价格梯度平缓

2. *单位租金的蜗居效应*：单位租金呈现*一居 > 两居 > 三居*的*反向递减*趋势，验证了“*蜗居效应*”，即一居室的单位租金是最高的，因为厨房、卫生间等“硬成本”被分摊到了较小的面积上，同时由于稀缺性、租赁灵活性、需求旺盛等因素导致溢价

3. *城市差异模式*：
   - *京沪特征*：三居室租金相近（8656 vs 8666元），但上海一居单位租金领先北京13元/㎡（105.2 vs 92.2），小户型竞争更激烈
   - *深圳特殊性*：一居总租金仅3943元（五城最低），但单位租金高达92.8元/㎡（接近北京水平），说明深圳一居室以超小户型为主（平均仅42㎡）
   - *杭州反常现象*：两居租金（3041元）*低于*一居（3286元），可能因两居多集中在远郊、一居集中在核心商圈

通过以上分析，也可以得出一些租赁启示：对于*性价比追求者*：选择三居室（单位租金最低，面积利用率高）；对于*预算敏感者*：选择两居室（总租金和单位租金的平衡点）；对于*单人租客*：需权衡一居室的便利性与高单价，深圳、上海需特别警惕小户型溢价陷阱

== 市场主体与中介品牌分布

=== 程序实现

可视化采用*堆积柱状图*：上半部分为绝对房源数量，下半部分为市场占有率。品牌房源分组和统计的核心代码如下：

```python
# 按城市×品牌分组统计房源数
summary=df.groupby(['城市','品牌']).size().reset_index(name='房源数')
city_totals = df.groupby('城市').size() # 计算市占率
summary['市占率'] = (summary['房源数量'] / city_totals) * 100
```

=== 结果分析

五城市品牌分布对比结果如@img:brand-comparison 所示，可以得出以下核心发现：

+ *品牌格局的城市差异*（双轨制市场）：
  - *京沪模式*（机构主导型）：*链家垄断*，北上均超75%，绝对主导地位；*贝壳优选补充*，北京17.0%、上海24.7%，作为链家旗下子品牌形成双品牌战略。另外，京沪市场几乎无"链家/个人"标签房源，反映*高度机构化*特征，可能是因为京沪对个人出租资质审核更严，租客偏好品牌中介（合同规范、维权便利）或链家深耕多年拥有垄断性数据优势
  - *广深杭模式*（个人活跃型）：*个人房源主导*，广杭深圳均超70%，个人房东或小中介通过链家平台发布；*链家品牌弱化*，广杭深均低于20%，纯链家代理房源占比较低；*贝壳优选边缘化*，占比几乎可忽略。这可能与市场开放度高（南方城市对个人房源管控宽松、城中村大量存在），成本驱动（房东倾向自行发布避免中介费）或租客群体差异（外来务工人员对品牌溢价敏感度低）有关
+ *链家的双面战略*：在机构化成熟市场抢占份额，在分散市场收割平台佣金
   - *直营为主*：在京沪采取直营模式，房源由链家经纪人独家代理，确保服务标准化
   - *平台为辅*：在广深杭提供平台服务，允许个人房东或小中介入驻，通过流量变现

#imagex(
  image(
    "../../output/analysis/brand_comparison.png",
    width: 83%,
  ),
  caption: [五城市租房中介品牌分析：房源分布vs市场占有率],
  label-name: "brand-comparison",
)

= 房源属性与空间价值挖掘

== 城市内部板块均价热度分析

=== 程序实现

本节通过 `src/analysis/block_comparison.py` 模块分析各城市内部不同板块的租金热度。`BlockComparator` 类对每个板块进行统计聚合，筛选活跃板块，并按单位租金排序取TOP15。核心代码如下：

```python
# 按板块分组聚合
block_stats = city_df.groupby('板块').agg({
    '单位租金': 'mean', '租金': ['mean', 'median'], '链接': 'count'})
# 筛选活跃板块（房源量 >= 最小阈值）
active_blocks = block_stats[block_stats['房源量'] >= min_listing_count]
# 排序取TOP15
top_expensive = active_blocks.sort_values('单价均价', ascending=False).head(15)
top_cheap = active_blocks.sort_values('单价均价', ascending=True).head(15)
```

可视化采用左右对比的水平条形图，左侧展示最贵TOP15板块（深红渐变），右侧展示最亲民TOP15板块（绿色渐变），直观呈现城市内部租金热度的极端差异。

=== 结果分析

以北京为例（@img:block-beijing），板块租金呈现显著的两极分化特征：

1. *板块租金极差惊人*最贵板块是最亲民板块的*11.3倍*（222.0 / 19.7），印证了"地段决定一切"的铁律

2. *最贵板块特征*：地处*历史文化核心*（地安门等老城区），靠近故宫、南锣鼓巷等地标，稀缺性极高；或位于*金融CBD*（金融街等金融商务区），高薪人群集中，支付能力强。

3. *最亲民板块特征*：*地理位置*均位于六环外或跨省交界（如古北口镇靠近河北），距市中心50+公里；*产业特征方面*，大兴机场空港、燕山等新兴产业区，配套尚未成熟，租金处于价值洼地

#imagex(
  image(
    "../../output/analysis/block_analysis_北京.png",
    width: 80%,
  ),
  caption: [北京板块租金深度分析：最贵vs最亲民],
  label-name: "block-beijing",
)

其他城市的板块租金情况如@img:fourcitybankuai 所示。

- *上海*：最贵板块集中在新天地#footnote[上海最贵板块刚好是新天地，与一个地域段子“上海人出了新天地呼吸都困难”不谋而合。]、淮海路、静安寺、人民广场等核心商圈；最亲民板块在崇明岛、金山等郊区。
- *广州*：珠江新城、金融城等CBD租金领先；花都、从化等外围区县租金亲民
- *深圳*：深圳湾、福田中心区、南山科技园等单价高企；坪山等新兴区域相对友好
- *杭州*：钱江新城、西湖周边租金高昂；余杭、萧山等郊区性价比突出

通过以上分析，可以给需要租房的用户以下几点意见：对于*高薪职场人*，核心板块租金虽高，但通勤时间短，节省时间成本；对于*预算有限者*，选择地铁沿线的次核心板块，可兼顾通勤和成本。

#imagex(
  subimagex(
    image("../../output/analysis/block_analysis_上海.png"),
    caption: [上海板块租金深度分析：最贵 vs 最亲民],
    label-name: "bankuai-sh",
  ),
  subimagex(
    image("../../output/analysis/block_analysis_广州.png"),
    caption: [广州板块租金深度分析：最贵 vs 最亲民],
    label-name: "bankuai-gz",
  ),
  subimagex(
    image("../../output/analysis/block_analysis_深圳.png"),
    caption: [深圳板块租金深度分析：最贵 vs 最亲民],
    label-name: "bankuai-sz",
  ),
  subimagex(
    image("../../output/analysis/block_analysis_杭州.png"),
    caption: [杭州板块租金深度分析：最贵 vs 最亲民],
    label-name: "bankuai-hz",
  ),
  columns: (1fr, 1fr),
  caption: [四座城市板块租金对比分析],
  label-name: "fourcitybankuai",
)

== 房屋朝向对租金的影响分析

=== 程序实现

本节通过 `src/analysis/orientation_comparison.py` 模块分析房屋朝向对租金的影响。核心难点是处理多朝向房源（如"南 北"），需拆分为多行统计。

```python
for _, row in df.iterrows(): # 拆分多朝向房源
    orientations = str(row['朝向']).split()  # 按空格分割
    for orient in orientations:
        if orient in MAJOR_ORIENTATIONS:  # 仅保留8大朝向
            new_row = row.copy(), new_row['朝向'] = orient
            expanded_rows.append(new_row)
df_expanded = pd.DataFrame(expanded_rows)
# 按城市×朝向二级分组统计
stats = df_expanded.groupby(['城市', '朝向']).agg({
    '单位租金': ['mean', 'max', 'min', 'median', 'count']})
```

可视化采用*分组柱状图 + 热力图*组合（@img:orientation-comparison），代码实现略。

=== 结果分析

五城市朝向租金对比结果如@img:orientation-comparison 所示，可以得出以下关键结论：

#imagex(
  image(
    "../../output/analysis/orientation_comparison.png",
    width: 95%,
  ),
  caption: [五城市租房朝向深度分析：单位租金vs房源分布],
  label-name: "orientation-comparison",
)

+ *朝向偏好的城市异质性*：朝向的分析结果与传统认知中“南向最贵”的差异较大，其中上海异常西北朝向最贵（111.1元/㎡），远超南向（84.4元/㎡）；北京偏好东向（91.0）领先南向（72.2），东北向（89.3）也高于南向；而深圳西向溢价（98.6）显著高于南向（81.7）。

+ *朝向偏好差异的原因分析*：由于朝向与传统认知差异较大，这里给出几点原因，仅作为个人猜测
  - *地理气候因素*：
    - *上海*：受东海季风影响，西北向可避开梅雨季主导风向，通风干燥；
    - *北京*：冬季西北风强劲，东向避风效果好；东向早晨采光充足，符合职场人作息
    - *广州*：地处珠江出海口，东向受珠江水系影响，靠近CBD商圈（珠江新城）推高租金
  - *供需关系*：
    - *南向房源占比*：热力图显示南向房源量占比高达60-70%（深蓝色），供给充足压低价格
    - *稀缺朝向溢价*：西北、东北等非主流朝向房源量少，稀缺性推高单价

3. *朝向与房源量的负相关*（供需悖论）：
   - *南向*：房源量最大，但单价并非最高，验证"供给过剩"假说
   - *西北/东北*：房源量最少，但单价反而较高，印证"物以稀为贵"

因此，对于朝向选择，可以采取以下策略：
  - *追求性价比*：选择南向（供给充足、价格亲民、采光好），适合大众租客
  - *平衡之选*：东南、西南等复合朝向，兼顾采光与通风，单价居中

= 经济关联与深度拓展研究

== 租房负担能力与收入关系分析

=== 程序实现

本节基于`SalaryRentAnalyzer`类，通过整合各城市租金数据#footnote[*租金使用中位数而非均值*，因为中位数不受极端高价豪宅影响，更能代表普通租客的真实负担]与公开统计年鉴#footnote[工资数据来源于2024年各城市发布的统计年鉴。]中的工资数据（非私营单位、私营单位、居民可支配收入三个口径），计算六类衍生指标#footnote[国际通行标准认为"租金占收入30%以内"为合理区间，超过则属于租金压力型家庭
]，以评估不同城市的租房负担与收入水平的关系。核心代码如下：

```python
# 步骤1：按城市分组计算租金统计
rent_stats = df_all.groupby('城市').agg({
    '单位租金': ['mean', 'median', 'std'],  # 元/㎡/月
    '租金': ['mean', 'median']              # 元/月
})
# 步骤2：合并工资数据
SALARY_DATA = {
    '北京': (224608, 106905, 92464),  # 后略
}
# 步骤3：计算6类衍生指标
# 指标A: 30% 私营月薪能租多少平米？（租房自由度）
merged['可租面积_私营30%'] = (
  merged['私营月薪'] * 0.3 / merged['单位租金中位数']).round(1)
# 剩余指标代码略
```

=== 结果分析

五城市工资-租金关系对比如@img:salary-rent 所示，可得如下核心发现：

#imagex(
  image(
    "../../output/analysis/salary_rent_comparison.png",
    width: 90%,
  ),
  caption: [五城市工资-租金关系对比],
  label-name: "salary-rent",
)

+ *深圳租房负担最重*：
   - *租金收入比高达63.0%*，即中位数房源需占用私营员工月薪的63%，远超国际警戒线（30%），这意味着深圳打工人每月收入的近2/3用于支付房租，基本无储蓄空间；且*30平米小单间需占月薪29.1%*，即使压缩居住空间到30平米（约一居室标准），仍需支付近三成月薪
   - *根本原因分析*：深圳房租相对于私营工资过高，高科技企业集中的南山、福田核心区推高了整体租金水平，但大量外来务工者的收入并未同步上涨

+ *杭州租房性价比最高*：
   - *租金收入比仅36.5%*，为五城市最低，租房压力相对可控，*30%月薪可租50.5平米*，约可覆盖两居室，租房自由度最高
   - *优势来源*：杭州工资水平中等，但租金相对较低，互联网大厂高薪岗位集中在少数人群，大量传统产业从业者可享受较低租金

+ *京沪租房压力次之*：
   - *租金收入比分别为56.1%和53.9%*，介于深圳与广杭之间，*30%月薪可租38.2平米（北京）和34.4平米（上海）*，基本够住但空间有限
   - *"高工资高房租"陷阱*：虽然京沪私营月薪全国最高，但单位租金也同样高，工资增长被房租涨幅抵消

+ *工资与租金的强相关性*：
   - *Pearson相关系数0.820*（见@img:salary-rent 左上子图），工资水平与单位租金呈强正相关，*房租跟着工资涨*：城市工资越高，房租也越高，但涨幅并非线性——深圳工资不及京沪但房租相当，导致租金收入比失衡

通过以上分析，可以得到政策启示如下，单纯提高最低工资无法改善租房负担，需配套增加保障性租赁住房供给。

== 互联网核心区的通勤半径与租金衰减

=== 程序实现

本节基于`DistanceDecayAnalyzer`类，通过计算每个房源到主要就业中心（CBD、互联网园区、产业园等#footnote[以北京为例，选取中关村、国贸、金融街、西二旗，其他城市类似。]）的距离，分析距离与租金之间的衰减关系。调用高德地图API计算驾车距离作为通勤成本的衡量，测试线性、多项式、对数、指数四类回归模型，并通过R²、MAE、RMSE、MAPE四个指标选择最优模型。核心代码如下：

```python
# 步骤1：计算最小距离（每个房源到所有就业中心的最短距离）
df['最小距离'] = df[就业中心距离列].min(axis=1)
# 步骤2：测试多种回归模型
models = ['linear', 'polynomial_2', ...]
for model_type in models:
    # 拟合模型，实现略
    # 步骤3：计算评估指标
    r_squared = model.score(X, y_true)              # R²（拟合优度）
    # 剩余指标略    
# 步骤4：按R²排序，选择最优模型
comparison_df = comparison_df.sort_values('R²', ascending=False)
```

=== 结果分析

以北京为例#footnote[由于篇幅限制，这里无法展示所有城市。]，五种回归模型对比结果如@tbl:distance-models 所示，租金随距离的衰减趋势如@img:distance-decay 所示，可得如下核心发现：

#tablex(
  // 数据区：按行平铺（7 列）
  [三次多项式],
  [$y = -0.00 x^3 + 0.11 x^2 - 6.02 x + 145.84$],
  [0.516], [18.7], [27.9], [26.1],

  [二次多项式],
  [$y = 0.06 x^2 - 5.05 x + 141.62$],
  [0.515], [18.8], [27.9], [26.4],

  [指数模型],
  [$y = 130.00 times e^{-0.0354 x}$],
  [0.497], [18.5], [28.5], [24.4],

  [对数模型],
  [$y = -36.35 times ln(x) + 174.08$],
  [0.488], [19.2], [28.7], [27.3],

  [线性模型],
  [$y = -2.52 x + 123.07$],
  [0.473], [20.2], [29.1], [29.5],

  // 表头 + 表头下横线（标准三线表关键）
  header: (
    [*模型*],
    [*方程*],
    [*R²*],
    [*MAE*],
    [*RMSE*],
    [*MAPE(%)*],
    table.hline(end: 6, stroke: 0.25pt),
  ),

  columns: 6,
  align: (left, left, center, center, center, center, center),
  caption: [北京租金-距离回归模型对比],
  label-name: "distance-models",
)

#imagex(
  image(
    "../../output/distance_analysis/bj_min_distance_regression.png",
    width: 70%,
  ),
  caption: [北京租金-距离衰减曲线（三次多项式拟合，R²=0.516）],
  label-name: "distance-decay",
)

+ *最优模型为三次多项式*：*R²=0.516*，解释了51.6%的租金变异，说明距离是租金的重要决定因素（但非唯一因素）；*MAPE=26.1%*，平均预测误差约为实际租金的26%，在城市复杂环境下属于可接受范围。三次多项式能更好地捕捉近郊快速衰减、远郊趋于平缓的非线性特征

+ *三圈层衰减规律*：*核心圈（0-10km）*快速陡降，*过渡圈（10-30km）*持续衰减，*远郊圈（30km+）*平缓稳定。符合城市经济学中的"通勤成本模型"，租金随通勤距离呈指数衰减
+ *跨城市对比*：*五城市均呈现相似衰减规律*，但存在*城市形态差异*，通过对城市租金热力图（@img:fivecity-heatmap）可以进一步观察城市的中心化特征，其中北京上海呈现明显的中心化特征，而深圳，广州等分布较为离散

#imagex(
  subimagex(
    image("../../output/maps/bj_rental_heatmap.png"),
    caption: [北京热力图],
    label-name: "heatmap-bj",
  ),
  subimagex(
    image("../../output/maps/sh_rental_heatmap.png"),
    caption: [上海热力图],
    label-name: "heatmap-sh",
  ),
  subimagex(
    image("../../output/maps/gz_rental_heatmap.png"),
    caption: [广州热力图],
    label-name: "heatmap-gz",
  ),
  subimagex(
    image("../../output/maps/sz_rental_heatmap.png"),
    caption: [深圳热力图],
    label-name: "heatmap-sz",
  ),
  subimagex(
    image("../../output/maps/hz_rental_heatmap.png"),
    caption: [杭州热力图],
    label-name: "heatmap-hz",
  ),

  columns: (1fr, 1fr, 1fr, 1fr, 1fr),
  gutter: 0.6em,
  caption: [北上广深杭租金空间分布热力图],
  label-name: "fivecity-heatmap",
)

== 周边配套设施对租金的影响研究

=== 程序实现

本节基于`AmenityAnalyzer`类，通过之前爬取到的房源周边1km半径内的星巴克、麦当劳数量，分析配套密度对租金的影响。核心实现包括：

+ *统计假设检验*：t检验#footnote[样本量足够大，即使数据不完全正态分布，t检验仍然稳健。]判断有无配套的租金差异显著性
+ *相关性分析*：Pearson/Spearman相关系数量化配套数量与租金的关系
+ *配套密度分级*：按总配套数量分为"无/低/中/高"四档，对比租金差异

=== 结果分析

以北京为例#footnote[其余城市由于篇幅限制无法展示。]，星巴克与麦当劳的统计假设检验结果如@tbl:amenity-ttest 所示，相关性分析结果如@tbl:amenity-correlation 所示，配套设施分布与租金热力图如@img:amenity-heatmap 所示，基于以上数据与图表，可得如下核心发现：

#tablex(
  // 数据区（8 列）
  [星巴克], [16900], [89.1], [9611], [58.0], [+31.1], [+53.5], [$< 0.001$],
  [麦当劳], [21435], [81.4], [5076], [62.8], [+18.6], [+29.7], [$< 0.001$],

  // 表头 + 表头下横线（三线表）
  header: (
    [*配套类型*],
    [*有配套#linebreak()样本量*],
    [*有配套#linebreak()均值*],
    [*无配套#linebreak()样本量*],
    [*无配套#linebreak()均值*],
    [*绝对溢价*],
    [*相对溢价(%)*],
    table.hline(end: 8, stroke: 0.25pt),
    [*p值*],
  ),

  columns: 8,
  align: (left, center, center, center, center, center, center, center),

  caption: [北京星巴克/麦当劳溢价效应 t 检验结果（p 值 < 0.001 表示极显著）],
  label-name: "amenity-ttest",
)

#tablex(
  // 数据区（6 列）
  [星巴克数量], [0.435], [$< 0.001$], [0.537], [$< 0.001$], [26511],
  [麦当劳数量], [0.343], [$< 0.001$], [0.360], [$< 0.001$], [26511],
  [配套总数],   [0.451], [$< 0.001$], [0.513], [$< 0.001$], [26511],

  // 表头 + 表头下横线（三线表）
  header: (
    [*配套类型*],
    [*Pearson r*],
    [*Pearson p*],
    [*Spearman ρ*],
    [*Spearman p*],
    table.hline(end: 6, stroke: 0.25pt),
    [*样本量*],
  ),

  columns: 6,
  align: (left, center, center, center, center, center),

  caption: [*北京配套设施与租金的相关性分析*（r/ρ：相关系数，p：显著性水平）],
  label-name: "amenity-correlation",
)

#imagex(
  image(
    "../../output/amenity_analysis/bj_heatmap.png",
    width: 70%,
  ),
  caption: [北京配套设施密度与租金热力图],
  label-name: "amenity-heatmap",
)


+ *星巴克溢价效应显著*，*统计极显著*：从经济学角度解释，星巴克选址严格筛选高消费力区域（商圈、写字楼、高端社区），其存在本身就是区域成熟度的信号
+ *麦当劳溢价次之但仍显著*：溢价低于星巴克的原因可能为麦当劳覆盖更广（包括部分中低端区域），对消费力的筛选效应弱于星巴克
+ *配套密度呈阶梯式溢价*：*无配套*作为基准组，*低配套*（1-2家）+20.4%，*中配套*（3-5家）+38.3%，*高配套*（≥6家）+94.4%，说明"高配套区"形成临界质变
+ *跨城市对比*：*五城市均呈现相似规律*，均在40-50%区间。*深圳溢价略低*，可能与城中村大量存在有关，城中村租金极低但完全无配套，拉低了整体对比度

= 总结与展望

本项目以北京、上海、广州、深圳、杭州五个重点城市的租房市场为研究对象，从租金水平、户型结构、品牌分布、板块差异、朝向溢价、工资收入比、通勤距离衰减、配套设施影响等八个维度展开，构建了一套从数据采集、清洗、分析到可视化的完整工作流程。通过对11.4万余条真实房源数据的多维度分析，我对国内一线及新一线城市的租赁市场特征有了更深入的认识，同时在Python编程、数据分析和工程实践方面也收获颇丰。

*心得体会方面*，本项目是我第一次完整实践"数据采集-清洗-分析-可视化"的全流程工作。在爬虫开发过程中，链家反爬机制的IceManSDK拦截曾让我一度陷入困境，最初尝试逆向该SDK但发现其核心逻辑在后端、难以伪造，最终采用"策略切换+低频爬取"的方案绕过拦截。数据清洗环节让我体会到"垃圾进、垃圾出"的道理，数据质量直接决定分析结论的可信度。数据分析以及可视化部分，通过 pandas、matplotlib 等强大包，绘制分组柱状图、热力图、箱线图等图表类型，选择合适的图表能让数据"说话"。

项目也存在一些*局限性*。虽然爬取的数据覆盖度比较全面，对城市的各个区域和不同类型的房源都进行了采样爬取，但存在时间维度缺失，本项目仅采集了2025年12月的横截面数据，无法分析租金的季节性波动、长期趋势、等时间序列特征，这在一定程度上限制了分析的深度。后续将针对该问题进行进一步优化。

总的来说，本项目让我从一个Python初学者成长为能够独立完成数据分析全流程的实践者，不仅锻炼了编程能力，同时对真实数据的解读和分析也增强了全过程实践的趣味性。

#show: appendix

= 项目结构说明

由于篇幅限制，报告中并未展现完整的图表和代码内容，可查看一并提交的项目文件（结构说明如下）或我制作的网页(https://yokumii.github.io/Lianjia-Housing-Analysis/)#footnote[*遵循学术诚信*，代码和数据集不会公开，仅部署静态网页方便查看和评阅。]。


```
.
├── pyproject.toml                    # 项目依赖配置(uv管理)
├── uv.lock                           # 依赖锁定文件
├── settings.py                       # 全局配置文件
├── README.md                         # 项目说明文文件
├── src/                              # 源代码目录
│   ├── cli.py                        # 命令行入口
│   ├── spider/                       # 爬虫模块
│   │   ├── core/                     # 核心功能
│   │   │   ├── orchestrator.py      # 爬取调度器
│   │   │   ├── parser.py             # HTML解析器
│   │   │   ├── url_generator.py     # URL生成器
│   │   │   ├── state.py              # 状态管理器
│   │   │   └── strategies/           # 爬取策略
│   │   │       ├── abstract.py       # 抽象基类
│   │   │       ├── http_strategy.py  # HTTP请求策略
│   │   │       └── drission_strategy.py  # DrissionPage策略
│   │   ├── items/                    # 数据模型
│   │   │   └── models.py             # RentHouseItem定义
│   │   ├── storage/                  # 存储模块
│   │   │   └── csv_writer.py         # CSV写入器
│   │   └── config/                   # 配置文件
│   │       └── constants.py          # 常量定义
│   ├── preprocess/                   # 数据预处理模块
│   │   ├── data_cleaner.py           # 数据清洗(异常值/缺失值)
│   │   ├── coordinates.py            # 坐标转换(高德API)
│   │   └── constants.py              # 预处理常量
│   ├── analysis/                     # 数据分析模块
│   │   ├── city_comparison.py        # 城市对比分析
│   │   ├── layout_analysis.py        # 户型分析
│   │   ├── block_comparison.py       # 板块分析
│   │   ├── orientation_visualizer.py # 朝向分析
│   │   ├── brand_visualizer.py       # 品牌分析
│   │   ├── salary_rent_comparison.py # 工资租金比分析
│   │   ├── distance_decay.py         # 距离衰减分析
│   │   ├── amenity_analyzer.py       # 配套设施分析
│   │   └── map_visualizer.py         # 地图可视化
│   └── crawler/                      # 外部数据爬取
│       └── amenity_crawler.py        # POI采集
├── data/                             # 数据文件目录
│   ├── xxx_rental.csv                # 原始爬取数据(bj/sh/gz/sz/hz)
│   ├── xxx_rental_clean.csv          # 清洗后数据
│   ├── xxx_rental_with_coordinate.csv  # 带坐标数据
│   ├── xxx_rental_with_distances.csv # 带通勤距离数据
│   └── xxx_rental_with_amenities.csv # 带配套设施数据
├── output/                           # 分析结果输出
│   ├── analysis/                     # 统计分析结果
│   │   ├── city_statistics.csv       # 城市对比统计
│   │   ├── layout_statistics.csv     # 户型统计
│   │   ├── layout_pivot.csv          # 户型交叉表
│   │   ├── block_stats_xxx.csv       # 各城市板块统计
│   │   ├── orientation_statistics.csv  # 朝向统计
│   │   ├── orientation_pivot.csv     # 朝向交叉表
│   │   ├── brand_statistics.csv      # 品牌统计
│   │   ├── brand_pivot.csv           # 品牌交叉表
│   │   └── salary_rent_statistics.csv  # 工资租金比统计
│   ├── maps/                         # 地图可视化结果
│   │   └── xxx_rental_heatmap.html   # 各城市热力图
│   ├── distance_analysis/            # 通勤距离分析结果
│   │   ├── xxx_distance_stats.csv     # 距离分组统计
│   │   └── xxx_model_comparison.csv   # 回归模型对比
│   └── amenity_analysis/             # 配套设施分析结果
│       ├── xxx_density_stats.csv      # 配套密度统计
│       └── xxx_amenity_report.md      # 配套分析报告
└── scripts/                          # 快捷执行脚本，略
```

// 请根据文档类型，自行选择 if-else 中的内容

#if doctype != "report" [
  #if doctype == "bachelor" [
    #achievement(
      papers: (
        "Chen H, Chan C T. Acoustic cloaking in three dimensions using acoustic metamaterials[J]. Applied Physics Letters, 2007, 91:183518.",
        "Chen H, Wu B I, Zhang B, et al. Electromagnetic Wave Interactions with a Metamaterial Cloak[J]. Physical Review Letters, 2007, 99(6):63903.",
      ),
      patents: ("第一发明人, 永动机[P], 专利申请号202510149890.0.",),
    )

    #acknowledgement[
      致谢主要感谢导师和对论文工作有直接贡献和帮助的人士和单位。致谢言语应谦虚诚恳，实事求是。
    ]

    #summary-en[
      HCCI (Homogenous Charge Compression Ignition)combustion has advantages in terms of efficiency and reduced emission. HCCI combustion can not only ensure both the high economic and dynamic quality of the engine, but also efficiently reduce the NOx and smoke emission. Moreover, one of the remarkable characteristics of HCCI combustion is that the ignition and combustion process are controlled by the chemical kinetics, so the HCCI ignition time can vary significantly with the changes of engine configuration parameters and operating conditions......
    ]
  ] else [
    #acknowledgement[
      致谢主要感谢导师和对论文工作有直接贡献和帮助的人士和单位。致谢言语应谦虚诚恳，实事求是。
    ]

    #achievement(
      papers: (
        "Chen H, Chan C T. Acoustic cloaking in three dimensions using acoustic metamaterials[J]. Applied Physics Letters, 2007, 91:183518.",
        "Chen H, Wu B I, Zhang B, et al. Electromagnetic Wave Interactions with a Metamaterial Cloak[J]. Physical Review Letters, 2007, 99(6):63903.",
      ),
      patents: ("第一发明人, 永动机[P], 专利申请号202510149890.0.",),
    )
  ]
]

