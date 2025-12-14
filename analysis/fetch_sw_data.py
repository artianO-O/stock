#!/usr/bin/env python3
"""
获取申万行业指数历史数据
申万行业分类是A股最常用的行业分类标准，和同花顺行业分类较为接近
"""

import akshare as ak
import pandas as pd
from datetime import datetime
from collections import defaultdict
import json
import time

# 申万一级行业代码和名称映射
SW_INDUSTRIES = {
    '801010': '农林牧渔',
    '801020': '采掘',
    '801030': '化工',
    '801040': '钢铁',
    '801050': '有色金属',
    '801080': '电子',
    '801110': '家用电器',
    '801120': '食品饮料',
    '801130': '纺织服装',
    '801140': '轻工制造',
    '801150': '医药生物',
    '801160': '公用事业',
    '801170': '交通运输',
    '801180': '房地产',
    '801200': '商业贸易',
    '801210': '休闲服务',
    '801230': '综合',
    '801710': '建筑材料',
    '801720': '建筑装饰',
    '801730': '电气设备',
    '801740': '国防军工',
    '801750': '计算机',
    '801760': '传媒',
    '801770': '通信',
    '801780': '银行',
    '801790': '非银金融',
    '801880': '汽车',
    '801890': '机械设备',
    '801950': '煤炭',
    '801960': '石油石化',
    '801970': '环保',
    '801980': '美容护理',
    '801990': '社会服务',
}

def get_industry_history(code, name):
    """获取单个行业指数的历史数据"""
    try:
        df = ak.index_hist_sw(symbol=code, period='day')
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"  获取 {name} 失败: {e}")
    return None

def calculate_monthly_returns(df):
    """计算月度涨跌幅"""
    if df is None or df.empty:
        return {}
    
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.sort_values('日期')
    
    # 筛选2023年以后的数据
    df = df[df['日期'] >= '2023-01-01']
    
    # 按月分组
    df['年月'] = df['日期'].dt.strftime('%Y-%m')
    
    monthly_returns = {}
    for ym, group in df.groupby('年月'):
        if len(group) >= 5:  # 至少5个交易日
            first_close = group.iloc[0]['收盘']
            last_close = group.iloc[-1]['收盘']
            if first_close > 0:
                ret = (last_close - first_close) / first_close * 100
                monthly_returns[ym] = round(ret, 2)
    
    return monthly_returns

def main():
    print("=" * 60)
    print("申万行业指数月度数据获取")
    print("=" * 60)
    
    # 获取每个行业的历史数据
    all_returns = {}
    success_count = 0
    
    for code, name in SW_INDUSTRIES.items():
        print(f"获取 {name}({code}) 数据...")
        try:
            df = get_industry_history(code, name)
            if df is not None and not df.empty:
                returns = calculate_monthly_returns(df)
                if returns:
                    all_returns[name] = returns
                    success_count += 1
                    print(f"  ✓ 获取到 {len(returns)} 个月数据")
            time.sleep(0.3)  # 避免请求过快
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    print(f"\n成功获取 {success_count} 个行业数据")
    
    # 统计每月涨幅Top3
    all_months = set()
    for returns in all_returns.values():
        all_months.update(returns.keys())
    
    top3_per_month = {}
    for ym in sorted(all_months):
        month_data = []
        for industry, returns in all_returns.items():
            if ym in returns:
                month_data.append({
                    'industry': industry,
                    'return': returns[ym]
                })
        
        month_data.sort(key=lambda x: x['return'], reverse=True)
        top3_per_month[ym] = month_data[:3]
    
    # 统计每个月份（1-12月）的行业表现规律
    monthly_patterns = defaultdict(lambda: defaultdict(list))
    for industry, returns in all_returns.items():
        for ym, ret in returns.items():
            month = int(ym.split('-')[1])
            monthly_patterns[month][industry].append(ret)
    
    # 计算每个月份每个行业的平均表现
    monthly_summary = {}
    for month in range(1, 13):
        industry_stats = []
        for industry, returns in monthly_patterns[month].items():
            if len(returns) >= 2:  # 至少2年数据
                avg = sum(returns) / len(returns)
                up_count = sum(1 for r in returns if r > 0)
                up_ratio = up_count / len(returns) * 100
                industry_stats.append({
                    'industry': industry,
                    'avg_return': round(avg, 2),
                    'up_ratio': round(up_ratio, 0),
                    'years': len(returns)
                })
        
        industry_stats.sort(key=lambda x: x['avg_return'], reverse=True)
        monthly_summary[month] = industry_stats[:5]  # Top5
    
    # 保存数据
    result = {
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_source': '申万行业指数 (via AkShare)',
        'industry_returns': all_returns,
        'top3_per_month': top3_per_month,
        'monthly_summary': monthly_summary
    }
    
    with open('data/sw_sector_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n数据已保存到 data/sw_sector_analysis.json")
    
    # 打印月度规律
    print("\n" + "=" * 60)
    print("月度行业表现规律（2023-2025年统计）")
    print("=" * 60)
    
    for month in range(1, 13):
        print(f"\n【{month}月】")
        for item in monthly_summary.get(month, []):
            print(f"  {item['industry']}: 平均{item['avg_return']:+.2f}% (上涨率{item['up_ratio']:.0f}%)")
    
    # 打印最近12个月Top3
    print("\n" + "=" * 60)
    print("最近每月涨幅 Top3 板块")
    print("=" * 60)
    
    for ym in sorted(top3_per_month.keys())[-12:]:
        print(f"\n{ym}:")
        for item in top3_per_month[ym]:
            print(f"  {item['industry']}: {item['return']:+.2f}%")

if __name__ == '__main__':
    main()

