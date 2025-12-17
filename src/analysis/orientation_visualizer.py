import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from pathlib import Path
from typing import Optional


class OrientationVisualizer:
    """朝向租房数据可视化工具"""

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
        df_expanded: pd.DataFrame,
        stats: pd.DataFrame,
        output_dir: str = 'output/analysis',
        show: bool = True,
        save: bool = True
    ):
        """
        生成朝向对比可视化图表（2x2 布局）

        Args:
            df_expanded: 拆分后的数据 DataFrame
            stats: 统计结果 DataFrame
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        # 创建 2x2 画布
        fig = plt.figure(figsize=(20, 14))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. 左上：单位租金均价分组柱状图
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_grouped_bar(
            ax=ax1,
            df=df_expanded,
            metric='单位租金',
            title='各城市不同朝向单位租金均价对比',
            ylabel='单位租金均价 (元/㎡/月)',
            palette='Set2'
        )

        # 2. 右上：房源量分组柱状图
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_count_bar(
            ax=ax2,
            df=df_expanded,
            title='各城市不同朝向房源量对比（拆分后）',
            ylabel='房源量（拆分后行数）',
            palette='Set3'
        )

        # 3. 左下：单位租金均价热力图
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_heatmap(
            ax=ax3,
            df=df_expanded,
            metric='单位租金',
            title='单位租金均价热力图（朝向 × 城市）',
            cmap='YlOrRd',
            cbar_label='元/㎡/月'
        )

        # 4. 右下：房源量热力图
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_heatmap(
            ax=ax4,
            df=df_expanded,
            metric='count',
            title='房源量热力图（朝向 × 城市，拆分后）',
            cmap='Blues',
            cbar_label='房源量（拆分后行数）'
        )

        # 总标题
        plt.suptitle(
            '5 城市租房朝向深度分析：单位租金 vs 房源分布',
            fontsize=22,
            fontweight='bold',
            y=0.98
        )

        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / 'orientation_comparison.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')

            if self.verbose:
                print(f"\n✓ 图表已保存: {save_file}")

        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)

    def _plot_grouped_bar(
        self,
        ax,
        df: pd.DataFrame,
        metric: str,
        title: str,
        ylabel: str,
        palette: str
    ):
        """
        绘制分组柱状图（城市 × 朝向）

        Args:
            ax: matplotlib axes
            df: 数据框
            metric: 指标列名
            title: 图表标题
            ylabel: y 轴标签
            palette: 调色板
        """
        # 按城市和朝向分组计算均值
        grouped = df.groupby(['城市', '朝向'])[metric].mean().reset_index()

        # 绘制分组柱状图
        sns.barplot(
            data=grouped,
            x='朝向',
            y=metric,
            hue='城市',
            ax=ax,
            palette=palette
        )

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('朝向', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(title='城市', fontsize=10, title_fontsize=11, loc='upper right')
        ax.grid(axis='y', linestyle='--', alpha=0.4)

        # 旋转 x 轴标签
        ax.tick_params(axis='x', rotation=0)

    def _plot_count_bar(
        self,
        ax,
        df: pd.DataFrame,
        title: str,
        ylabel: str,
        palette: str
    ):
        """
        绘制房源量分组柱状图

        Args:
            ax: matplotlib axes
            df: 数据框
            title: 图表标题
            ylabel: y 轴标签
            palette: 调色板
        """
        # 按城市和朝向分组计数
        grouped = df.groupby(['城市', '朝向']).size().reset_index(name='count')

        # 绘制分组柱状图
        sns.barplot(
            data=grouped,
            x='朝向',
            y='count',
            hue='城市',
            ax=ax,
            palette=palette
        )

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('朝向', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(title='城市', fontsize=10, title_fontsize=11, loc='upper right')
        ax.grid(axis='y', linestyle='--', alpha=0.4)

        # 旋转 x 轴标签
        ax.tick_params(axis='x', rotation=0)

    def _plot_heatmap(
        self,
        ax,
        df: pd.DataFrame,
        metric: str,
        title: str,
        cmap: str,
        cbar_label: str
    ):
        """
        绘制热力图（朝向 × 城市）

        Args:
            ax: matplotlib axes
            df: 数据框
            metric: 指标（'单位租金' 或 'count'）
            title: 图表标题
            cmap: 颜色映射
            cbar_label: 颜色条标签
        """
        # 生成透视表
        if metric == 'count':
            pivot = df.pivot_table(
                index='朝向',
                columns='城市',
                aggfunc='size',
                fill_value=0
            )
        else:
            pivot = df.pivot_table(
                values=metric,
                index='朝向',
                columns='城市',
                aggfunc='mean'
            )

        # 绘制热力图
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.0f' if metric == 'count' else '.1f',
            cmap=cmap,
            ax=ax,
            cbar_kws={'label': cbar_label},
            linewidths=0.5,
            linecolor='white'
        )

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('城市', fontsize=12)
        ax.set_ylabel('朝向', fontsize=12)

        # 调整刻度标签
        ax.tick_params(axis='x', rotation=0)
        ax.tick_params(axis='y', rotation=0)
