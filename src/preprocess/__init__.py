from .data_cleaner import DataCleaner
from .coordinates import add_coordinates


__all__ = ['DataCleaner', 'add_coordinates', 'process_rental_data']


def process_rental_data(
    input_path: str,
    output_path: str,
    api_key: str = '',
    add_coords: bool = False,
    verbose: bool = True,
) -> None:
    """
    完整的数据预处理流程

    包括：数据清洗、坐标添加等

    Args:
        input_path: 输入 CSV 文件路径
        output_path: 输出 CSV 文件路径
        api_key: 高德 API Key（用于坐标添加，可选）
        add_coords: 是否添加地理坐标
        verbose: 是否打印详细日志
    """
    import os
    import pandas as pd

    if not os.path.exists(input_path):
        print(f"❌ 文件不存在: {input_path}")
        return

    # 读取数据
    try:
        df = pd.read_csv(input_path, encoding='utf-8-sig')
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    # 步骤 1: 数据清洗
    if verbose:
        print("\n" + "=" * 60)
        print("步骤 1: 数据清洗")
        print("=" * 60)

    cleaner = DataCleaner(verbose=verbose)
    df_clean = cleaner.clean(df)

    # 步骤 2: 添加坐标（可选）
    if add_coords and api_key:
        if verbose:
            print("\n" + "=" * 60)
            print("步骤 2: 添加地理坐标")
            print("=" * 60)
        df_clean = add_coordinates(df_clean, api_key, verbose=verbose)

    # 步骤 3: 保存数据
    try:
        df_clean.to_csv(output_path, index=False, encoding='utf-8-sig')
        cleaner.print_summary(df_clean)
        print(f"\n📄 输出文件: {output_path}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")

if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("使用方式: python -m src.preprocess <input.csv> [output.csv]")
        print("\n示例:")
        print("  python -m src.preprocess data/bj_rental.csv data/bj_rental_clean.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.csv', '_clean.csv')