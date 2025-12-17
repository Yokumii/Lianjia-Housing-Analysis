#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.distance_decay import DistanceDecayAnalyzer
from src.analysis.distance_visualizer import DistanceVisualizer


def main():
    parser = argparse.ArgumentParser(
        description='分析房租随距离核心就业区的衰减规律',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析北京的距离衰减（全局最近距离）
  python scripts/analyze_distance_decay.py --city bj

  # 分析上海和深圳
  python scripts/analyze_distance_decay.py --city sh sz

  # 分析所有城市
  python scripts/analyze_distance_decay.py

  # 分析单位租金而非总租金
  python scripts/analyze_distance_decay.py --city bj --metric 单位租金

  # 限制最大距离（只分析 20km 以内）
  python scripts/analyze_distance_decay.py --city bj --max-distance 20

  # 分析特定就业中心
  python scripts/analyze_distance_decay.py --city bj --center 西二旗

  # 生成可视化（同心圆地图 + 散点图）
  python scripts/analyze_distance_decay.py --city bj --visualize

  # 找出价格洼地（残差阈值 -800）
  python scripts/analyze_distance_decay.py --city bj --find-value-zones --threshold -800

  # 静默模式
  python scripts/analyze_distance_decay.py --city bj --quiet
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
        '--metric',
        type=str,
        choices=['租金', '单位租金'],
        default='单位租金',
        help='分析指标（默认: 单位租金，推荐）'
    )

    parser.add_argument(
        '--max-distance',
        type=float,
        default=None,
        help='最大距离限制（公里），超过此距离的数据点会被过滤'
    )

    parser.add_argument(
        '--center',
        type=str,
        default=None,
        help='指定分析单个就业中心（例如: 西二旗）'
    )

    parser.add_argument(
        '--model',
        type=str,
        choices=['linear', 'poly2', 'poly3', 'log', 'exp', 'compare'],
        default='compare',
        help='回归模型（默认: compare，对比所有模型）'
    )

    parser.add_argument(
        '--find-value-zones',
        action='store_true',
        help='找出价格洼地（性价比高的区域）'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=-500,
        help='残差阈值（默认: -500，负值表示低于预测值）'
    )

    parser.add_argument(
        '--visualize',
        action='store_true',
        help='生成可视化（同心圆地图 + 散点图）'
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='数据目录（默认: data）'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output/distance_analysis',
        help='输出目录（默认: output/distance_analysis）'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式（不打印详细日志）'
    )

    args = parser.parse_args()

    # 创建输出目录
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 初始化分析器和可视化工具
    analyzer = DistanceDecayAnalyzer(verbose=not args.quiet)
    visualizer = None
    if args.visualize:
        visualizer = DistanceVisualizer(data_dir=args.data_dir, verbose=not args.quiet)

    # 处理每个城市
    for city_code in args.city:
        print(f"\n{'='*60}")
        print(f"分析 {city_code.upper()} 的距离衰减...")
        print(f"{'='*60}")

        # 加载带距离的数据
        distance_file = Path(args.data_dir) / f'{city_code}_rental_with_distances.csv'

        if not distance_file.exists():
            print(f"⚠️ 跳过 {city_code}: 距离数据文件不存在 ({distance_file})")
            print(f"   请先运行: python scripts/calculate_distances.py --city {city_code}")
            continue

        try:
            df = pd.read_csv(distance_file)
            analyzer.load_distance_data(df, city_code)

            # 计算最近距离
            if '最近距离(km)' not in df.columns:
                df = analyzer.calculate_min_distance()

                # 保存带最近距离的数据到文件（覆盖原文件）
                df.to_csv(distance_file, index=False, encoding='utf-8-sig')
                if not args.quiet:
                    print(f"\n✓ 最近距离已保存到: {distance_file}")

            if args.center:
                # 分析指定就业中心
                print(f"\n分析就业中心: {args.center}")
                results = analyzer.analyze_by_center(
                    center_name=args.center,
                    metric=args.metric,
                    max_distance_km=args.max_distance
                )

                # 可视化
                if args.visualize and visualizer:
                    # 同心圆地图
                    circle_map_file = output_path / f'{city_code}_{args.center}_circle_map.html'
                    visualizer.generate_circle_map(
                        city_code=city_code,
                        center_name=args.center,
                        output_file=str(circle_map_file)
                    )

                    # 散点图
                    scatter_file = output_path / f'{city_code}_{args.center}_regression.png'
                    visualizer.generate_regression_plot(
                        city_code=city_code,
                        regression_results=results,
                        output_file=str(scatter_file),
                        use_min_distance=False,
                        center_name=args.center,
                        metric=args.metric
                    )

            else:
                # 全局分析（最近距离）
                print(f"\n使用全局最近距离分析")

                # 根据选择的模型运行回归
                if args.model == 'compare':
                    # 对比所有模型
                    comparison_df = analyzer.compare_models(
                        metric=args.metric,
                        max_distance_km=args.max_distance
                    )

                    # 保存对比结果
                    comparison_file = output_path / f'{city_code}_model_comparison.csv'
                    comparison_df.to_csv(comparison_file, index=False, encoding='utf-8-sig')
                    if not args.quiet:
                        print(f"\n✓ 模型对比结果已保存: {comparison_file}")

                    # 使用最佳模型的结果（第一行）
                    best_model = comparison_df.iloc[0]['模型']
                    if best_model == 'linear':
                        results = analyzer.linear_regression_analysis(args.metric, args.max_distance)
                    elif best_model.startswith('polynomial_'):
                        degree = int(best_model.split('_')[1])
                        results = analyzer.polynomial_regression_analysis(args.metric, degree, args.max_distance)
                    elif best_model == 'logarithmic':
                        results = analyzer.logarithmic_regression_analysis(args.metric, args.max_distance)
                    elif best_model == 'exponential':
                        results = analyzer.exponential_regression_analysis(args.metric, args.max_distance)
                    else:
                        results = analyzer.linear_regression_analysis(args.metric, args.max_distance)

                elif args.model == 'linear':
                    results = analyzer.linear_regression_analysis(
                        metric=args.metric,
                        max_distance_km=args.max_distance
                    )
                elif args.model == 'poly2':
                    results = analyzer.polynomial_regression_analysis(
                        metric=args.metric,
                        degree=2,
                        max_distance_km=args.max_distance
                    )
                elif args.model == 'poly3':
                    results = analyzer.polynomial_regression_analysis(
                        metric=args.metric,
                        degree=3,
                        max_distance_km=args.max_distance
                    )
                elif args.model == 'log':
                    results = analyzer.logarithmic_regression_analysis(
                        metric=args.metric,
                        max_distance_km=args.max_distance
                    )
                elif args.model == 'exp':
                    results = analyzer.exponential_regression_analysis(
                        metric=args.metric,
                        max_distance_km=args.max_distance
                    )
                else:
                    results = analyzer.linear_regression_analysis(
                        metric=args.metric,
                        max_distance_km=args.max_distance
                    )

                # 找出价格洼地
                if args.find_value_zones:
                    value_zones = analyzer.find_value_zones(
                        metric=args.metric,
                        regression_results=results,
                        residual_threshold=args.threshold
                    )

                    # 保存价格洼地数据
                    value_zones_file = output_path / f'{city_code}_value_zones.csv'
                    value_zones.to_csv(value_zones_file, index=False, encoding='utf-8-sig')
                    if not args.quiet:
                        print(f"\n✓ 价格洼地数据已保存: {value_zones_file}")

                # 可视化
                if args.visualize and visualizer:
                    # 散点图（全局最近距离）
                    scatter_file = output_path / f'{city_code}_min_distance_regression.png'
                    visualizer.generate_regression_plot(
                        city_code=city_code,
                        regression_results=results,
                        output_file=str(scatter_file),
                        use_min_distance=True,
                        metric=args.metric
                    )

            # 距离分组统计
            if not args.quiet:
                stats_df = analyzer.get_summary_statistics()

                # 保存统计数据
                stats_file = output_path / f'{city_code}_distance_stats.csv'
                stats_df.to_csv(stats_file, encoding='utf-8-sig')
                print(f"\n✓ 距离分组统计已保存: {stats_file}")

        except Exception as e:
            print(f"❌ 处理 {city_code} 时出错: {e}")
            import traceback
            if not args.quiet:
                traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print("距离衰减分析完成")
    print(f"{'='*60}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
