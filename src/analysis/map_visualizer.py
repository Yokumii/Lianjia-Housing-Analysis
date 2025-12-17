import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from pathlib import Path
from typing import Optional, List, Tuple

# 尝试导入 contextily 用于静态地图底图
try:
    import contextily as cx
    HAS_CONTEXTILY = True
except ImportError:
    HAS_CONTEXTILY = False


class MapVisualizer:
    """城市租金热力图可视化工具"""

    # 城市中心坐标（用于地图初始位置）
    CITY_CENTERS = {
        '北京': (39.9042, 116.4074),
        '上海': (31.2304, 121.4737),
        '广州': (23.1291, 113.2644),
        '深圳': (22.5431, 114.0579),
        '杭州': (30.2741, 120.1551)
    }

    # 城市代码到名称的映射
    CITY_CODE_MAP = {
        'bj': '北京',
        'sh': '上海',
        'gz': '广州',
        'sz': '深圳',
        'hz': '杭州'
    }

    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化地图可视化工具

        Args:
            data_dir: 数据文件目录
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        self.df = None
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

    @staticmethod
    def _wgs84_to_web_mercator(df: pd.DataFrame, lon: str = "经度", lat: str = "纬度") -> pd.DataFrame:
        """
        将经纬度转换为 Web Mercator 投影 (EPSG:3857) 以适配底图

        Args:
            df: 包含经纬度的 DataFrame
            lon: 经度列名
            lat: 纬度列名

        Returns:
            添加了 x, y 列的 DataFrame（Web Mercator 坐标）
        """
        k = 6378137  # 地球半径（米）
        df = df.copy()
        df["x"] = df[lon] * (k * np.pi / 180.0)
        df["y"] = np.log(np.tan((90 + df[lat]) * np.pi / 360.0)) * k
        return df

    def load_coordinate_data(self, city_code: str) -> pd.DataFrame:
        """
        加载指定城市的坐标数据

        Args:
            city_code: 城市代码（bj/sh/gz/sz/hz）

        Returns:
            包含坐标的 DataFrame

        Raises:
            FileNotFoundError: 数据文件不存在
        """
        city_name = self.CITY_CODE_MAP.get(city_code)
        if not city_name:
            raise ValueError(f"无效的城市代码: {city_code}")

        # 读取坐标数据文件
        coord_file = self.data_dir / f"{city_code}_rental_with_coordinate.csv"

        if not coord_file.exists():
            raise FileNotFoundError(f"坐标数据文件不存在: {coord_file}")

        df = pd.read_csv(coord_file)

        if self.verbose:
            print(f"\n✓ 读取 {city_name} 坐标数据: {len(df):,} 行")

        # 过滤有效坐标（去除 NaN 和异常值）
        df_valid = df.dropna(subset=['经度', '纬度', '单位租金'])

        if self.verbose:
            valid_count = len(df_valid)
            total_count = len(df)
            coverage = valid_count / total_count * 100 if total_count > 0 else 0
            print(f"✓ 有效坐标数据: {valid_count:,} 行 ({coverage:.1f}% 覆盖率)")

        # 过滤极值（1st 和 99th 百分位，避免异常值影响热力图）
        q1 = df_valid['单位租金'].quantile(0.01)
        q99 = df_valid['单位租金'].quantile(0.99)
        df_filtered = df_valid[
            (df_valid['单位租金'] >= q1) &
            (df_valid['单位租金'] <= q99)
        ]

        if self.verbose:
            print(f"✓ 过滤极值后: {len(df_filtered):,} 行 (保留 {q1:.1f}~{q99:.1f} 元/㎡/月)")

        self.df = df_filtered
        return df_filtered

    def generate_heatmap(
        self,
        city_code: str,
        output_dir: str = 'output/maps',
        zoom_start: int = 11,
        radius: int = 15,
        blur: int = 20,
        max_zoom: int = 13,
        save_png: bool = True
    ) -> Tuple[str, Optional[str]]:
        """
        生成城市租金热力图（交互式 HTML 地图 + 可选静态 PNG 图片）

        Args:
            city_code: 城市代码（bj/sh/gz/sz/hz）
            output_dir: 输出目录
            zoom_start: 初始缩放级别（默认 11）
            radius: 热力图半径（默认 15）
            blur: 热力图模糊度（默认 20）
            max_zoom: 最大缩放级别（默认 13）
            save_png: 是否同时生成静态 PNG 图片（默认 True）

        Returns:
            (HTML文件路径, PNG文件路径) 的元组
        """
        city_name = self.CITY_CODE_MAP.get(city_code)

        # 加载数据（如果未加载）
        if self.df is None or '城市' not in self.df.columns or self.df['城市'].iloc[0] != city_name:
            self.load_coordinate_data(city_code)

        # 获取城市中心坐标
        center_lat, center_lng = self.CITY_CENTERS.get(city_name, (39.9042, 116.4074))

        if self.verbose:
            print(f"\n生成 {city_name} 租金热力图...")
            print(f"  中心坐标: ({center_lat:.4f}, {center_lng:.4f})")
            print(f"  数据点数: {len(self.df):,}")

        # === 1. 生成交互式 HTML 地图 ===
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom_start,
            tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
            attr='高德地图'
        )

        # 准备热力图数据：[[lat, lng, weight], ...]
        heat_data = [
            [row['纬度'], row['经度'], row['单位租金']]
            for _, row in self.df.iterrows()
        ]

        # 添加热力图层
        HeatMap(
            heat_data,
            radius=radius,
            blur=blur,
            max_zoom=max_zoom,
            gradient={
                0.0: 'blue',
                0.3: 'cyan',
                0.5: 'lime',
                0.7: 'yellow',
                1.0: 'red'
            }
        ).add_to(m)

        # 保存 HTML 文件
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        html_file = output_path / f'{city_code}_rental_heatmap.html'

        m.save(str(html_file))

        if self.verbose:
            print(f"\n✓ 交互式地图已保存: {html_file}")
            print(f"  文件大小: {html_file.stat().st_size / 1024:.1f} KB")

        # === 2. 生成静态 PNG 图片 ===
        png_file = None
        if save_png:
            png_file = self._generate_static_map(
                city_code=city_code,
                city_name=city_name,
                output_dir=output_dir
            )

        return str(html_file), png_file

    def _generate_static_map(
        self,
        city_code: str,
        city_name: str,
        output_dir: str = 'output/maps'
    ) -> Optional[str]:
        """
        生成静态地图（PNG 图片，热力图形式）

        Args:
            city_code: 城市代码
            city_name: 城市名称
            output_dir: 输出目录

        Returns:
            PNG 文件路径，如果生成失败则返回 None
        """
        if self.verbose:
            print(f"\n生成 {city_name} 静态热力图...")

        fig = plt.figure(figsize=(14, 14))
        ax = plt.gca()

        # 检查是否可以加载底图
        if HAS_CONTEXTILY:
            if self.verbose:
                print("  使用高德地图底图...")

            # 1. 坐标转换 (WGS84 -> Web Mercator)
            df_projected = self._wgs84_to_web_mercator(self.df)
            x_col, y_col = 'x', 'y'

            # 2. 使用 hexbin 绘制热力图（六边形密度图）
            # gridsize 控制六边形的大小（数值越大，六边形越小，细节越多）
            hexbin = ax.hexbin(
                df_projected[x_col],
                df_projected[y_col],
                C=df_projected['单位租金'],  # 颜色由单位租金决定
                gridsize=50,  # 六边形网格大小
                cmap='RdYlBu_r',  # 红色=高租金，蓝色=低租金
                reduce_C_function=np.mean,  # 每个六边形内取平均值
                mincnt=1,  # 至少包含1个点才显示
                alpha=0.8,
                edgecolors='none'
            )

            # 3. 添加高德底图
            amap_url = 'http://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7'
            try:
                cx.add_basemap(ax, source=amap_url, crs='EPSG:3857', attribution='高德地图', alpha=0.5)
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠️ 底图加载失败: {e} (可能网络超时)")

            # 移除坐标轴刻度
            ax.set_axis_off()

        else:
            # 无 contextily 库，绘制无底图版本
            if self.verbose:
                print("  ⚠️ 未检测到 contextily 库，绘制无底图版本")

            # 使用 hexbin 绘制热力图
            hexbin = ax.hexbin(
                self.df['经度'],
                self.df['纬度'],
                C=self.df['单位租金'],
                gridsize=50,
                cmap='RdYlBu_r',
                reduce_C_function=np.mean,
                mincnt=1,
                alpha=0.8,
                edgecolors='w',
                linewidths=0.2
            )

            ax.set_xlabel('经度', fontsize=12)
            ax.set_ylabel('纬度', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_aspect('equal')

        # 添加标题
        plt.title(
            f'{city_name} 租房价格热力图 (颜色越红越贵)',
            fontsize=16,
            fontweight='bold',
            pad=20
        )

        # 添加颜色条
        cbar = plt.colorbar(hexbin, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('单位租金 (元/㎡/月)', fontsize=12)

        # 保存 PNG 文件
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        png_file = output_path / f'{city_code}_rental_heatmap.png'

        plt.savefig(png_file, dpi=300, bbox_inches='tight')
        plt.close(fig)

        if self.verbose:
            print(f"\n✓ 静态热力图已保存: {png_file}")
            print(f"  文件大小: {png_file.stat().st_size / 1024:.1f} KB")

        return str(png_file)

    def generate_all_cities(
        self,
        city_codes: Optional[List[str]] = None,
        output_dir: str = 'output/maps',
        **heatmap_kwargs
    ) -> dict:
        """
        批量生成所有城市的热力图

        Args:
            city_codes: 城市代码列表（默认所有城市）
            output_dir: 输出目录
            **heatmap_kwargs: 传递给 generate_heatmap 的额外参数

        Returns:
            城市代码到 (HTML路径, PNG路径) 元组的映射
        """
        if city_codes is None:
            city_codes = ['bj', 'sh', 'gz', 'sz', 'hz']

        results = {}

        for city_code in city_codes:
            try:
                html_file, png_file = self.generate_heatmap(
                    city_code=city_code,
                    output_dir=output_dir,
                    **heatmap_kwargs
                )
                results[city_code] = (html_file, png_file)
            except Exception as e:
                if self.verbose:
                    print(f"\n❌ {self.CITY_CODE_MAP.get(city_code, city_code)} 热力图生成失败: {e}")
                results[city_code] = (None, None)

        if self.verbose:
            print("\n" + "="*80)
            success_count = len([v for v in results.values() if v[0] is not None])
            print(f"✓ 批量生成完成: {success_count} / {len(city_codes)} 个城市成功")
            print("="*80)

        return results


def visualize_city_heatmap(
    city_code: str,
    data_dir: str = 'data',
    output_dir: str = 'output/maps',
    verbose: bool = True,
    **heatmap_kwargs
) -> Tuple[str, Optional[str]]:
    """
    生成单个城市的租金热力图（便捷函数）

    Args:
        city_code: 城市代码（bj/sh/gz/sz/hz）
        data_dir: 数据文件目录
        output_dir: 输出目录
        verbose: 是否打印详细日志
        **heatmap_kwargs: 传递给热力图的额外参数

    Returns:
        (HTML文件路径, PNG文件路径) 的元组
    """
    visualizer = MapVisualizer(data_dir=data_dir, verbose=verbose)
    return visualizer.generate_heatmap(
        city_code=city_code,
        output_dir=output_dir,
        **heatmap_kwargs
    )


def visualize_all_cities(
    city_codes: Optional[List[str]] = None,
    data_dir: str = 'data',
    output_dir: str = 'output/maps',
    verbose: bool = True,
    **heatmap_kwargs
) -> dict:
    """
    批量生成所有城市的租金热力图（便捷函数）

    Args:
        city_codes: 城市代码列表（默认所有城市）
        data_dir: 数据文件目录
        output_dir: 输出目录
        verbose: 是否打印详细日志
        **heatmap_kwargs: 传递给热力图的额外参数

    Returns:
        城市代码到 (HTML路径, PNG路径) 元组的映射
    """
    visualizer = MapVisualizer(data_dir=data_dir, verbose=verbose)
    return visualizer.generate_all_cities(
        city_codes=city_codes,
        output_dir=output_dir,
        **heatmap_kwargs
    )
