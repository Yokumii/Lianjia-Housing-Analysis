import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BlockComparator:
    """板块租房数据对比分析器"""
    
    # 城市代码到中文名称的映射
    CITY_NAMES = {
        'bj': '北京',
        'sh': '上海',
        'sz': '深圳',
        'gz': '广州',
        'hz': '杭州'
    }
    
    # 最小房源数阈值（过滤小样本板块）
    MIN_LISTING_COUNT = 20
    
    def __init__(
        self,
        data_dir: str = 'data',
        min_listing_count: int = 20,
        verbose: bool = True
    ):
        """
        初始化板块对比分析器
        
        Args:
            data_dir: 数据文件目录
            min_listing_count: 最小房源数阈值（过滤小样本板块）
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.min_listing_count = min_listing_count
        self.verbose = verbose
        self.df_all = None
        self.city_stats = {}  # 各城市板块统计结果
    
    def load_data(self, city_codes: Optional[List[str]] = None) -> pd.DataFrame:
        """
        加载城市租房数据
        
        Args:
            city_codes: 城市代码列表，默认加载所有城市
        
        Returns:
            合并后的数据框
        """
        if city_codes is None:
            city_codes = list(self.CITY_NAMES.keys())
        
        all_data = []
        
        for city_code in city_codes:
            file_path = self.data_dir / f"{city_code}_rental_clean.csv"
            
            if not file_path.exists():
                if self.verbose:
                    print(f"⚠️  未找到 {city_code} 的数据文件: {file_path}")
                continue
            
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                # 确保有城市和板块列
                city_name = self.CITY_NAMES.get(city_code, city_code)
                df['城市'] = city_name
                
                if '板块' not in df.columns:
                    if self.verbose:
                        print(f"⚠️  {city_name} 数据缺少\"板块\"字段")
                    continue
                
                all_data.append(df)
                
                if self.verbose:
                    unique_blocks = df['板块'].nunique()
                    print(f"✓ 读取 {city_name:6} 数据: {len(df):>7,} 行，{unique_blocks:>4} 个板块")
            
            except Exception as e:
                if self.verbose:
                    print(f"❌ 读取失败 ({city_code}): {e}")
        
        if not all_data:
            raise FileNotFoundError("未找到任何城市数据文件")
        
        self.df_all = pd.concat(all_data, ignore_index=True)
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"合计: {len(self.df_all):,} 行数据，{len(all_data)} 个城市")
            print(f"{'='*60}\n")
        
        return self.df_all
    
    def analyze_city_blocks(
        self,
        city_name: str,
        top_n: int = 15
    ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        分析单个城市的板块数据
        
        Args:
            city_name: 城市名称（中文）
            top_n: 返回 Top N 最贵/最便宜板块
        
        Returns:
            (最贵板块 DataFrame, 最便宜板块 DataFrame)
        """
        if self.df_all is None:
            raise ValueError("请先调用 load_data() 加载数据")
        
        # 过滤该城市数据
        city_df = self.df_all[self.df_all['城市'] == city_name].copy()
        
        if city_df.empty:
            if self.verbose:
                print(f"⚠️  未找到 {city_name} 的数据")
            return None, None
        
        # 过滤：去除无效板块名
        city_df = city_df[~city_df['板块'].isin(['未知', 'NaN'])]
        city_df = city_df[city_df['板块'].notna()]
        
        # 聚合：计算每个板块的统计指标
        block_stats = city_df.groupby('板块').agg({
            '单位租金': 'mean',      # 单价均价
            '租金': ['mean', 'median'],  # 总价均价和中位数
            '链接': 'count'          # 房源数量
        })
        
        # 重命名列
        block_stats.columns = ['单价均价', '总价均价', '总价中位数', '房源量']
        block_stats = block_stats.round(1)
        
        # 筛选：只看活跃板块（房源量 >= 阈值）
        active_blocks = block_stats[block_stats['房源量'] >= self.min_listing_count]
        
        if active_blocks.empty:
            if self.verbose:
                print(f"  ⚠️  {city_name} 没有满足房源量 >= {self.min_listing_count} 的板块")
            return None, None
        
        # 排序：取出最贵和最便宜
        top_expensive = active_blocks.sort_values('单价均价', ascending=False).head(top_n)
        top_cheap = active_blocks.sort_values('单价均价', ascending=True).head(top_n)
        
        # 保存统计结果
        self.city_stats[city_name] = {
            'all_blocks': active_blocks,
            'top_expensive': top_expensive,
            'top_cheap': top_cheap
        }
        
        if self.verbose:
            print(f"🔍 分析 {city_name} 板块数据:")
            print(f"  总板块数: {len(block_stats)}，活跃板块数: {len(active_blocks)}")
            print(f"  💎 最贵板块 Top 3: {top_expensive.index[:3].tolist()}")
            print(f"  🥬 最亲民板块 Top 3: {top_cheap.index[:3].tolist()}")
        
        return top_expensive, top_cheap
    
    def analyze_all_cities(self, top_n: int = 15) -> Dict[str, Dict]:
        """
        分析所有已加载城市的板块数据
        
        Args:
            top_n: 返回 Top N 最贵/最便宜板块
        
        Returns:
            城市统计结果字典
        """
        if self.df_all is None:
            raise ValueError("请先调用 load_data() 加载数据")
        
        available_cities = self.df_all['城市'].unique()
        
        for city in available_cities:
            self.analyze_city_blocks(city, top_n=top_n)
            if self.verbose:
                print()  # 添加空行分隔
        
        return self.city_stats
    
    def get_summary_table(self, city_name: str) -> pd.DataFrame:
        """
        获取城市板块汇总表（Top 10 最贵 + Top 10 最便宜）
        
        Args:
            city_name: 城市名称
        
        Returns:
            汇总表 DataFrame
        """
        if city_name not in self.city_stats:
            raise ValueError(f"请先对 {city_name} 调用 analyze_city_blocks()")
        
        stats = self.city_stats[city_name]
        top_exp = stats['top_expensive'].head(10).copy()
        top_cheap = stats['top_cheap'].head(10).copy()
        
        # 添加标签列
        top_exp['类型'] = '最贵'
        top_cheap['类型'] = '最亲民'
        
        # 合并
        summary = pd.concat([top_exp, top_cheap])
        return summary


