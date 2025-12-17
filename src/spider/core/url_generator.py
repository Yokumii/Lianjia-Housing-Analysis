from typing import Dict, List


class UrlGenerator:
    """自动生成链家 URL"""

    # 城区配置
    DISTRICTS = {
        'bj': [
            'dongcheng', 'xicheng', 'chaoyang', 'haidian', 'fengtai', 'shijingshan',
            'tongzhou', 'changping', 'daxing', 'shunyi', 'fangshan', 'mentougou',
            'pinggu', 'huairou', 'miyun', 'yanqing'
        ],
        'sh': [
            'pudong', 'minhang', 'baoshan', 'xuhui', 'putuo', 'yangpu', 'changning',
            'songjiang', 'jiading', 'huangpu', 'jingan', 'hongkou', 'qingpu',
            'fengxian', 'jinshan', 'chongming'
        ],
        'gz': [
            'tianhe', 'yuexiu', 'liwan', 'haizhu', 'panyu', 'baiyun', 'huangpu',
            'conghua', 'zengcheng', 'huadu', 'nansha', 'nanhai', 'shunde'
        ],
        'sz': [
            'luohuqu', 'futianqu', 'nanshanqu', 'yantianqu', 'baoanqu', 'longgangqu',
            'longhuaqu', 'guangmingqu', 'pingshanqu', 'dapengxinqu'
        ],
        'hz': [
            'xihu', 'qiantang', 'linping', 'gongshu', 'shangcheng', 'binjiang',
            'yuhang', 'xiaoshan', 'tonglu', 'chunan', 'jiande', 'fuyang', 'linan'
        ]
    }

    # 房产类型到 URL 路径的映射
    PROPERTY_TYPE_PATH = {
        'rental': 'zufang',
        'secondhand': 'ershoufang',
        'new_house': 'loupan',
    }

    @staticmethod
    def get_task_keys(city: str) -> List[str]:
        """
        获取城市的所有任务键（city|district 格式）

        Args:
            city: 城市代码（bj, sh, sz, gz, hz）

        Returns:
            List[str]: 任务键列表，格式为 ['bj|dongcheng', 'bj|xicheng', ...]
        """
        districts = UrlGenerator.DISTRICTS.get(city, [])
        return [f"{city}|{district}" for district in districts]

    @staticmethod
    def build_url(city: str, district: str, page: int, property_type: str) -> str:
        """
        构建单个 URL

        Args:
            city: 城市代码
            district: 城区代码
            page: 页码
            property_type: 房产类型（rental, secondhand, new_house）

        Returns:
            str: 完整 URL
        """
        property_path = UrlGenerator.PROPERTY_TYPE_PATH.get(property_type, 'zufang')

        if page == 1:
            # 第一页不需要 pg{page}
            return f"https://{city}.lianjia.com/{property_path}/{district}/"
        else:
            return f"https://{city}.lianjia.com/{property_path}/{district}/pg{page}/"

    @staticmethod
    def get_all_task_keys(cities: List[str]) -> Dict[str, int]:
        """
        为多个城市生成所有任务键和初始页码

        Args:
            cities: 城市代码列表

        Returns:
            Dict[str, int]: {task_key: initial_page}，格式 {'bj|dongcheng': 1, ...}
        """
        task_keys = {}
        for city in cities:
            for key in UrlGenerator.get_task_keys(city):
                task_keys[key] = 1  # 所有任务初始页码为 1
        return task_keys
