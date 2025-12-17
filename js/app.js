// ==================== 全局变量 ====================
let analysisData = {};
let blockChartInstance = null;
let distanceChartInstance = null;
let amenityChartInstance = null;

// ==================== 数据加载 ====================
async function loadData() {
    try {
        const response = await fetch('data/analysis_data.json');
        analysisData = await response.json();
        console.log('数据加载成功', analysisData);
        initCharts();
    } catch (error) {
        console.error('数据加载失败:', error);
    }
}

// ==================== 初始化所有图表 ====================
function initCharts() {
    // 1. 城市对比 - 总租金分布（箱线图）
    renderCityRentChart();

    // 2. 城市对比 - 单位租金对比（柱状图）
    renderCityPricePerM2Chart();

    // 3. 户型分析 - 总租金对比（分组柱状图）
    renderLayoutRentChart();

    // 4. 户型分析 - 单位租金对比（分组柱状图）
    renderLayoutPricePerM2Chart();

    // 5. 板块分析（默认显示北京，支持城市切换）
    renderBlockChart('北京');

    // 6. 朝向分析（分组柱状图）
    renderOrientationChart();

    // 7. 品牌分布（堆叠柱状图）
    renderBrandChart();

    // 8. 工资租金关系 - 散点图
    renderSalaryScatterChart();

    // 9. 工资租金关系 - 可租面积柱状图
    renderAffordableAreaChart();

    // 10. 工资租金关系 - 租金收入比柱状图
    renderRentToIncomeChart();

    // 11. 距离衰减分析（默认显示北京）
    renderDistanceDecayChart('北京');

    // 12. 周边设施溢价分析（默认显示北京）
    renderAmenityDensityChart('北京');
}

// ==================== 1. 城市总租金分布（箱线图改为柱状图+误差线）====================
function renderCityRentChart() {
    const chart = echarts.init(document.getElementById('chart-city-rent'));
    const data = analysisData.city_stats;

    const option = {
        title: {
            text: '五城市总租金对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: ['平均租金', '中位数租金'],
            top: 30
        },
        xAxis: {
            type: 'category',
            data: data.cities,
            axisLabel: { fontSize: 12 }
        },
        yAxis: {
            type: 'value',
            name: '租金（元/月）',
            axisLabel: { formatter: '{value}' }
        },
        series: [
            {
                name: '平均租金',
                type: 'bar',
                data: data.rent_avg,
                itemStyle: { color: '#5470c6' },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}'
                }
            },
            {
                name: '中位数租金',
                type: 'bar',
                data: data.rent_median,
                itemStyle: { color: '#91cc75' },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}'
                }
            }
        ]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 2. 城市单位租金对比（柱状图）====================
function renderCityPricePerM2Chart() {
    const chart = echarts.init(document.getElementById('chart-city-price-per-m2'));
    const data = analysisData.city_stats;

    const option = {
        title: {
            text: '五城市单位租金对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: ['平均单价', '中位数单价'],
            top: 30
        },
        xAxis: {
            type: 'category',
            data: data.cities
        },
        yAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）'
        },
        series: [
            {
                name: '平均单价',
                type: 'bar',
                data: data.price_per_m2_avg,
                itemStyle: { color: '#ee6666' },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}'
                }
            },
            {
                name: '中位数单价',
                type: 'bar',
                data: data.price_per_m2_median,
                itemStyle: { color: '#fac858' },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}'
                }
            }
        ]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 3. 户型总租金对比（分组柱状图）====================
