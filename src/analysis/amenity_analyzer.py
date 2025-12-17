import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Optional, Tuple
from pathlib import Path


class AmenityAnalyzer:
    """配套设施溢价分析器"""

    # 城市代码到名称的映射
    CITY_NAMES = {
        'bj': '北京',
        'sh': '上海',
        'gz': '广州',
        'sz': '深圳',
        'hz': '杭州'
    }

    def __init__(self, verbose: bool = True):
        """
        初始化分析器

        Args:
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
        self.df = None
        self.city_code = None
        self.city_name = None

    def load_data(self, city_code: str, data_file: Optional[str] = None):
        """
        加载数据

        Args:
            city_code: 城市代码
            data_file: 数据文件路径（默认: data/{city}_rental_with_amenities.csv）
        """
        self.city_code = city_code
        self.city_name = self.CITY_NAMES.get(city_code, city_code.upper())

        if data_file is None:
            data_file = f'data/{city_code}_rental_with_amenities.csv'

        self.df = pd.read_csv(data_file)

        if self.verbose:
            print(f"✓ 加载 {self.city_name} 数据: {len(self.df):,} 行")

    def add_labels(self) -> pd.DataFrame:
        """
        添加标签列

        Returns:
            添加标签后的DataFrame
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 检查必需列
        required_cols = ['星巴克数量', '麦当劳数量', '单位租金']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"缺少必需列: {missing_cols}")

        # 添加二元标签（有/无）
        self.df['有星巴克'] = (self.df['星巴克数量'] > 0).astype(int)
        self.df['有麦当劳'] = (self.df['麦当劳数量'] > 0).astype(int)

        # 添加分级标签
        self.df['星巴克密度'] = pd.cut(
            self.df['星巴克数量'],
            bins=[-1, 0, 1, 3, 999],
            labels=['无', '低(1)', '中(2-3)', '高(4+)']
        )

        self.df['麦当劳密度'] = pd.cut(
            self.df['麦当劳数量'],
            bins=[-1, 0, 1, 2, 999],
            labels=['无', '低(1)', '中(2)', '高(3+)']
        )

        # 添加综合配套标签
        self.df['配套总数'] = self.df['星巴克数量'] + self.df['麦当劳数量']
        self.df['配套丰富度'] = pd.cut(
            self.df['配套总数'],
            bins=[-1, 0, 1, 3, 999],
            labels=['无配套', '低', '中', '高']
        )

        if self.verbose:
            print(f"\n✓ 标签化完成")
            print(f"  有星巴克: {self.df['有星巴克'].sum():,} ({self.df['有星巴克'].sum()/len(self.df)*100:.1f}%)")
            print(f"  有麦当劳: {self.df['有麦当劳'].sum():,} ({self.df['有麦当劳'].sum()/len(self.df)*100:.1f}%)")

        return self.df

    def ttest_analysis(self, amenity_type: str = 'starbucks') -> Dict:
        """
        t检验：比较有/无配套设施的单位租金差异

        Args:
            amenity_type: 配套类型（'starbucks' 或 'mcdonalds'）

        Returns:
            包含t检验结果的字典
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 确定标签列
        if amenity_type == 'starbucks':
            label_col = '有星巴克'
            name = '星巴克'
        elif amenity_type == 'mcdonalds':
            label_col = '有麦当劳'
            name = '麦当劳'
        else:
            raise ValueError("amenity_type 必须是 'starbucks' 或 'mcdonalds'")

        # 分组数据
        df_clean = self.df.dropna(subset=['单位租金', label_col])
        group_with = df_clean[df_clean[label_col] == 1]['单位租金']
        group_without = df_clean[df_clean[label_col] == 0]['单位租金']

        # t检验
        t_stat, p_value = stats.ttest_ind(group_with, group_without, equal_var=False)

        # 计算效应量（Cohen's d）
        mean_with = group_with.mean()
        mean_without = group_without.mean()
        pooled_std = np.sqrt((group_with.std()**2 + group_without.std()**2) / 2)
        cohens_d = (mean_with - mean_without) / pooled_std

        # 计算溢价
        premium = mean_with - mean_without
        premium_pct = (premium / mean_without) * 100

        results = {
            'amenity_type': name,
            'with_amenity': {
                'count': len(group_with),
                'mean': mean_with,
                'median': group_with.median(),
                'std': group_with.std()
            },
            'without_amenity': {
                'count': len(group_without),
                'mean': mean_without,
                'median': group_without.median(),
                'std': group_without.std()
            },
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'premium': premium,
            'premium_pct': premium_pct,
            'significant': p_value < 0.05
        }

        if self.verbose:
            self._print_ttest_results(results)

        return results

    def correlation_analysis(self, amenity_type: str = 'starbucks') -> Dict:
        """
        相关性分析：配套数量 vs 单位租金

        Args:
            amenity_type: 配套类型（'starbucks' 或 'mcdonalds' 或 'total'）

        Returns:
            包含相关性分析结果的字典
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 确定数量列
        if amenity_type == 'starbucks':
            count_col = '星巴克数量'
            name = '星巴克'
        elif amenity_type == 'mcdonalds':
            count_col = '麦当劳数量'
            name = '麦当劳'
        elif amenity_type == 'total':
            count_col = '配套总数'
            name = '配套总数'
        else:
            raise ValueError("amenity_type 必须是 'starbucks', 'mcdonalds' 或 'total'")

        # 清洗数据
        df_clean = self.df.dropna(subset=['单位租金', count_col])

        # Pearson相关系数
        pearson_r, pearson_p = stats.pearsonr(
            df_clean[count_col],
            df_clean['单位租金']
        )

        # Spearman相关系数（秩相关，对异常值更robust）
        spearman_r, spearman_p = stats.spearmanr(
            df_clean[count_col],
            df_clean['单位租金']
        )

        # 按数量分组统计
        grouped = df_clean.groupby(count_col)['单位租金'].agg(['count', 'mean', 'median', 'std'])

        results = {
            'amenity_type': name,
            'sample_size': len(df_clean),
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'grouped_stats': grouped.to_dict('index')
        }

        if self.verbose:
            self._print_correlation_results(results)

        return results

    def density_analysis(self) -> pd.DataFrame:
        """
        配套密度分级分析

        Returns:
            按配套丰富度分组的统计DataFrame
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 按配套丰富度分组
        grouped = self.df.groupby('配套丰富度', observed=True).agg({
            '单位租金': ['count', 'mean', 'median', 'std'],
            '租金': 'mean',
            '面积': 'mean'
        }).round(2)

        # 扁平化列名
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
        grouped = grouped.rename(columns={
            '单位租金_count': '样本量',
            '单位租金_mean': '单位租金均值',
            '单位租金_median': '单位租金中位数',
            '单位租金_std': '单位租金标准差',
            '租金_mean': '总租金均值',
            '面积_mean': '平均面积'
        })

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"{self.city_name} - 配套密度分级统计")
            print(f"{'='*60}")
            print(grouped.to_string())
            print(f"{'='*60}\n")

        return grouped

    def _print_ttest_results(self, results: Dict):
        """打印t检验结果"""
        print(f"\n{'='*60}")
        print(f"{self.city_name} - {results['amenity_type']} t检验")
        print(f"{'='*60}")
        print(f"\n【有{results['amenity_type']}】")
        print(f"  样本量: {results['with_amenity']['count']:,}")
        print(f"  均值: {results['with_amenity']['mean']:.2f} 元/㎡")
        print(f"  中位数: {results['with_amenity']['median']:.2f} 元/㎡")
        print(f"  标准差: {results['with_amenity']['std']:.2f}")

        print(f"\n【无{results['amenity_type']}】")
        print(f"  样本量: {results['without_amenity']['count']:,}")
        print(f"  均值: {results['without_amenity']['mean']:.2f} 元/㎡")
        print(f"  中位数: {results['without_amenity']['median']:.2f} 元/㎡")
        print(f"  标准差: {results['without_amenity']['std']:.2f}")

        print(f"\n【统计检验】")
        print(f"  t统计量: {results['t_statistic']:.4f}")

        # 智能显示p值：小于0.0001时用科学计数法
        p_val = results['p_value']
        if p_val < 0.0001:
            p_str = f"p < 0.0001 ({p_val:.2e})"
        else:
            p_str = f"p = {p_val:.6f}"

        sig_mark = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'n.s.'
        print(f"  {p_str} {sig_mark}")
        print(f"  效应量(Cohen's d): {results['cohens_d']:.4f}")

        print(f"\n【溢价分析】")
        print(f"  绝对溢价: {results['premium']:+.2f} 元/㎡")
        print(f"  相对溢价: {results['premium_pct']:+.2f}%")

        if results['significant']:
            print(f"\n✓ 结论: 有{results['amenity_type']}的房源单位租金**显著高于**无{results['amenity_type']}的房源")
        else:
            print(f"\n✗ 结论: 差异不显著（p >= 0.05）")

        print(f"{'='*60}\n")

    def _print_correlation_results(self, results: Dict):
        """打印相关性分析结果"""
        print(f"\n{'='*60}")
        print(f"{self.city_name} - {results['amenity_type']}数量 vs 单位租金")
        print(f"{'='*60}")
        print(f"\n样本量: {results['sample_size']:,}")

        print(f"\n【Pearson相关系数】")
        print(f"  r = {results['pearson_r']:.4f}")
        # 智能显示p值
        p_pearson = results['pearson_p']
        if p_pearson < 0.0001:
            p_str = f"p < 0.0001 ({p_pearson:.2e})"
        else:
            p_str = f"p = {p_pearson:.6f}"
        sig_mark = '***' if p_pearson < 0.001 else '**' if p_pearson < 0.01 else '*' if p_pearson < 0.05 else 'n.s.'
        print(f"  {p_str} {sig_mark}")

        print(f"\n【Spearman相关系数】(秩相关)")
        print(f"  ρ = {results['spearman_r']:.4f}")
        # 智能显示p值
        p_spearman = results['spearman_p']
        if p_spearman < 0.0001:
            p_str = f"p < 0.0001 ({p_spearman:.2e})"
        else:
            p_str = f"p = {p_spearman:.6f}"
        sig_mark = '***' if p_spearman < 0.001 else '**' if p_spearman < 0.01 else '*' if p_spearman < 0.05 else 'n.s.'
        print(f"  {p_str} {sig_mark}")

        if results['pearson_r'] > 0 and results['pearson_p'] < 0.05:
            strength = '强' if abs(results['pearson_r']) > 0.5 else '中等' if abs(results['pearson_r']) > 0.3 else '弱'
            print(f"\n✓ 结论: {results['amenity_type']}数量与单位租金存在**{strength}正相关**")
        elif results['pearson_p'] >= 0.05:
            print(f"\n✗ 结论: 相关性不显著（p >= 0.05）")
        else:
            print(f"\n✗ 结论: 存在负相关（异常）")

        print(f"{'='*60}\n")
