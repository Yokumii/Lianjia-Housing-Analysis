import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from pathlib import Path
from typing import Optional


class CityVisualizer:
    """城市租房数据可视化工具"""
    
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
        df: pd.DataFrame,
        stats: pd.DataFrame,
        output_dir: str = 'output/analysis',
        show: bool = True,
        save: bool = True
    ):
        """
        生成城市对比可视化图表
        
        Args:
            df: 原始数据框
            stats: 统计摘要数据框
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        # 创建 2x2 画布
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        plt.subplots_adjust(hspace=0.3, wspace=0.25)
        
        # 配色方案
        palette = sns.color_palette("Set2", len(df['城市'].unique()))
        
        # === 图1: 租金箱线图 ===
        self._plot_boxplot(
            df=df,
            ax=axes[0, 0],
            y_col='租金',
            title='各城市租金分布（箱线图）',
            ylabel='租金 (元/月)',
            palette=palette
        )
        
        # === 图2: 单位租金箱线图 ===
        self._plot_boxplot(
            df=df,
            ax=axes[0, 1],
            y_col='单位租金',
            title='各城市单位租金分布（箱线图）',
            ylabel='单位租金 (元/㎡/月)',
            palette=palette
        )
        
        # === 图3: 租金均价分组柱状图 ===
        self._plot_barplot(
            stats=stats,
            ax=axes[1, 0],
            metric='租金',
            title='各城市租金统计对比（柱状图）',
            ylabel='租金 (元/月)',
            palette="Blues_d"
        )
        
        # === 图4: 单位租金均价分组柱状图 ===
        self._plot_barplot(
            stats=stats,
            ax=axes[1, 1],
            metric='单位租金',
            title='各城市单位租金统计对比（柱状图）',
            ylabel='单位租金 (元/㎡/月)',
            palette="Greens_d"
        )
        
        # 总标题
        plt.suptitle('五城租房市场：租金与单价全景对比', fontsize=22, fontweight='bold', y=0.98)
        
        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / 'city_comparison.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            
            if self.verbose:
                print(f"📊 可视化图表已保存: {save_file}")
        
        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)
    
    def _plot_boxplot(
        self,
        df: pd.DataFrame,
        ax,
        y_col: str,
        title: str,
        ylabel: str,
        palette
    ):
        """
        绘制箱线图
        
        Args:
            df: 数据框
            ax: matplotlib axes
            y_col: y 轴列名
            title: 图表标题
            ylabel: y 轴标签
            palette: 调色板
        """
        # 按中位数排序
        order = df.groupby('城市')[y_col].median().sort_values(ascending=False).index
        
        # 绘制箱线图（不显示异常值，避免图表过于拥挤）
        sns.boxplot(
            x='城市',
            y=y_col,
            hue='城市',
            data=df,
            ax=ax,
            order=order,
            palette=palette,
            showfliers=False,  # 不显示离群点
            legend=False
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_xlabel('')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 添加中位数标注
        medians = df.groupby('城市')[y_col].median()[order]
        for i, (city, median_val) in enumerate(medians.items()):
            ax.text(
                i, median_val,
                f'{median_val:.0f}',
                ha='center', va='bottom',
                fontsize=9, fontweight='bold',
                color='darkred'
            )
    
    def _plot_barplot(
        self,
        stats: pd.DataFrame,
        ax,
        metric: str,
        title: str,
        ylabel: str,
        palette: str
    ):
        """
        绘制分组柱状图（显示均价、最高、最低、中位数）
        
        Args:
            stats: 统计摘要数据框
            ax: matplotlib axes
            metric: 指标名称（'租金' 或 '单位租金'）
            title: 图表标题
            ylabel: y 轴标签
            palette: 调色板名称
        """
        # 提取数据
        data = stats[metric][['均价', '最高价', '最低价', '中位数']].copy()
        
        # 按均价排序
        data = data.sort_values('均价', ascending=False)
        
        # 准备绘图数据
        x = range(len(data))
        width = 0.2
        
        # 绘制分组柱状图
        colors = sns.color_palette(palette, 4)
        
        bars1 = ax.bar(
            [i - 1.5*width for i in x], 
            data['均价'], 
            width, 
            label='均价',
            color=colors[0],
            edgecolor='black',
            linewidth=0.5
        )
        bars2 = ax.bar(
            [i - 0.5*width for i in x], 
            data['最高价'], 
            width, 
            label='最高价',
            color=colors[1],
            edgecolor='black',
            linewidth=0.5
        )
        bars3 = ax.bar(
            [i + 0.5*width for i in x], 
            data['最低价'], 
            width, 
            label='最低价',
            color=colors[2],
            edgecolor='black',
            linewidth=0.5
        )
        bars4 = ax.bar(
            [i + 1.5*width for i in x], 
            data['中位数'], 
            width, 
            label='中位数',
            color=colors[3],
            edgecolor='black',
            linewidth=0.5
        )
        
        # 设置标签
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_xlabel('')
        ax.set_xticks(x)
        ax.set_xticklabels(data.index, fontsize=10)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 添加数值标注（仅标注均价，避免过于拥挤）
        for i, v in enumerate(data['均价']):
            ax.text(
                i - 1.5*width, v + (data['最高价'].max() * 0.02),
                f'{v:.0f}',
                ha='center', va='bottom',
                fontsize=8, fontweight='bold'
            )
