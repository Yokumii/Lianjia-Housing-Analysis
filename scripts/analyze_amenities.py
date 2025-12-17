#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.amenity_analyzer import AmenityAnalyzer
from src.analysis.amenity_visualizer import AmenityVisualizer


def main():
    parser = argparse.ArgumentParser(
        description='分析配套设施对租金的溢价效应',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析北京的配套溢价
  python scripts/analyze_amenities.py --city bj

  # 分析并生成所有可视化
  python scripts/analyze_amenities.py --city bj --visualize

  # 只分析星巴克
  python scripts/analyze_amenities.py --city bj --amenity starbucks

  # 静默模式（仅输出结果文件）
  python scripts/analyze_amenities.py --city bj --visualize --quiet
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
        '--amenity',
        type=str,
        choices=['starbucks', 'mcdonalds', 'both'],
        default='both',
        help='配套类型（默认: both，分析两种配套）'
    )

    parser.add_argument(
        '--visualize',
        action='store_true',
        help='生成可视化图表'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output/amenity_analysis',
        help='输出目录（默认: output/amenity_analysis）'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式，减少输出'
    )

    args = parser.parse_args()

    city_code = args.city
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 检查输入文件
    data_file = f'data/{city_code}_rental_with_amenities.csv'
    if not Path(data_file).exists():
        print(f"❌ 数据文件不存在: {data_file}")
        print(f"提示：请先运行 python scripts/fetch_amenities.py --city {city_code}")
        sys.exit(1)

    # 初始化分析器
    analyzer = AmenityAnalyzer(verbose=not args.quiet)
    analyzer.load_data(city_code, data_file)

    # 添加标签
    df = analyzer.add_labels()

    # 执行分析
    print(f"\n{'='*60}")
    print(f"开始配套溢价分析")
    print(f"{'='*60}\n")

    # 确定要分析的配套类型
    amenity_types = []
    if args.amenity in ['starbucks', 'both']:
        amenity_types.append('starbucks')
    if args.amenity in ['mcdonalds', 'both']:
        amenity_types.append('mcdonalds')

    # 存储结果
    ttest_results = {}
    correlation_results = {}

    # 分析每种配套
    for amenity in amenity_types:
        # t检验
        ttest_results[amenity] = analyzer.ttest_analysis(amenity)

        # 相关性分析
        correlation_results[amenity] = analyzer.correlation_analysis(amenity)

    # 配套总数相关性分析
    correlation_results['total'] = analyzer.correlation_analysis('total')

    # 密度分级分析
    density_stats = analyzer.density_analysis()

    # 保存统计结果
    density_stats.to_csv(output_dir / f'{city_code}_density_stats.csv')
    if not args.quiet:
        print(f"\n✓ 密度统计已保存: {output_dir / f'{city_code}_density_stats.csv'}")

    # 生成可视化
    if args.visualize:
        print(f"\n{'='*60}")
        print(f"生成可视化图表")
        print(f"{'='*60}\n")

        visualizer = AmenityVisualizer(verbose=not args.quiet)
        visualizer.load_data(city_code, df)

        # 箱线图（有/无对比）
        for amenity in amenity_types:
            visualizer.plot_boxplot_comparison(
                amenity_type=amenity,
                output_file=str(output_dir / f'{city_code}_{amenity}_boxplot.png'),
                ttest_results=ttest_results[amenity]
            )

        # 散点图（数量 vs 租金）
        for amenity in amenity_types:
            visualizer.plot_scatter_correlation(
                amenity_type=amenity,
                output_file=str(output_dir / f'{city_code}_{amenity}_scatter.png'),
                correlation_results=correlation_results[amenity]
            )

        # 配套总数散点图
        visualizer.plot_scatter_correlation(
            amenity_type='total',
            output_file=str(output_dir / f'{city_code}_total_scatter.png'),
            correlation_results=correlation_results['total']
        )

        # 密度分级柱状图
        visualizer.plot_density_barplot(
            output_file=str(output_dir / f'{city_code}_density_barplot.png'),
            density_stats=density_stats
        )

        # 热力图（交叉影响）
        visualizer.plot_heatmap_comparison(
            output_file=str(output_dir / f'{city_code}_heatmap.png')
        )

    # 生成分析报告
    report_file = output_dir / f'{city_code}_amenity_report.md'
    generate_report(
        city_code=city_code,
        ttest_results=ttest_results,
        correlation_results=correlation_results,
        density_stats=density_stats,
        output_file=report_file,
        has_visualizations=args.visualize
    )

    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"分析完成")
        print(f"{'='*60}")
        print(f"输出目录: {output_dir}")
        print(f"分析报告: {report_file}")
        print(f"{'='*60}\n")


