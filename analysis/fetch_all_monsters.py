#!/usr/bin/env python3
"""
获取全市场每月涨幅最高的股票（扩大股票池版本）
使用腾讯API批量获取
"""

import urllib.request
import json
from datetime import datetime
import ssl
import time
from tqdm import tqdm
import concurrent.futures
from threading import Lock

ssl._create_default_https_context = ssl._create_unverified_context

# 更大的股票池（覆盖各行业 + 中小盘）
def get_extended_stock_list():
    """获取扩展的股票列表"""
    stocks = [
        # === 军工航天 ===
        ('000547', '航天发展'), ('600343', '航天动力'), ('600893', '航发动力'),
        ('002025', '航天电器'), ('600760', '中航沈飞'), ('000768', '中航西飞'),
        ('600862', '中航高科'), ('600118', '中国卫星'), ('000738', '航发控制'),
        ('600316', '洪都航空'), ('002013', '中航机电'), ('600765', '中航重机'),
        ('600038', '中直股份'), ('000901', '航天科技'), ('600391', '航发科技'),
        ('002190', '成飞集成'), ('600677', '航天通信'), ('600435', '北方导航'),
        
        # === AI/科技 ===
        ('002230', '科大讯飞'), ('300418', '昆仑万维'), ('688256', '寒武纪'),
        ('688041', '海光信息'), ('300474', '景嘉微'), ('002415', '海康威视'),
        ('300229', '拓尔思'), ('300624', '万兴科技'), ('002049', '紫光国微'),
        ('300496', '中科创达'), ('300454', '深信服'), ('688111', '金山办公'),
        ('300033', '同花顺'), ('002555', '三七互娱'), ('300253', '卫宁健康'),
        
        # === 光模块/通信 ===
        ('300308', '中际旭创'), ('300502', '新易盛'), ('002475', '立讯精密'),
        ('000063', '中兴通讯'), ('600703', '三安光电'), ('300296', '利亚德'),
        ('300394', '天孚通信'), ('688498', '源杰科技'), ('300602', '飞荣达'),
        
        # === 半导体/芯片 ===
        ('002371', '北方华创'), ('688012', '中微公司'), ('688981', '中芯国际'),
        ('603501', '韦尔股份'), ('002916', '深南电路'), ('603986', '兆易创新'),
        ('300782', '卓胜微'), ('688536', '思瑞浦'), ('688008', '澜起科技'),
        ('002049', '紫光国微'), ('300661', '圣邦股份'), ('300223', '北京君正'),
        
        # === 新能源 ===
        ('300750', '宁德时代'), ('002594', '比亚迪'), ('601012', '隆基绿能'),
        ('002460', '赣锋锂业'), ('600438', '通威股份'), ('002459', '晶澳科技'),
        ('688599', '天合光能'), ('002129', 'TCL中环'), ('300274', '阳光电源'),
        ('002074', '国轩高科'), ('300014', '亿纬锂能'), ('002812', '恩捷股份'),
        
        # === 金融 ===
        ('600030', '中信证券'), ('601318', '中国平安'), ('600036', '招商银行'),
        ('601688', '华泰证券'), ('601211', '国泰君安'), ('600837', '海通证券'),
        ('601066', '中信建投'), ('600999', '招商证券'), ('601377', '兴业证券'),
        
        # === 消费/白酒 ===
        ('600519', '贵州茅台'), ('000858', '五粮液'), ('000333', '美的集团'),
        ('000651', '格力电器'), ('601888', '中国中免'), ('000568', '泸州老窖'),
        ('600690', '海尔智家'), ('002304', '洋河股份'), ('600600', '青岛啤酒'),
        
        # === 周期/资源 ===
        ('601088', '中国神华'), ('600028', '中国石化'), ('601857', '中国石油'),
        ('601899', '紫金矿业'), ('600019', '宝钢股份'), ('000725', '京东方A'),
        ('600489', '中金黄金'), ('601600', '中国铝业'), ('600362', '江西铜业'),
        
        # === 电力 ===
        ('600900', '长江电力'), ('600886', '国投电力'), ('601985', '中国核电'),
        ('600025', '华能水电'), ('600011', '华能国际'), ('600027', '华电国际'),
        
        # === 医药 ===
        ('300760', '迈瑞医疗'), ('000661', '长春高新'), ('603259', '药明康德'),
        ('300122', '智飞生物'), ('002007', '华兰生物'), ('600276', '恒瑞医药'),
        
        # === 地产基建 ===
        ('600048', '保利发展'), ('601668', '中国建筑'), ('601390', '中国中铁'),
        ('000002', '万科A'), ('001979', '招商蛇口'), ('600606', '绿地控股'),
        
        # === 传媒游戏 ===
        ('002602', '世纪华通'), ('002027', '分众传媒'), ('300413', '芒果超媒'),
        ('002607', '中公教育'), ('300058', '蓝色光标'), ('002624', '完美世界'),
        
        # === 中小盘/题材股 ===
        ('603778', '国晟科技'), ('002927', '泰永长征'), ('300805', '电声股份'),
        ('603225', '新凤鸣'), ('002985', '北摩高科'), ('603179', '新泉股份'),
        ('300865', '大宏立'), ('002984', '森麒麟'), ('300919', '中伟股份'),
        ('002791', '坚朗五金'), ('603893', '瑞芯微'), ('300285', '国瓷材料'),
        ('300896', '爱美客'), ('688169', '石头科技'), ('300759', '康龙化成'),
        
        # === 更多中小盘题材股 ===
        ('002600', '领益智造'), ('002241', '歌尔股份'), ('603501', '韦尔股份'),
        ('300408', '三环集团'), ('002463', '沪电股份'), ('688036', '传音控股'),
        ('300595', '欧普康视'), ('300347', '泰格医药'), ('300760', '迈瑞医疗'),
        ('601100', '恒立液压'), ('603288', '海天味业'), ('603899', '晨光文具'),
    ]
    
    # 去重
    seen = set()
    unique_stocks = []
    for code, name in stocks:
        if code not in seen:
            seen.add(code)
            unique_stocks.append((code, name))
    
    return unique_stocks

