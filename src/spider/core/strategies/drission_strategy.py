import time
from typing import Dict, Any, Optional
from .abstract import CrawlStrategy


class DrissionPageStrategy(CrawlStrategy):
    """基于 DrissionPage 库的浏览器自动化爬取策略"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 DrissionPage 策略

        Args:
            config: 配置参数，支持：
                {
                    'headless': True,       # 无头模式
                    'timeout': 30,          # 页面加载超时（秒）
                    'wait_after_load': 1,   # 页面加载后等待时间（秒）
                    'user_agent': '...',    # 自定义 User-Agent
                    'proxy': '...',         # 代理 URL
                    'disable_images': False,# 禁用图片加载（提速）
                    'window_size': (1920, 1080),  # 浏览器窗口大小
                }
        """
        super().__init__(config)

        # 初始化实例变量（防止 __del__ 出错）
        self.page: Optional['ChromiumPage'] = None
        self.options = None
        self._initialized = False

        # 延迟导入（避免没有安装 DrissionPage 时报错）
        try:
            from DrissionPage import ChromiumPage, ChromiumOptions
        except ImportError:
            raise ImportError(
                "请先安装 DrissionPage: uv sync --extra drission\n"
                "或手动安装: pip install drissionpage>=4.0.0"
            )

        # 提取配置
        self.headless = config.get('headless', True)
        self.timeout = config.get('timeout', 30)
        self.wait_after_load = config.get('wait_after_load', 1)
        self.disable_images = config.get('disable_images', False)
        self.window_size = config.get('window_size', (1920, 1080))

        # 创建浏览器选项
        options = ChromiumOptions()

        # 无头模式
        if self.headless:
            options.headless(True)

        # 窗口大小
        if self.window_size:
            width, height = self.window_size
            options.set_argument(f'--window-size={width},{height}')

        # 自定义 User-Agent
        if config.get('user_agent'):
            options.set_user_agent(config['user_agent'])

        # 代理设置
        if config.get('proxy'):
            options.set_proxy(config['proxy'])

        # 禁用图片加载（提速）
        if self.disable_images:
            options.set_pref('profile.managed_default_content_settings.images', 2)

        # 其他性能优化设置
        options.set_argument('--disable-gpu')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-blink-features=AutomationControlled')

        # 保存配置
        self.options = options

    def _ensure_initialized(self):
        """确保浏览器已初始化"""
        if not self._initialized:
            from DrissionPage import ChromiumPage
            self.page = ChromiumPage(addr_or_opts=self.options)
            self.page.set.timeouts(base=self.timeout)
            self._initialized = True

    def fetch_page(self, url: str, **kwargs) -> str:
        """
        获取页面 HTML

        Args:
            url: 目标 URL
            **kwargs: 额外参数：
                - wait_after_load: 覆盖默认等待时间
                - wait_selector: 等待特定元素出现（CSS 选择器）
                - execute_script: 执行 JavaScript 代码

        Returns:
            str: 页面 HTML 内容

        Raises:
            Exception: 页面加载失败或超时
        """
        self._ensure_initialized()

        try:
            # 访问页面
            self.page.get(url)

            # 等待特定元素（如果指定）
            if kwargs.get('wait_selector'):
                selector = kwargs['wait_selector']
                self.page.wait.ele_displayed(selector, timeout=self.timeout)

            # 执行自定义 JavaScript（如果指定）
            if kwargs.get('execute_script'):
                script = kwargs['execute_script']
                self.page.run_js(script)

            # 等待页面稳定
            wait_time = kwargs.get('wait_after_load', self.wait_after_load)
            if wait_time > 0:
                time.sleep(wait_time)

            # 返回页面 HTML
            return self.page.html

        except Exception as e:
            raise Exception(f"DrissionPage 获取页面失败: {url}, 错误: {e}")

    def close(self):
        """关闭浏览器并清理资源"""
        if self.page:
            try:
                self.page.quit()
            except Exception:
                pass  # 忽略关闭时的错误
            finally:
                self.page = None
                self._initialized = False

    def __repr__(self) -> str:
        return (
            f"DrissionPageStrategy("
            f"headless={self.headless}, "
            f"timeout={self.timeout}s"
            f")"
        )

    def __del__(self):
        """析构函数：确保浏览器被关闭"""
        self.close()
