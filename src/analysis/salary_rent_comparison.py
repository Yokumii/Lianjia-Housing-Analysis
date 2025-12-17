import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict


class SalaryRentAnalyzer:
    """工资-租金关系分析器"""

    # 城市代码映射
    CITY_MAPPING = {
        'bj': '北京',
        'sh': '上海',
        'sz': '深圳',
        'gz': '广州',
        'hz': '杭州'
    }

    # 2024年城市工资数据（来源：各市统计局）
    # 格式：{城市: (非私营年薪, 私营年薪, 人均可支配收入)}
    SALARY_DATA = {
        '北京': (224608, 106905, 92464),
        '上海': (229337, 111347, 93095),
        '广州': (159312, 82907, 83436),
        '深圳': (174478, 95217, 81123),
        '杭州': (162774, 92054, 83356)
    }

    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化工资-租金分析器

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
        计算工资-租金关系统计

        Returns:
            DataFrame（城市、租金统计、工资数据、衍生指标）
        """
        if self.df_all is None:
            raise ValueError("请先调用 load_data() 加载数据")

        if self.verbose:
            print("\n" + "="*80)
            print("正在计算工资-租金关系指标...")
            print("="*80)

        # 1. 计算各城市租金统计（使用中位数更能代表普通人）
        rent_stats = self.df_all.groupby('城市').agg({
            '单位租金': ['mean', 'median', 'std'],
            '租金': ['mean', 'median']
        }).reset_index()

        # 展平列名
        rent_stats.columns = [
            '城市',
            '单位租金均价', '单位租金中位数', '单位租金标准差',
            '总租金均价', '总租金中位数'
        ]

        # 四舍五入
        for col in rent_stats.columns:
            if col != '城市':
                rent_stats[col] = rent_stats[col].round(1)

        # 2. 添加工资数据
        salary_list = []
        for city, (public_salary, private_salary, disposable_income) in self.SALARY_DATA.items():
            salary_list.append({
                '城市': city,
                '非私营年薪': public_salary,
                '私营年薪': private_salary,
                '人均可支配收入': disposable_income,
                '非私营月薪': round(public_salary / 12, 0),
                '私营月薪': round(private_salary / 12, 0),
                '月可支配收入': round(disposable_income / 12, 0)
            })
        salary_df = pd.DataFrame(salary_list)

        # 3. 合并数据
        merged = pd.merge(rent_stats, salary_df, on='城市')

        # 4. 计算衍生指标
        # 指标A: 30% 私营月薪能租多少平米？（租房自由度）
        merged['可租面积_私营30%'] = (
            merged['私营月薪'] * 0.3 / merged['单位租金中位数']
        ).round(1)

        # 指标B: 30% 可支配收入能租多少平米？（实际租房能力）
        merged['可租面积_可支配30%'] = (
            merged['月可支配收入'] * 0.3 / merged['单位租金中位数']
        ).round(1)

        # 指标C: 租30平米需要花多少比例的私营月薪？（生存压力）
        merged['30平米房租占私营月薪%'] = (
            (merged['单位租金中位数'] * 30) / merged['私营月薪'] * 100
        ).round(1)

        # 指标D: 租30平米需要花多少比例的可支配收入？（实际压力）
        merged['30平米房租占可支配收入%'] = (
            (merged['单位租金中位数'] * 30) / merged['月可支配收入'] * 100
        ).round(1)

        # 指标E: 租房性价比（工资/租金比，数值越大越划算）
        merged['租房性价比_私营'] = (
            merged['私营月薪'] / merged['单位租金中位数']
        ).round(1)

        # 指标F: 租金收入比（租金占收入比，数值越小越轻松）
        merged['租金收入比_总租金/私营'] = (
            merged['总租金中位数'] / merged['私营月薪'] * 100
        ).round(1)

        if self.verbose:
            print(f"✓ 统计完成: {len(merged)} 个城市")

        return merged

    def print_statistics(self, stats: pd.DataFrame):
        """
        打印格式化的统计表格

        Args:
            stats: 统计结果 DataFrame
        """
        print("\n" + "="*80)
        print("工资-租金关系统计")
        print("="*80)

        # 打印核心指标
        core_cols = [
            '城市',
            '单位租金中位数',
            '私营月薪',
            '月可支配收入',
            '可租面积_私营30%',
            '30平米房租占私营月薪%',
            '租房性价比_私营'
        ]

        print("\n【核心指标】")
        print(stats[core_cols].to_string(index=False))

        # 打印洞察
        print("\n" + "="*80)
        print("关键洞察")
        print("="*80)

        # 租房自由度排名
        best_afford = stats.loc[stats['可租面积_私营30%'].idxmax()]
        worst_afford = stats.loc[stats['可租面积_私营30%'].idxmin()]

        print(f"\n💡 租房自由度:")
        print(f"   最高: {best_afford['城市']} ({best_afford['可租面积_私营30%']:.1f} ㎡)")
        print(f"   最低: {worst_afford['城市']} ({worst_afford['可租面积_私营30%']:.1f} ㎡)")

        # 租房压力排名
        best_pressure = stats.loc[stats['30平米房租占私营月薪%'].idxmin()]
        worst_pressure = stats.loc[stats['30平米房租占私营月薪%'].idxmax()]

        print(f"\n💡 租房压力:")
        print(f"   最低: {best_pressure['城市']} ({best_pressure['30平米房租占私营月薪%']:.1f}%)")
        print(f"   最高: {worst_pressure['城市']} ({worst_pressure['30平米房租占私营月薪%']:.1f}%)")

        # 租房性价比排名
        best_value = stats.loc[stats['租房性价比_私营'].idxmax()]
        worst_value = stats.loc[stats['租房性价比_私营'].idxmin()]

        print(f"\n💡 租房性价比:")
        print(f"   最高: {best_value['城市']} ({best_value['租房性价比_私营']:.1f})")
        print(f"   最低: {worst_value['城市']} ({worst_value['租房性价比_私营']:.1f})")


def analyze_salary_rent(
    data_dir: str = 'data',
    output_dir: str = 'output/analysis',
    city_codes: Optional[List[str]] = None,
    show_plot: bool = True,
    save_plot: bool = True,
    save_stats: bool = True,
    verbose: bool = True
) -> tuple:
    """
    一键完整工资-租金分析（加载→统计→保存→可视化）

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
    analyzer = SalaryRentAnalyzer(data_dir=data_dir, verbose=verbose)
    df_all = analyzer.load_data(city_codes=city_codes)

    # 2. 计算统计
    stats = analyzer.calculate_statistics()

    # 3. 打印统计
    if verbose:
        analyzer.print_statistics(stats)

    # 4. 保存统计表格
    if save_stats:
        stats_file = output_path / 'salary_rent_statistics.csv'
        stats.to_csv(stats_file, index=False, encoding='utf-8-sig')

        if verbose:
            print(f"\n✓ 统计表格已保存: {stats_file}")

    # 5. 可视化
    if show_plot or save_plot:
        try:
            from .salary_rent_visualizer import SalaryRentVisualizer

            visualizer = SalaryRentVisualizer(verbose=verbose)
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
