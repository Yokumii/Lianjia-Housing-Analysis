import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from pathlib import Path
from typing import Optional


class BrandVisualizer:
    """品牌租房数据可视化工具"""

    def __init__(self, verbose: bool = True):
        """
        初始化可视化工具

        Args:
            verbose: 是否打印详细日志
        """
        self.verbose = verbose
        self._setup_chinese_font()

    def _setup_chinese_font(self):
        """配置中文字体，解决乱码问题"""
        system = platform.system()

        if system == 'Windows':
            plt.rcParams['font.sans-serif'] = ['SimHei']
        elif system == 'Darwin':  # macOS
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
        else:  # Linux
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']

        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    def plot_comparison(
        self,
        stats: pd.DataFrame,
        output_dir: str = 'output/analysis',
        show: bool = True,
        save: bool = True
    ):
        """
        生成品牌对比可视化图表

        Args:
            stats: 统计结果 DataFrame
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        # 生成透视表
        pivot_counts = stats.pivot(
            index='城市',
            columns='品牌',
            values='房源数量'
        ).fillna(0)

        pivot_pct = stats.pivot(
            index='城市',
            columns='品牌',
            values='市占率'
        ).fillna(0)

        # 获取品牌列表（按总房源数量排序）
        brand_totals = stats.groupby('品牌')['房源数量'].sum().sort_values(ascending=False)
        brands = brand_totals.index.tolist()

        # 重排透视表列顺序
        pivot_counts = pivot_counts[brands]
        pivot_pct = pivot_pct[brands]

        # 生成配色（tab10 调色板）
        colors = sns.color_palette("tab10", n_colors=len(brands))

        # 创建 2x1 画布
        fig = plt.figure(figsize=(16, 14))
        gs = fig.add_gridspec(2, 1, hspace=0.35)

        # === 图1：房源数量堆积柱状图（垂直） ===
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_stacked_bar_vertical(
            ax=ax1,
            pivot=pivot_counts,
            colors=colors,
            title='各城市中介品牌【房源总量】分布',
            ylabel='房源数量 (套)'
        )

        # === 图2：市占率堆积柱状图（水平） ===
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_stacked_bar_horizontal(
            ax=ax2,
            pivot=pivot_pct,
            colors=colors,
            title='各城市中介品牌【市场占有率】对比',
            xlabel='百分比 (%)'
        )

        # 总标题
        plt.suptitle(
            '5 城市租房中介品牌分析：房源分布 vs 市场占有率',
            fontsize=22,
            fontweight='bold',
            y=0.98
        )

        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / 'brand_comparison.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')

            if self.verbose:
                print(f"\n✓ 图表已保存: {save_file}")

        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)

    def _plot_stacked_bar_vertical(
        self,
        ax,
        pivot: pd.DataFrame,
        colors: list,
        title: str,
        ylabel: str
    ):
        """
        绘制垂直堆积柱状图

        Args:
            ax: matplotlib axes
            pivot: 透视表（城市 × 品牌）
            colors: 颜色列表
            title: 图表标题
            ylabel: y 轴标签
        """
        pivot.plot(
            kind='bar',
            stacked=True,
            ax=ax,
            color=colors,
            width=0.7
        )

        ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel('', fontsize=12)
        ax.legend(title='品牌', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        # 在柱子顶部标注总数
        totals = pivot.sum(axis=1)
        for i, total in enumerate(totals):
            if total > 0:
                ax.text(
                    i,
                    total + 100,
                    f'{int(total):,}',
                    ha='center',
                    va='bottom',
                    fontweight='bold',
                    fontsize=10
                )

        # 旋转 x 轴标签
        ax.tick_params(axis='x', rotation=0)

    def _plot_stacked_bar_horizontal(
        self,
        ax,
        pivot: pd.DataFrame,
        colors: list,
        title: str,
        xlabel: str
    ):
        """
        绘制水平堆积百分比柱状图

        Args:
            ax: matplotlib axes
            pivot: 透视表（城市 × 品牌，值为百分比）
            colors: 颜色列表
            title: 图表标题
            xlabel: x 轴标签
        """
        pivot.plot(
            kind='barh',
            stacked=True,
            ax=ax,
            color=colors,
            width=0.7
        )

        ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('', fontsize=12)
        ax.legend(title='品牌', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=10)

        # 在柱子内部标注百分比
        for c in ax.containers:
            labels = [f'{v.get_width():.1f}%' if v.get_width() > 3 else '' for v in c]
            ax.bar_label(
                c,
                labels=labels,
                label_type='center',
                fontsize=9,
                color='white',
                fontweight='bold'
            )

        # 旋转 y 轴标签
        ax.tick_params(axis='y', rotation=0)

    def plot_pie_charts(
        self,
        stats: pd.DataFrame,
        output_dir: str = 'output/analysis',
        show: bool = True,
        save: bool = True
    ):
        """
        生成各城市品牌分布饼图（5 个子图）

        Args:
            stats: 统计结果 DataFrame
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        cities = stats['城市'].unique()

        # 创建 2x3 画布（5 个城市 + 1 个空位）
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()

        # 获取品牌列表（按总房源数量排序）
        brand_totals = stats.groupby('品牌')['房源数量'].sum().sort_values(ascending=False)
        brands = brand_totals.index.tolist()
        colors = sns.color_palette("tab10", n_colors=len(brands))

        for i, city in enumerate(cities):
            city_data = stats[stats['城市'] == city].copy()
            city_data = city_data.set_index('品牌').reindex(brands).fillna(0)

            # 绘制饼图
            axes[i].pie(
                city_data['房源数量'],
                labels=city_data.index,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            axes[i].set_title(f'{city} 品牌分布', fontsize=14, fontweight='bold')

        # 隐藏多余的子图
        for j in range(len(cities), len(axes)):
            axes[j].axis('off')

        # 总标题
        plt.suptitle(
            '5 城市租房中介品牌分布（饼图）',
            fontsize=20,
            fontweight='bold',
            y=0.98
        )

        plt.tight_layout()

        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / 'brand_pie_charts.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')

            if self.verbose:
                print(f"\n✓ 饼图已保存: {save_file}")

        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)