function renderLayoutRentChart() {
    const chart = echarts.init(document.getElementById('chart-layout-rent'));
    const data = analysisData.layout_stats;

    // 按城市和户型组织数据
    const cities = ['上海', '北京', '广州', '杭州', '深圳'];
    const layouts = ['一居', '两居', '三居'];
    const seriesData = {};

    layouts.forEach(layout => {
        seriesData[layout] = cities.map(city => {
            const item = data.find(d => d.city === city && d.layout === layout);
            return item ? item.rent_avg : 0;
        });
    });

    const option = {
        title: {
            text: '各城市户型总租金对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: layouts,
            top: 30
        },
        xAxis: {
            type: 'category',
            data: cities
        },
        yAxis: {
            type: 'value',
            name: '平均租金（元/月）'
        },
        series: layouts.map((layout, index) => ({
            name: layout,
            type: 'bar',
            data: seriesData[layout],
            itemStyle: {
                color: ['#5470c6', '#91cc75', '#fac858'][index]
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{c}'
            }
        }))
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 4. 户型单位租金对比（分组柱状图）====================
function renderLayoutPricePerM2Chart() {
    const chart = echarts.init(document.getElementById('chart-layout-price-per-m2'));
    const data = analysisData.layout_stats;

    const cities = ['上海', '北京', '广州', '杭州', '深圳'];
    const layouts = ['一居', '两居', '三居'];
    const seriesData = {};

    layouts.forEach(layout => {
        seriesData[layout] = cities.map(city => {
            const item = data.find(d => d.city === city && d.layout === layout);
            return item ? item.price_per_m2_avg.toFixed(1) : 0;
        });
    });

    const option = {
        title: {
            text: '各城市户型单位租金对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: layouts,
            top: 30
        },
        xAxis: {
            type: 'category',
            data: cities
        },
        yAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）'
        },
        series: layouts.map((layout, index) => ({
            name: layout,
            type: 'bar',
            data: seriesData[layout],
            itemStyle: {
                color: ['#ee6666', '#73c0de', '#3ba272'][index]
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{c}'
            }
        }))
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 5. 板块分析（水平条形图，支持城市切换）====================
function renderBlockChart(cityName) {
    if (!blockChartInstance) {
        blockChartInstance = echarts.init(document.getElementById('chart-block'));
    }

    const data = analysisData.block_stats;
    const cityData = data.filter(d => d.city === cityName);

    // 按单价排序，取TOP10
    const sortedByPrice = [...cityData].sort((a, b) => b.price_per_m2_avg - a.price_per_m2_avg);
    const top10 = sortedByPrice.slice(0, 10);

    const displayData = top10;

    const option = {
        title: {
            text: `${cityName} TOP10 热门板块`,
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
                const p = params[0];
                return `${p.name}<br/>单位租金: ${p.value} 元/㎡`;
            }
        },
        grid: {
            left: '15%',
            right: '10%',
            top: 60,
            bottom: 60
        },
        xAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）'
        },
        yAxis: {
            type: 'category',
            data: displayData.map(d => d.block),
            axisLabel: {
                fontSize: 11,
                width: 100,
                overflow: 'truncate'
            }
        },
        series: [{
            name: '单位租金',
            type: 'bar',
            data: displayData.map(d => d.price_per_m2_avg.toFixed(1)),
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#ee6666' },
                    { offset: 1, color: '#fc8452' }
                ])
            },
            label: {
                show: true,
                position: 'right',
                formatter: '{c}'
            }
        }]
    };

    blockChartInstance.setOption(option);

    // 更新标题和洞察
    document.getElementById('block-chart-title').textContent = `${cityName} TOP10 热门板块`;
}

