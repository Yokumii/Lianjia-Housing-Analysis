import pandas as pd
import requests
import time
from typing import Tuple, Optional

class CoordinateProvider:
    """地理坐标提供者"""

    def __init__(self, api_key: str, verbose: bool = True):
        """
        初始化坐标提供者

        Args:
            api_key: 高德地图 Web 服务 API Key
            verbose: 是否打印详细日志
        """
        self.api_key = api_key
        self.verbose = verbose
        self.base_url = "https://restapi.amap.com/v3/geocode/geo"
        self.stats = {
            'success': 0,
            'not_found': 0,
            'error': 0,
            'over_limit': False,
        }

    def _log(self, msg: str):
        """打印日志"""
        if self.verbose:
            print(msg)

    def get_coordinates(
        self,
        address: str,
        city: str,
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        调用高德 API 获取经纬度

        Args:
            address: 完整地址（如 "北京朝阳区"）
            city: 城市名称

        Returns:
            Tuple: (经度, 纬度, 状态码)
        """
        params = {
            'address': address,
            'city': city,
            'key': self.api_key,
            'output': 'JSON'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # 成功获取
                if data.get('status') == '1' and int(data.get('count', 0)) > 0:
                    location = data['geocodes'][0]['location']
                    lng, lat = location.split(',')
                    self.stats['success'] += 1
                    return float(lng), float(lat), 'SUCCESS'

                # 配额超限
                elif data.get('infocode') == '10003':
                    self.stats['over_limit'] = True
                    return None, None, 'OVER_LIMIT'

                # 其它失败（查无此地）
                else:
                    self.stats['not_found'] += 1
                    return None, None, 'NOT_FOUND'

        except Exception:
            self.stats['error'] += 1
            return None, None, 'ERROR'

        self.stats['error'] += 1
        return None, None, 'UNKNOWN'

    def fetch_row_coordinates(self, row: pd.Series) -> Tuple[Optional[float], Optional[float], str]:
        """
        为单条记录智能获取坐标（自动降级搜索）

        策略顺序：
        1. 小区级别（最精确）
        2. 商圈/板块级别
        3. 行政区级别（兜底）

        Args:
            row: DataFrame 的一行数据

        Returns:
            Tuple: (经度, 纬度, 精度等级)
        """
        # 已有坐标直接返回
        if pd.notna(row.get('经度')):
            level = row.get('坐标精度', '已有')
            return row['经度'], row['纬度'], level

        city = str(row.get('城市', ''))
        district = str(row.get('区域', ''))
        community = str(row.get('小区', ''))
        biz_circle = str(row.get('板块', ''))

        # 构建搜索策略
        strategies = []

        # 策略 A：精确到小区（优先级最高）
        if community and community not in ('nan', '未知', ''):
            strategies.append((f"{city}{district}{community}", "小区"))
            strategies.append((f"{city}{community}", "小区(模糊)"))

        # 策略 B：精确到商圈/板块
        if biz_circle and biz_circle not in ('nan', '未知', ''):
            strategies.append((f"{city}{district}{biz_circle}", "板块"))

        # 策略 C：精确到行政区（兜底）
        if district and district not in ('nan', '未知', ''):
            strategies.append((f"{city}{district}", "行政区"))

        # 尝试每个策略
        for address, level in strategies:
            lng, lat, status = self.get_coordinates(address, city)

            # 配额超限，直接抛出异常
            if status == 'OVER_LIMIT':
                raise RuntimeError("API_QUOTA_EXCEEDED")

            if status == 'SUCCESS':
                time.sleep(0.05)  # 成功后稍微休息
                return lng, lat, level

            time.sleep(0.02)  # 失败也休息

        return None, None, "失败"


def add_coordinates(
    df: pd.DataFrame,
    api_key: str,
    batch_size: int = 50,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    为 DataFrame 添加地理坐标

    Args:
        df: 输入 DataFrame
        api_key: 高德 API Key
        batch_size: 批次大小（每 N 条记录保存一次）
        verbose: 是否打印详细日志

    Returns:
        包含坐标的 DataFrame
    """
    if not api_key:
        if verbose:
            print("⚠️  未提供 API Key，跳过坐标添加")
        return df

    if verbose:
        print("🌐 开始添加地理坐标...")

    # 初始化列
    if '经度' not in df.columns:
        df['经度'] = None
    if '纬度' not in df.columns:
        df['纬度'] = None
    if '坐标精度' not in df.columns:
        df['坐标精度'] = None

    # 筛选待处理数据
    mask_todo = df['经度'].isna()
    todo_count = mask_todo.sum()

    if verbose:
        print(f"待处理数据: {todo_count} 条 (已跳过 {len(df) - todo_count} 条已有坐标数据)")

    if todo_count == 0:
        if verbose:
            print("✅ 所有数据均已有经纬度，无需处理")
        return df

    # 初始化提供者
    provider = CoordinateProvider(api_key, verbose=verbose)

    # 处理数据
    indices = df[mask_todo].index

    try:
        for i in range(0, len(indices), batch_size):
            batch_idx = indices[i : i + batch_size]

            for idx in batch_idx:
                try:
                    row = df.loc[idx]
                    lng, lat, level = provider.fetch_row_coordinates(row)
                    df.at[idx, '经度'] = lng
                    df.at[idx, '纬度'] = lat
                    df.at[idx, '坐标精度'] = level

                except RuntimeError as e:
                    if str(e) == "API_QUOTA_EXCEEDED":
                        if verbose:
                            print("\n🚨 今日 API 额度已用完！")
                        return df

    except KeyboardInterrupt:
        if verbose:
            print("\n⏸️  用户中断")

    # 统计
    success_count = df['经度'].notna().sum()
    if verbose:
        print(f"\n✅ 处理完成！")
        print(f"📊 成功获取坐标: {success_count}/{len(df)} ({success_count/len(df)*100:.1f}%)")
        if '坐标精度' in df.columns:
            print("\n🎯 坐标精度分布:")
            print(df['坐标精度'].value_counts())

    return df
