import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from pathlib import Path


class BlockVisualizer:
    """板块租房数据可视化工具"""
    
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
    
    def plot_city_blocks(
        self,
        city_name: str,
        top_expensive: pd.DataFrame,
        top_cheap: pd.DataFrame,
        output_dir: str = 'output/analysis',
        show: bool = True,
        save: bool = True
    ):
        """
        生成单个城市的板块对比可视化图表
        
        Args:
            city_name: 城市名称
            top_expensive: 最贵板块 DataFrame
            top_cheap: 最便宜板块 DataFrame
            output_dir: 输出目录
            show: 是否显示图表
            save: 是否保存图表
        """
        # 创建 1x2 画布
        fig, axes = plt.subplots(1, 2, figsize=(18, 12))
        plt.subplots_adjust(wspace=0.3)
        
        # === 左图：最贵板块 Top 15 ===
        self._plot_horizontal_bar(
            ax=axes[0],
            data=top_expensive,
            title=f'【{city_name}】租金最贵板块 TOP{len(top_expensive)} (元/㎡/月)',
            xlabel='单位租金均价 (元/㎡/月)',
            palette='Reds_r',  # 红色系（反转使顶部更深）
            value_offset=2
        )
        
        # === 右图：最亲民板块 Top 15 ===
        self._plot_horizontal_bar(
            ax=axes[1],
            data=top_cheap,
            title=f'【{city_name}】租金最亲民板块 TOP{len(top_cheap)} (元/㎡/月)',
            xlabel='单位租金均价 (元/㎡/月)',
            palette='Greens_d',  # 绿色系
            value_offset=2
        )
        
        # 总标题
        plt.suptitle(
            f'{city_name}板块租金深度分析：最贵 vs 最亲民',
            fontsize=22,
            fontweight='bold',
            y=0.98
        )
        
        # 保存图表
        if save:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            save_file = output_path / f'block_analysis_{city_name}.png'
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            
            if self.verbose:
                print(f"  📊 {city_name} 图表已保存: {save_file}")
        
        # 显示图表
        if show:
            plt.show()
        else:
            plt.close(fig)
    
    def _plot_horizontal_bar(
        self,
        ax,
        data: pd.DataFrame,
        title: str,
        xlabel: str,
        palette: str,
        value_offset: float = 2
    ):
        """
        绘制横向柱状图
        
        Args:
            ax: matplotlib axes
            data: 数据框（必须包含 '单价均价' 列，index 为板块名）
            title: 图表标题
            xlabel: x 轴标签
            palette: 调色板
            value_offset: 数值标注偏移量
        """
        # 绘制横向柱状图
        sns.barplot(
            x='单价均价',
            y=data.index,
            data=data,
            ax=ax,
            palette=palette,
            hue=data.index,
            legend=False
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel('')
        
        # 网格线
        ax.grid(axis='x', linestyle='--', alpha=0.4)
        
        # 在柱子末端标注数值
        for i, v in enumerate(data['单价均价']):
            ax.text(
                v + value_offset,
                i,
                f'{v:.1f}',
                va='center',
                fontsize=10,
                fontweight='bold'
            )
        
        # 调整 y 轴刻度标签（确保板块名完全显示）
        ax.tick_params(axis='y', labelsize=10)
