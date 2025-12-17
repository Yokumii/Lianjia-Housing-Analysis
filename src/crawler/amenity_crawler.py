import requests
import pandas as pd
import json
import time
from pathlib import Path
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote


class AmenityCrawler:
    """配套设施数据爬虫"""

    # API端点
    STARBUCKS_API = "https://www.starbucks.com.cn/api/stores/nearby"
    MCDONALDS_API = "https://www.mcdonalds.com.cn/ajaxs/search_by_point"

    def __init__(
        self,
        radius_m: int = 1000,
        max_workers: int = 5,
        verbose: bool = True
    ):
        """
        初始化爬虫

        Args:
            radius_m: 搜索半径（米），默认1000米
            max_workers: 并发线程数
            verbose: 是否打印详细日志
        """
        self.radius_m = radius_m
        self.max_workers = max_workers
        self.verbose = verbose

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'starbucks_total': 0,
            'mcdonalds_total': 0
        }

    def fetch_starbucks(self, lat: float, lon: float) -> Optional[int]:
        """
        查询周边星巴克数量

        Args:
            lat: 纬度
            lon: 经度

        Returns:
            门店数量，失败返回None
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'radius': self.radius_m,
                'limit': 1000,
                'locale': 'ZH',
                'features': ''
            }

            response = requests.get(
                self.STARBUCKS_API,
                params=params,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                count = data.get('meta', {}).get('total', 0)
                return count
            else:
                if self.verbose:
                    print(f"⚠️ 星巴克API返回异常: {response.status_code}")
                return None

        except Exception as e:
            if self.verbose:
                print(f"⚠️ 星巴克API请求失败: {e}")
            return None

    def fetch_mcdonalds(self, lat: float, lon: float) -> Optional[int]:
        """
        查询周边麦当劳数量

        Args:
            lat: 纬度
            lon: 经度

        Returns:
            门店数量，失败返回None
        """
        try:
            # 构造POST参数（需要URL编码）
            point = f"{lat},{lon}"
            data = {
                'point': point,
                'type': ''
            }

            response = requests.post(
                self.MCDONALDS_API,
                data=data,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                stores = result.get('data', [])

                # 过滤距离在radius_m内的门店
                count = sum(1 for store in stores
                           if store.get('_distance', float('inf')) <= self.radius_m)
                return count
            else:
                if self.verbose:
                    print(f"⚠️ 麦当劳API返回异常: {response.status_code}")
                return None

        except Exception as e:
            if self.verbose:
                print(f"⚠️ 麦当劳API请求失败: {e}")
            return None

    def fetch_amenities_with_retry(
        self,
        lat: float,
        lon: float,
        max_retries: int = 3
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        查询配套设施数量（带重试）

        Args:
            lat: 纬度
            lon: 经度
            max_retries: 最大重试次数

        Returns:
            (星巴克数量, 麦当劳数量)
        """
        starbucks_count = None
        mcdonalds_count = None

        # 重试星巴克API
        for attempt in range(max_retries):
            starbucks_count = self.fetch_starbucks(lat, lon)
            if starbucks_count is not None:
                break
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避

        # 重试麦当劳API
        for attempt in range(max_retries):
            mcdonalds_count = self.fetch_mcdonalds(lat, lon)
            if mcdonalds_count is not None:
                break
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

        return starbucks_count, mcdonalds_count

    def _process_single_row(
        self,
        idx: int,
        lat: float,
        lon: float
    ) -> Tuple[int, Optional[int], Optional[int]]:
        """
        处理单个房源

        Args:
            idx: 行索引
            lat: 纬度
            lon: 经度

        Returns:
            (idx, 星巴克数量, 麦当劳数量)
        """
        starbucks, mcdonalds = self.fetch_amenities_with_retry(lat, lon)

        if starbucks is not None and mcdonalds is not None:
            self.stats['success'] += 1
            self.stats['starbucks_total'] += starbucks
            self.stats['mcdonalds_total'] += mcdonalds
        else:
            self.stats['failed'] += 1

        return idx, starbucks, mcdonalds

    def process_city(
        self,
        city_code: str,
        input_file: str,
        output_file: str,
        resume: bool = True
    ):
        """
        批量处理城市数据

        Args:
            city_code: 城市代码（bj/sh等）
            input_file: 输入CSV文件路径
            output_file: 输出CSV文件路径
            resume: 是否从断点恢复
        """
        print(f"\n{'='*60}")
        print(f"开始爬取 {city_code.upper()} 的配套设施数据")
        print(f"搜索半径: {self.radius_m}米")
        print(f"{'='*60}\n")

        # 读取数据
        df = pd.read_csv(input_file)
        self.stats['total'] = len(df)

        # 检查必需列
        if '经度' not in df.columns or '纬度' not in df.columns:
            raise ValueError("输入CSV必须包含'经度'和'纬度'列")

        # 过滤有效坐标
        df_valid = df.dropna(subset=['经度', '纬度']).copy()
        df_valid = df_valid.reset_index(drop=False)
        df_valid.rename(columns={'index': 'original_idx'}, inplace=True)

        print(f"✓ 总房源数: {len(df):,}")
        print(f"✓ 有效坐标: {len(df_valid):,}")

        # 加载进度
        progress_file = Path('cache') / f'{city_code}_amenity_progress.json'
        progress_file.parent.mkdir(parents=True, exist_ok=True)

        processed_indices = set()
        if resume and progress_file.exists():
            processed_indices = self._load_progress(progress_file)
            print(f"✓ 从断点恢复，已处理: {len(processed_indices):,} 条\n")

        # 初始化结果列
        if '星巴克数量' not in df.columns:
            df['星巴克数量'] = None
        if '麦当劳数量' not in df.columns:
            df['麦当劳数量'] = None

        # 准备待处理的任务
        tasks = []
        for _, row in df_valid.iterrows():
            idx = row['original_idx']
            if idx not in processed_indices:
                tasks.append((idx, row['纬度'], row['经度']))

        if not tasks:
            print("✓ 所有数据已处理完毕！")
            return

        print(f"待处理: {len(tasks):,} 条\n")

        # 并发处理
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single_row, idx, lat, lon): idx
                for idx, lat, lon in tasks
            }

            for i, future in enumerate(as_completed(futures), 1):
                idx, starbucks, mcdonalds = future.result()

                # 更新DataFrame
                df.loc[idx, '星巴克数量'] = starbucks
                df.loc[idx, '麦当劳数量'] = mcdonalds

                # 记录进度
                processed_indices.add(idx)

                # 定期保存
                if i % 100 == 0:
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    self._save_progress(progress_file, list(processed_indices), len(df_valid))

                    elapsed = time.time() - start_time
                    speed = i / elapsed
                    eta = (len(tasks) - i) / speed if speed > 0 else 0

                    print(f"进度: {i}/{len(tasks)} ({i/len(tasks)*100:.1f}%) | "
                          f"成功: {self.stats['success']} | "
                          f"失败: {self.stats['failed']} | "
                          f"速度: {speed:.1f} 条/秒 | "
                          f"预计剩余: {eta/60:.1f} 分钟")

        # 最终保存
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        if progress_file.exists():
            progress_file.unlink()  # 删除进度文件

        # 打印统计
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"爬取完成！")
        print(f"{'='*60}")
        print(f"总耗时: {elapsed/60:.1f} 分钟")
        print(f"成功: {self.stats['success']:,} ({self.stats['success']/len(tasks)*100:.1f}%)")
        print(f"失败: {self.stats['failed']:,}")
        print(f"星巴克总数: {self.stats['starbucks_total']:,}")
        print(f"麦当劳总数: {self.stats['mcdonalds_total']:,}")
        print(f"平均每个房源: 星巴克 {self.stats['starbucks_total']/self.stats['success']:.2f}, "
              f"麦当劳 {self.stats['mcdonalds_total']/self.stats['success']:.2f}")
        print(f"\n✓ 结果已保存: {output_file}")
        print(f"{'='*60}\n")

    def _save_progress(self, progress_file: Path, processed_indices: list, total: int):
        """保存进度"""
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_indices': processed_indices,
                'total': total,
                'timestamp': time.time()
            }, f)

    def _load_progress(self, progress_file: Path) -> set:
        """加载已处理的行索引"""
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_indices', []))
        except Exception:
            return set()
