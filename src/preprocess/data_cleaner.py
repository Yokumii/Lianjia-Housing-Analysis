import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from .constants import (
    THRESHOLD_AREA_MIN,
    THRESHOLD_AREA_MAX,
    THRESHOLD_UNIT_PRICE_MAX,
    THRESHOLD_UNIT_PRICE_MIN,
    THRESHOLD_RENT_MIN,
    THRESHOLD_RENT_MAX,
    CRITICAL_COLUMNS,
    OUTPUT_COLUMNS,
    DEFAULT_BRAND,
    SUMMARY_COLUMNS,
    DECIMAL_PLACES,
)


class DataCleaner:
    """数据清洗器"""

    def __init__(self, verbose: bool = True):
        """
        初始化数据清洗器

        Args:
            verbose: 是否打印详细日志
        """
        self.verbose = verbose
        self.stats = {
            'original_count': 0,
            'after_dedup': 0,
            'after_4plus_removal': 0,
            'after_area_cleanup': 0,
            'after_critical_cleanup': 0,
            'final_count': 0,
        }

    def _log(self, msg: str):
        """打印日志（如果启用详细模式）"""
        if self.verbose:
            print(msg)

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        执行完整的数据清洗流程

        Args:
            df: 输入的 DataFrame

        Returns:
            清洗后的 DataFrame
        """
        self.stats['original_count'] = len(df)
        self._log(f"📊 原始数据量: {len(df)} 条")

        # 步骤 1: 标准化缺失值
        df = self._standardize_missing_values(df)

        # 步骤 2: 智能去重
        df = self._deduplicate_by_link(df)

        # 步骤 3: 删除"四居+"房源
        df = self._remove_4plus_layout(df)

        # 步骤 4: 业务规则异常值清洗
        df = self._clean_business_outliers(df)

        # 步骤 5: 缺失值处理
        df = self._handle_missing_values(df)

        # 步骤 6: 计算单位面积租金
        df = self._calculate_unit_price(df)

        # 步骤 7: 列顺序整理
        df = self._reorder_columns(df)

        self.stats['final_count'] = len(df)
        return df

    def _standardize_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 1: 标准化缺失值（将"未知"、空值统一转为 NaN）"""
        self._log("🧹 正在标准化缺失值(未知/0/空)...")

        # 字符串类型的"未知"或空字符 -> NaN
        df.replace(['未知', ' ', ''], np.nan, inplace=True)

        # 数值字段转换与 0 值处理
        numeric_cols = ['租金', '面积']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df.loc[df[col] == 0, col] = np.nan

        return df

    def _deduplicate_by_link(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 2: 智能去重（按链接分组，取每列的第一个非空值）"""
        if '链接' not in df.columns:
            return df

        self._log("🔄 正在合并重复项并互补缺失数据...")
        before_dedup = len(df)

        # 按链接分组，取每列的第一个非空值
        df = df.groupby('链接', as_index=False).first()

        self.stats['after_dedup'] = len(df)
        removed = before_dedup - len(df)
        if removed > 0:
            self._log(f"✂️  合并去重: {before_dedup} -> {len(df)} 条 (减少 {removed} 条)")

        return df

    def _remove_4plus_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 3: 删除"四居+"房源"""
        if '户型' not in df.columns:
            return df

        count_4plus = len(df[df['户型'] == '四居+'])
        if count_4plus > 0:
            self._log(f"🚫 剔除 '四居+' 房源: {count_4plus} 条")
            df = df[df['户型'] != '四居+']

        self.stats['after_4plus_removal'] = len(df)
        return df

    def _clean_business_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 4: 业务规则异常值清洗"""
        self._log("🔍 正在进行业务规则异常值清洗...")

        # 面积异常（仅针对非空值）
        if '面积' in df.columns:
            outlier_area = df[
                df['面积'].notna() &
                ((df['面积'] < THRESHOLD_AREA_MIN) | (df['面积'] > THRESHOLD_AREA_MAX))
            ]
            if not outlier_area.empty:
                self._log(f"  🗑️  剔除面积异常数据: {len(outlier_area)} 条")
                self._log(f"     (规则: 面积 < {THRESHOLD_AREA_MIN}㎡ 或 > {THRESHOLD_AREA_MAX}㎡)")
                # 保留：(面积在范围内) 或 (面积为空)
                df = df[
                    (
                        (df['面积'] >= THRESHOLD_AREA_MIN) &
                        (df['面积'] <= THRESHOLD_AREA_MAX)
                    ) |
                    df['面积'].isna()
                ]

        # 租金异常（仅针对非空值）
        if '租金' in df.columns:
            outlier_rent = df[
                df['租金'].notna() &
                ((df['租金'] < THRESHOLD_RENT_MIN) | (df['租金'] > THRESHOLD_RENT_MAX))
            ]
            if not outlier_rent.empty:
                self._log(f"  🗑️  剔除租金异常数据: {len(outlier_rent)} 条")
                self._log(f"     (规则: 租金 < {THRESHOLD_RENT_MIN}元 或 > {THRESHOLD_RENT_MAX}元)")
                df = df[
                    (
                        (df['租金'] >= THRESHOLD_RENT_MIN) &
                        (df['租金'] <= THRESHOLD_RENT_MAX)
                    ) |
                    df['租金'].isna()
                ]

        self.stats['after_area_cleanup'] = len(df)
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 5: 缺失值处理"""
        self._log("🔧 正在处理缺失值...")

        # 品牌缺失 -> 填充为默认值
        if '品牌' in df.columns:
            brand_missing_count = df['品牌'].isna().sum()
            if brand_missing_count > 0:
                df['品牌'] = df['品牌'].fillna(DEFAULT_BRAND)
                self._log(f"  🔹 已填充 {brand_missing_count} 条缺失的品牌信息为 '{DEFAULT_BRAND}'")

        # 关键字段缺失 -> 删除记录
        cols_to_drop = [c for c in CRITICAL_COLUMNS if c in df.columns]
        if cols_to_drop:
            self._log(f"  🔍 检查关键字段缺失情况: {cols_to_drop}")
            initial_len = len(df)
            df.dropna(subset=cols_to_drop, inplace=True)
            dropped_len = initial_len - len(df)

            if dropped_len > 0:
                self._log(f"  🗑️  已直接删除 {dropped_len} 条缺失关键信息的数据")
            else:
                self._log("  ✅ 关键字段数据完整，无需删除。")

        self.stats['after_critical_cleanup'] = len(df)
        return df

    def _calculate_unit_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 6: 计算单位面积租金"""
        self._log("🧮 计算单位面积租金(元/平米)...")

        if '租金' not in df.columns or '面积' not in df.columns:
            self._log("  ⚠️  缺少'租金'或'面积'列，跳过计算")
            return df

        # 确保是数值类型
        df['租金'] = pd.to_numeric(df['租金'], errors='coerce')
        df['面积'] = pd.to_numeric(df['面积'], errors='coerce')

        # 计算单位租金
        df['单位租金'] = (df['租金'] / df['面积']).round(DECIMAL_PLACES)

        # 异常值清洗：单价逻辑异常
        outlier_unit = df[
            (df['单位租金'] > THRESHOLD_UNIT_PRICE_MAX) |
            (df['单位租金'] < THRESHOLD_UNIT_PRICE_MIN)
        ]
        if not outlier_unit.empty:
            self._log(f"  🗑️  剔除单价逻辑异常数据: {len(outlier_unit)} 条")
            self._log(
                f"     (规则: 单价 > {THRESHOLD_UNIT_PRICE_MAX} "
                f"或 < {THRESHOLD_UNIT_PRICE_MIN}元/平/月)"
            )
            df = df[
                (df['单位租金'] <= THRESHOLD_UNIT_PRICE_MAX) &
                (df['单位租金'] >= THRESHOLD_UNIT_PRICE_MIN)
            ]

        return df

    def _reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤 7: 列顺序整理"""
        # 按首选顺序排列列
        final_cols = [c for c in OUTPUT_COLUMNS if c in df.columns]
        # 把剩余的列（如果有）加到后面
        final_cols += [c for c in df.columns if c not in final_cols]

        return df[final_cols]

    def print_summary(self, df: pd.DataFrame) -> None:
        """打印清洗过程统计和数据摘要"""
        if not self.verbose:
            return

        print("\n" + "=" * 60)
        print("✅ 数据清洗完成！")
        print("=" * 60)

        print("\n📊 清洗过程统计:")
        print(f"  原始数据量:           {self.stats['original_count']:7d} 条")
        print(f"  去重后:              {self.stats['after_dedup']:7d} 条")
        print(f"  删除四居+后:          {self.stats['after_4plus_removal']:7d} 条")
        print(f"  异常值清洗后:        {self.stats['after_area_cleanup']:7d} 条")
        print(f"  关键字段清洗后:      {self.stats['after_critical_cleanup']:7d} 条")
        print(f"  最终有效数据:        {self.stats['final_count']:7d} 条")

        # 数据概览
        summary_cols = [c for c in SUMMARY_COLUMNS if c in df.columns]
        if summary_cols:
            print("\n📈 数据概览:")
            print(df[summary_cols].describe().round(DECIMAL_PLACES))
