#!/usr/bin/env python3
"""
获取真实的每月涨幅最高股票（妖股）
使用腾讯API获取历史K线数据
"""

import urllib.request
import json
from datetime import datetime, timedelta
import ssl
import time
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context

# 热门股票池（各行业代表 - 扩大范围）
HOT_STOCKS = [
    # AI/科技
    ('002230', '科大讯飞'), ('300418', '昆仑万维'), ('688256', '寒武纪'),
    ('688041', '海光信息'), ('300474', '景嘉微'), ('002415', '海康威视'),
    ('300229', '拓尔思'), ('300624', '万兴科技'), ('002049', '紫光国微'),
    # 通信/光模块
    ('300308', '中际旭创'), ('300502', '新易盛'), ('002475', '立讯精密'),
    ('000063', '中兴通讯'), ('600703', '三安光电'), ('300296', '利亚德'),
    # 新能源
    ('300750', '宁德时代'), ('002594', '比亚迪'), ('601012', '隆基绿能'),
    ('002460', '赣锋锂业'), ('600438', '通威股份'), ('002459', '晶澳科技'),
    # 军工
    ('600343', '航天动力'), ('600893', '航发动力'), ('002025', '航天电器'),
    ('600760', '中航沈飞'), ('000768', '中航西飞'), ('600862', '中航高科'),
    # 金融
    ('600030', '中信证券'), ('601318', '中国平安'), ('600036', '招商银行'),
    ('601688', '华泰证券'), ('601211', '国泰君安'), ('600837', '海通证券'),
    # 消费
    ('600519', '贵州茅台'), ('000858', '五粮液'), ('000333', '美的集团'),
    ('000651', '格力电器'), ('601888', '中国中免'), ('000568', '泸州老窖'),
    # 周期
    ('601088', '中国神华'), ('600028', '中国石化'), ('000725', '京东方A'),
    ('601857', '中国石油'), ('601899', '紫金矿业'), ('600019', '宝钢股份'),
    # 电力
    ('600900', '长江电力'), ('600886', '国投电力'), ('601985', '中国核电'),
    ('600025', '华能水电'), ('600011', '华能国际'),
    # 半导体
    ('002371', '北方华创'), ('688012', '中微公司'), ('688981', '中芯国际'),
    ('603501', '韦尔股份'), ('002916', '深南电路'),
    # 医药
    ('300760', '迈瑞医疗'), ('000661', '长春高新'), ('603259', '药明康德'),
    # 地产基建
    ('600048', '保利发展'), ('601668', '中国建筑'), ('601390', '中国中铁'),
    # 传媒游戏
    ('002602', '世纪华通'), ('002027', '分众传媒'), ('300413', '芒果超媒'),
]

def get_stock_kline(code, days=500):
    """获取股票K线数据"""
    # 确定市场前缀
    if code.startswith('6'):
        symbol = f'sh{code}'
    else:
        symbol = f'sz{code}'
    
    url = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,{days},qfq'
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            
            if 'data' in data and symbol in data['data']:
                stock_data = data['data'][symbol]
                day_data = stock_data.get('qfqday', stock_data.get('day', []))
                return day_data
    except Exception as e:
        pass
    
    return []

def calculate_monthly_return(kline_data, year, month):
    """计算指定月份的涨幅"""
    month_str = f'{year}-{month:02d}'
    
    # 筛选该月的数据
    month_data = [d for d in kline_data if d[0].startswith(month_str)]
    
    if len(month_data) < 2:
        return None
    
    first_close = float(month_data[0][2])  # 开盘第一天的收盘价
    last_close = float(month_data[-1][2])  # 最后一天的收盘价
    
    if first_close <= 0:
        return None
    
    return round((last_close - first_close) / first_close * 100, 2)

