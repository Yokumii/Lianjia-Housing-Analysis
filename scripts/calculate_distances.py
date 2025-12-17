#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.distance_calculator import DistanceCalculator
from settings import AMAP_API_KEY


def main():
    parser = argparse.ArgumentParser(
        description='计算房源到核心就业区的距离',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 计算北京所有房源到就业中心的驾车距离
  python scripts/calculate_distances.py --city bj

  # 计算上海和深圳的距离（驾车）
  python scripts/calculate_distances.py --city sh sz

  # 计算所有城市的直线距离
  python scripts/calculate_distances.py --distance-type 0

  # 强制重新计算（忽略缓存）
  python scripts/calculate_distances.py --city bj --force

  # 静默模式
  python scripts/calculate_distances.py --city bj --quiet
        """
    )

    parser.add_argument(
        '--city',
        nargs='+',
        choices=['bj', 'sh', 'gz', 'sz', 'hz'],
        default=['bj', 'sh', 'gz', 'sz', 'hz'],
        help='城市代码（可指定多个，默认所有城市）'
    )

    parser.add_argument(
        '--distance-type',
        type=int,
        choices=[0, 1],
        default=1,
        help='距离类型：0=直线距离, 1=驾车距离（默认）'
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='数据目录（默认: data）'
    )

    parser.add_argument(
        '--cache-dir',
        type=str,
        default='cache/distances',
        help='缓存目录（默认: cache/distances）'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新计算（忽略缓存）'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式（不打印详细日志）'
    )

    args = parser.parse_args()

    # 检查 API key
    if not AMAP_API_KEY:
        print("❌ 错误: 未配置高德地图 API key")
        print("请在 settings.py 中设置 AMAP_API_KEY")
        return 1

    # 初始化计算器
    calculator = DistanceCalculator(
        api_key=AMAP_API_KEY,
        cache_dir=args.cache_dir,
        verbose=not args.quiet
    )

    # 处理每个城市
    for city_code in args.city:
        print(f"\n{'='*60}")
        print(f"开始计算 {city_code.upper()} 的距离...")
        print(f"{'='*60}")

        # 构造坐标数据文件路径
        coord_file = Path(args.data_dir) / f'{city_code}_rental_with_coordinate.csv'

        if not coord_file.exists():
            print(f"⚠️ 跳过 {city_code}: 坐标数据文件不存在 ({coord_file})")
            continue

        try:
            # 计算距离
            df_result = calculator.calculate_distances(
                city_code=city_code,
                coord_data_file=str(coord_file),
                distance_type=args.distance_type,
                force_recalculate=args.force
            )

            # 保存结果
            output_file = Path(args.data_dir) / f'{city_code}_rental_with_distances.csv'
            df_result.to_csv(output_file, index=False, encoding='utf-8-sig')

            if not args.quiet:
                print(f"\n✓ 结果已保存: {output_file}")
                print(f"  总行数: {len(df_result):,}")
                distance_cols = [col for col in df_result.columns if col.startswith('距离_')]
                print(f"  距离列数: {len(distance_cols)}")

        except Exception as e:
            print(f"❌ 处理 {city_code} 时出错: {e}")
            continue

    print(f"\n{'='*60}")
    print("距离计算完成")
    print(f"{'='*60}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
