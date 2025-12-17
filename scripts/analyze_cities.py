#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis import analyze_cities


def main():
    parser = argparse.ArgumentParser(
        description='城市租房数据分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  # 分析所有城市，显示并保存图表
  python scripts/analyze_cities.py

  # 仅分析北京和上海
  python scripts/analyze_cities.py --city bj sh

  # 不显示图表（仅保存）
  python scripts/analyze_cities.py --no-plot

  # 自定义输出目录
  python scripts/analyze_cities.py --output output/custom

  # 仅生成统计表格，不生成图表
  python scripts/analyze_cities.py --no-save-plot --no-plot

  # 静默模式
  python scripts/analyze_cities.py --quiet
        '''
    )
    
    parser.add_argument(
        '--city',
        nargs='+',
        choices=['bj', 'sh', 'sz', 'gz', 'hz'],
        help='城市代码（可多选），默认分析所有城市'
    )
    
    parser.add_argument(
        '--data-dir',
        default='data',
        help='数据文件目录（默认: data）'
    )
    
    parser.add_argument(
        '--output',
        default='output/analysis',
        help='输出目录（默认: output/analysis）'
    )
    
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='不显示图表（仍会保存）'
    )
    
    parser.add_argument(
        '--no-save-plot',
        action='store_true',
        help='不保存图表'
    )
    
    parser.add_argument(
        '--no-save-stats',
        action='store_true',
        help='不保存统计表格'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式，不打印详细日志'
    )
    
    args = parser.parse_args()
    
    # 执行分析
    try:
        print("="*80)
        print("🏠 城市租房数据分析工具")
        print("="*80)
        print()
        
        df_all, stats = analyze_cities(
            data_dir=args.data_dir,
            output_dir=args.output,
            city_codes=args.city,
            show_plot=not args.no_plot,
            save_plot=not args.no_save_plot,
            save_stats=not args.no_save_stats,
            verbose=not args.quiet
        )
        
        print()
        print("="*80)
        print("✅ 分析完成！")
        print(f"   数据总量: {len(df_all):,} 条")
        print(f"   分析城市: {len(stats)} 个")
        print(f"   输出目录: {args.output}")
        print("="*80)
        
        return 0
    
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        print(f"   请确保数据文件位于 {args.data_dir} 目录", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n❌ 分析失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
