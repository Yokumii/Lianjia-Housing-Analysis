import math
import re
from typing import List, Dict, Any, Optional, Tuple
from lxml import html as lxml_html
from ..items.models import PropertyType, HouseItem, RentalHouse, SecondHandHouse


class ParseError(Exception):
    """解析错误"""
    pass


class Parser:
    """CSS 选择器解析器"""

    # 每页固定房源数（链家规则）
    ITEMS_PER_PAGE = 30

    def __init__(self, property_type: PropertyType, selectors: Dict[str, str]):
        """
        初始化解析器

        Args:
            property_type: 房产类型（RENTAL 或 SECONDHAND）
            selectors: CSS 选择器映射
        """
        self.property_type = property_type
        self.selectors = selectors
        self._validate_selectors()

    def _validate_selectors(self):
        """验证必要的选择器"""
        required = ['house_list']
        missing = [k for k in required if k not in self.selectors]
        if missing:
            raise ValueError(f"缺少必需的选择器: {missing}")

    def get_max_page(self, html_content: str) -> int:
        """
        从 HTML 中提取最大页码

        实现逻辑：
        1. 尝试从 HTML 中提取总房源数
        2. 使用 ceil(total_count / 30) 计算最大页码
        3. 如果无法提取，返回 1（表示只有一页或无数据）

        Args:
            html_content: HTML 原始文本

        Returns:
            int: 最大页码
        """
        try:
            tree = lxml_html.fromstring(html_content)
        except Exception:
            return 1

        # 尝试多种选择器提取总房源数
        total_count_str = None

        # 优先尝试配置中的 total_count 选择器
        if 'total_count' in self.selectors:
            try:
                selector = self.selectors['total_count']
                elements = tree.cssselect(selector)
                if elements:
                    total_count_str = self._extract_text_from_element(elements[0])
            except Exception:
                pass

        # 如果没有找到，尝试常见的选择器（二手房）
        if not total_count_str:
            try:
                elements = tree.cssselect('.total span')
                if elements:
                    total_count_str = self._extract_text_from_element(elements[0])
            except Exception:
                pass

        # 尝试从 resultDes 中提取（链家常见结构）
        if not total_count_str:
            try:
                elements = tree.cssselect('.resultDes .total span')
                if elements:
                    total_count_str = self._extract_text_from_element(elements[0])
            except Exception:
                pass

        # 如果找到了总数，计算最大页码
        if total_count_str:
            try:
                # 提取数字（可能包含逗号等字符）
                numbers = re.findall(r'\d+', str(total_count_str).replace(',', ''))
                if numbers:
                    total_count = int(numbers[0])
                    if total_count > 0:
                        max_page = math.ceil(total_count / self.ITEMS_PER_PAGE)
                        return max_page
            except Exception:
                pass

        # 默认返回 1（无法获取页码信息时）
        return 1

    def parse(self, html_content: str, city: str, **kwargs) -> List[HouseItem]:
        """
        解析 HTML，返回房源对象列表

        Args:
            html_content: HTML 原始文本
            city: 城市代码
            **kwargs: 额外的元数据（如 district, area 等）

        Returns:
            List[HouseItem]: 房源数据列表
        """
        try:
            tree = lxml_html.fromstring(html_content)
        except Exception as e:
            raise ParseError(f"HTML 解析失败: {e}")

        items = []

        try:
            # 使用 CSS 选择器获取房源列表
            house_elements = tree.cssselect(self.selectors['house_list'])
        except Exception as e:
            raise ParseError(f"无法选择房源列表: {e}")

        for idx, house_elem in enumerate(house_elements):
            try:
                item = self._parse_single_item(house_elem, city, **kwargs)
                if item:
                    items.append(item)
            except Exception as e:
                # 单个房源解析失败，记录但继续处理其他房源
                print(f"[警告] 解析第 {idx} 个房源失败: {e}")
                continue

        return items

    def _parse_single_item(self, house_elem, city: str, **kwargs) -> Optional[HouseItem]:
        """
        解析单个房源元素

        根据房产类型，对二手房和租房采用不同的解析策略
        """
        if self.property_type == PropertyType.SECONDHAND:
            return self._parse_secondhand_item(house_elem, city, **kwargs)
        elif self.property_type == PropertyType.RENTAL:
            return self._parse_rental_item(house_elem, city, **kwargs)
        else:
            raise ValueError(f"不支持的房产类型: {self.property_type}")

    def _parse_secondhand_item(self, house_elem, city: str, **kwargs) -> Optional[HouseItem]:
        """
        解析二手房房源

        HTML 结构：
        ```html
        <li class="clear">
          <div class="title"><a href="/ershoufang/101234567.html">房源描述文本</a></div>
          <div class="totalPrice"><span>298</span></div>
          <div class="unitPrice"><span>56000</span></div>
          <div class="positionInfo"><a>小区名</a></div>
          <div class="houseInfo">2室2厅 | 53.82平米 | 南北 | 精装 | 高楼层(共6层) | 2008年 | 板楼</div>
        </li>
        ```
        """
        # 1. 房源编号和标题 - 从 href 属性提取
        house_id = None
        name = None
        title_link_elem = self._css_select_one(house_elem, self.selectors.get('title_link'))
        if title_link_elem is not None:
            href = title_link_elem.get('href', '')
            if href:
                # 从 /ershoufang/101234567.html 提取编号
                match = re.search(r'/ershoufang/(\d+)', href)
                if match:
                    house_id = match.group(1)
            # 获取 <a> 标签内的文本作为房源描述
            name = self._extract_text_from_element(title_link_elem)

        if not house_id:
            return None  # 无法获取房源编号，跳过此房源

        # 2. 价格信息
        price_str = self._css_select_text(house_elem, self.selectors.get('price'))
        try:
            price = int(float(price_str)) if price_str else 0
        except (ValueError, TypeError):
            price = 0

        # 3. 小区名称
        community = self._css_select_text(house_elem, self.selectors.get('community'))

        # 4. 从 .houseInfo 的混合文本中分离多个字段
        # 格式: "2室2厅 | 53.82平米 | 南北 | 精装 | 高楼层(共6层) | 2008年 | 板楼"
        house_info_text = self._css_select_text(house_elem, self.selectors.get('house_info'), '')
        layout, square, direction, building_year = self._parse_house_info(house_info_text)

        # 5. 生成唯一房源 ID（用于去重）
        hash_id = self._generate_hash_id(house_id, city, community or name or '')

        # 6. 创建二手房数据模型
        item = SecondHandHouse(
            city=city,
            house_id=house_id,  # 链家房源编号
            name=name or '',     # 房源描述/标题
            price=price,         # 总价（万）
            district='',         # 二手房页面通常没有单独的区字段
            street='',
            community=community or '',  # 小区名
            layout=layout or '',  # 户型
            square=square,       # 面积
            direction=direction or '',  # 朝向
            floor='',
            building_year=building_year,  # 建筑年份
            property_rights='',  # 产权类型
            renovation='',       # 装修状况
        )

        return item

    def _parse_rental_item(self, house_elem, city: str, **kwargs) -> Optional[HouseItem]:
        """
        解析租房房源

        HTML 结构：
        ```html
        <div class="content__list--item" data-ad_type="0" data-t="default">
          <div class="content__list--item--title"><a href="/zufang/...">房源标题</a></div>
          <div class="content__list--item-price"><em>3100</em></div>
          <div class="content__list--item--des">
            <a>顺义</a><a>顺义城</a><a>石园北区</a>
            3室1厅1卫 / 111.89㎡ / 西南 / ...
          </div>
          <div class="content__list--item--brand"><span class="brand">链家</span></div>
        </div>
        ```
        """
        # 获取城市代码（用于 URL 构建）
        city_code = kwargs.get('city_code', 'bj')

        # 过滤广告和推荐房源
        if house_elem.get('data-ad_type') != '0':
            return None
        if house_elem.get('data-t') != 'default':
            return None

        # 1. 提取标题和链接
        title_elem = self._css_select_one(house_elem, self.selectors.get('title_link'))
        if title_elem is None:
            return None

        name = self._extract_text_from_element(title_elem)
        if not name:
            return None

        # 提取链接
        link_suffix = title_elem.get('href', '')
        url = f"https://{city_code}.lianjia.com{link_suffix}" if link_suffix.startswith('/') else link_suffix

        # 2. 提取租金价格
        price_str = self._css_select_text(house_elem, self.selectors.get('price'), '0')
        try:
            price = int(float(price_str)) if price_str else 0
        except (ValueError, TypeError):
            price = 0

        # 3. 提取地理位置信息（区域、板块、小区）
        location_elems = house_elem.cssselect(self.selectors.get('location_links', '.content__list--item--des a'))
        district = location_elems[0].text.strip() if len(location_elems) > 0 else '未知'
        street = location_elems[1].text.strip() if len(location_elems) > 1 else '未知'
        community = location_elems[2].text.strip() if len(location_elems) > 2 else '未知'

        # 4. 解析描述文本（面积、户型详情、朝向）
        des_elem = self._css_select_one(house_elem, self.selectors.get('des_text'))
        square = None
        layout_detail = '未知'
        direction = '未知'

        if des_elem is not None:
            # 提取文本，移除所有 <a> 标签
            des_copy = des_elem
            for a in des_copy.cssselect('a'):
                parent = a.getparent()
                if parent is not None:
                    parent.remove(a)

            # 获取所有文本节点并分割
            text_content = ''.join(des_copy.xpath('.//text()'))

            # 使用 / 和其他分隔符进行分割
            parts = []
            for part in text_content.split('/'):
                cleaned = part.strip()
                if cleaned and cleaned != '-':
                    parts.append(cleaned)

            # 从分割的部分提取各个字段
            for part in parts:
                # 提取面积（含 ㎡）
                if '㎡' in part:
                    square_str = part.replace('㎡', '').strip()
                    try:
                        square = float(square_str)
                    except (ValueError, TypeError):
                        square = None
                # 提取户型详情（含 室 或 房间）
                elif '室' in part or '房间' in part:
                    layout_detail = part
                # 提取朝向（含方向字但不含 厅/卫/层）
                elif any(d in part for d in ['东', '南', '西', '北']) and not any(x in part for x in ['厅', '卫', '层']):
                    direction = part

        # 5. 提取品牌
        brand = self._css_select_text(house_elem, self.selectors.get('brand'), '链家')

        # 6. 从户型详情推断户型分类（一居/两居/三居）
        layout = self._infer_layout_from_detail(layout_detail)

        # 7. 生成唯一房源 ID（用于去重）
        house_id = self._generate_hash_id(name, city, district)

        # 8. 创建租房数据模型
        item = RentalHouse(
            city=city,
            house_id=house_id,
            name=name,
            price=price,
            district=district,
            street=street,
            community=community,
            layout=layout,
            layout_detail=layout_detail,
            square=square,
            direction=direction,
            brand=brand,
            url=url,
        )

        return item

    def _infer_layout_from_detail(self, layout_detail: str) -> str:
        """
        从户型详情推断户型分类（一居/两居/三居）

        例如：
        - "1室1厅" → "一居"
        - "2室1厅" → "两居"
        - "3室1厅" → "三居"
        - "1房间2卫" → "一居"
        - "3房间2卫" → "三居"
        - "4室2厅" → "三居"（≥3室 都视为三居）
        - "未知" → "未知"
        """
        if not layout_detail or layout_detail == '未知':
            return '未知'

        # 使用正则提取第一个数字（房间数）
        # 支持 "室" 或 "房间" 两种格式
        match = re.search(r'(\d+)\s*(?:室|房间)', layout_detail)
        if match:
            room_count = int(match.group(1))
            if room_count == 1:
                return '一居'
            elif room_count == 2:
                return '两居'
            elif room_count >= 3:
                return '三居'

        return '未知'

    def _parse_house_info(self, house_info_text: str) -> Tuple[str, Optional[float], str, Optional[int]]:
        """
        从混合的 houseInfo 文本中分离多个字段

        输入格式示例:
        "2室2厅 | 53.82平米 | 南北 | 精装 | 高楼层(共6层) | 2008年 | 板楼"

        返回: (layout, square, direction, building_year)
        """
        if not house_info_text:
            return '', None, '', None

        # 用 | 或空格分割
        parts = [p.strip() for p in house_info_text.split('|')]

        layout = parts[0] if len(parts) > 0 else ''  # "2室2厅"
        square = None
        direction = ''
        building_year = None

        # 解析面积（含"平米"或"m²"字样）
        if len(parts) > 1:
            square_text = parts[1]
            match = re.search(r'([\d.]+)\s*[平米m²]+', square_text)
            if match:
                try:
                    square = float(match.group(1))
                except (ValueError, TypeError):
                    square = None

        # 解析朝向（南、北、东、西等）
        if len(parts) > 2:
            direction_text = parts[2]
            # 提取所有朝向字符
            directions = re.findall(r'[南北东西]', direction_text)
            if directions:
                direction = ' '.join(directions) if len(directions) > 1 else directions[0]

        # 解析建筑年份（找"年"字后的数字）
        if len(parts) >= 5:  # 通常在第5个元素
            year_text = parts[5] if len(parts) > 5 else house_info_text
            match = re.search(r'(\d{4})\s*年', year_text)
            if match:
                try:
                    building_year = int(match.group(1))
                except (ValueError, TypeError):
                    building_year = None

        return layout, square, direction, building_year

    @staticmethod
    def _css_select_one(elem, selector: Optional[str]):
        """从元素中使用 CSS 选择器获取单个元素（不是文本）"""
        if not selector:
            return None
        try:
            results = elem.cssselect(selector)
            if results:
                return results[0]  # 返回元素对象，而不是文本
        except Exception:
            pass
        return None

    @staticmethod
    def _css_select_text(elem, selector: Optional[str], default: str = '') -> str:
        """从元素中使用 CSS 选择器提取文本"""
        if not selector:
            return default
        try:
            results = elem.cssselect(selector)
            if results:
                element = results[0]
                text = Parser._extract_text_from_element(element)
                return text if text else default
        except Exception:
            pass
        return default

    @staticmethod
    def _extract_text_from_element(element) -> Optional[str]:
        """从 lxml 元素中提取文本"""
        try:
            # 获取元素的文本内容
            text = ''.join(element.xpath('.//text()'))
            return text.strip() if text else None
        except Exception:
            pass
        return None

    @staticmethod
    def _generate_hash_id(name: str, city: str, district: Optional[str]) -> str:
        """生成唯一房源 ID"""
        import hashlib
        unique_str = f"{city}_{district or ''}_{name}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]

