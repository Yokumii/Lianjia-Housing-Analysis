import time
import math
from typing import Dict, List, Any, Optional, Tuple
from ..items.models import PropertyType
from .parser import Parser
from .state import StateManager
from .strategies.abstract import CrawlStrategy
from .strategies.http_strategy import HttpStrategy
from .url_generator import UrlGenerator
from ..storage.csv_writer import CsvWriter
from ..config.constants import CityConfig, Selectors, HttpConfig, Paths


class SpiderOrchestrator:
    """爬虫协调器"""

    def __init__(
        self,
        city: str,
        property_type: str,
        strategy: CrawlStrategy,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化爬虫协调器

        Args:
            city: 城市代码（bj, sh, sz, gz, hz）
            property_type: 房产类型（rental, secondhand）
            strategy: 爬取策略实例
            config: 额外配置
        """
        # 验证城市
        if not CityConfig.validate_city(city):
            raise ValueError(f"不支持的城市: {city}，支持的城市: {list(CityConfig.CITIES.keys())}")

        self.city = city
        self.property_type = property_type
        self.strategy = strategy
        self.config = config or {}

        # 初始化 Parser
        selectors = Selectors.get_selectors(property_type)
        self.parser = Parser(PropertyType(property_type), selectors)

        # 初始化文件路径
        self.csv_path = Paths.get_csv_path(city, property_type)
        self.progress_file = Paths.get_progress_file(city, property_type)

        # 初始化存储和状态管理
        self.writer = CsvWriter(self.csv_path, dedup_key='house_id')
        self.state_manager = StateManager(self.progress_file)

        # 爬取统计
        self.stats = {
            'total_pages': 0,
            'total_items': 0,
            'total_written': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None,
        }

    def crawl(
        self,
        delay: float = 1.0,
        resume: bool = True,
    ) -> Dict[str, Any]:
        """
        执行爬虫任务

        Args:
            delay: 每次请求间隔（秒）
            resume: 是否从进度文件恢复

        Returns:
            Dict: 爬取统计信息
        """
        self.stats['start_time'] = time.time()

        # 生成所有城市/城区的任务键
        task_keys = UrlGenerator.get_all_task_keys([self.city])
        self.state_manager.init_tasks(task_keys, self.csv_path)

        # 获取待处理的任务
        pending_tasks = self.state_manager.get_pending_tasks()

        print(f"\n{'='*60}")
        print(f"开始爬取 {CityConfig.get_city_name(self.city)} {self.property_type}")
        print(f"城区总数: {len(task_keys)}")
        print(f"待处理城区: {len(pending_tasks)}")
        print(f"CSV 文件: {self.csv_path}")
        print(f"{'='*60}\n")

        # 遍历待处理的任务（city|district, page_num）
        for task_idx, (task_key, page_num) in enumerate(pending_tasks, 1):
            # 解析任务键
            parts = task_key.split('|')
            if len(parts) != 2:
                print(f"❌ 无效的任务键格式: {task_key}")
                continue

            city_code, district = parts

            try:
                # === 核心逻辑 1：构建 URL ===
                url = UrlGenerator.build_url(city_code, district, page_num, self.property_type)
                print(f"[{task_idx}/{len(pending_tasks)}] {task_key} - 正在爬取页面 {page_num}: {url}")

                # === 核心逻辑 2：获取页面 ===
                html = self.strategy.fetch_page(url)

                # === 核心逻辑 3：提取最大页码 ===
                max_page = self.parser.get_max_page(html)

                # === 核心逻辑 4：检查页码是否超出 ===
                if page_num > max_page:
                    print(f"  📌 页码 {page_num} 超出最大页码 {max_page}，任务完成 (-1)")
                    self.state_manager.mark_done(task_key)
                    continue

                # === 核心逻辑 5：解析数据 ===
                city_name = CityConfig.get_city_name(city_code)
                items = self.parser.parse(html, city_name, district=district, city_code=city_code)

                # 检查是否无数据
                if len(items) == 0:
                    print(f"  📭 无数据，任务完成 (-1)")
                    self.state_manager.mark_done(task_key)
                    continue

                # === 核心逻辑 6：存储数据 ===
                written = self.writer.append(items, verbose=False)
                self.stats['total_items'] += len(items)
                self.stats['total_written'] += written

                print(f"  ✓ 解析 {len(items)} 条，写入 {written} 条 | 最大页码: {max_page}")

                # === 核心逻辑 7：决定下一步 ===
                if page_num >= max_page:
                    # 已是最后一页，任务完成
                    print(f"  ✓ 已完成所有页面 (最大页码: {max_page})")
                    self.state_manager.mark_done(task_key)
                else:
                    # 还有下一页，更新页码继续爬取
                    next_page = page_num + 1
                    self.state_manager.update_page(task_key, next_page)
                    print(f"  → 继续爬取下一页 ({next_page}/{max_page})")

                self.stats['total_pages'] += 1

            except Exception as e:
                print(f"  ✗ 错误: {e}")
                self.stats['errors'] += 1

            # 等待（避免被反爬）
            if task_idx < len(pending_tasks):
                time.sleep(delay)

        # 完成统计
        self.stats['end_time'] = time.time()
        elapsed = self.stats['end_time'] - self.stats['start_time']

        # 打印完成统计
        progress = self.state_manager.get_progress()
        print(f"\n{'='*60}")
        print(f"爬取统计")
        print(f"已完成城区: {progress['completed']}/{progress['total']}")
        print(f"待处理城区: {progress['pending']}")
        print(f"总爬取页数: {self.stats['total_pages']}")
        print(f"总房源: {self.stats['total_items']}")
        print(f"写入 CSV: {self.stats['total_written']}")
        print(f"错误数: {self.stats['errors']}")
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"{'='*60}\n")

        # 如果所有任务完成，清理进度文件
        if self.state_manager.is_complete():
            self.state_manager.cleanup()

        return self.stats

    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        return self.state_manager.get_progress()

    def close(self):
        """关闭资源"""
        if self.strategy:
            self.strategy.close()

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动清理"""
        self.close()


class UnifiedSpider:
    """统一爬虫"""

    @staticmethod
    def create_http_spider(
        city: str,
        property_type: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> SpiderOrchestrator:
        """
        创建 HTTP 爬虫

        Args:
            city: 城市代码
            property_type: 房产类型（rental, secondhand）
            headers: 自定义 headers（可选，默认使用 settings.py 中的配置）

        Returns:
            SpiderOrchestrator: 爬虫实例

        Raises:
            ValueError: 如果 settings.py 中的 Cookie 为空
        """
        # 检查 Cookie 是否已填入
        if not HttpConfig.validate_cookie():
            raise ValueError(
                "❌ Cookie 未填入！\n"
                "请编辑 settings.py，在 Cookie = \"\" 处填入你的 Cookie\n"
                "步骤：\n"
                "  1. 打开浏览器，访问 https://bj.lianjia.com\n"
                "  2. F12 打开开发者工具 → Network → 找任意请求\n"
                "  3. 点击请求 → Headers → 复制 Cookie 值\n"
                "  4. 粘贴到 settings.py 的 Cookie = \"\" 中"
            )

        # 使用 settings.py 中的配置
        config = HttpConfig.get_config()

        # 如果提供了自定义 headers，合并到配置中
        if headers:
            config['headers'].update(headers)

        strategy = HttpStrategy(config)
        return SpiderOrchestrator(city, property_type, strategy)

    @staticmethod
    def create_selenium_spider(
        city: str,
        property_type: str,
        headless: bool = True,
    ) -> SpiderOrchestrator:
        """
        创建 Selenium 爬虫（后续实现）

        Args:
            city: 城市代码
            property_type: 房产类型
            headless: 是否无头模式

        Returns:
            SpiderOrchestrator: 爬虫实例
        """
        raise NotImplementedError("Selenium 爬虫将在后续版本实现")

    @staticmethod
    def create_drission_spider(
        city: str,
        property_type: str,
        headless: bool = True,
    ) -> SpiderOrchestrator:
        """
        创建 DrissionPage 爬虫

        Args:
            city: 城市代码
            property_type: 房产类型
            headless: 是否无头模式（默认 True）

        Returns:
            SpiderOrchestrator: 爬虫实例
        """
        from .strategies.drission_strategy import DrissionPageStrategy

        # DrissionPage 配置
        config = {
            'headless': headless,
            'timeout': 30,
            'wait_after_load': 1.5,  # 页面加载后等待 1.5 秒
            'disable_images': False,  # 不禁用图片（某些页面可能依赖图片加载完成）
            'window_size': (1920, 1080),
        }

        strategy = DrissionPageStrategy(config)
        return SpiderOrchestrator(city, property_type, strategy)