// ==================== 6. 朝向分析（分组柱状图）====================
function renderOrientationChart() {
    const chart = echarts.init(document.getElementById('chart-orientation'));
    const data = analysisData.orientation_stats;

    const cities = ['上海', '北京', '广州', '杭州', '深圳'];
    const orientations = ['东', '南', '西', '北', '东南', '东北', '西南', '西北'];

    const seriesData = cities.map(city => {
        return {
            name: city,
            type: 'bar',
            data: orientations.map(orient => {
                const item = data.find(d => d.city === city && d.orientation === orient);
                return item ? item.price_per_m2_avg.toFixed(1) : 0;
            })
        };
    });

    const option = {
        title: {
            text: '各城市朝向单位租金对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            data: cities,
            top: 30
        },
        xAxis: {
            type: 'category',
            data: orientations
        },
        yAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）'
        },
        series: seriesData
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 7. 品牌分布（堆叠柱状图）====================
function renderBrandChart() {
    const chart = echarts.init(document.getElementById('chart-brand'));
    const data = analysisData.brand_stats;

    const cities = ['上海', '北京', '广州', '杭州', '深圳'];
    const brands = [...new Set(data.map(d => d.brand))];

    const seriesData = brands.map(brand => {
        return {
            name: brand,
            type: 'bar',
            stack: 'total',
            data: cities.map(city => {
                const item = data.find(d => d.city === city && d.brand === brand);
                return item ? item.market_share.toFixed(1) : 0;
            }),
            label: {
                show: true,
                formatter: '{c}%'
            }
        };
    });

    const option = {
        title: {
            text: '各城市品牌市场份额（%）',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
                let result = params[0].name + '<br/>';
                params.forEach(p => {
                    result += `${p.seriesName}: ${p.value}%<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: brands,
            top: 30
        },
        xAxis: {
            type: 'category',
            data: cities
        },
        yAxis: {
            type: 'value',
            name: '市场份额（%）',
            max: 100
        },
        series: seriesData
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 8. 工资租金关系 - 散点图 ====================
function renderSalaryScatterChart() {
    const chart = echarts.init(document.getElementById('chart-salary-scatter'));
    const data = analysisData.salary_rent;

    const scatterData = data.cities.map((city, index) => ({
        name: city,
        value: [data.salary_private_monthly[index], data.price_per_m2_avg[index]]
    }));

    const option = {
        title: {
            text: '工资 vs 单位租金相关性',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `${params.data.name}<br/>私营月薪: ${params.value[0]} 元<br/>单位租金: ${params.value[1]} 元/㎡`;
            }
        },
        xAxis: {
            type: 'value',
            name: '私营月薪（元）',
            min: 6000,
            max: 10000
        },
        yAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）',
            min: 40,
            max: 90
        },
        series: [{
            type: 'scatter',
            data: scatterData,
            symbolSize: 20,
            itemStyle: {
                color: '#5470c6'
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{b}'
            }
        }]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 9. 工资租金关系 - 可租面积 ====================
function renderAffordableAreaChart() {
    const chart = echarts.init(document.getElementById('chart-affordable-area'));
    const data = analysisData.salary_rent;

    const option = {
        title: {
            text: '租房自由度（30%工资可租面积）',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        xAxis: {
            type: 'category',
            data: data.cities
        },
        yAxis: {
            type: 'value',
            name: '可租面积（㎡）'
        },
        series: [{
            name: '可租面积',
            type: 'bar',
            data: data.affordable_area_30pct,
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#91cc75' },
                    { offset: 1, color: '#5470c6' }
                ])
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{c} ㎡'
            }
        }]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 10. 工资租金关系 - 租金收入比 ====================
function renderRentToIncomeChart() {
    const chart = echarts.init(document.getElementById('chart-rent-to-income'));
    const data = analysisData.salary_rent;

    const option = {
        title: {
            text: '租金收入比（总租金/私营月薪）',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        xAxis: {
            type: 'category',
            data: data.cities
        },
        yAxis: {
            type: 'value',
            name: '租金收入比（%）',
            max: 70
        },
        series: [{
            name: '租金收入比',
            type: 'bar',
            data: data.rent_to_income_ratio,
            itemStyle: {
                color: function(params) {
                    const value = params.value;
                    if (value > 50) return '#ee6666'; // 红色：压力大
                    if (value > 40) return '#fac858'; // 黄色：中等
                    return '#91cc75'; // 绿色：友好
                }
            },
            markLine: {
                data: [
                    { yAxis: 30, name: '警戒线30%', lineStyle: { color: '#ee6666', type: 'dashed' } }
                ]
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{c}%'
            }
        }]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ==================== 11. 距离衰减分析（散点图+折线图）====================
function renderDistanceDecayChart(cityName) {
    if (!distanceChartInstance) {
        distanceChartInstance = echarts.init(document.getElementById('chart-distance-decay'));
    }

    const cityData = analysisData.distance_stats[cityName];
    if (!cityData) {
        console.error('距离衰减数据未找到:', cityName);
        return;
    }

    const stats = cityData.stats;
    const models = cityData.models;

    // 找出最优模型（R²最高）
    const bestModelIndex = models.r_squared.indexOf(Math.max(...models.r_squared));
    const bestModel = models.names[bestModelIndex];

    const option = {
        title: {
            text: `${cityName} 租金-距离衰减曲线`,
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' }
        },
        legend: {
            data: ['实际租金', '最优拟合曲线'],
            top: 30
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%'
        },
        xAxis: {
            type: 'value',
            name: '距离就业中心（km）',
            nameLocation: 'middle',
            nameGap: 30
        },
        yAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）',
            nameLocation: 'middle',
            nameGap: 50
        },
        series: [
            {
                name: '实际租金',
                type: 'scatter',
                data: stats.distance_groups.map((dist, index) => [dist, stats.price_per_m2_avg[index]]),
                symbolSize: function(data) {
                    // 根据房源数量调整点的大小
                    const index = stats.distance_groups.indexOf(data[0]);
                    const count = stats.count[index];
                    return Math.sqrt(count) / 5 + 5; // 最小5，按平方根缩放
                },
                itemStyle: {
                    color: 'rgba(84, 112, 198, 0.7)'
                }
            },
            {
                name: '最优拟合曲线',
                type: 'line',
                data: stats.distance_groups.map((dist, index) => [dist, stats.price_per_m2_avg[index]]),
                smooth: true,
                lineStyle: {
                    color: '#ee6666',
                    width: 2
                },
                showSymbol: false
            }
        ]
    };

    distanceChartInstance.setOption(option);

    // 更新标题和洞察
    document.getElementById('distance-chart-title').textContent = `${cityName} 租金-距离衰减曲线`;
}

// ==================== 12. 周边设施溢价分析（柱状图）====================
function renderAmenityDensityChart(cityName) {
    if (!amenityChartInstance) {
        amenityChartInstance = echarts.init(document.getElementById('chart-amenity-density'));
    }

    const cityData = analysisData.amenity_stats[cityName];
    if (!cityData) {
        console.error('周边设施数据未找到:', cityName);
        return;
    }

    const option = {
        title: {
            text: `${cityName} 配套设施密度与租金关系`,
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
                const p = params[0];
                const index = cityData.density_levels.indexOf(p.name);
                return `${p.name}<br/>
                        单位租金: ${cityData.price_per_m2_avg[index].toFixed(1)} 元/㎡<br/>
                        总租金: ${cityData.rent_avg[index].toFixed(0)} 元<br/>
                        样本量: ${cityData.count[index]} 套`;
            }
        },
        xAxis: {
            type: 'category',
            data: cityData.density_levels,
            axisLabel: { fontSize: 12 }
        },
        yAxis: {
            type: 'value',
            name: '单位租金（元/㎡/月）'
        },
        series: [{
            name: '单位租金',
            type: 'bar',
            data: cityData.price_per_m2_avg.map(v => v.toFixed(1)),
            itemStyle: {
                color: function(params) {
                    const colors = ['#91cc75', '#fac858', '#ee6666', '#5470c6'];
                    return colors[params.dataIndex];
                }
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{c}'
            }
        }]
    };

    amenityChartInstance.setOption(option);

    // 更新标题和洞察
    document.getElementById('amenity-chart-title').textContent = `${cityName} 配套设施密度与租金关系`;
}

// ==================== 13. 城市热力图切换 ====================
function switchHeatmap(cityName) {
    const cityCodeMap = {
        '北京': 'bj',
        '上海': 'sh',
        '广州': 'gz',
        '深圳': 'sz',
        '杭州': 'hz'
    };

    const cityCode = cityCodeMap[cityName];
    const iframe = document.getElementById('heatmap-iframe');
    iframe.src = `maps/${cityCode}_rental_heatmap.html`;

    // 更新标题
    document.getElementById('heatmap-chart-title').textContent = `${cityName}租金热力图`;
}

// ==================== 城市选择器事件绑定 ====================
function initCitySelector() {
    const cityButtons = document.querySelectorAll('.city-btn');

    cityButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // 移除所有active类
            cityButtons.forEach(b => b.classList.remove('active'));
            // 添加当前active类
            this.classList.add('active');
            // 重新渲染板块图表
            const cityName = this.getAttribute('data-city');
            renderBlockChart(cityName);
        });
    });
}

// ==================== 返回顶部按钮 ====================
function initBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ==================== 距离衰减城市选择器 ====================
function initDistanceCitySelector() {
    const cityButtons = document.querySelectorAll('.city-btn-distance');

    cityButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            cityButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const cityName = this.getAttribute('data-city');
            renderDistanceDecayChart(cityName);
        });
    });
}

// ==================== 周边设施城市选择器 ====================
function initAmenityCitySelector() {
    const cityButtons = document.querySelectorAll('.city-btn-amenity');

    cityButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            cityButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const cityName = this.getAttribute('data-city');
            renderAmenityDensityChart(cityName);
        });
    });
}

// ==================== 热力图城市选择器 ====================
function initHeatmapCitySelector() {
    const cityButtons = document.querySelectorAll('.city-btn-heatmap');

    cityButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            cityButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const cityName = this.getAttribute('data-city');
            switchHeatmap(cityName);
        });
    });
}

// ==================== 页面加载完成后初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    initCitySelector();
    initDistanceCitySelector();
    initAmenityCitySelector();
    initHeatmapCitySelector();
    initBackToTop();
});
