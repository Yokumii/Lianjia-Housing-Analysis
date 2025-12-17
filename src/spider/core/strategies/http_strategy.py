import requests
from typing import Dict, Any, Optional
from .abstract import CrawlStrategy


class HttpStrategy(CrawlStrategy):
    """基于 requests 库的 HTTP 爬取策略"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 HTTP 策略

        Args:
            config: 配置参数，支持：
                {
                    'timeout': 30,          # 请求超时（秒）
                    'retries': 3,           # 重试次数
                    'headers': {...},       # 自定义 headers
                    'cookies': {...},       # Cookie
                    'proxy': '...',         # 代理 URL
                    'verify_ssl': True,     # 是否验证 SSL
                }
        """
        super().__init__(config)

        # 提取配置
        self.timeout = config.get('timeout', 30)
        self.retries = config.get('retries', 3)
        self.verify_ssl = config.get('verify_ssl', True)

        # 创建 session
        self.session = requests.Session()

        # 配置默认 headers（模拟浏览器）
        default_headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,image/apng,*/*;q=0.8'
            ),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # 合并用户提供的 headers
        if config.get('headers'):
            default_headers.update(config['headers'])
        self.session.headers.update(default_headers)

        # 设置 Cookie
        if config.get('cookies'):
            self.session.cookies.update(config['cookies'])

        # 设置代理
        if config.get('proxy'):
            proxies = {
                'http': config['proxy'],
                'https': config['proxy'],
            }
            self.session.proxies.update(proxies)

    def fetch_page(self, url: str, **kwargs) -> str:
        """
        获取页面 HTML

        Args:
            url: 目标 URL
            **kwargs: 额外参数（如 headers, cookies 等）

        Returns:
            str: 页面 HTML 内容

        Raises:
            requests.RequestException: 网络请求失败
        """
        # 合并额外的 headers
        headers = dict(self.session.headers)
        if kwargs.get('headers'):
            headers.update(kwargs['headers'])

        # 合并额外的 cookies
        cookies = dict(self.session.cookies)
        if kwargs.get('cookies'):
            cookies.update(kwargs['cookies'])

        # 重试逻辑
        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    allow_redirects=True,
                )
                response.raise_for_status()
                return response.text

            except requests.Timeout:
                last_error = f"请求超时（{self.timeout}s）"
            except requests.ConnectionError as e:
                last_error = f"连接错误: {e}"
            except requests.HTTPError as e:
                # HTTP 错误（如 403, 404）- 不重试
                raise e
            except Exception as e:
                last_error = str(e)

            # 如果不是最后一次尝试，继续重试
            if attempt < self.retries - 1:
                print(f"[重试] {attempt + 1}/{self.retries} 失败: {last_error}, URL: {url}")

        # 所有重试都失败
        raise requests.RequestException(
            f"在 {self.retries} 次尝试后仍无法获取: {last_error}"
        )

    def close(self):
        """关闭 session"""
        if self.session:
            self.session.close()

    def __repr__(self) -> str:
        return f"HttpStrategy(timeout={self.timeout}, retries={self.retries})"
