import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from scipy import stats


class DistanceDecayAnalyzer:
    """距离衰减分析器"""

    # 城市代码到名称的映射
    CITY_CODE_MAP = {
        'bj': '北京',
        'sh': '上海',
        'gz': '广州',
        'sz': '深圳',
        'hz': '杭州'
    }

    # 就业中心列表
    EMPLOYMENT_CENTERS = {
        'bj': ['西二旗', '望京', '国贸', '金融街'],
        'sh': ['陆家嘴', '张江科学城', '漕河泾', '外滩'],
        'sz': ['南山科技园', '深圳湾', '福田CBD', '坂田科技城'],
        'gz': ['珠江新城', '体育西路', '天河软件园', '广州科学城'],
        'hz': ['未来科技城', '钱江新城', '滨江区', '湖滨商圈']
    }

    def __init__(self, verbose: bool = True):
        """
        初始化分析器

        Args:
            verbose: 是否打印详细日志
        """
        self.df = None
        self.city_code = None
        self.city_name = None
        self.verbose = verbose

    def load_distance_data(self, df: pd.DataFrame, city_code: str):
        """
        加载包含距离信息的数据

        Args:
            df: 包含距离列的 DataFrame
            city_code: 城市代码
        """
        self.df = df.copy()
        self.city_code = city_code
        self.city_name = self.CITY_CODE_MAP.get(city_code, city_code)

        if self.verbose:
            print(f"\n✓ 加载 {self.city_name} 数据: {len(self.df):,} 行")

    def calculate_min_distance(self) -> pd.DataFrame:
        """
        计算每个房源到最近就业中心的距离

        Returns:
            更新后的 DataFrame
        """
        if self.df is None:
            raise ValueError("请先调用 load_distance_data() 加载数据")

        # 获取距离列
        distance_cols = [col for col in self.df.columns if col.startswith('距离_')]
        center_names = [col.replace('距离_', '') for col in distance_cols]

        if not distance_cols:
            raise ValueError("数据中没有距离列（格式应为 '距离_xxx'）")

        # 计算最近距离和对应的就业中心
        distances = self.df[distance_cols].values
        min_distances = np.nanmin(distances, axis=1)
        min_indices = np.nanargmin(distances, axis=1)

        self.df['最近距离(km)'] = min_distances / 1000  # 转换为公里
        self.df['最近就业区'] = [center_names[idx] for idx in min_indices]

        if self.verbose:
            print(f"\n✓ 计算最近距离完成")
            print(f"  有效数据: {len(self.df):,} 行")
            print(f"  最近距离范围: {self.df['最近距离(km)'].min():.1f} ~ {self.df['最近距离(km)'].max():.1f} km")

        return self.df

    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """计算回归指标"""
        # R²
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # MAE
        mae = np.mean(np.abs(y_true - y_pred))

        # RMSE
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

        # MAPE
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        return {
            'r_squared': r_squared,
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }

    def linear_regression_analysis(
        self,
        metric: str = '租金',
        max_distance_km: Optional[float] = None
    ) -> Dict:
        """
        线性回归分析：y = ax + b

        Args:
            metric: 分析指标（'租金' 或 '单位租金'）
            max_distance_km: 最大距离限制（公里）

        Returns:
            回归分析结果字典
        """
        if '最近距离(km)' not in self.df.columns:
            raise ValueError("请先调用 calculate_min_distance() 计算最近距离")

        # 准备数据
        df_clean = self.df.dropna(subset=['最近距离(km)', metric])

        # 过滤距离
        if max_distance_km is not None:
            df_clean = df_clean[df_clean['最近距离(km)'] <= max_distance_km]

        x = df_clean['最近距离(km)'].values
        y = df_clean[metric].values

        if len(x) < 10:
            raise ValueError(f"有效数据点太少（{len(x)}），无法进行回归分析")

        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # 预测值
        y_pred = slope * x + intercept

        # 计算评估指标
        metrics = self._calculate_metrics(y, y_pred)

        # 结果
        results = {
            'model': 'linear',
            'equation': f'y = {slope:.2f}x + {intercept:.2f}',
            'slope': slope,
            'intercept': intercept,
            'r_squared': metrics['r_squared'],
            'mae': metrics['mae'],
            'rmse': metrics['rmse'],
            'mape': metrics['mape'],
            'p_value': p_value,
            'std_err': std_err,
            'sample_size': len(x),
            'metric': metric,
            'max_distance_km': max_distance_km
        }

        if self.verbose:
            self._print_regression_results(results, '线性回归')

        return results

    def polynomial_regression_analysis(
        self,
        metric: str = '租金',
        degree: int = 2,
        max_distance_km: Optional[float] = None
    ) -> Dict:
        """
        多项式回归分析：y = a₀ + a₁x + a₂x² + ... + aₙxⁿ

        Args:
            metric: 分析指标
            degree: 多项式次数（2=二次，3=三次）
            max_distance_km: 最大距离限制

        Returns:
            回归分析结果字典
        """
        if '最近距离(km)' not in self.df.columns:
            raise ValueError("请先调用 calculate_min_distance() 计算最近距离")

        # 准备数据
        df_clean = self.df.dropna(subset=['最近距离(km)', metric])
        if max_distance_km is not None:
            df_clean = df_clean[df_clean['最近距离(km)'] <= max_distance_km]

        x = df_clean['最近距离(km)'].values
        y = df_clean[metric].values

        if len(x) < 10:
            raise ValueError(f"有效数据点太少（{len(x)}）")

        # 多项式拟合
        coeffs = np.polyfit(x, y, degree)
        poly = np.poly1d(coeffs)
        y_pred = poly(x)

        # 计算评估指标
        metrics = self._calculate_metrics(y, y_pred)

        # 构建方程字符串
        terms = []
        for i, coef in enumerate(coeffs):
            power = degree - i
            if power == 0:
                terms.append(f"{coef:.2f}")
            elif power == 1:
                terms.append(f"{coef:.2f}x")
            else:
                terms.append(f"{coef:.2f}x^{power}")
        equation = ' + '.join(terms).replace('+ -', '- ')

        results = {
            'model': f'polynomial_{degree}',
            'equation': f'y = {equation}',
            'coefficients': coeffs.tolist(),
            'degree': degree,
            'r_squared': metrics['r_squared'],
            'mae': metrics['mae'],
            'rmse': metrics['rmse'],
            'mape': metrics['mape'],
            'sample_size': len(x),
            'metric': metric,
            'max_distance_km': max_distance_km
        }

        if self.verbose:
            self._print_regression_results(results, f'{degree}次多项式回归')

        return results

    def logarithmic_regression_analysis(
        self,
        metric: str = '租金',
        max_distance_km: Optional[float] = None
    ) -> Dict:
        """
        对数回归分析：y = a × ln(x) + b

        Args:
            metric: 分析指标
            max_distance_km: 最大距离限制

        Returns:
            回归分析结果字典
        """
        if '最近距离(km)' not in self.df.columns:
            raise ValueError("请先调用 calculate_min_distance() 计算最近距离")

        # 准备数据
        df_clean = self.df.dropna(subset=['最近距离(km)', metric])
        if max_distance_km is not None:
            df_clean = df_clean[df_clean['最近距离(km)'] <= max_distance_km]

        # 过滤距离 <= 0 的数据（对数不能为负）
        df_clean = df_clean[df_clean['最近距离(km)'] > 0]

        x = df_clean['最近距离(km)'].values
        y = df_clean[metric].values

        if len(x) < 10:
            raise ValueError(f"有效数据点太少（{len(x)}）")

        # 对数回归：y = a * ln(x) + b
        x_log = np.log(x)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_log, y)

        # 预测值
        y_pred = slope * x_log + intercept

        # 计算评估指标
        metrics = self._calculate_metrics(y, y_pred)

        results = {
            'model': 'logarithmic',
            'equation': f'y = {slope:.2f} × ln(x) + {intercept:.2f}',
            'slope': slope,
            'intercept': intercept,
            'r_squared': metrics['r_squared'],
            'mae': metrics['mae'],
            'rmse': metrics['rmse'],
            'mape': metrics['mape'],
            'p_value': p_value,
            'std_err': std_err,
            'sample_size': len(x),
            'metric': metric,
            'max_distance_km': max_distance_km
        }

        if self.verbose:
            self._print_regression_results(results, '对数回归')

        return results

    def exponential_regression_analysis(
        self,
        metric: str = '租金',
        max_distance_km: Optional[float] = None
    ) -> Dict:
        """
        指数回归分析：y = a × e^(bx)

        Args:
            metric: 分析指标
            max_distance_km: 最大距离限制

        Returns:
            回归分析结果字典
        """
        if '最近距离(km)' not in self.df.columns:
            raise ValueError("请先调用 calculate_min_distance() 计算最近距离")

        # 准备数据
        df_clean = self.df.dropna(subset=['最近距离(km)', metric])
        if max_distance_km is not None:
            df_clean = df_clean[df_clean['最近距离(km)'] <= max_distance_km]

        # 过滤 y <= 0 的数据（对数不能为负）
        df_clean = df_clean[df_clean[metric] > 0]

        x = df_clean['最近距离(km)'].values
        y = df_clean[metric].values

        if len(x) < 10:
            raise ValueError(f"有效数据点太少（{len(x)}）")

        # 指数回归：y = a * e^(bx)
        # 取对数：ln(y) = ln(a) + bx
        y_log = np.log(y)
        slope, intercept_log, r_value, p_value, std_err = stats.linregress(x, y_log)

        # 还原参数
        a = np.exp(intercept_log)
        b = slope

        # 预测值
        y_pred = a * np.exp(b * x)

        # 计算评估指标
        metrics = self._calculate_metrics(y, y_pred)

        results = {
            'model': 'exponential',
            'equation': f'y = {a:.2f} × e^({b:.4f}x)',
            'a': a,
            'b': b,
            'r_squared': metrics['r_squared'],
            'mae': metrics['mae'],
            'rmse': metrics['rmse'],
            'mape': metrics['mape'],
            'p_value': p_value,
            'sample_size': len(x),
            'metric': metric,
            'max_distance_km': max_distance_km
        }

        if self.verbose:
            self._print_regression_results(results, '指数回归')

        return results

    def compare_models(
        self,
        metric: str = '租金',
        max_distance_km: Optional[float] = None
    ) -> pd.DataFrame:
        """
        对比所有回归模型

        Args:
            metric: 分析指标
            max_distance_km: 最大距离限制

        Returns:
            模型对比结果 DataFrame
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"模型对比分析 - {self.city_name}")
            print(f"{'='*60}\n")

        models_results = []

        # 线性回归
        try:
            result = self.linear_regression_analysis(metric, max_distance_km)
            models_results.append(result)
        except Exception as e:
            if self.verbose:
                print(f"⚠️ 线性回归失败: {e}")

        # 多项式回归（2次、3次）
        for degree in [2, 3]:
            try:
                result = self.polynomial_regression_analysis(metric, degree, max_distance_km)
                models_results.append(result)
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ {degree}次多项式回归失败: {e}")

        # 对数回归
        try:
            result = self.logarithmic_regression_analysis(metric, max_distance_km)
            models_results.append(result)
        except Exception as e:
            if self.verbose:
                print(f"⚠️ 对数回归失败: {e}")

        # 指数回归
        try:
            result = self.exponential_regression_analysis(metric, max_distance_km)
            models_results.append(result)
        except Exception as e:
            if self.verbose:
                print(f"⚠️ 指数回归失败: {e}")

        # 转换为 DataFrame
        comparison_df = pd.DataFrame([
            {
                '模型': r['model'],
                '方程': r['equation'],
                'R²': r['r_squared'],
                'MAE': r['mae'],
                'RMSE': r['rmse'],
                'MAPE(%)': r['mape'],
                '样本量': r['sample_size']
            }
            for r in models_results
        ])

        # 按 R² 降序排序
        comparison_df = comparison_df.sort_values('R²', ascending=False).reset_index(drop=True)

        if self.verbose:
            print(f"\n{'='*60}")
            print("模型对比结果（按 R² 排序）")
            print(f"{'='*60}")
            print(comparison_df.to_string(index=False))
            print(f"\n最佳模型: {comparison_df.iloc[0]['模型']} (R² = {comparison_df.iloc[0]['R²']:.4f})")
            print(f"{'='*60}\n")

        return comparison_df

    def _print_regression_results(self, results: Dict, model_name: str):
        """打印回归结果"""
        print(f"\n{'='*60}")
        print(f"{self.city_name} - {model_name} 分析")
        print(f"{'='*60}")
        print(f"样本量: {results['sample_size']:,} 个房源")
        if results.get('max_distance_km'):
            print(f"距离限制: ≤ {results['max_distance_km']:.1f} km")
        print(f"\n回归方程: {results['equation']}")
        print(f"\n评估指标:")
        print(f"  R² (决定系数):    {results['r_squared']:.4f}")
        print(f"  MAE (平均绝对误差): {results['mae']:.2f} 元")
        print(f"  RMSE (均方根误差):  {results['rmse']:.2f} 元")
        print(f"  MAPE (平均相对误差): {results['mape']:.2f}%")
        print(f"{'='*60}")

    def find_value_zones(
        self,
        metric: str = '租金',
        regression_results: Dict = None,
        residual_threshold: float = -500
    ) -> pd.DataFrame:
        """
        找出性价比高的区域（价格洼地）

        Args:
            metric: 分析指标
            regression_results: 回归分析结果（如果为None，则自动运行线性回归）
            residual_threshold: 残差阈值（负值表示低于预测值）

        Returns:
            价格洼地数据
        """
        if regression_results is None:
            regression_results = self.linear_regression_analysis(metric)

        # 计算预测值和残差
        if regression_results['model'] == 'linear':
            slope = regression_results['slope']
            intercept = regression_results['intercept']
            self.df['预测租金'] = slope * self.df['最近距离(km)'] + intercept
        else:
            # 其他模型暂不支持价格洼地识别
            raise ValueError("价格洼地识别目前只支持线性回归模型")

        self.df['残差'] = self.df[metric] - self.df['预测租金']

        # 筛选价格洼地
        value_zones = self.df[self.df['残差'] < residual_threshold].copy()
        value_zones = value_zones.sort_values('残差')

        if self.verbose and len(value_zones) > 0:
            print(f"\n发现 {len(value_zones):,} 个性价比房源（残差 < {residual_threshold}）")

            # 按区域统计
            if '区域' in value_zones.columns:
                top_areas = value_zones.groupby('区域').agg({
                    '残差': ['count', 'mean']
                }).round(0)
                top_areas.columns = ['房源数', '平均低于预测(元)']
                top_areas = top_areas.sort_values('房源数', ascending=False).head(5)

                print(f"\n最高性价比区域 Top 5:")
                for area, row in top_areas.iterrows():
                    print(f"  - {area}: {int(row['房源数'])} 套房源，平均低于预测 {abs(int(row['平均低于预测(元)']))} 元")

        return value_zones

    def get_summary_statistics(self, distance_bins: int = 20) -> pd.DataFrame:
        """
        获取距离分组的统计信息

        Args:
            distance_bins: 距离分组数量

        Returns:
            分组统计 DataFrame
        """
        if '最近距离(km)' not in self.df.columns:
            raise ValueError("请先调用 calculate_min_distance() 计算最近距离")

        # 按距离分组（每 2km 一组）
        self.df['距离分组'] = (self.df['最近距离(km)'] // 2) * 2

        # 统计每组的平均值
        stats_df = self.df.groupby('距离分组').agg({
            '租金': ['count', 'mean', 'std', 'min', 'max'],
            '单位租金': ['mean', 'std']
        }).round(2)

        stats_df.columns = ['房源数', '平均租金', '租金标准差', '最低租金', '最高租金',
                            '平均单位租金', '单位租金标准差']

        return stats_df.reset_index()

    def analyze_by_center(
        self,
        center_name: str,
        metric: str = '租金',
        max_distance_km: Optional[float] = None
    ) -> Dict:
        """
        单独分析某个就业中心的距离衰减（使用线性回归）

        Args:
            center_name: 就业中心名称
            metric: 分析指标
            max_distance_km: 最大距离限制

        Returns:
            回归分析结果
        """
        distance_col = f'距离_{center_name}'

        if distance_col not in self.df.columns:
            raise ValueError(f"数据中没有 '{distance_col}' 列")

        # 准备数据
        df_clean = self.df.dropna(subset=[distance_col, metric])
        df_clean['距离(km)'] = df_clean[distance_col] / 1000

        # 过滤距离
        if max_distance_km is not None:
            df_clean = df_clean[df_clean['距离(km)'] <= max_distance_km]

        x = df_clean['距离(km)'].values
        y = df_clean[metric].values

        if len(x) < 10:
            raise ValueError(f"有效数据点太少（{len(x)}）")

        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        y_pred = slope * x + intercept
        metrics = self._calculate_metrics(y, y_pred)

        results = {
            'model': 'linear',
            'center': center_name,
            'equation': f'y = {slope:.2f}x + {intercept:.2f}',
            'slope': slope,
            'intercept': intercept,
            'r_squared': metrics['r_squared'],
            'mae': metrics['mae'],
            'rmse': metrics['rmse'],
            'mape': metrics['mape'],
            'p_value': p_value,
            'std_err': std_err,
            'sample_size': len(x),
            'metric': metric,
            'max_distance_km': max_distance_km
        }

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"{self.city_name} - {center_name} 距离衰减分析")
            print(f"{'='*60}")
            print(f"样本量: {results['sample_size']:,} 个房源")
            if max_distance_km:
                print(f"距离限制: ≤ {max_distance_km:.1f} km")
            print(f"\n回归方程: {results['equation']}")
            print(f"\n衰减系数: 每增加 1km，{metric} {'降低' if slope < 0 else '增加'} {abs(slope):.2f} 元")
            print(f"R²: {results['r_squared']:.4f}")
            print(f"MAE: {results['mae']:.2f} 元")
            print(f"{'='*60}")

        return results
