import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class LayoutComparator:
    """户型租房数据对比分析器"""
    
    # 城市代码到中文名称的映射
    CITY_NAMES = {
        'bj': '北京',
        'sh': '上海',
        'sz': '深圳',
        'gz': '广州',
        'hz': '杭州'
    }
    
    # 目标户型（已在预处理时过滤四居+）
    TARGET_LAYOUTS = ['一居', '两居', '三居']
    
    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化户型对比分析器
        
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
        加载城市租房数据并过滤目标户型
        
        Args:
            city_codes: 城市代码列表，默认加载所有城市
        
        Returns:
            合并后的数据框（仅包含目标户型）
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
                
                # 确保有城市和户型列
                city_name = self.CITY_NAMES.get(city_code, city_code)
                df['城市'] = city_name
                
                # 过滤目标户型
                if '户型' in df.columns:
                    df = df[df['户型'].isin(self.TARGET_LAYOUTS)]
                    
                    if not df.empty:
                        all_data.append(df)
                        
                        if self.verbose:
                            layout_dist = df['户型'].value_counts()
                            layout_str = ', '.join([f"{k}:{v}" for k, v in layout_dist.items()])
                            print(f"✓ 读取 {city_name:6} 数据: {len(df):>7,} 行 ({layout_str})")
                else:
                    if self.verbose:
                        print(f"⚠️  {city_name} 数据缺少\"户型\"字段")
            
            except Exception as e:
                if self.verbose:
                    print(f"❌ 读取失败 ({city_code}): {e}")
        
        if not all_data:
            raise FileNotFoundError("未找到任何城市数据文件或户型数据")
        
        self.df_all = pd.concat(all_data, ignore_index=True)
        
        # 设置户型为有序分类（确保图表中按一居→两居→三居排序）
        self.df_all['户型'] = pd.Categorical(
            self.df_all['户型'],
            categories=self.TARGET_LAYOUTS,
            ordered=True
        )
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"合计: {len(self.df_all):,} 行数据，{len(all_data)} 个城市")
            total_dist = self.df_all['户型'].value_counts()
            print(f"户型分布: {dict(total_dist)}")
            print(f"{'='*60}\n")
        
        return self.df_all
    
    def calculate_statistics(self) -> pd.DataFrame:
        """
        计算各城市、各户型的租金统计指标
        
        Returns:
            统计摘要数据框（MultiIndex: 城市-户型）
        """
        if self.df_all is None:
            raise ValueError("请先调用 load_data() 加载数据")
        
        # 按城市和户型分组聚合
        stats = self.df_all.groupby(['城市', '户型']).agg({
            '租金': ['mean', 'max', 'min', 'median', 'count'],
            '单位租金': ['mean', 'max', 'min', 'median']
        }).round(1)
        
        # 重命名列索引为中文
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
        
        print("\n" + "="*100)
        print("📊 五城租房市场：分户型详细统计报告")
        print("="*100)
        
        # 配置 pandas 显示选项
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1500)
        pd.set_option('display.unicode.east_asian_width', True)
        
        print(stats)
        print("="*100)
        
        # 打印关键洞察
        print("\n💡 关键发现:")
        
        # 各户型平均租金
        for layout in self.TARGET_LAYOUTS:
            avg_rents = []
            for city in stats.index.get_level_values(0).unique():
                if (city, layout) in stats.index:
                    avg_rents.append((city, stats.loc[(city, layout), ('租金', '均价')]))
            
            if avg_rents:
                avg_rents.sort(key=lambda x: x[1], reverse=True)
                print(f"\n  【{layout}】租金均价排名:")
                for i, (city, rent) in enumerate(avg_rents[:3], 1):
                    print(f"    {i}. {city}: {rent:.1f} 元/月")
        
        print()
    
    def get_pivot_table(
        self,
        metric: str = '租金',
        stat: str = '均价'
    ) -> pd.DataFrame:
        """
        生成透视表（城市 x 户型）
        
        Args:
            metric: 指标名称（'租金' 或 '单位租金'）
            stat: 统计量名称（'均价', '最高价', '最低价', '中位数'）
        
        Returns:
            透视表 DataFrame（行=城市，列=户型）
        """
        if self.stats_summary is None:
            raise ValueError("请先调用 calculate_statistics() 计算统计数据")
        
        # 从 MultiIndex 中提取数据
        pivot_data = []
        for city in self.stats_summary.index.get_level_values(0).unique():
            row = {'城市': city}
            for layout in self.TARGET_LAYOUTS:
                if (city, layout) in self.stats_summary.index:
                    value = self.stats_summary.loc[(city, layout), (metric, stat)]
                    row[layout] = value
                else:
                    row[layout] = None
            pivot_data.append(row)
        
        pivot_df = pd.DataFrame(pivot_data).set_index('城市')
        return pivot_df


def analyze_layouts(
    data_dir: str = 'data',
    output_dir: str = 'output/analysis',
    city_codes: Optional[List[str]] = None,
    show_plot: bool = True,
    save_plot: bool = True,
    save_stats: bool = True,
    verbose: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    分析户型租房数据（统计 + 可视化）
    
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
    from .layout_visualizer import LayoutVisualizer
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 数据加载与统计
    comparator = LayoutComparator(data_dir=data_dir, verbose=verbose)
    df_all = comparator.load_data(city_codes=city_codes)
    stats = comparator.calculate_statistics()
    comparator.print_statistics()
    
    # 保存统计表格
    if save_stats:
        stats_file = output_path / 'layout_statistics.csv'
        stats.to_csv(stats_file, encoding='utf-8-sig')
        
        # 同时保存透视表（更易读）
        pivot_rent = comparator.get_pivot_table(metric='租金', stat='均价')
        pivot_unit = comparator.get_pivot_table(metric='单位租金', stat='均价')
        
        pivot_file = output_path / 'layout_pivot.csv'
        with open(pivot_file, 'w', encoding='utf-8-sig') as f:
            f.write("# 租金均价（元/月）\n")
            pivot_rent.to_csv(f)
            f.write("\n# 单位租金均价（元/㎡/月）\n")
            pivot_unit.to_csv(f)
        
        if verbose:
            print(f"📄 统计表格已保存: {stats_file}")
            print(f"📄 透视表已保存: {pivot_file}")
    
    # 2. 可视化
    visualizer = LayoutVisualizer(verbose=verbose)
    visualizer.plot_layout_comparison(
        df=df_all,
        stats=stats,
        output_dir=output_dir,
        show=show_plot,
        save=save_plot
    )
    
    return df_all, stats