def get_stock_kline(code, days=800):
    """获取股票K线数据"""
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
                return data['data'][symbol].get('qfqday', data['data'][symbol].get('day', []))
    except:
        pass
    return []

def calculate_monthly_return(kline_data, year, month):
    """计算指定月份的涨幅"""
    month_str = f'{year}-{month:02d}'
    month_data = [d for d in kline_data if d[0].startswith(month_str)]
    
    if len(month_data) < 2:
        return None
    
    first_close = float(month_data[0][2])
    last_close = float(month_data[-1][2])
    
    if first_close <= 0:
        return None
    
    return round((last_close - first_close) / first_close * 100, 2)

def guess_theme(name, code):
    """根据股票名称猜测主题"""
    themes = {
        'AI': ['讯飞', '昆仑', '寒武纪', '海光', '商汤', '万维', '拓尔思', '万兴', '同花顺'],
        '芯片': ['芯片', '半导体', '紫光', '中芯', '北方华创', '中微', '韦尔', '兆易', '卓胜微'],
        '光模块': ['旭创', '新易盛', '立讯', '利亚德', '天孚'],
        '军工': ['航天', '航空', '中航', '航发', '洪都', '成飞', '国防', '北方导航'],
        '新能源': ['宁德', '比亚迪', '隆基', '锂业', '通威', '晶澳', '天合', '阳光', '亿纬'],
        '金融': ['证券', '银行', '平安', '国泰', '海通', '华泰', '中信建投'],
        '白酒': ['茅台', '五粮液', '泸州', '洋河'],
        '家电': ['美的', '格力', '海尔'],
        '电力': ['电力', '水电', '核电', '华能', '长江'],
        '资源': ['神华', '石化', '石油', '紫金', '中金', '铝业', '铜业'],
        '通信': ['中兴', '三安', '通信'],
        '医药': ['迈瑞', '长春', '药明', '智飞', '恒瑞'],
    }
    
    for theme, keywords in themes.items():
        for keyword in keywords:
            if keyword in name:
                return theme
    
    if code.startswith('688'):
        return '科创板'
    elif code.startswith('300'):
        return '创业板'
    else:
        return '其他'

def main():
    print("=" * 60)
    print("A股全市场月度妖股统计（扩展股票池）")
    print("=" * 60)
    
    current_date = datetime.now()
    stocks = get_extended_stock_list()
    
    print(f"\n股票池: {len(stocks)} 只股票")
    
    # 定义月份
    months_to_analyze = []
    for year in [2023, 2024, 2025]:
        for month in range(1, 13):
            if year == 2025 and month > current_date.month:
                break
            months_to_analyze.append((year, month))
    
    print(f"分析 {len(months_to_analyze)} 个月份...")
    
    # 获取所有股票的K线数据
    stock_klines = {}
    print("\n正在获取K线数据...")
    
    for code, name in tqdm(stocks, desc="获取K线"):
        kline = get_stock_kline(code, 800)
        if kline:
            stock_klines[code] = {'name': name, 'kline': kline}
        time.sleep(0.1)
    
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
    for month, stocks_data in monthly_monsters.items():
        themes = [s['theme'] for s in stocks_data]
        monthly_themes[month] = themes
    
    result = {
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_source': f'腾讯财经历史K线统计（{len(stocks)}只股票）',
        'stock_count': len(stocks),
        'monthly_monsters': monthly_monsters,
        'monthly_themes': monthly_themes
    }
    
    # 保存数据
    with open('data/monster_stocks.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("数据已保存到 data/monster_stocks.json")
    print("=" * 60)
    
    # 打印统计
    for year in [2023, 2024, 2025]:
        print(f"\n=== {year}年 月度妖股 ===")
        for month in range(1, 13):
            month_key = f'{year}-{month:02d}'
            if month_key in monthly_monsters:
                stocks_data = monthly_monsters[month_key]
                top1 = stocks_data[0]
                sign = '+' if top1['return'] >= 0 else ''
                print(f"  {month:2d}月: {top1['name']} {sign}{top1['return']}% [{top1['theme']}]")

if __name__ == '__main__':
    main()
