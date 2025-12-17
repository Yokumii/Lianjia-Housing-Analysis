import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import platform
from pathlib import Path


class SalaryRentVisualizer:
    """工资-租金关系可视化工具"""

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
        生成工资-租金关系可视化图表（2x2 布局）

        Args:
            stats: 统计结果 DataFrame
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        # 创建 2x2 画布
        fig = plt.figure(figsize=(18, 16))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # === 图1：工资 vs 单位租金散点图 + 回归线 ===
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_salary_rent_scatter(ax=ax1, stats=stats)

        # === 图2：租房自由度柱状图 ===
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_affordability_bar(ax=ax2, stats=stats)

        # === 图3：租房压力对比柱状图 ===
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_pressure_bar(ax=ax3, stats=stats)

        # === 图4：租房性价比雷达图/柱状图 ===
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_value_bar(ax=ax4, stats=stats)

        # 总标题
        plt.suptitle(
            '5 城市工资-租金关系深度分析：租房自由度 vs 租房压力',
            fontsize=22,
            fontweight='bold',
            y=0.98
        )

        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / 'salary_rent_comparison.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')

            if self.verbose:
                print(f"\n✓ 图表已保存: {save_file}")

        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)

    def _plot_salary_rent_scatter(self, ax, stats: pd.DataFrame):
        """
        绘制工资 vs 单位租金散点图 + 回归线

        Args:
            ax: matplotlib axes
            stats: 统计结果 DataFrame
        """
        # 绘制散点
        sns.scatterplot(
            x='私营月薪',
            y='单位租金中位数',
            data=stats,
            ax=ax,
            s=300,
            hue='城市',
            palette='Set1',
            legend=False
        )

        # 添加趋势线（回归线）
        sns.regplot(
            x='私营月薪',
            y='单位租金中位数',
            data=stats,
            ax=ax,
            scatter=False,
            color='grey',
            line_kws={'linestyle': '--', 'linewidth': 2, 'alpha': 0.7}
        )

        # 计算相关系数（使用 numpy）
        corr = np.corrcoef(
            stats['私营月薪'],
            stats['单位租金中位数']
        )[0, 1]

        # 标注城市名
        for _, row in stats.iterrows():
            ax.text(
                row['私营月薪'] + 100,
                row['单位租金中位数'],
                row['城市'],
                fontsize=11,
                fontweight='bold',
                va='center'
            )

        ax.set_title(
            f'工资水平 vs 单位租金（相关系数: {corr:.3f}）',
            fontsize=14,
            fontweight='bold',
            pad=15
        )
        ax.set_xlabel('私营单位平均月薪 (元)', fontsize=12)
        ax.set_ylabel('单位租金中位数 (元/㎡/月)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.4)

        # 添加说明文字
        ax.text(
            0.02, 0.98,
            '越偏离虚线越特殊\n高于虚线：租金偏高\n低于虚线：租金偏低',
            transform=ax.transAxes,
            fontsize=9,
            va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3)
        )

    def _plot_affordability_bar(self, ax, stats: pd.DataFrame):
        """
        绘制租房自由度柱状图

        Args:
            ax: matplotlib axes
            stats: 统计结果 DataFrame
        """
        # 排序
        data_sorted = stats.sort_values('可租面积_私营30%', ascending=True)

        # 颜色映射：面积越小（压力越大）越红，越大越绿
        norm = plt.Normalize(
            data_sorted['可租面积_私营30%'].min(),
            data_sorted['可租面积_私营30%'].max()
        )
        colors = plt.cm.RdYlGn(norm(data_sorted['可租面积_私营30%'].values))

        # 绘制柱状图
        bars = ax.barh(
            data_sorted['城市'],
            data_sorted['可租面积_私营30%'],
            color=colors
        )

        ax.set_title(
            '租房自由度：拿出30%私营月薪，能租多大的房子？',
            fontsize=14,
            fontweight='bold',
            pad=15
        )
        ax.set_xlabel('可租面积 (㎡)', fontsize=12)
        ax.set_ylabel('', fontsize=12)

        # 添加警戒线（20㎡是蜗居线）
        ax.axvline(x=20, color='red', linestyle='--', alpha=0.7, linewidth=2, label='蜗居线 (20㎡)')
        ax.axvline(x=30, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='及格线 (30㎡)')
        ax.legend(fontsize=10, loc='lower right')

        # 标注数值
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height()/2,
                f'{width:.1f}㎡',
                va='center',
                fontsize=11,
                fontweight='bold'
            )

        ax.grid(axis='x', linestyle='--', alpha=0.3)

    def _plot_pressure_bar(self, ax, stats: pd.DataFrame):
        """
        绘制租房压力对比柱状图

        Args:
            ax: matplotlib axes
            stats: 统计结果 DataFrame
        """
        # 准备数据
        data_sorted = stats.sort_values('30平米房租占私营月薪%', ascending=False)

        # 绘制分组柱状图
        x = np.arange(len(data_sorted))
        width = 0.35

        bars1 = ax.bar(
            x - width/2,
            data_sorted['30平米房租占私营月薪%'],
            width,
            label='占私营月薪比例',
            color='#ff6b6b'
        )

        bars2 = ax.bar(
            x + width/2,
            data_sorted['30平米房租占可支配收入%'],
            width,
            label='占可支配收入比例',
            color='#4ecdc4'
        )

        ax.set_title(
            '租房压力：租30㎡单间需要花多少比例的收入？',
            fontsize=14,
            fontweight='bold',
            pad=15
        )
        ax.set_ylabel('收入占比 (%)', fontsize=12)
        ax.set_xlabel('', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(data_sorted['城市'], fontsize=11)
        ax.legend(fontsize=10)

        # 添加警戒线（30%是警戒线）
        ax.axhline(y=30, color='red', linestyle='--', alpha=0.7, linewidth=2, label='警戒线 (30%)')
        ax.axhline(y=50, color='darkred', linestyle='--', alpha=0.7, linewidth=2, label='危险线 (50%)')

        # 标注数值
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    height + 1,
                    f'{height:.1f}%',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold'
                )

        ax.grid(axis='y', linestyle='--', alpha=0.3)

    def _plot_value_bar(self, ax, stats: pd.DataFrame):
        """
        绘制租房性价比柱状图

        Args:
            ax: matplotlib axes
            stats: 统计结果 DataFrame
        """
        # 排序
        data_sorted = stats.sort_values('租房性价比_私营', ascending=True)

        # 颜色映射：性价比越高越绿
        norm = plt.Normalize(
            data_sorted['租房性价比_私营'].min(),
            data_sorted['租房性价比_私营'].max()
        )
        colors = plt.cm.RdYlGn(norm(data_sorted['租房性价比_私营'].values))

        # 绘制柱状图
        bars = ax.barh(
            data_sorted['城市'],
            data_sorted['租房性价比_私营'],
            color=colors
        )

        ax.set_title(
            '租房性价比：每1元租金对应多少元工资？',
            fontsize=14,
            fontweight='bold',
            pad=15
        )
        ax.set_xlabel('性价比指数（工资/租金）', fontsize=12)
        ax.set_ylabel('', fontsize=12)

        # 标注数值
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height()/2,
                f'{width:.1f}',
                va='center',
                fontsize=11,
                fontweight='bold'
            )

        ax.grid(axis='x', linestyle='--', alpha=0.3)

        # 添加说明文字
        ax.text(
            0.02, 0.02,
            '数值越大，性价比越高\n（工资高、租金低）',
            transform=ax.transAxes,
            fontsize=9,
            va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3)
        )
