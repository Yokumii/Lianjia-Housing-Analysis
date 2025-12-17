import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class LayoutAnalyzer:
    """户型分析器"""

    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化分析器

        Args:
            data_dir: 数据目录
            verbose: 是否打印详细日志
        """
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        self.cities = ['bj', 'sh', 'sz', 'gz', 'hz']
        self.city_names = {
            'bj': '北京',
            'sh': '上海',
            'sz': '深圳',
            'gz': '广州',
            'hz': '杭州'
        }
        self.layouts = ['一居', '两居', '三居']
        self.df_all = None
        self.stats = None

    def _log(self, msg: str):
        """打印日志"""
        if self.verbose:
            print(msg)

    def load_data(self) -> pd.DataFrame:
        """加载所有城市的清洗数据"""
        self._log("📂 正在加载数据...")

        all_data = []
        for city_code in self.cities:
            file_path = self.data_dir / f"{city_code}_rental_clean.csv"

            if not file_path.exists():
                self._log(f"⚠️  文件不存在: {file_path}")
                continue

            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                df['城市代码'] = city_code
                df['城市'] = self.city_names[city_code]
                all_data.append(df)
                self._log(f"✓ {self.city_names[city_code]:6} 加载完成: {len(df):6,} 条记录")
            except Exception as e:
                self._log(f"❌ {file_path} 读取失败: {e}")

        if not all_data:
            self._log("❌ 未加载任何数据")
            return pd.DataFrame()

        self.df_all = pd.concat(all_data, ignore_index=True)
        self._log(f"\n✅ 总计加载: {len(self.df_all):,} 条记录\n")
        return self.df_all

    def calculate_statistics(self) -> pd.DataFrame:
        """
        按城市和户型分组，计算统计数据

        Returns:
            统计汇总表 (城市 × 户型)
        """
        if self.df_all is None or self.df_all.empty:
            self._log("❌ 无数据可分析")
            return None

        self._log("📊 计算统计数据...\n")

        # 按城市 × 户型分组
        grouped = self.df_all.groupby(['城市', '户型']).agg({
            '租金': ['count', 'mean', 'median', 'min', 'max', 'std'],
            '单位租金': ['mean', 'median', 'min', 'max'],
        }).round(1)

        # 展平多层索引
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

        # 重命名列名
        grouped = grouped.rename(columns={
            '租金_count': '房源数',
            '租金_mean': '均价',
            '租金_median': '中位价',
            '租金_min': '最低价',
            '租金_max': '最高价',
            '租金_std': '标准差',
            '单位租金_mean': '单价均值',
            '单位租金_median': '单价中位',
            '单位租金_min': '单价最低',
            '单位租金_max': '单价最高',
        })

        self.stats = grouped
        return grouped

    def get_city_layout_comparison(self) -> pd.DataFrame:
        """
        获取城市-户型对比表（关键指标）

        Returns:
            包含房源数、均价、中位价、最低价、最高价的汇总表
        """
        if self.stats is None:
            return None

        # 选择关键列
        key_columns = ['房源数', '均价', '中位价', '最低价', '最高价', '单价均值']
        result = self.stats[key_columns].copy()

        return result

    def print_summary_table(self):
        """打印对比表"""
        if self.stats is None:
            self._log("❌ 请先调用 calculate_statistics()")
            return

        print("\n" + "="*100)
        print("📊 5城户型对比总表 - 按户型分类")
        print("="*100)

        # 按户型分组打印
        for layout in self.layouts:
            print(f"\n【{layout}房源统计】")
            print("-" * 100)

            # 获取该户型的数据
            layout_data = self.stats.loc[(slice(None), layout), :]
            layout_data.index = layout_data.index.get_level_values('城市')

            # 选择关键列
            key_cols = ['房源数', '均价', '中位价', '最低价', '最高价', '单价均值']
            display_df = layout_data[key_cols].copy()

            # 格式化
            display_df['房源数'] = display_df['房源数'].astype(int)
            display_df['均价'] = display_df['均价'].apply(lambda x: f"¥{x:,.0f}")
            display_df['中位价'] = display_df['中位价'].apply(lambda x: f"¥{x:,.0f}")
            display_df['最低价'] = display_df['最低价'].apply(lambda x: f"¥{x:,.0f}")
            display_df['最高价'] = display_df['最高价'].apply(lambda x: f"¥{x:,.0f}")
            display_df['单价均值'] = display_df['单价均值'].apply(lambda x: f"¥{x:.1f}")

            print(display_df.to_string())

        print("\n" + "="*100 + "\n")

    def get_city_comparison_by_layout(self) -> Dict[str, pd.DataFrame]:
        """
        按户型返回城市对比数据

        Returns:
            {户型: DataFrame} 的字典
        """
        if self.stats is None:
            return {}

        result = {}
        for layout in self.layouts:
            try:
                layout_data = self.stats.loc[(slice(None), layout), :].copy()
                layout_data.index = layout_data.index.get_level_values('城市')
                result[layout] = layout_data
            except KeyError:
                continue

        return result

    def get_stats_by_city_layout(self) -> Dict[str, Dict[str, dict]]:
        """
        获取结构化的统计数据

        Returns:
            {城市: {户型: {统计项: 值}}} 的嵌套字典
        """
        if self.df_all is None or self.df_all.empty:
            return {}

        result = {}

        for city in self.df_all['城市'].unique():
            result[city] = {}
            city_data = self.df_all[self.df_all['城市'] == city]

            for layout in self.layouts:
                layout_data = city_data[city_data['户型'] == layout]

                if layout_data.empty:
                    continue

                result[city][layout] = {
                    'count': len(layout_data),
                    'mean_rent': layout_data['租金'].mean(),
                    'median_rent': layout_data['租金'].median(),
                    'min_rent': layout_data['租金'].min(),
                    'max_rent': layout_data['租金'].max(),
                    'std_rent': layout_data['租金'].std(),
                    'mean_unit_price': layout_data['单位租金'].mean(),
                    'median_unit_price': layout_data['单位租金'].median(),
                    'min_unit_price': layout_data['单位租金'].min(),
                    'max_unit_price': layout_data['单位租金'].max(),
                }

        return result

    def export_stats_to_csv(self, output_path: str = 'data/layout_comparison.csv'):
        """
        导出统计数据到 CSV

        Args:
            output_path: 输出文件路径
        """
        if self.stats is None:
            self._log("❌ 请先调用 calculate_statistics()")
            return

        self.stats.to_csv(output_path, encoding='utf-8-sig')
        self._log(f"✅ 数据已导出到: {output_path}")
