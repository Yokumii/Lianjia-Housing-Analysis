from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class CrawlStrategy(ABC):
    """
    爬取策略的抽象基类
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化策略

        Args:
            config: 策略配置，例如：
                {
                    'timeout': 30,
                    'headers': {...},
                    'cookies': {...},
                    'proxy': '...',
                    ...
                }
        """
        self.config = config

    @abstractmethod
    def fetch_page(self, url: str, **kwargs) -> str:
        """
        获取页面 HTML

        Args:
            url: 目标 URL
            **kwargs: 额外参数（如 headers, cookies 等）

        Returns:
            str: 页面 HTML 原始文本

        Raises:
            Exception: 网络错误或页面获取失败
        """
        pass

    @abstractmethod
    def close(self):
        """清理资源（关闭连接、浏览器进程等）"""
        pass

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动清理"""
        self.close()