def guess_theme(name, code):
    """根据股票名称猜测主题"""
    themes = {
        'AI': ['讯飞', '昆仑', '寒武纪', '海光', '商汤', '万维', '拓尔思'],
        '芯片': ['芯片', '半导体', '紫光', '中芯', '北方华创', '中微', '韦尔'],
        '光模块': ['旭创', '新易盛', '立讯', '利亚德'],
        '军工': ['航天', '航空', '军工', '中航', '航发'],
        '新能源': ['宁德', '比亚迪', '隆基', '锂业', '通威', '晶澳'],
        '金融': ['证券', '银行', '平安', '国泰', '海通', '华泰'],
        '白酒': ['茅台', '五粮液', '泸州', '洋河'],
        '家电': ['美的', '格力', '海尔'],
        '电力': ['电力', '水电', '核电', '华能'],
        '煤炭石化': ['神华', '石化', '石油', '煤炭'],
        '通信': ['中兴', '三安', '通信'],
        '医药': ['迈瑞', '长春', '药明'],
    }
    
    for theme, keywords in themes.items():
        for keyword in keywords:
            if keyword in name:
                return theme
    
    return '其他'

def main():
    print("=" * 60)
    print("A股月度妖股统计（真实数据 - 腾讯API）")
    print("=" * 60)
    
    current_date = datetime.now()
    
    # 定义要分析的月份
    months_to_analyze = []
    for year in [2023, 2024, 2025]:
        for month in range(1, 13):
            if year == 2025 and month > current_date.month:
                break
            months_to_analyze.append((year, month))
    
    print(f"\n分析 {len(months_to_analyze)} 个月份，{len(HOT_STOCKS)} 只股票...")
    
    # 先获取所有股票的K线数据
    stock_klines = {}
    print("\n正在获取K线数据...")
    
    for code, name in tqdm(HOT_STOCKS, desc="获取K线"):
        kline = get_stock_kline(code, 800)  # 获取约3年数据
        if kline:
            stock_klines[code] = {'name': name, 'kline': kline}
        time.sleep(0.1)  # 避免请求过快
    
    print(f"成功获取 {len(stock_klines)} 只股票的K线数据")
    
    # 分析每个月的涨幅
    monthly_monsters = {}
    
    print("\n正在统计月度涨幅...")
    for year, month in tqdm(months_to_analyze, desc="统计月份"):
        month_key = f'{year}-{month:02d}'
        monthly_returns = []
        
        for code, data in stock_klines.items():
            name = data['name']
            kline = data['kline']
            
            ret = calculate_monthly_return(kline, year, month)
            if ret is not None:
                theme = guess_theme(name, code)
                monthly_returns.append({
                    'code': code,
                    'name': name,
                    'return': ret,
                    'theme': theme
                })
        
        # 排序取Top3
        monthly_returns.sort(key=lambda x: x['return'], reverse=True)
        top3 = monthly_returns[:3]
        
        if top3:
            monthly_monsters[month_key] = top3
    
    if not monthly_monsters:
        print("获取数据失败！")
        return
    
    # 统计主题
    monthly_themes = {}
    for month, stocks in monthly_monsters.items():
        themes = [s['theme'] for s in stocks]
        monthly_themes[month] = themes
    
    result = {
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_source': '腾讯财经历史K线数据统计',
        'stock_count': len(HOT_STOCKS),
        'monthly_monsters': monthly_monsters,
        'monthly_themes': monthly_themes
    }
    
    # 保存数据
    with open('data/monster_stocks.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("数据已保存到 data/monster_stocks.json")
    print("=" * 60)
    
    # 打印每年的统计
    for year in [2023, 2024, 2025]:
        print(f"\n=== {year}年 月度妖股 ===")
        for month in range(1, 13):
            month_key = f'{year}-{month:02d}'
            if month_key in monthly_monsters:
                stocks = monthly_monsters[month_key]
                top1 = stocks[0]
                sign = '+' if top1['return'] >= 0 else ''
                print(f"  {month:2d}月: {top1['name']} {sign}{top1['return']}% [{top1['theme']}]")

if __name__ == '__main__':
    main()
