import os
import pandas as pd
from typing import List, Dict, Any, Optional
from ..items.models import (
    HouseItem, RentalHouse, SecondHandHouse,
    CSV_COLUMNS_RENTAL, CSV_COLUMNS_SECONDHAND
)


class CsvWriter:
    """CSV 文件写入器"""

    def __init__(self, filename: str):
        """
        初始化 CSV 写入器

        Args:
            filename: 输出 CSV 文件名
        """
        self.filename = filename
        self.file_exists = os.path.exists(filename)

    def append(self, items: List[HouseItem], verbose: bool = True) -> int:
        """
        将房源数据追加到 CSV 文件
        Args:
            items: HouseItem 对象列表
            verbose: 是否打印日志

        Returns:
            int: 实际写入的行数
        """
        if not items:
            return 0

        # 转换为字典列表
        data_dicts = [item.to_dict() for item in items]
        df_new = pd.DataFrame(data_dicts)

        # 获取 CSV 列顺序
        if items and isinstance(items[0], RentalHouse):
            columns = CSV_COLUMNS_RENTAL
        elif items and isinstance(items[0], SecondHandHouse):
            columns = CSV_COLUMNS_SECONDHAND
        else:
            # 默认使用 df 现有的列
            columns = df_new.columns.tolist()

        # 调整列顺序（只保留存在的列）
        existing_cols = [c for c in columns if c in df_new.columns]
        df_new = df_new[existing_cols]

        # 写入 CSV
        try:
            df_new.to_csv(
                self.filename,
                mode='a',
                index=False,
                encoding='utf-8-sig',
                header=not self.file_exists,
            )
            self.file_exists = True

            rows_written = len(df_new)
            if verbose:
                print(f"✓ 已写入 {rows_written} 条数据到: {self.filename}")

            return rows_written

        except PermissionError:
            print(f"[错误] 文件被占用，请关闭: {self.filename}")
            raise
        except Exception as e:
            print(f"[错误] 写入 CSV 失败: {e}")
            raise

    def get_row_count(self) -> int:
        """获取 CSV 文件中的行数"""
        if not os.path.exists(self.filename):
            return 0

        try:
            df = pd.read_csv(self.filename, encoding='utf-8-sig')
            return len(df)
        except Exception:
            return 0

    def __repr__(self) -> str:
        row_count = self.get_row_count()
        return f"CsvWriter(file={self.filename}, rows={row_count})"
