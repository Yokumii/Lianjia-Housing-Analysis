import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Optional
import platform


class AmenityVisualizer:
    """配套设施溢价可视化工具"""

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
        初始化可视化器

        Args:
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
        self.df = None
        self.city_code = None
        self.city_name = None

        # 设置绘图风格
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 300

        # 设置中文字体
        self._setup_chinese_font()

    def _setup_chinese_font(self):
        """设置中文字体"""
        system = platform.system()
        if system == 'Darwin':  # macOS
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Songti SC', 'STHeiti']
        elif system == 'Windows':
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
        else:  # Linux
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Droid Sans Fallback']
        plt.rcParams['axes.unicode_minus'] = False

    def load_data(self, city_code: str, df: pd.DataFrame):
        """
        加载数据

        Args:
            city_code: 城市代码
            df: 包含配套数据的DataFrame
        """
        self.city_code = city_code
        self.city_name = self.CITY_NAMES.get(city_code, city_code.upper())
        self.df = df

        if self.verbose:
            print(f"✓ 加载 {self.city_name} 可视化数据: {len(df):,} 行")

    def plot_boxplot_comparison(
        self,
        amenity_type: str,
        output_file: str,
        ttest_results: Optional[Dict] = None
    ) -> str:
        """
        绘制箱线图：有/无配套的单位租金分布对比

        Args:
            amenity_type: 配套类型（'starbucks' 或 'mcdonalds'）
            output_file: 输出文件路径
            ttest_results: t检验结果（可选，用于标注显著性）

        Returns:
            输出文件路径
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 确定标签列和名称
        if amenity_type == 'starbucks':
            label_col = '有星巴克'
            name = '星巴克'
            color = '#00704A'  # 星巴克绿
        elif amenity_type == 'mcdonalds':
            label_col = '有麦当劳'
            name = '麦当劳'
            color = '#FFC72C'  # 麦当劳黄
        else:
            raise ValueError("amenity_type 必须是 'starbucks' 或 'mcdonalds'")

        # 准备数据
        df_clean = self.df.dropna(subset=['单位租金', label_col]).copy()
        df_clean['配套'] = df_clean[label_col].map({0: f'无{name}', 1: f'有{name}'})

        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 7))

        # 绘制箱线图
        sns.boxplot(
            data=df_clean,
            x='配套',
            y='单位租金',
            palette=[color, '#E0E0E0'],
            ax=ax,
            showfliers=False  # 不显示异常值点（太多会很乱）
        )

        # 绘制均值点
        means = df_clean.groupby('配套')['单位租金'].mean()
        x_positions = range(len(means))
        ax.plot(x_positions, means.values, 'r*', markersize=15, label='均值', zorder=5)

        # 添加显著性标记
        if ttest_results and ttest_results['significant']:
            y_max = df_clean['单位租金'].quantile(0.95)
            h = y_max * 0.05
            ax.plot([0, 0, 1, 1], [y_max, y_max+h, y_max+h, y_max], 'k-', linewidth=1.5)

            sig_text = '***' if ttest_results['p_value'] < 0.001 else '**' if ttest_results['p_value'] < 0.01 else '*'
            ax.text(0.5, y_max+h, sig_text, ha='center', va='bottom', fontsize=16)

        # 设置标签
        ax.set_xlabel('', fontsize=12)
        ax.set_ylabel('单位租金 (元/㎡)', fontsize=12)
        ax.set_title(
            f'{self.city_name} - {name}对单位租金的影响\n箱线图对比',
            fontsize=14,
            fontweight='bold'
        )

        # 添加统计信息文本框
        if ttest_results:
            stats_text = (
                f"样本量: 有{ttest_results['with_amenity']['count']:,} | "
                f"无{ttest_results['without_amenity']['count']:,}\n"
                f"溢价: {ttest_results['premium']:+.2f} 元/㎡ ({ttest_results['premium_pct']:+.1f}%)\n"
                f"p值: {ttest_results['p_value']:.4f}"
            )
            ax.text(
                0.02, 0.98,
                stats_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            )

        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')

        # 保存图表
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        if self.verbose:
            print(f"✓ 箱线图已保存: {output_path}")

        return str(output_path)

    def plot_scatter_correlation(
        self,
        amenity_type: str,
        output_file: str,
        correlation_results: Optional[Dict] = None
    ) -> str:
        """
        绘制散点图+回归线：配套数量 vs 单位租金

        Args:
            amenity_type: 配套类型（'starbucks', 'mcdonalds' 或 'total'）
            output_file: 输出文件路径
            correlation_results: 相关性分析结果（可选）

        Returns:
            输出文件路径
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 确定数量列和名称
        if amenity_type == 'starbucks':
            count_col = '星巴克数量'
            name = '星巴克'
            color = '#00704A'
        elif amenity_type == 'mcdonalds':
            count_col = '麦当劳数量'
            name = '麦当劳'
            color = '#FFC72C'
        elif amenity_type == 'total':
            count_col = '配套总数'
            name = '配套总数'
            color = '#1f77b4'
        else:
            raise ValueError("amenity_type 必须是 'starbucks', 'mcdonalds' 或 'total'")

        # 准备数据
        df_clean = self.df.dropna(subset=['单位租金', count_col])

        # 限制显示范围（过滤极端值）
        max_count = df_clean[count_col].quantile(0.95)
        df_plot = df_clean[df_clean[count_col] <= max_count]

        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 7))

        # 绘制散点图
        ax.scatter(
            df_plot[count_col],
            df_plot['单位租金'],
            alpha=0.3,
            s=10,
            color=color,
            label='实际数据'
        )

        # 绘制回归线
        from scipy.stats import linregress
        x = df_plot[count_col]
        y = df_plot['单位租金']
        slope, intercept, r_value, p_value, std_err = linregress(x, y)

        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept

        ax.plot(
            x_line,
            y_line,
            'r--',
            linewidth=2,
            label=f'回归线: y = {slope:.2f}x + {intercept:.2f}'
        )

        # 绘制分组均值
        grouped = df_plot.groupby(count_col)['单位租金'].mean()
        ax.plot(
            grouped.index,
            grouped.values,
            'b-',
            linewidth=2,
            marker='o',
            markersize=8,
            label='分组均值'
        )

        # 设置标签
        ax.set_xlabel(f'{name}数量', fontsize=12)
        ax.set_ylabel('单位租金 (元/㎡)', fontsize=12)
        ax.set_title(
            f'{self.city_name} - {name}数量与单位租金的关系\n散点图 + 回归分析',
            fontsize=14,
            fontweight='bold'
        )

        # 添加统计信息
        if correlation_results:
            stats_text = (
                f"样本量: {correlation_results['sample_size']:,}\n"
                f"Pearson r: {correlation_results['pearson_r']:.4f}\n"
                f"p值: {correlation_results['pearson_p']:.4f}\n"
                f"Spearman ρ: {correlation_results['spearman_r']:.4f}"
            )
            ax.text(
                0.02, 0.98,
                stats_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            )

        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)

        # 保存图表
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        if self.verbose:
            print(f"✓ 散点图已保存: {output_path}")

        return str(output_path)

    def plot_density_barplot(
        self,
        output_file: str,
        density_stats: pd.DataFrame
    ) -> str:
        """
        绘制分组柱状图：不同配套密度的租金对比

        Args:
            output_file: 输出文件路径
            density_stats: 密度统计DataFrame

        Returns:
            输出文件路径
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 创建图表
        fig, ax1 = plt.subplots(figsize=(12, 7))

        # 绘制租金柱状图
        x = np.arange(len(density_stats))
        width = 0.35

        bars1 = ax1.bar(
            x - width/2,
            density_stats['单位租金均值'],
            width,
            label='单位租金',
            color='#3498db',
            alpha=0.8
        )

        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{height:.1f}',
                ha='center',
                va='bottom',
                fontsize=9
            )

        # 创建第二个y轴（样本量）
        ax2 = ax1.twinx()
        bars2 = ax2.bar(
            x + width/2,
            density_stats['样本量'],
            width,
            label='样本量',
            color='#e74c3c',
            alpha=0.6
        )

        # 添加样本量标签
        for bar in bars2:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{int(height):,}',
                ha='center',
                va='bottom',
                fontsize=9
            )

        # 设置标签
        ax1.set_xlabel('配套丰富度', fontsize=12)
        ax1.set_ylabel('单位租金 (元/㎡)', fontsize=12, color='#3498db')
        ax2.set_ylabel('样本量', fontsize=12, color='#e74c3c')

        ax1.set_title(
            f'{self.city_name} - 配套丰富度分级分析\n双轴柱状图',
            fontsize=14,
            fontweight='bold'
        )

        ax1.set_xticks(x)
        ax1.set_xticklabels(density_stats.index)
        ax1.tick_params(axis='y', labelcolor='#3498db')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')

        # 添加图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        ax1.grid(True, alpha=0.3, axis='y')

        # 保存图表
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        if self.verbose:
            print(f"✓ 柱状图已保存: {output_path}")

        return str(output_path)

    def plot_heatmap_comparison(
        self,
        output_file: str
    ) -> str:
        """
        绘制热力图：星巴克 x 麦当劳的交叉影响

        Args:
            output_file: 输出文件路径

        Returns:
            输出文件路径
        """
        if self.df is None:
            raise ValueError("请先调用 load_data() 加载数据")

        # 准备数据
        df_clean = self.df.dropna(subset=['单位租金', '有星巴克', '有麦当劳'])

        # 创建分组
        pivot = df_clean.groupby(['有星巴克', '有麦当劳'])['单位租金'].mean().unstack()
        pivot.index = pivot.index.map({0: '无星巴克', 1: '有星巴克'})
        pivot.columns = pivot.columns.map({0: '无麦当劳', 1: '有麦当劳'})

        # 创建图表
        fig, ax = plt.subplots(figsize=(8, 6))

        sns.heatmap(
            pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=pivot.values.mean(),
            cbar_kws={'label': '单位租金 (元/㎡)'},
            ax=ax
        )

        ax.set_title(
            f'{self.city_name} - 配套设施交叉影响热力图\n单位租金均值',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.set_xlabel('')
        ax.set_ylabel('')

        # 保存图表
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        if self.verbose:
            print(f"✓ 热力图已保存: {output_path}")

        return str(output_path)
