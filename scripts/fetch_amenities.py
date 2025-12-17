#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.amenity_crawler import AmenityCrawler


def main():
    parser = argparse.ArgumentParser(
        description='获取周边配套设施数据（星巴克、麦当劳）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取北京的配套数据（1km半径）
  python scripts/fetch_amenities.py --city bj

  # 获取上海的配套数据（500m半径）
  python scripts/fetch_amenities.py --city sh --radius 500

  # 使用10个并发线程加速
  python scripts/fetch_amenities.py --city bj --workers 10

  # 从头开始（忽略断点）
  python scripts/fetch_amenities.py --city bj --no-resume
        """
    )

    parser.add_argument(
        '--city',
        type=str,
        required=True,
        choices=['bj', 'sh', 'gz', 'sz', 'hz'],
        help='城市代码'
    )

    parser.add_argument(
        '--radius',
        type=int,
        default=1000,
        help='搜索半径（米），默认1000米'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='并发线程数，默认5（建议不超过10）'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='输入CSV文件路径（默认: data/{city}_rental_with_distances.csv）'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='输出CSV文件路径（默认: data/{city}_rental_with_amenities.csv）'
    )

    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='从头开始，忽略断点'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式，减少输出'
    )

    args = parser.parse_args()

    # 确定文件路径
    city_code = args.city
    input_file = args.input or f'data/{city_code}_rental_with_distances.csv'
    output_file = args.output or f'data/{city_code}_rental_with_amenities.csv'

    # 检查输入文件
    if not Path(input_file).exists():
        # 尝试查找其他可能的输入文件
        alternative = f'data/{city_code}_rental_with_coordinates.csv'
        if Path(alternative).exists():
            input_file = alternative
            print(f"⚠️ 未找到距离数据，使用坐标数据: {input_file}")
        else:
            print(f"❌ 输入文件不存在: {input_file}")
            print(f"提示：请先运行 python scripts/calculate_distances.py --city {city_code}")
            sys.exit(1)

    # 初始化爬虫
    crawler = AmenityCrawler(
        radius_m=args.radius,
        max_workers=args.workers,
        verbose=not args.quiet
    )

    # 开始爬取
    try:
        crawler.process_city(
            city_code=city_code,
            input_file=input_file,
            output_file=output_file,
            resume=not args.no_resume
        )
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断，进度已保存")
        print(f"下次运行将从断点继续")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
