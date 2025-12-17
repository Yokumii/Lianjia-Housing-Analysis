import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import platform


class DistanceVisualizer:
    """距离可视化工具"""

    # 城市代码到名称的映射
    CITY_CODE_MAP = {
        'bj': '北京',
        'sh': '上海',
        'gz': '广州',
        'sz': '深圳',
        'hz': '杭州'
    }

    # 城市中心坐标（用于地图初始视图）
    CITY_CENTERS = {
        'bj': (39.9042, 116.4074),
        'sh': (31.2304, 121.4737),
        'gz': (23.1291, 113.2644),
        'sz': (22.5431, 114.0579),
        'hz': (30.2741, 120.1551)
    }

    # 就业中心坐标（与 distance_calculator.py 保持一致）
    EMPLOYMENT_CENTERS = {
        'bj': {
            '西二旗': (116.306295, 40.053034),
            '望京': (116.466485, 39.995197),
            '国贸': (116.459288, 39.910882),
            '金融街': (116.357325, 39.910142)
        },
        'sh': {
            '陆家嘴': (121.5025, 31.237015),
            '张江科学城': (121.643677, 31.206884),
            '漕河泾': (121.416405, 31.16791),
            '外滩': (121.492127, 31.233516)
        },
        'sz': {
            '南山科技园': (113.94631, 22.543723),
            '深圳湾': (113.972602, 22.518968),
            '福田CBD': (114.055963, 22.525845),
            '坂田科技城': (114.055362, 22.636404)
        },
        'gz': {
            '珠江新城': (113.321202, 23.119366),
            '体育西路': (113.321503, 23.131138),
            '天河软件园': (113.412453, 23.171807),
            '广州科学城': (113.44952, 23.165789)
        },
        'hz': {
            '未来科技城': (120.007498, 30.295056),
            '钱江新城': (120.214223, 30.250328),
            '滨江区': (120.211981, 30.208332),
            '湖滨商圈': (120.164471, 30.252148)
        }
    }

    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化可视化工具

        Args:
            data_dir: 数据目录
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        self.df = None
        self.city_code = None
        self.city_name = None

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

    def load_distance_data(self, city_code: str) -> pd.DataFrame:
        """
        加载包含距离信息的数据

        Args:
            city_code: 城市代码

        Returns:
            包含距离列的 DataFrame
        """
        self.city_code = city_code
        self.city_name = self.CITY_CODE_MAP.get(city_code, city_code)

        # 尝试加载带距离信息的数据
        distance_file = self.data_dir / f'{city_code}_rental_with_distances.csv'

        if not distance_file.exists():
            raise FileNotFoundError(
                f"未找到距离数据文件: {distance_file}\n"
                f"请先使用 DistanceCalculator 计算距离"
            )

        self.df = pd.read_csv(distance_file)

        if self.verbose:
            print(f"\n✓ 加载 {self.city_name} 距离数据: {len(self.df):,} 行")
            distance_cols = [col for col in self.df.columns if col.startswith('距离_')]
            print(f"  距离列数: {len(distance_cols)}")

        return self.df

    def generate_circle_map(
        self,
        city_code: str,
        center_name: str,
        output_file: str,
        radii: List[int] = [3000, 5000, 10000]
    ) -> str:
        """
        生成同心圆地图

        Args:
            city_code: 城市代码
            center_name: 就业中心名称
            output_file: 输出文件路径
            radii: 同心圆半径列表（米）

        Returns:
            输出文件路径
        """
        if self.df is None or self.city_code != city_code:
            self.load_distance_data(city_code)

        # 获取就业中心坐标
        center_coord = self.EMPLOYMENT_CENTERS[city_code].get(center_name)
        if center_coord is None:
            raise ValueError(f"未找到就业中心 {center_name} 的坐标")

        center_lng, center_lat = center_coord

        # 创建地图
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=12,
            tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
            attr='高德地图'
        )

        # 添加就业中心标记
        folium.Marker(
            location=[center_lat, center_lng],
            popup=f'<b>{center_name}</b>',
            icon=folium.Icon(color='red', icon='briefcase', prefix='fa'),
            tooltip=center_name
        ).add_to(m)

        # 添加同心圆
        colors = ['blue', 'green', 'orange']
        for i, radius in enumerate(radii):
            folium.Circle(
                location=[center_lat, center_lng],
                radius=radius,
                color=colors[i % len(colors)],
                fill=False,
                weight=2,
                opacity=0.7,
                popup=f'{radius/1000:.0f} km'
            ).add_to(m)

        # 准备热力图数据（仅显示有效坐标的房源）
        df_valid = self.df.dropna(subset=['纬度', '经度', '单位租金'])

        # 过滤极值（1st~99th 百分位）
        lower = df_valid['单位租金'].quantile(0.01)
        upper = df_valid['单位租金'].quantile(0.99)
        df_valid = df_valid[(df_valid['单位租金'] >= lower) & (df_valid['单位租金'] <= upper)]

        if len(df_valid) > 0:
            # 归一化单位租金到 [0, 1]
            min_rent = df_valid['单位租金'].min()
            max_rent = df_valid['单位租金'].max()
            df_valid['热力强度'] = (df_valid['单位租金'] - min_rent) / (max_rent - min_rent)

            # 构造热力图数据：[纬度, 经度, 强度]
            heat_data = df_valid[['纬度', '经度', '热力强度']].values.tolist()

            # 添加热力图层
            HeatMap(
                heat_data,
                radius=15,
                blur=20,
                max_zoom=13,
                gradient={
                    0.0: 'blue',
                    0.3: 'cyan',
                    0.5: 'lime',
                    0.7: 'yellow',
                    1.0: 'red'
                }
            ).add_to(m)

        # 保存地图
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_path))

        if self.verbose:
            print(f"\n✓ 同心圆地图已保存: {output_path}")
            print(f"  就业中心: {center_name}")
            print(f"  同心圆半径: {', '.join([f'{r/1000:.0f}km' for r in radii])}")
            print(f"  热力图数据点: {len(df_valid):,}")

        return str(output_path)

    def generate_regression_plot(
        self,
        city_code: str,
        regression_results: Dict,
        output_file: str,
        use_min_distance: bool = True,
        center_name: Optional[str] = None,
        metric: str = '租金'
    ) -> str:
        """
        生成距离-租金散点图 + 回归线

        Args:
            city_code: 城市代码
            regression_results: 回归分析结果字典
            output_file: 输出文件路径
            use_min_distance: 是否使用最近距离（True）还是指定就业中心距离（False）
            center_name: 就业中心名称（当 use_min_distance=False 时使用）
            metric: 分析指标（'租金' 或 '单位租金'）

        Returns:
            输出文件路径
        """
        if self.df is None or self.city_code != city_code:
            self.load_distance_data(city_code)

        # 确定距离列
        if use_min_distance:
            if '最近距离(km)' not in self.df.columns:
                raise ValueError("数据中没有 '最近距离(km)' 列，请先计算最近距离")
            distance_col = '最近距离(km)'
            title_suffix = '所有就业中心（最近距离）'
        else:
            if center_name is None:
                raise ValueError("当 use_min_distance=False 时，必须指定 center_name")
            distance_col = f'距离_{center_name}'
            if distance_col not in self.df.columns:
                raise ValueError(f"数据中没有 '{distance_col}' 列")
            # 转换为公里
            self.df[f'{distance_col}(km)'] = self.df[distance_col] / 1000
            distance_col = f'{distance_col}(km)'
            title_suffix = center_name

        # 准备数据
        df_clean = self.df.dropna(subset=[distance_col, metric])

        # 过滤距离（如果回归结果中有限制）
        max_dist = regression_results.get('max_distance_km')
        if max_dist is not None:
            df_clean = df_clean[df_clean[distance_col] <= max_dist]

        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 7))

        # 绘制散点图
        ax.scatter(
            df_clean[distance_col],
            df_clean[metric],
            alpha=0.3,
            s=10,
            color='gray',
            label='实际数据'
        )

        # 绘制回归线
        model_type = regression_results.get('model', 'linear')
        r_squared = regression_results['r_squared']
        equation = regression_results['equation']

        x_range = np.linspace(df_clean[distance_col].min(), df_clean[distance_col].max(), 100)

        # 根据模型类型计算预测值
        if model_type == 'linear':
            slope = regression_results['slope']
            intercept = regression_results['intercept']
            y_pred = slope * x_range + intercept
        elif model_type.startswith('polynomial_'):
            coeffs = regression_results['coefficients']
            poly = np.poly1d(coeffs)
            y_pred = poly(x_range)
        elif model_type == 'logarithmic':
            slope = regression_results['slope']
            intercept = regression_results['intercept']
            y_pred = slope * np.log(x_range) + intercept
        elif model_type == 'exponential':
            a = regression_results['a']
            b = regression_results['b']
            y_pred = a * np.exp(b * x_range)
        else:
            # 默认使用线性回归
            slope = regression_results.get('slope', 0)
            intercept = regression_results.get('intercept', 0)
            y_pred = slope * x_range + intercept

        ax.plot(
            x_range,
            y_pred,
            'r--',
            linewidth=2,
            label=f'回归线: {equation}\nR² = {r_squared:.4f}'
        )

        # 按距离分组绘制平均值折线
        df_clean['距离分组'] = (df_clean[distance_col] // 2) * 2
        grouped = df_clean.groupby('距离分组')[metric].mean()

        ax.plot(
            grouped.index,
            grouped.values,
            'b-',
            linewidth=2,
            marker='o',
            markersize=6,
            label='分组平均值（每2km）'
        )

        # 设置标签和标题
        ax.set_xlabel('距离 (km)', fontsize=12)
        ax.set_ylabel(f'{metric} (元{"" if metric == "租金" else "/㎡"})', fontsize=12)
        ax.set_title(
            f'{self.city_name} - {metric}距离衰减分析\n{title_suffix}',
            fontsize=14,
            fontweight='bold'
        )
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        # 添加统计信息文本框
        stats_lines = [
            f'样本量: {regression_results["sample_size"]:,}',
        ]

        # 线性和对数模型显示衰减系数
        if model_type in ['linear', 'logarithmic']:
            slope = regression_results['slope']
            stats_lines.append(f'衰减系数: {abs(slope):.2f} 元/km')
        else:
            # 多项式和指数模型显示模型类型
            model_names = {
                'polynomial_2': '二次多项式',
                'polynomial_3': '三次多项式',
                'exponential': '指数衰减'
            }
            model_display = model_names.get(model_type, model_type)
            stats_lines.append(f'模型: {model_display}')

        stats_lines.append(f'决定系数: {r_squared:.4f}')
        stats_text = '\n'.join(stats_lines)
        ax.text(
            0.02, 0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        # 保存图表
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        if self.verbose:
            print(f"\n✓ 回归散点图已保存: {output_path}")
            print(f"  分析对象: {title_suffix}")
            print(f"  样本量: {regression_results['sample_size']:,}")
            print(f"  R²: {r_squared:.4f}")

        return str(output_path)

    def visualize_all_centers(
        self,
        city_code: str,
        output_dir: str
    ) -> Dict[str, Tuple[str, str]]:
        """
        批量生成所有就业中心的可视化

        Args:
            city_code: 城市代码
            output_dir: 输出目录

        Returns:
            字典：{就业中心名称: (同心圆地图路径, 散点图路径)}
        """
        if self.df is None or self.city_code != city_code:
            self.load_distance_data(city_code)

        centers = self.EMPLOYMENT_CENTERS.get(city_code, {})
        if not centers:
            raise ValueError(f"未定义城市 {city_code} 的就业中心")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}

        for center_name in centers.keys():
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"生成 {center_name} 可视化...")
                print(f"{'='*60}")

            # 生成同心圆地图
            circle_map_file = output_path / f'{city_code}_{center_name}_circle_map.html'
            try:
                circle_map_path = self.generate_circle_map(
                    city_code=city_code,
                    center_name=center_name,
                    output_file=str(circle_map_file)
                )
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠️ 生成同心圆地图失败: {e}")
                circle_map_path = None

            results[center_name] = (circle_map_path, None)

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"批量可视化完成")
            print(f"{'='*60}")
            success_count = sum(1 for paths in results.values() if paths[0] is not None)
            print(f"✓ 成功生成 {success_count}/{len(centers)} 个就业中心的可视化")

        return results


def visualize_city_circles(
    city_code: str,
    data_dir: str = 'data',
    output_dir: str = 'output/distance_maps'
) -> Dict[str, Tuple[str, str]]:
    """
    便捷函数：生成指定城市所有就业中心的同心圆地图

    Args:
        city_code: 城市代码
        data_dir: 数据目录
        output_dir: 输出目录

    Returns:
        字典：{就业中心名称: (同心圆地图路径, 散点图路径)}
    """
    visualizer = DistanceVisualizer(data_dir=data_dir, verbose=True)
    return visualizer.visualize_all_centers(city_code, output_dir)
