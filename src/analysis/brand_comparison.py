import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict


class BrandComparator:
    """品牌租房数据统计分析器"""

    # 城市代码映射
    CITY_MAPPING = {
        'bj': '北京',
        'sh': '上海',
        'sz': '深圳',
        'gz': '广州',
        'hz': '杭州'
    }

    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化品牌对比分析器

        Args:
            data_dir: 数据文件目录
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        self.df_all = None

    def load_data(self, city_codes: Optional[List[str]] = None) -> pd.DataFrame:
        """
        加载城市租房数据

        Args:
            city_codes: 城市代码列表，默认加载所有城市

        Returns:
            合并后的 DataFrame
        """
        if city_codes is None:
            city_codes = list(self.CITY_MAPPING.keys())

        dfs = []
        for code in city_codes:
            file_path = self.data_dir / f'{code}_rental_clean.csv'
            if not file_path.exists():
                if self.verbose:
                    print(f"⚠️  警告: 文件不存在 {file_path}")
                continue

            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df['城市'] = self.CITY_MAPPING[code]
            dfs.append(df)

            if self.verbose:
                print(f"✓ 读取 {self.CITY_MAPPING[code]} 数据: {len(df):,} 行")

        if not dfs:
            raise FileNotFoundError("没有找到任何数据文件")

        self.df_all = pd.concat(dfs, ignore_index=True)

        if self.verbose:
            print(f"\n合计: {len(self.df_all):,} 行数据，{len(city_codes)} 个城市")

        return self.df_all

    def calculate_statistics(self) -> pd.DataFrame:
        """
        计算城市-品牌分组统计

        Returns:
            DataFrame（城市、品牌、房源数量、市占率）
        """
        if self.df_all is None:
            raise ValueError("请先调用 load_data() 加载数据")

        if self.verbose:
            print("\n" + "="*80)
            print("正在计算品牌分布统计...")
            print("="*80)

        # 填充缺失值
        df = self.df_all.copy()
        df['品牌'] = df['品牌'].fillna('未知品牌')

        # 按城市和品牌分组统计
        summary = df.groupby(['城市', '品牌']).size().reset_index(name='房源数量')

        # 计算每个城市的总房源数
        city_totals = df.groupby('城市').size().reset_index(name='城市总数')
        summary = pd.merge(summary, city_totals, on='城市')

        # 计算市占率
        summary['市占率'] = (summary['房源数量'] / summary['城市总数'] * 100).round(1)

        # 排序：按城市和房源数量降序
        summary = summary.sort_values(['城市', '房源数量'], ascending=[True, False])

        if self.verbose:
            print(f"✓ 统计完成: {len(summary)} 个城市-品牌组合")

        return summary

    def print_statistics(self, stats: pd.DataFrame):
        """
        打印格式化的统计表格

        Args:
            stats: 统计结果 DataFrame
        """
        print("\n" + "="*80)
        print("品牌分布统计")
        print("="*80)

        for city in self.CITY_MAPPING.values():
            if city not in stats['城市'].values:
                continue

            print(f"\n【{city}】")
            city_stats = stats[stats['城市'] == city].copy()

            # 打印表格
            for _, row in city_stats.iterrows():
                print(f"  {row['品牌']}: {row['房源数量']:,} 套 ({row['市占率']:.1f}%)")

            # 找出市占率最高的品牌
            max_brand = city_stats.iloc[0]
            print(f"\n  💡 {city} 主导品牌: {max_brand['品牌']} ({max_brand['市占率']:.1f}%)")

    def get_pivot_table(self, stats: pd.DataFrame) -> pd.DataFrame:
        """
        生成城市 × 品牌透视表（房源数量）

        Args:
            stats: 统计结果 DataFrame

        Returns:
            透视表 DataFrame
        """
        pivot = stats.pivot(
            index='城市',
            columns='品牌',
            values='房源数量'
        ).fillna(0)

        # 转换为整数
        pivot = pivot.astype(int)

        return pivot

    def get_pivot_table_pct(self, stats: pd.DataFrame) -> pd.DataFrame:
        """
        生成城市 × 品牌透视表（市占率）

        Args:
            stats: 统计结果 DataFrame

        Returns:
            透视表 DataFrame
        """
        pivot = stats.pivot(
            index='城市',
            columns='品牌',
            values='市占率'
        ).fillna(0)

        # 四舍五入
        pivot = pivot.round(1)

        return pivot


def analyze_brands(
    data_dir: str = 'data',
    output_dir: str = 'output/analysis',
    city_codes: Optional[List[str]] = None,
    show_plot: bool = True,
    save_plot: bool = True,
    save_stats: bool = True,
    verbose: bool = True
) -> tuple:
    """
    一键完整品牌分析（加载→统计→保存→可视化）

    Args:
        data_dir: 数据文件目录
        output_dir: 输出目录
        city_codes: 城市代码列表，默认全部
        show_plot: 是否显示图表
        save_plot: 是否保存图表
        save_stats: 是否保存统计表格
        verbose: 是否打印详细日志

    Returns:
        (df_all, stats): 原始数据和统计结果
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. 加载数据
    comparator = BrandComparator(data_dir=data_dir, verbose=verbose)
    df_all = comparator.load_data(city_codes=city_codes)

    # 2. 计算统计
    stats = comparator.calculate_statistics()

    # 3. 打印统计
    if verbose:
        comparator.print_statistics(stats)

    # 4. 保存统计表格
    if save_stats:
        stats_file = output_path / 'brand_statistics.csv'
        stats.to_csv(stats_file, index=False, encoding='utf-8-sig')

        # 保存透视表
        pivot = comparator.get_pivot_table(stats)
        pivot_file = output_path / 'brand_pivot.csv'
        pivot.to_csv(pivot_file, encoding='utf-8-sig')

        # 保存市占率透视表
        pivot_pct = comparator.get_pivot_table_pct(stats)
        pivot_pct_file = output_path / 'brand_pivot_pct.csv'
        pivot_pct.to_csv(pivot_pct_file, encoding='utf-8-sig')

        if verbose:
            print(f"\n✓ 统计表格已保存:")
            print(f"  {stats_file}")
            print(f"  {pivot_file}")
            print(f"  {pivot_pct_file}")

    # 5. 可视化
    if show_plot or save_plot:
        try:
            from .brand_visualizer import BrandVisualizer

            visualizer = BrandVisualizer(verbose=verbose)
            visualizer.plot_comparison(
                stats=stats,
                output_dir=output_dir,
                show=show_plot,
                save=save_plot
            )
        except ImportError:
            if verbose:
                print("\n⚠️  警告: 可视化模块未找到，跳过图表生成")

    return df_all, stats
