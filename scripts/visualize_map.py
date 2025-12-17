#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis import visualize_city_heatmap, visualize_all_cities


def main():
    parser = argparse.ArgumentParser(
        description='城市租金热力图可视化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  # 生成所有城市热力图
  python scripts/visualize_map.py

  # 仅生成北京和上海热力图
  python scripts/visualize_map.py --city bj sh

  # 自定义热力图参数（半径和模糊度）
  python scripts/visualize_map.py --city bj --radius 20 --blur 25

  # 自定义输出目录
  python scripts/visualize_map.py --output output/custom_maps

  # 静默模式
  python scripts/visualize_map.py --quiet
        '''
    )

    parser.add_argument(
        '--city',
        nargs='+',
        choices=['bj', 'sh', 'sz', 'gz', 'hz'],
        help='城市代码（可多选），默认生成所有城市'
    )

    parser.add_argument(
        '--data-dir',
        default='data',
        help='数据文件目录（默认: data）'
    )

    parser.add_argument(
        '--output',
        default='output/maps',
        help='输出目录（默认: output/maps）'
    )

    parser.add_argument(
        '--zoom',
        type=int,
        default=11,
        help='地图初始缩放级别（默认: 11）'
    )

    parser.add_argument(
        '--radius',
        type=int,
        default=15,
        help='热力图半径（默认: 15）'
    )

    parser.add_argument(
        '--blur',
        type=int,
        default=20,
        help='热力图模糊度（默认: 20）'
    )

    parser.add_argument(
        '--max-zoom',
        type=int,
        default=13,
        help='最大缩放级别（默认: 13）'
    )

    parser.add_argument(
        '--no-png',
        action='store_true',
        help='不生成静态 PNG 图片（仅生成交互式 HTML）'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式，不打印详细日志'
    )

    args = parser.parse_args()

    # 热力图参数
    heatmap_kwargs = {
        'zoom_start': args.zoom,
        'radius': args.radius,
        'blur': args.blur,
        'max_zoom': args.max_zoom,
        'save_png': not args.no_png  # 默认生成 PNG，除非指定 --no-png
    }

    # 执行可视化
    try:
        print("="*80)
        print("🗺️  城市租金热力图可视化工具")
        print("="*80)
        print()

        if args.city:
            # 生成指定城市
            if len(args.city) == 1:
                # 单个城市
                city_code = args.city[0]
                city_names = {'bj': '北京', 'sh': '上海', 'gz': '广州', 'sz': '深圳', 'hz': '杭州'}
                print(f"生成 {city_names[city_code]} 热力图...")
                print()

                html_file, png_file = visualize_city_heatmap(
                    city_code=city_code,
                    data_dir=args.data_dir,
                    output_dir=args.output,
                    verbose=not args.quiet,
                    **heatmap_kwargs
                )

                print()
                print("="*80)
                print("✅ 热力图生成完成！")
                print(f"   交互式地图: {html_file}")
                if png_file:
                    print(f"   静态地图:   {png_file}")
                print("="*80)

            else:
                # 多个城市
                print(f"生成 {len(args.city)} 个城市的热力图...")
                print()

                results = visualize_all_cities(
                    city_codes=args.city,
                    data_dir=args.data_dir,
                    output_dir=args.output,
                    verbose=not args.quiet,
                    **heatmap_kwargs
                )

                print()
                print("="*80)
                print("✅ 批量生成完成！")
                success_count = len([v for v in results.values() if v[0] is not None])
                print(f"   成功: {success_count} / {len(args.city)} 个城市")
                print(f"   输出目录: {args.output}")
                print("="*80)

        else:
            # 生成所有城市
            print("生成所有城市的热力图...")
            print()

            results = visualize_all_cities(
                data_dir=args.data_dir,
                output_dir=args.output,
                verbose=not args.quiet,
                **heatmap_kwargs
            )

            print()
            print("="*80)
            print("✅ 批量生成完成！")
            success_count = len([v for v in results.values() if v[0] is not None])
            print(f"   成功: {success_count} / 5 个城市")
            print(f"   输出目录: {args.output}")
            print("="*80)

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        print(f"   请确保坐标数据文件位于 {args.data_dir} 目录", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n❌ 可视化失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
