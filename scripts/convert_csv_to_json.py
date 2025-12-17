#!/usr/bin/env python3
import pandas as pd
import json
from pathlib import Path

def convert_csv_to_json():
    """转换所有CSV数据为JSON"""
    output_dir = Path('output/analysis')
    docs_data_dir = Path('gh-pages/data')
    docs_data_dir.mkdir(parents=True, exist_ok=True)

    data = {}

    # 1. 城市统计
    try:
        df = pd.read_csv(output_dir / 'city_statistics.csv', header=[0, 1], index_col=0, encoding='utf-8-sig')
        cities = df.index.tolist()
        data['city_stats'] = {
            'cities': cities,
            'rent_avg': df[('租金', '均价')].tolist(),
            'rent_max': df[('租金', '最高价')].tolist(),
            'rent_min': df[('租金', '最低价')].tolist(),
            'rent_median': df[('租金', '中位数')].tolist(),
            'count': df[('租金', '数量')].tolist(),
            'price_per_m2_avg': df[('单位租金', '均价')].tolist(),
            'price_per_m2_max': df[('单位租金', '最高价')].tolist(),
            'price_per_m2_min': df[('单位租金', '最低价')].tolist(),
            'price_per_m2_median': df[('单位租金', '中位数')].tolist(),
        }
        print("✓ 城市统计数据转换完成")
    except Exception as e:
        print(f"✗ 城市统计数据转换失败: {e}")

    # 2. 户型统计
    try:
        df = pd.read_csv(output_dir / 'layout_statistics.csv', header=[0, 1], index_col=[0, 1], encoding='utf-8-sig')
        layout_data = []
        for (city, layout), row in df.iterrows():
            layout_data.append({
                'city': city,
                'layout': layout,
                'rent_avg': float(row[('租金', '均价')]),
                'rent_median': float(row[('租金', '中位数')]),
                'count': int(row[('租金', '数量')]),
                'price_per_m2_avg': float(row[('单位租金', '均价')]),
                'price_per_m2_median': float(row[('单位租金', '中位数')]),
            })
        data['layout_stats'] = layout_data
        print("✓ 户型统计数据转换完成")
    except Exception as e:
        print(f"✗ 户型统计数据转换失败: {e}")

    # 3. 工资-租金关系
    try:
        df = pd.read_csv(output_dir / 'salary_rent_statistics.csv', encoding='utf-8-sig')
        data['salary_rent'] = {
            'cities': df['城市'].tolist(),
            'price_per_m2_avg': df['单位租金均价'].tolist(),
            'price_per_m2_median': df['单位租金中位数'].tolist(),
            'rent_avg': df['总租金均价'].tolist(),
            'rent_median': df['总租金中位数'].tolist(),
            'salary_private_monthly': df['私营月薪'].tolist(),
            'disposable_income_monthly': df['月可支配收入'].tolist(),
            'affordable_area_30pct': df['可租面积_私营30%'].tolist(),
            'rent_burden_30m2': df['30平米房租占私营月薪%'].tolist(),
            'rent_to_income_ratio': df['租金收入比_总租金/私营'].tolist(),
        }
        print("✓ 工资-租金数据转换完成")
    except Exception as e:
        print(f"✗ 工资-租金数据转换失败: {e}")

    # 4. 朝向统计
    try:
        df = pd.read_csv(output_dir / 'orientation_statistics.csv', encoding='utf-8-sig')
        orientation_data = []
        for _, row in df.iterrows():
            orientation_data.append({
                'city': row['城市'],
                'orientation': row['朝向'],
                'price_per_m2_avg': float(row['单位租金_均价']),
                'count': int(row['房源量']),
            })
        data['orientation_stats'] = orientation_data
        print("✓ 朝向统计数据转换完成")
    except Exception as e:
        print(f"✗ 朝向统计数据转换失败: {e}")

    # 5. 品牌统计
    try:
        df = pd.read_csv(output_dir / 'brand_statistics.csv', encoding='utf-8-sig')
        brand_data = []
        for _, row in df.iterrows():
            brand_data.append({
                'city': row['城市'],
                'brand': row['品牌'],
                'count': int(row['房源数量']),
                'market_share': float(row['市占率'])
            })
        data['brand_stats'] = brand_data
        print("✓ 品牌统计数据转换完成")
    except Exception as e:
        print(f"✗ 品牌统计数据转换失败: {e}")

    # 6. 板块统计（合并所有城市）
    block_data = []
    for city_name in ['北京', '上海', '广州', '深圳', '杭州']:
        try:
            df = pd.read_csv(output_dir / f'block_stats_{city_name}.csv', encoding='utf-8-sig')
            for _, row in df.iterrows():
                block_data.append({
                    'city': city_name,
                    'block': row['板块'],
                    'count': int(row['房源量']),
                    'rent_avg': float(row['总价均价']),
                    'price_per_m2_avg': float(row['单价均价']),
                })
        except Exception as e:
            print(f"✗ {city_name}板块数据转换失败: {e}")
    if block_data:
        data['block_stats'] = block_data
        print("✓ 板块统计数据转换完成")

    # 7. 距离衰减分析（合并所有城市）
    distance_dir = Path('output/distance_analysis')
    distance_data = {}
    for city_code, city_name in [('bj', '北京'), ('sh', '上海'), ('gz', '广州'), ('sz', '深圳'), ('hz', '杭州')]:
        try:
            # 读取距离分组统计
            stats_df = pd.read_csv(distance_dir / f'{city_code}_distance_stats.csv', encoding='utf-8-sig')
            # 读取模型对比
            model_df = pd.read_csv(distance_dir / f'{city_code}_model_comparison.csv', encoding='utf-8-sig')

            distance_data[city_name] = {
                'stats': {
                    'distance_groups': stats_df['距离分组'].tolist(),
                    'count': stats_df['房源数'].tolist(),
                    'rent_avg': stats_df['平均租金'].tolist(),
                    'price_per_m2_avg': stats_df['平均单位租金'].tolist()
                },
                'models': {
                    'names': model_df['模型'].tolist(),
                    'equations': model_df['方程'].tolist(),
                    'r_squared': model_df['R²'].tolist(),
                    'mae': model_df['MAE'].tolist()
                }
            }
        except Exception as e:
            print(f"✗ {city_name}距离衰减数据转换失败: {e}")
    if distance_data:
        data['distance_stats'] = distance_data
        print("✓ 距离衰减数据转换完成")

    # 8. 周边设施分析（合并所有城市）
    amenity_dir = Path('output/amenity_analysis')
    amenity_data = {}
    for city_code, city_name in [('bj', '北京'), ('sh', '上海'), ('gz', '广州'), ('sz', '深圳'), ('hz', '杭州')]:
        try:
            df = pd.read_csv(amenity_dir / f'{city_code}_density_stats.csv', encoding='utf-8-sig')
            amenity_data[city_name] = {
                'density_levels': df['配套丰富度'].tolist(),
                'count': df['样本量'].tolist(),
                'price_per_m2_avg': df['单位租金均值'].tolist(),
                'rent_avg': df['总租金均值'].tolist()
            }
        except Exception as e:
            print(f"✗ {city_name}周边设施数据转换失败: {e}")
    if amenity_data:
        data['amenity_stats'] = amenity_data
        print("✓ 周边设施数据转换完成")

    # 保存为JSON
    output_file = docs_data_dir / 'analysis_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 所有数据已转换并保存到: {output_file}")
    print(f"   总数据量: {len(json.dumps(data))} 字节")

if __name__ == '__main__':
    convert_csv_to_json()
