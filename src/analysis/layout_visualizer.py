import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from pathlib import Path
from typing import Optional


class LayoutVisualizer:
    """户型租房数据可视化工具"""
    
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
    
    def plot_layout_comparison(
        self,
        df: pd.DataFrame,
        stats: pd.DataFrame,
        output_dir: str = 'output/analysis',
        show: bool = True,
        save: bool = True
    ):
        """
        生成户型对比可视化图表
        
        Args:
            df: 原始数据框
            stats: 统计摘要数据框
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        # 创建 3 张子图（2 个分组柱状图 + 1 个热力图）
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.25, height_ratios=[1, 1, 1.2])
        
        # 配色方案
        palette = "Set2"
        
        # === 图1: 租金分组柱状图 ===
        ax1 = fig.add_subplot(gs[0, :])  # 占据第一行全部
        self._plot_grouped_barplot(
            df=df,
            ax=ax1,
            y_col='租金',
            title='五城各户型【总租金】均价对比',
            ylabel='租金 (元/月)',
            palette=palette
        )
        
        # === 图2: 单位租金分组柱状图 ===
        ax2 = fig.add_subplot(gs[1, :])  # 占据第二行全部
        self._plot_grouped_barplot(
            df=df,
            ax=ax2,
            y_col='单位租金',
            title='五城各户型【单位面积租金】均价对比',
            ylabel='单位租金 (元/㎡/月)',
            palette=palette
        )
        
        # === 图3: 租金热力图 ===
        ax3 = fig.add_subplot(gs[2, 0])
        self._plot_heatmap(
            stats=stats,
            ax=ax3,
            metric='租金',
            stat='均价',
            title='租金均价热力图（元/月）',
            fmt='.0f'
        )
        
        # === 图4: 单位租金热力图 ===
        ax4 = fig.add_subplot(gs[2, 1])
        self._plot_heatmap(
            stats=stats,
            ax=ax4,
            metric='单位租金',
            stat='均价',
            title='单位租金均价热力图（元/㎡/月）',
            fmt='.1f'
        )
        
        # 总标题
        plt.suptitle(
            '五城租房市场：户型与租金深度对比分析',
            fontsize=24,
            fontweight='bold',
            y=0.98
        )
        
        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / 'layout_comparison.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            
            if self.verbose:
                print(f"📊 可视化图表已保存: {save_file}")
        
        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)
    
    def _plot_grouped_barplot(
        self,
        df: pd.DataFrame,
        ax,
        y_col: str,
        title: str,
        ylabel: str,
        palette: str
    ):
        """
        绘制分组柱状图（城市 x 户型）
        
        Args:
            df: 数据框
            ax: matplotlib axes
            y_col: y 轴列名
            title: 图表标题
            ylabel: y 轴标签
            palette: 调色板
        """
        # 绘制分组柱状图
        sns.barplot(
            x='城市',
            y=y_col,
            hue='户型',
            data=df,
            ax=ax,
            palette=palette,
            errorbar=None  # 不显示误差线
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel('')
        
        # 图例放置在右侧外部
        ax.legend(
            title='户型',
            bbox_to_anchor=(1.02, 1),
            loc='upper left',
            borderaxespad=0,
            fontsize=11
        )
        
        # 网格线
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 在柱子上标注数值
        for container in ax.containers:
            if y_col == '租金':
                ax.bar_label(container, fmt='%.0f', padding=3, fontsize=9)
            else:
                ax.bar_label(container, fmt='%.1f', padding=3, fontsize=9)
    
    def _plot_heatmap(
        self,
        stats: pd.DataFrame,
        ax,
        metric: str,
        stat: str,
        title: str,
        fmt: str = '.1f'
    ):
        """
        绘制热力图（城市 x 户型）
        
        Args:
            stats: 统计摘要数据框
            ax: matplotlib axes
            metric: 指标名称（'租金' 或 '单位租金'）
            stat: 统计量名称（'均价', '最高价', '最低价', '中位数'）
            title: 图表标题
            fmt: 数值格式
        """
        # 构建透视表
        pivot_data = []
        cities = stats.index.get_level_values(0).unique()
        layouts = ['一居', '两居', '三居']
        
        for city in cities:
            row = []
            for layout in layouts:
                if (city, layout) in stats.index:
                    value = stats.loc[(city, layout), (metric, stat)]
                    row.append(value)
                else:
                    row.append(None)
            pivot_data.append(row)
        
        pivot_df = pd.DataFrame(pivot_data, index=cities, columns=layouts)

        # 确定色标标签
        cbar_label = '元/月' if metric == '租金' else '元/㎡/月'

        # 绘制热力图
        sns.heatmap(
            pivot_df,
            annot=True,
            fmt=fmt,
            cmap='YlOrRd',  # 黄-橙-红配色
            ax=ax,
            cbar_kws={'label': cbar_label},
            linewidths=0.5,
            linecolor='white'
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('户型', fontsize=11)
        ax.set_ylabel('城市', fontsize=11)
        
        # 调整刻度标签
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha='right')
