#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.preprocess import process_rental_data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='租房数据预处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 处理北京租房数据
  python scripts/preprocess_data.py --city bj

  # 同时处理多个城市
  python scripts/preprocess_data.py --city bj sh gz

  # 自定义输入输出文件
  python scripts/preprocess_data.py \\
    --input data/bj_rental.csv \\
    --output data/bj_rental_clean.csv

  # 添加地理坐标
  python scripts/preprocess_data.py --city bj \\
    --add-coords --api-key "你的高德API_KEY"

  # 静默模式（不打印日志）
  python scripts/preprocess_data.py --city bj --quiet
        """,
    )

    parser.add_argument(
        '--city',
        type=str,
        nargs='+',
        help='城市代码 (bj, sh, sz, gz, hz，可多选)',
    )

    parser.add_argument(
        '--input',
        type=str,
        help='输入 CSV 文件路径（与 --city 互斥）',
    )

    parser.add_argument(
        '--output',
        type=str,
        help='输出 CSV 文件路径（与 --city 互斥）',
    )

    parser.add_argument(
        '--add-coords',
        action='store_true',
        help='是否添加地理坐标',
    )

    parser.add_argument(
        '--api-key',
        type=str,
        default='',
        help='高德地图 Web 服务 API Key',
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式，不打印详细日志',
    )

    args = parser.parse_args()

    # 验证参数
    if args.city and (args.input or args.output):
        print("❌ 错误: --city 和 --input/--output 不能同时使用")
        sys.exit(1)

    if not args.city and not args.input:
        print("❌ 错误: 必须指定 --city 或 --input")
        sys.exit(1)

    if args.add_coords and not args.api_key:
        print("⚠️  警告: --add-coords 需要提供 --api-key，将跳过坐标添加")
        args.add_coords = False

    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)

    verbose = not args.quiet

    if args.city:
        # 按城市处理
        city_names = {
            'bj': '北京',
            'sh': '上海',
            'sz': '深圳',
            'gz': '广州',
            'hz': '杭州',
        }

        for city_code in args.city:
            city_name = city_names.get(city_code)
            if not city_name:
                print(f"⚠️  未知的城市代码: {city_code}")
                continue

            input_file = data_dir / f"{city_name}_租房数据.csv"

            if not input_file.exists():
                print(f"⚠️  文件不存在，跳过: {input_file}")
                continue

            # 根据是否添加坐标，决定输出文件名
            if args.add_coords:
                output_file = data_dir / f"{city_name}_租房数据_含坐标.csv"
            else:
                output_file = data_dir / f"{city_name}_租房数据_clean.csv"

            print(f"\n{'='*60}")
            print(f"处理城市: {city_name} ({city_code})")
            print(f"{'='*60}")

            process_rental_data(
                str(input_file),
                str(output_file),
                api_key=args.api_key,
                add_coords=args.add_coords,
                verbose=verbose,
            )

    else:
        # 使用指定的输入输出文件
        if not args.output:
            if args.add_coords:
                args.output = args.input.replace('.csv', '_含坐标.csv')
            else:
                args.output = args.input.replace('.csv', '_clean.csv')

        print(f"\n{'='*60}")
        print(f"处理文件: {args.input}")
        print(f"{'='*60}")

        process_rental_data(
            args.input,
            args.output,
            api_key=args.api_key,
            add_coords=args.add_coords,
            verbose=verbose,
        )


if __name__ == '__main__':
    main()