def analyze_blocks(
    data_dir: str = 'data',
    output_dir: str = 'output/analysis',
    city_codes: Optional[List[str]] = None,
    top_n: int = 15,
    min_listing_count: int = 20,
    show_plot: bool = True,
    save_plot: bool = True,
    save_stats: bool = True,
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Dict]]:
    """
    分析板块租房数据（统计 + 可视化）
    
    Args:
        data_dir: 数据文件目录
        output_dir: 输出目录
        city_codes: 城市代码列表（默认所有城市）
        top_n: Top N 最贵/最便宜板块
        min_listing_count: 最小房源数阈值
        show_plot: 是否显示图表
        save_plot: 是否保存图表
        save_stats: 是否保存统计表格
        verbose: 是否打印详细日志
    
    Returns:
        (原始数据框, 城市统计结果字典)
    """
    from .block_visualizer import BlockVisualizer
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 数据加载与统计
    comparator = BlockComparator(
        data_dir=data_dir,
        min_listing_count=min_listing_count,
        verbose=verbose
    )
    df_all = comparator.load_data(city_codes=city_codes)
    city_stats = comparator.analyze_all_cities(top_n=top_n)
    
    # 保存统计表格
    if save_stats:
        for city_name in city_stats.keys():
            summary = comparator.get_summary_table(city_name)
            stats_file = output_path / f'block_stats_{city_name}.csv'
            summary.to_csv(stats_file, encoding='utf-8-sig')
            
            if verbose:
                print(f"📄 统计表格已保存: {stats_file}")
    
    # 2. 可视化
    visualizer = BlockVisualizer(verbose=verbose)
    
    for city_name, stats in city_stats.items():
        if stats['top_expensive'] is not None:
            visualizer.plot_city_blocks(
                city_name=city_name,
                top_expensive=stats['top_expensive'],
                top_cheap=stats['top_cheap'],
                output_dir=output_dir,
                show=show_plot,
                save=save_plot
            )
    
    return df_all, city_stats
