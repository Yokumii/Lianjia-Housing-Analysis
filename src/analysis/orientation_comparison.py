import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict


class OrientationComparator:
    """朝向租房数据统计分析器"""

    # 8 大朝向（固定顺序）
    MAJOR_ORIENTATIONS = ['东', '南', '西', '北', '东南', '东北', '西南', '西北']

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
        初始化朝向对比分析器

        Args:
            data_dir: 数据文件目录
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        self.df_all = None
        self.df_expanded = None

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

    def expand_orientations(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        将多朝向房源拆分为单朝向行

        例如："南 北" → 两行（朝向分别为 "南" 和 "北"，其他字段相同）

        Args:
            df: 输入 DataFrame，默认使用 self.df_all

        Returns:
            拆分后的 DataFrame
        """
        if df is None:
            df = self.df_all

        if df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        if self.verbose:
            print("\n" + "="*80)
            print("正在拆分多朝向房源...")
            print("="*80)

        expanded_rows = []

        for idx, row in df.iterrows():
            orient_str = row['朝向']

            # 过滤无效值
            if pd.isna(orient_str) or str(orient_str).strip() in ['未知', 'nan', '']:
                continue

            # 按空格分割朝向
            orientations = str(orient_str).split()

            # 对每个朝向创建一行
            for orient in orientations:
                orient = orient.strip()

                # 过滤无效朝向
                if not orient or orient in ['未知', 'nan']:
                    continue

                # 仅保留 8 大朝向
                if orient in self.MAJOR_ORIENTATIONS:
                    new_row = row.copy()
                    new_row['朝向'] = orient
                    expanded_rows.append(new_row)

        self.df_expanded = pd.DataFrame(expanded_rows)

        # 设置朝向为有序分类变量
        self.df_expanded['朝向'] = pd.Categorical(
            self.df_expanded['朝向'],
            categories=self.MAJOR_ORIENTATIONS,
            ordered=True
        )

        if self.verbose:
            print(f"✓ 拆分完成:")
            print(f"  原始房源数: {len(df):,}")
            print(f"  拆分后行数: {len(self.df_expanded):,}")
            print(f"  扩展倍数: {len(self.df_expanded) / len(df):.2f}x")
            print(f"\n  注意: 一个多朝向房源会产生多行，统计时房源量会大于实际房源数")

        return self.df_expanded

    def calculate_statistics(self) -> pd.DataFrame:
        """
        计算城市-朝向分组统计

        Returns:
            MultiIndex DataFrame（城市 × 朝向）
        """
        if self.df_expanded is None:
            raise ValueError("请先调用 expand_orientations() 拆分数据")

        if self.verbose:
            print("\n" + "="*80)
            print("正在计算统计指标...")
            print("="*80)

        # 按城市和朝向分组统计
        stats = self.df_expanded.groupby(['城市', '朝向']).agg({
            '单位租金': ['mean', 'max', 'min', 'median', 'count']
        })

        # 重命名列
        column_mapping = {
            'mean': '均价',
            'max': '最高价',
            'min': '最低价',
            'median': '中位数',
            'count': '房源量'
        }
        stats = stats.rename(columns=column_mapping, level=1)

        # 展平列名
        stats.columns = [f'单位租金_{col}' if col != '房源量' else col
                        for _, col in stats.columns]

        # 四舍五入
        for col in stats.columns:
            if col != '房源量':
                stats[col] = stats[col].round(1)

        if self.verbose:
            print(f"✓ 统计完成: {len(stats)} 个城市-朝向组合")

        return stats

    def print_statistics(self, stats: pd.DataFrame):
        """
        打印格式化的统计表格

        Args:
            stats: 统计结果 DataFrame
        """
        print("\n" + "="*80)
        print("朝向租金统计（单位租金，元/㎡/月）")
        print("="*80)

        for city in self.CITY_MAPPING.values():
            if city not in stats.index:
                continue

            print(f"\n【{city}】")
            city_stats = stats.loc[city]

            # 按朝向排序（使用 MAJOR_ORIENTATIONS 顺序）
            city_stats = city_stats.reindex(
                [o for o in self.MAJOR_ORIENTATIONS if o in city_stats.index]
            )

            print(city_stats.to_string())

            # 找出最贵和最便宜的朝向
            max_orient = city_stats['单位租金_均价'].idxmax()
            min_orient = city_stats['单位租金_均价'].idxmin()
            max_price = city_stats.loc[max_orient, '单位租金_均价']
            min_price = city_stats.loc[min_orient, '单位租金_均价']

            print(f"\n  💡 {city} 朝向洞察:")
            print(f"     最贵朝向: {max_orient} ({max_price:.1f} 元/㎡/月)")
            print(f"     最便宜朝向: {min_orient} ({min_price:.1f} 元/㎡/月)")
            print(f"     价格差: {max_price - min_price:.1f} 元/㎡/月 ({(max_price / min_price - 1) * 100:.1f}%)")

    def get_pivot_table(self) -> pd.DataFrame:
        """
        生成城市 × 朝向透视表（单位租金均价）

        Returns:
            透视表 DataFrame
        """
        if self.df_expanded is None:
            raise ValueError("请先调用 expand_orientations() 拆分数据")

        pivot = self.df_expanded.pivot_table(
            values='单位租金',
            index='朝向',
            columns='城市',
            aggfunc='mean'
        )

        # 按朝向顺序排序
        pivot = pivot.reindex(
            [o for o in self.MAJOR_ORIENTATIONS if o in pivot.index]
        )

        # 四舍五入
        pivot = pivot.round(1)

        return pivot


def analyze_orientations(
    data_dir: str = 'data',
    output_dir: str = 'output/analysis',
    city_codes: Optional[List[str]] = None,
    show_plot: bool = True,
    save_plot: bool = True,
    save_stats: bool = True,
    verbose: bool = True
) -> tuple:
    """
    一键完整朝向分析（加载→拆分→统计→保存→可视化）

    Args:
        data_dir: 数据文件目录
        output_dir: 输出目录
        city_codes: 城市代码列表，默认全部
        show_plot: 是否显示图表
        save_plot: 是否保存图表
        save_stats: 是否保存统计表格
        verbose: 是否打印详细日志

    Returns:
        (df_expanded, stats): 拆分后数据和统计结果
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. 加载数据
    comparator = OrientationComparator(data_dir=data_dir, verbose=verbose)
    df_all = comparator.load_data(city_codes=city_codes)

    # 2. 拆分多朝向
    df_expanded = comparator.expand_orientations()

    # 3. 计算统计
    stats = comparator.calculate_statistics()

    # 4. 打印统计
    if verbose:
        comparator.print_statistics(stats)

    # 5. 保存统计表格
    if save_stats:
        stats_file = output_path / 'orientation_statistics.csv'
        stats.to_csv(stats_file, encoding='utf-8-sig')

        # 保存透视表
        pivot = comparator.get_pivot_table()
        pivot_file = output_path / 'orientation_pivot.csv'
        pivot.to_csv(pivot_file, encoding='utf-8-sig')

        if verbose:
            print(f"\n✓ 统计表格已保存:")
            print(f"  {stats_file}")
            print(f"  {pivot_file}")

    # 6. 可视化（需要单独实现 OrientationVisualizer）
    if show_plot or save_plot:
        try:
            from .orientation_visualizer import OrientationVisualizer

            visualizer = OrientationVisualizer(verbose=verbose)
            visualizer.plot_comparison(
                df_expanded=df_expanded,
                stats=stats,
                output_dir=output_dir,
                show=show_plot,
                save=save_plot
            )
        except ImportError:
            if verbose:
                print("\n⚠️  警告: 可视化模块未找到，跳过图表生成")

    return df_expanded, stats
