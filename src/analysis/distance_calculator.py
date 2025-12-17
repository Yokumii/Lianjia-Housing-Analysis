import pandas as pd
import numpy as np
import requests
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class DistanceCalculator:
    """距离计算器 - 调用高德地图 API"""

    # 高德 API 配置
    AMAP_API_URL = "https://restapi.amap.com/v3/distance"
    BATCH_SIZE = 50  # 每次批量查询的最大起点数
    QPS_LIMIT = 1  # 每秒最多请求数（保守估计）
    RETRY_TIMES = 3  # 失败重试次数
    RETRY_DELAY = 2  # 重试延迟（秒）

    # 核心就业区坐标（经度,纬度）
    EMPLOYMENT_CENTERS = {
        'bj': {
            '西二旗': (116.306295, 40.053034),
            '望京': (116.466485, 39.995197),
            '国贸': (116.459288, 39.910882),
            '金融街': (116.357325, 39.910142)
        },
        'sh': {
            '陆家嘴': (121.5025, 31.237015),
            '张江科学城': (121.643677, 31.206884),
            '漕河泾': (121.416405, 31.16791),
            '外滩': (121.492127, 31.233516)
        },
        'sz': {
            '南山科技园': (113.94631, 22.543723),
            '深圳湾': (113.972602, 22.518968),
            '福田CBD': (114.055963, 22.525845),
            '坂田科技城': (114.055362, 22.636404)
        },
        'gz': {
            '珠江新城': (113.321202, 23.119366),
            '体育西路': (113.321503, 23.131138),
            '天河软件园': (113.412453, 23.171807),
            '广州科学城': (113.44952, 23.165789)
        },
        'hz': {
            '未来科技城': (120.007498, 30.295056),
            '钱江新城': (120.214223, 30.250328),
            '滨江区': (120.211981, 30.208332),
            '湖滨商圈': (120.164471, 30.252148)
        }
    }

    def __init__(
        self,
        api_key: str,
        cache_dir: str = 'cache/distances',
        verbose: bool = True
    ):
        """
        初始化距离计算器

        Args:
            api_key: 高德地图 API key
            cache_dir: 缓存目录
            verbose: 是否打印详细日志
        """
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.last_request_time = 0
        self.request_count = 0

    def _rate_limit(self):
        """限流控制，确保不超过 QPS 限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        # 如果距离上次请求时间小于间隔，则等待
        min_interval = 1.0 / self.QPS_LIMIT
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()
        self.request_count += 1

    def _call_amap_api(
        self,
        origins: List[Tuple[float, float]],
        destination: Tuple[float, float],
        distance_type: int = 1
    ) -> List[Optional[float]]:
        """
        调用高德地图 API 计算距离

        Args:
            origins: 起点列表 [(lng, lat), ...]
            destination: 终点 (lng, lat)
            distance_type: 0=直线距离, 1=驾车距离

        Returns:
            距离列表（米），失败则为 None
        """
        # 限流
        self._rate_limit()

        # 构造请求参数
        origins_str = '|'.join([f"{lng},{lat}" for lng, lat in origins])
        dest_str = f"{destination[0]},{destination[1]}"

        params = {
            'key': self.api_key,
            'origins': origins_str,
            'destination': dest_str,
            'type': distance_type,
            'output': 'json'
        }

        # 发送请求（带重试）
        for attempt in range(self.RETRY_TIMES):
            try:
                response = requests.get(self.AMAP_API_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # 检查返回状态
                if data.get('status') != '1':
                    if self.verbose:
                        print(f"  ⚠️ API 返回错误: {data.get('info', 'Unknown error')}")
                    return [None] * len(origins)

                # 解析结果
                results = data.get('results', [])
                distances = []

                for result in results:
                    # 检查单条结果是否成功
                    if 'distance' in result and result.get('info') != '未知错误':
                        try:
                            dist = float(result['distance'])
                            distances.append(dist if dist > 0 else None)
                        except (ValueError, TypeError):
                            distances.append(None)
                    else:
                        distances.append(None)

                return distances

            except requests.exceptions.RequestException as e:
                if attempt < self.RETRY_TIMES - 1:
                    if self.verbose:
                        print(f"  ⚠️ 请求失败 (尝试 {attempt + 1}/{self.RETRY_TIMES}): {e}")
                    time.sleep(self.RETRY_DELAY)
                else:
                    if self.verbose:
                        print(f"  ❌ 请求最终失败: {e}")
                    return [None] * len(origins)

        return [None] * len(origins)

    def calculate_distances(
        self,
        city_code: str,
        coord_data_file: str,
        distance_type: int = 1,
        force_recalculate: bool = False
    ) -> pd.DataFrame:
        """
        计算指定城市所有房源到各核心就业区的距离

        Args:
            city_code: 城市代码（bj/sh/gz/sz/hz）
            coord_data_file: 坐标数据文件路径
            distance_type: 0=直线距离, 1=驾车距离
            force_recalculate: 是否强制重新计算（忽略缓存）

        Returns:
            包含距离信息的 DataFrame
        """
        # 检查缓存
        cache_file = self.cache_dir / f"{city_code}_distances_type{distance_type}.json"
        if cache_file.exists() and not force_recalculate:
            if self.verbose:
                print(f"\n✓ 从缓存加载距离数据: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                distances_cache = json.load(f)
            # 转换为 DataFrame 并返回
            return self._merge_distances_to_df(coord_data_file, distances_cache)

        # 读取坐标数据
        if self.verbose:
            print(f"\n读取 {city_code} 坐标数据...")
        df = pd.read_csv(coord_data_file)
        df = df.dropna(subset=['经度', '纬度'])

        if self.verbose:
            print(f"✓ 有效坐标数据: {len(df):,} 行")

        # 获取就业中心
        centers = self.EMPLOYMENT_CENTERS.get(city_code, {})
        if not centers:
            raise ValueError(f"未定义城市 {city_code} 的就业中心")

        # 准备距离缓存
        distances_cache = defaultdict(dict)

        # 对每个就业中心计算距离
        for center_name, center_coord in centers.items():
            if self.verbose:
                print(f"\n计算到 {center_name} 的距离...")

            # 准备起点坐标列表
            origins = [(row['经度'], row['纬度']) for _, row in df.iterrows()]

            # 分批调用 API
            all_distances = []
            total_batches = (len(origins) + self.BATCH_SIZE - 1) // self.BATCH_SIZE

            for batch_idx in range(0, len(origins), self.BATCH_SIZE):
                batch_origins = origins[batch_idx:batch_idx + self.BATCH_SIZE]
                current_batch = batch_idx // self.BATCH_SIZE + 1

                if self.verbose:
                    print(f"  批次 {current_batch}/{total_batches} ({len(batch_origins)} 个起点)...", end='')

                # 调用 API
                batch_distances = self._call_amap_api(
                    origins=batch_origins,
                    destination=center_coord,
                    distance_type=distance_type
                )

                all_distances.extend(batch_distances)

                if self.verbose:
                    success_count = sum(1 for d in batch_distances if d is not None)
                    print(f" ✓ 成功 {success_count}/{len(batch_distances)}")

            # 保存到缓存
            for idx, distance in enumerate(all_distances):
                distances_cache[str(idx)][center_name] = distance

        # 保存缓存到文件
        if self.verbose:
            print(f"\n保存缓存到 {cache_file}...")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(distances_cache, f, ensure_ascii=False, indent=2)

        if self.verbose:
            print(f"✓ API 调用总数: {self.request_count:,}")

        # 合并距离数据到 DataFrame
        return self._merge_distances_to_df(coord_data_file, distances_cache)

    def _merge_distances_to_df(
        self,
        coord_data_file: str,
        distances_cache: dict
    ) -> pd.DataFrame:
        """将缓存的距离数据合并到 DataFrame"""
        df = pd.read_csv(coord_data_file)
        df = df.dropna(subset=['经度', '纬度'])
        
        # 重置索引，确保索引从 0 开始连续
        df = df.reset_index(drop=True)

        # 添加距离列
        for idx in range(len(df)):
            idx_str = str(idx)
            if idx_str in distances_cache:
                for center_name, distance in distances_cache[idx_str].items():
                    col_name = f'距离_{center_name}'
                    df.loc[idx, col_name] = distance

        return df
