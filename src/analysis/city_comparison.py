import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CityComparator:
    """城市租房数据对比分析器"""
    
    # 城市代码到中文名称的映射
    CITY_NAMES = {
        'bj': '北京',
        'sh': '上海',
        'sz': '深圳',
        'gz': '广州',
        'hz': '杭州'
    }
    
    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化城市对比分析器
        
        Args:
            data_dir: 数据文件目录
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        self.df_all = None
        self.stats_summary = None
    
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
                # 确保有城市列（使用中文名）
                city_name = self.CITY_NAMES.get(city_code, city_code)
                df['城市'] = city_name
                all_data.append(df)
                
                if self.verbose:
                    print(f"✓ 读取 {city_name:6} 数据: {len(df):>7,} 行")
            
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
    
    def calculate_statistics(self) -> pd.DataFrame:
        """
        计算各城市租金统计指标
        
        Returns:
            统计摘要数据框（MultiIndex）
        """
        if self.df_all is None:
            raise ValueError("请先调用 load_data() 加载数据")
        
        # 聚合计算
        stats = self.df_all.groupby('城市').agg({
            '租金': ['mean', 'max', 'min', 'median', 'count'],
            '单位租金': ['mean', 'max', 'min', 'median']
        }).round(1)

        # 重命名列索引为中文（使用 rename 替代 set_levels）
        column_mapping = {
            'mean': '均价',
            'max': '最高价',
            'min': '最低价',
            'median': '中位数',
            'count': '数量'
        }
        stats = stats.rename(columns=column_mapping, level=1)
        
        self.stats_summary = stats
        return stats
    
    def print_statistics(self, stats: Optional[pd.DataFrame] = None):
        """
        打印统计表格
        
        Args:
            stats: 统计摘要数据框，默认使用 self.stats_summary
        """
        if stats is None:
            stats = self.stats_summary
        
        if stats is None:
            raise ValueError("请先调用 calculate_statistics() 计算统计数据")
        
        print("\n" + "="*80)
        print("📊 五城租房市场：租金与单价统计对比表")
        print("="*80)
        
        # 配置 pandas 显示选项
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.unicode.east_asian_width', True)
        
        print(stats)
        print("="*80)
        
        # 打印关键洞察
        print("\n💡 关键发现:")
        
        # 租金最高/最低城市
        avg_rent = stats['租金']['均价']
        print(f"  • 租金均价最高: {avg_rent.idxmax()} ({avg_rent.max():.1f} 元/月)")
        print(f"  • 租金均价最低: {avg_rent.idxmin()} ({avg_rent.min():.1f} 元/月)")
        
        # 单位租金最高/最低城市
        avg_unit = stats['单位租金']['均价']
        print(f"  • 单价均价最高: {avg_unit.idxmax()} ({avg_unit.max():.1f} 元/㎡/月)")
        print(f"  • 单价均价最低: {avg_unit.idxmin()} ({avg_unit.min():.1f} 元/㎡/月)")
        
        print()
    
    def get_statistics_dict(self, stats: Optional[pd.DataFrame] = None) -> Dict:
        """
        将统计数据转换为字典格式
        
        Args:
            stats: 统计摘要数据框
        
        Returns:
            嵌套字典 {city: {metric: {stat: value}}}
        """
        if stats is None:
            stats = self.stats_summary
        
        result = {}
        for city in stats.index:
            result[city] = {
                '租金': {
                    '均价': float(stats.loc[city, ('租金', '均价')]),
                    '最高价': float(stats.loc[city, ('租金', '最高价')]),
                    '最低价': float(stats.loc[city, ('租金', '最低价')]),
                    '中位数': float(stats.loc[city, ('租金', '中位数')]),
                    '数量': int(stats.loc[city, ('租金', '数量')]),
                },
                '单位租金': {
                    '均价': float(stats.loc[city, ('单位租金', '均价')]),
                    '最高价': float(stats.loc[city, ('单位租金', '最高价')]),
                    '最低价': float(stats.loc[city, ('单位租金', '最低价')]),
                    '中位数': float(stats.loc[city, ('单位租金', '中位数')]),
                }
            }
        
        return result


def analyze_cities(
    data_dir: str = 'data',
    output_dir: str = 'output/analysis',
    city_codes: Optional[List[str]] = None,
    show_plot: bool = True,
    save_plot: bool = True,
    save_stats: bool = True,
    verbose: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    分析城市租房数据（统计 + 可视化）
    
    Args:
        data_dir: 数据文件目录
        output_dir: 输出目录
        city_codes: 城市代码列表（默认所有城市）
        show_plot: 是否显示图表
        save_plot: 是否保存图表
        save_stats: 是否保存统计表格
        verbose: 是否打印详细日志
    
    Returns:
        (原始数据框, 统计摘要数据框)
    """
    from .visualizer import CityVisualizer
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 数据加载与统计
    comparator = CityComparator(data_dir=data_dir, verbose=verbose)
    df_all = comparator.load_data(city_codes=city_codes)
    stats = comparator.calculate_statistics()
    comparator.print_statistics()
    
    # 保存统计表格
    if save_stats:
        stats_file = output_path / 'city_statistics.csv'
        stats.to_csv(stats_file, encoding='utf-8-sig')
        if verbose:
            print(f"📄 统计表格已保存: {stats_file}")
    
    # 2. 可视化
    visualizer = CityVisualizer(verbose=verbose)
    visualizer.plot_comparison(
        df=df_all,
        stats=stats,
        output_dir=output_dir,
        show=show_plot,
        save=save_plot
    )
    
    return df_all, stats