def generate_report(
    city_code: str,
    ttest_results: dict,
    correlation_results: dict,
    density_stats,
    output_file: Path,
    has_visualizations: bool
):
    """生成Markdown格式的分析报告"""

    city_names = {
        'bj': '北京',
        'sh': '上海',
        'gz': '广州',
        'sz': '深圳',
        'hz': '杭州'
    }
    city_name = city_names.get(city_code, city_code.upper())

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {city_name}租房配套设施溢价分析报告\n\n")
        f.write(f"生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("---\n\n")
        f.write("## 1. 研究问题\n\n")
        f.write("周边有星巴克或麦当劳等高端配套设施的区域，是否存在租金溢价？\n\n")
        f.write("**假设**：这些配套设施代表了更高的社区活力和年轻人聚集度，可能推高单位租金。\n\n")

        # t检验结果
        f.write("---\n\n")
        f.write("## 2. 统计假设检验（t-test）\n\n")

        for amenity, results in ttest_results.items():
            name = '星巴克' if amenity == 'starbucks' else '麦当劳'
            f.write(f"### 2.{list(ttest_results.keys()).index(amenity)+1} {name}\n\n")

            f.write("| 分组 | 样本量 | 均值 (元/㎡) | 中位数 (元/㎡) | 标准差 |\n")
            f.write("|------|--------|--------------|----------------|--------|\n")
            f.write(f"| 有{name} | {results['with_amenity']['count']:,} | "
                   f"{results['with_amenity']['mean']:.2f} | "
                   f"{results['with_amenity']['median']:.2f} | "
                   f"{results['with_amenity']['std']:.2f} |\n")
            f.write(f"| 无{name} | {results['without_amenity']['count']:,} | "
                   f"{results['without_amenity']['mean']:.2f} | "
                   f"{results['without_amenity']['median']:.2f} | "
                   f"{results['without_amenity']['std']:.2f} |\n\n")

            f.write(f"**统计检验结果：**\n\n")
            f.write(f"- t统计量: {results['t_statistic']:.4f}\n")
            f.write(f"- p值: {results['p_value']:.6f} ")
            if results['p_value'] < 0.001:
                f.write("(*** 极显著)\n")
            elif results['p_value'] < 0.01:
                f.write("(** 非常显著)\n")
            elif results['p_value'] < 0.05:
                f.write("(* 显著)\n")
            else:
                f.write("(不显著)\n")

            f.write(f"- Cohen's d (效应量): {results['cohens_d']:.4f}\n\n")

            f.write(f"**溢价分析：**\n\n")
            f.write(f"- 绝对溢价: **{results['premium']:+.2f}** 元/㎡\n")
            f.write(f"- 相对溢价: **{results['premium_pct']:+.2f}%**\n\n")

            if results['significant']:
                f.write(f"✅ **结论**: 有{name}的房源单位租金**显著高于**无{name}的房源 (p < 0.05)\n\n")
            else:
                f.write(f"❌ **结论**: 差异不显著 (p ≥ 0.05)\n\n")

        # 相关性分析
        f.write("---\n\n")
        f.write("## 3. 相关性分析\n\n")

        f.write("### 3.1 Pearson & Spearman 相关系数\n\n")
        f.write("| 配套类型 | Pearson r | Pearson p | Spearman ρ | Spearman p | 样本量 |\n")
        f.write("|----------|-----------|-----------|------------|------------|--------|\n")

        for amenity, results in correlation_results.items():
            name = results['amenity_type']
            f.write(f"| {name} | {results['pearson_r']:.4f} | {results['pearson_p']:.6f} | "
                   f"{results['spearman_r']:.4f} | {results['spearman_p']:.6f} | "
                   f"{results['sample_size']:,} |\n")

        f.write("\n**解读**：\n\n")
        for amenity, results in correlation_results.items():
            name = results['amenity_type']
            if results['pearson_p'] < 0.05:
                strength = '强' if abs(results['pearson_r']) > 0.5 else '中等' if abs(results['pearson_r']) > 0.3 else '弱'
                direction = '正' if results['pearson_r'] > 0 else '负'
                f.write(f"- {name}数量与单位租金存在**{strength}{direction}相关** (r={results['pearson_r']:.4f}, p<0.05)\n")
            else:
                f.write(f"- {name}数量与单位租金相关性不显著 (p≥0.05)\n")

        f.write("\n")

        # 密度分级统计
        f.write("---\n\n")
        f.write("## 4. 配套密度分级统计\n\n")

        # 手动格式化Markdown表格（避免依赖tabulate）
        f.write("| 配套丰富度 | 样本量 | 单位租金均值 | 单位租金中位数 | 单位租金标准差 | 总租金均值 | 平均面积 |\n")
        f.write("|-----------|--------|-------------|---------------|--------------|-----------|----------|\n")
        for idx, row in density_stats.iterrows():
            f.write(f"| {idx} | {int(row['样本量']):,} | {row['单位租金均值']:.2f} | "
                   f"{row['单位租金中位数']:.2f} | {row['单位租金标准差']:.2f} | "
                   f"{row['总租金均值']:.2f} | {row['平均面积']:.2f} |\n")
        f.write("\n\n")

        # 可视化
        if has_visualizations:
            f.write("---\n\n")
            f.write("## 5. 可视化图表\n\n")
            f.write("以下图表已生成在输出目录中：\n\n")
            f.write("- 箱线图：有/无配套的租金分布对比\n")
            f.write("- 散点图：配套数量 vs 单位租金（带回归线）\n")
            f.write("- 柱状图：配套密度分级（双轴：租金+样本量）\n")
            f.write("- 热力图：星巴克 × 麦当劳交叉影响\n\n")

        # 结论
        f.write("---\n\n")
        f.write("## 6. 总结与建议\n\n")

        # 判断是否存在显著溢价
        has_significant = any(r['significant'] for r in ttest_results.values())

        if has_significant:
            f.write("### 6.1 主要发现\n\n")
            for amenity, results in ttest_results.items():
                if results['significant']:
                    name = '星巴克' if amenity == 'starbucks' else '麦当劳'
                    f.write(f"- ✅ **{name}溢价存在**：有{name}的房源单位租金平均高出 "
                           f"**{results['premium']:.2f} 元/㎡** ({results['premium_pct']:.1f}%)\n")

            f.write("\n### 6.2 实践建议\n\n")
            f.write("**对租客**：\n")
            f.write("- 如果预算有限，可以考虑避开配套密集区域，选择稍远但性价比更高的房源\n")
            f.write("- 如果追求便利性和社区活力，配套密集区的溢价是合理的\n\n")

            f.write("**对房东/投资者**：\n")
            f.write("- 周边配套设施是租金定价的重要参考因素\n")
            f.write("- 配套设施的增加可能带来租金升值空间\n\n")
        else:
            f.write("### 6.1 主要发现\n\n")
            f.write("- ❌ 在该城市，星巴克和麦当劳等配套设施**未表现出显著的租金溢价**\n")
            f.write("- 可能的原因：\n")
            f.write("  - 配套设施分布较为均匀，未形成明显的区域差异\n")
            f.write("  - 其他因素（如距离市中心、交通便利性）对租金的影响更大\n")
            f.write("  - 样本量或数据质量问题\n\n")

        f.write("---\n\n")
        f.write("*本报告由自动化脚本生成*\n")

    print(f"✓ 分析报告已保存: {output_file}")


if __name__ == '__main__':
    import pandas as pd
    main()
