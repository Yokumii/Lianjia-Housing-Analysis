from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class PropertyType(Enum):
    """房产类型"""
    SECONDHAND = "secondhand"  # 二手房
    RENTAL = "rental"          # 租房
    NEW_HOUSE = "new_house"    # 新房


class City(Enum):
    """城市代码"""
    BJ = "bj"   # 北京
    SH = "sh"   # 上海
    SZ = "sz"   # 深圳
    GZ = "gz"   # 广州
    HZ = "hz"   # 杭州


@dataclass
class HouseItem:
    """房产数据基类"""

    # 基本字段（所有房产类型通用）
    city: str                          # 城市代码（bj, sh, sz, gz, hz）
    district: Optional[str] = None     # 区域（朝阳、浦东等）
    street: Optional[str] = None       # 板块（街道）
    community: Optional[str] = None    # 小区名称
    layout: Optional[str] = None       # 户型（1室1厅、2室1厅等）
    layout_detail: Optional[str] = None  # 户型详情（从 houseInfo 提取的详细描述）
    name: str = ""                     # 房源名称/标题
    price: int = 0                     # 价格（元/月 或 元）
    square: Optional[float] = None     # 面积（平方米）
    direction: Optional[str] = None    # 朝向（南、北、东等）
    brand: Optional[str] = None        # 品牌（贝壳优选、链家等）
    url: Optional[str] = None          # 房源页面 URL

    # 内部字段（不导出到 CSV）
    house_id: str = ""                 # 唯一房源 ID（用于去重，不导出）
    floor: Optional[str] = None        # 楼层（不导出）
    tags: Optional[list] = field(default_factory=list)  # 标签列表（不导出）
    raw_data: Dict[str, Any] = field(default_factory=dict)  # 原始数据（不导出）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于存储到 CSV"""
        return {
            '城市': self.city,
            '区域': self.district or '',
            '板块': self.street or '',
            '小区': self.community or '',
            '户型': self.layout or '',
            '户型详情': self.layout_detail or '',
            '标题': self.name or '',
            '租金': self.price or '',
            '面积': self.square or '',
            '朝向': self.direction or '',
            '品牌': self.brand or '',
            '链接': self.url or '',
        }


@dataclass
class SecondHandHouse(HouseItem):
    """二手房数据模型"""

    building_year: Optional[int] = None    # 建筑年份
    property_rights: Optional[str] = None  # 产权（70年、50年等）
    renovation: Optional[str] = None       # 装修状态（精装、简装、毛坯）
    elevator: Optional[str] = None         # 是否有电梯

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'building_year': self.building_year,
            'property_rights': self.property_rights,
            'renovation': self.renovation,
            'elevator': self.elevator,
        })
        return data


@dataclass
class RentalHouse(HouseItem):
    """租房数据模型"""

    # 租赁相关字段（内部使用，不导出到 CSV）
    price_per_m2: Optional[float] = None   # 单位面积租金（元/m²）
    min_lease: Optional[str] = None        # 最小租期
    lease_type: Optional[str] = None       # 租赁类型（整租、合租等）

# CSV 导出时的字段顺序
CSV_COLUMNS_SECONDHAND = [
    'city', 'house_id', 'name', 'price', 'district', 'street', 'community',
    'layout', 'square', 'direction', 'floor', 'building_year', 'property_rights',
    'renovation', 'elevator', 'url', 'tags'
]

CSV_COLUMNS_RENTAL = [
    'city', 'house_id', 'name', 'price', 'district', 'street', 'community',
    'layout', 'square', 'direction', 'floor', 'price_per_m2', 'min_lease',
    'lease_type', 'url', 'tags'
]
