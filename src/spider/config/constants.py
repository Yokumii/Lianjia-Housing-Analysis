import os
import sys
from typing import Dict, Any

# ============ 导入用户配置 ============

def _load_user_settings():
    """从 settings.py 加载用户配置"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    settings_file = os.path.join(project_root, 'settings.py')

    if not os.path.exists(settings_file):
        raise ImportError(
            f"❌ 找不到配置文件: {settings_file}\n"
            "请在项目根目录创建 settings.py 文件\n"
            "参考：src/spider/config/settings.example.py"
        )

    # 动态导入 settings
    import importlib.util
    spec = importlib.util.spec_from_file_location("settings", settings_file)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    return settings, project_root

try:
    _user_settings, _project_root = _load_user_settings()
except Exception as e:
    raise ImportError(f"加载配置文件失败: {e}")


# ============ 城市配置 ============

class CityConfig:
    """城市配置信息（从 settings.py 读取）"""

    CITIES = _user_settings.CITIES

    @classmethod
    def validate_city(cls, city: str) -> bool:
        """验证城市代码是否有效"""
        return city in cls.CITIES

    @classmethod
    def get_city_name(cls, city: str) -> str:
        """获取城市中文名称"""
        return cls.CITIES.get(city, {}).get('name', city)

    @classmethod
    def get_url(cls, city: str, property_type: str) -> str:
        """获取城市对应房产类型的 URL"""
        city_config = cls.CITIES.get(city, {})
        if property_type == 'rental':
            return city_config.get('rental_url', '')
        elif property_type == 'secondhand':
            return city_config.get('secondhand_url', '')
        else:
            raise ValueError(f"不支持的房产类型: {property_type}")


# ============ XPath 选择器 ============

class Selectors:
    """页面 XPath 选择器（从 settings.py 读取）"""

    RENTAL_SELECTORS = _user_settings.RENTAL_SELECTORS
    SECONDHAND_SELECTORS = _user_settings.SECONDHAND_SELECTORS

    @classmethod
    def get_selectors(cls, property_type: str) -> Dict[str, str]:
        """获取对应房产类型的选择器"""
        if property_type == 'rental':
            return cls.RENTAL_SELECTORS.copy()
        elif property_type == 'secondhand':
            return cls.SECONDHAND_SELECTORS.copy()
        else:
            raise ValueError(f"不支持的房产类型: {property_type}")


# ============ HTTP 配置 ============

class HttpConfig:
    """HTTP 请求配置（从 settings.py 读取）"""

    # 用户填入的 Cookie 字符串
    COOKIE_STRING = _user_settings.Cookie.strip()

    # User-Agent
    USER_AGENT = _user_settings.USER_AGENT

    # 下载延迟
    DOWNLOAD_DELAY = _user_settings.DOWNLOAD_DELAY

    # 最大重试次数
    MAX_RETRIES = _user_settings.MAX_RETRIES

    # 代理
    PROXY = _user_settings.PROXY

    @staticmethod
    def validate_cookie() -> bool:
        """验证 Cookie 是否已填入"""
        return bool(HttpConfig.COOKIE_STRING)

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """获取请求 headers"""
        headers = {
            'User-Agent': HttpConfig.USER_AGENT,
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

        # 添加 Cookie
        if HttpConfig.COOKIE_STRING:
            headers['Cookie'] = HttpConfig.COOKIE_STRING

        return headers

    @staticmethod
    def get_config() -> Dict[str, Any]:
        """获取请求配置"""
        return {
            'timeout': 30,
            'retries': HttpConfig.MAX_RETRIES,
            'verify_ssl': True,
            'headers': HttpConfig.get_headers(),
            'proxy': HttpConfig.PROXY,
        }


# ============ 文件路径 ============

class Paths:
    """文件路径常量"""

    # 项目根目录
    PROJECT_ROOT = _project_root

    # 数据目录
    DATA_DIR = os.path.join(PROJECT_ROOT, _user_settings.DATA_DIR)

    @classmethod
    def ensure_data_dir(cls):
        """确保数据目录存在"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)

    @classmethod
    def get_csv_path(cls, city: str, property_type: str) -> str:
        """获取 CSV 文件路径"""
        cls.ensure_data_dir()
        city_name = CityConfig.get_city_name(city)
        if property_type == 'rental':
            filename = f"{city_name}_租房数据.csv"
        elif property_type == 'secondhand':
            filename = f"{city_name}_二手房数据.csv"
        else:
            filename = f"{city_name}_房产数据.csv"
        return os.path.join(cls.DATA_DIR, filename)

    @classmethod
    def get_progress_file(cls, city: str, property_type: str) -> str:
        """获取进度文件路径"""
        cls.ensure_data_dir()
        filename = f"{city}_{property_type}{_user_settings.PROGRESS_FILE_SUFFIX}"
        return os.path.join(cls.DATA_DIR, filename)
