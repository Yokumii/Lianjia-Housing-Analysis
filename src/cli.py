import argparse
import sys
from typing import Optional, List

from .spider.core.orchestrator import UnifiedSpider
from .spider.config.constants import CityConfig, HttpConfig


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """解析命令行参数"""

    parser = argparse.ArgumentParser(
        description='链家房产数据爬虫',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取北京租房数据（HTTP 方式）
  python -m src.cli --city bj --type rental --strategy http

  # 爬取上海二手房数据（支持断点续传）
  python -m src.cli --city sh --type secondhand --strategy http --resume

  # 同时爬取多个城市
  python -m src.cli --city bj sh sz --type rental --strategy http

  # 自定义延迟和重试次数
  python -m src.cli --city bj --type rental --delay 2.0 --retries 5
        """,
    )

    parser.add_argument(
        '--city',
        type=str,
        nargs='+',
        default=['bj'],
        help='城市代码 (bj, sh, sz, gz, hz，可多选)',
    )

    parser.add_argument(
        '--type',
        dest='property_type',
        choices=['rental', 'secondhand', 'new_house'],
        default='rental',
        help='房产类型 (默认: rental)',
    )

    parser.add_argument(
        '--strategy',
        choices=['http', 'selenium', 'drission'],
        default='http',
        help='爬取策略 (默认: http)',
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='每次请求间隔（秒，默认: 1.0）',
    )

    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help='HTTP 请求重试次数（默认: 3）',
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='从进度文件恢复（支持断点续传）',
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Selenium/DrissionPage 无头模式（默认: True）',
    )

    parser.add_argument(
        '--cookie',
        type=str,
        help='Cookie 字符串（如果需要）',
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None):
    """主程序入口"""

    try:
        parsed_args = parse_args(args)

        # 验证配置文件
        if not HttpConfig.validate_cookie():
            print("\n❌ Cookie 未填入！")
            print("="*60)
            print("请编辑 settings.py 文件，填入你的 Cookie")
            print("\n步骤：")
            print("  1. 打开浏览器，访问 https://bj.lianjia.com")
            print("  2. F12 打开开发者工具 → Network 标签")
            print("  3. 任意操作网站（翻页等），找到对链家的请求")
            print("  4. 点击请求 → Headers 标签 → 找到 Cookie")
            print("  5. 复制整个 Cookie 值")
            print("  6. 打开 settings.py，粘贴到 Cookie = \"\" 中")
            print("="*60)
            return 1

        # 验证城市
        invalid_cities = [c for c in parsed_args.city if not CityConfig.validate_city(c)]
        if invalid_cities:
            print(f"❌ 不支持的城市: {invalid_cities}")
            print(f"支持的城市: {list(CityConfig.CITIES.keys())}")
            return 1

        print(f"\n{'='*60}")
        print(f"链家房产数据爬虫")
        print(f"{'='*60}")
        print(f"城市: {', '.join([CityConfig.get_city_name(c) for c in parsed_args.city])}")
        print(f"房产类型: {parsed_args.property_type}")
        print(f"爬取策略: {parsed_args.strategy}")
        print(f"请求延迟: {parsed_args.delay} 秒")
        print(f"重试次数: {parsed_args.retries}")
        print(f"断点续传: {'✓' if parsed_args.resume else '✗'}")
        print(f"{'='*60}\n")

        # 选择爬取策略
        if parsed_args.strategy == 'http':
            factory_method = UnifiedSpider.create_http_spider
        elif parsed_args.strategy == 'selenium':
            factory_method = UnifiedSpider.create_selenium_spider
        elif parsed_args.strategy == 'drission':
            factory_method = UnifiedSpider.create_drission_spider
        else:
            print(f"❌ 不支持的策略: {parsed_args.strategy}")
            return 1

        # 逐城市爬取
        all_stats = {}
        for city in parsed_args.city:
            try:
                # 创建爬虫
                spider = factory_method(city, parsed_args.property_type)

                # 执行爬虫
                stats = spider.crawl(
                    delay=parsed_args.delay,
                    resume=parsed_args.resume,
                )
                all_stats[city] = stats

                spider.close()

            except Exception as e:
                print(f"❌ 爬取 {CityConfig.get_city_name(city)} 失败: {e}")
                return 1

        # 总结
        print(f"\n{'='*60}")
        print(f"所有城市爬取完成")
        print(f"{'='*60}")
        for city, stats in all_stats.items():
            print(f"{CityConfig.get_city_name(city)}: "
                  f"页数={stats['total_pages']}, "
                  f"房源={stats['total_items']}, "
                  f"写入={stats['total_written']}, "
                  f"错误={stats['errors']}")
        print(f"{'='*60}\n")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断爬虫")
        return 130
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
