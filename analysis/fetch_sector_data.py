"""
板块月度涨幅分析脚本
使用 Baostock 获取行业板块数据，计算每月涨幅前3的板块
"""

import baostock as bs
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def login():
    """登录 Baostock"""
    lg = bs.login()
    if lg.error_code != '0':
        print(f'登录失败: {lg.error_msg}')
        return False
    print('登录成功')
    return True


def get_industry_stocks():
    """获取所有股票的行业分类"""
    print('正在获取行业分类数据...')
    rs = bs.query_stock_industry()
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f'获取到 {len(df)} 只股票的行业分类')
    return df


def get_stock_monthly_data(code, start_date, end_date):
    """获取单只股票的月度数据"""
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,open,close",
        start_date=start_date,
        end_date=end_date,
        frequency="m",  # 月度数据
        adjustflag="2"  # 前复权
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        return None
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    
    # 计算月度涨幅 = (收盘价 - 开盘价) / 开盘价
    df['return'] = (df['close'] - df['open']) / df['open'] * 100
    df['year_month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    
    return df[['year_month', 'return']]


def calculate_industry_returns(industry_df, start_date, end_date):
    """计算每个行业每个月的平均涨幅"""
    
    # 按行业分组
    industries = industry_df['industry'].unique()
    print(f'共有 {len(industries)} 个行业板块')
    
    industry_returns = {}
    
    for i, industry in enumerate(industries):
        if not industry or industry == '':
            continue
            
        stocks = industry_df[industry_df['industry'] == industry]['code'].tolist()
        
        # 限制每个行业最多取50只股票（加快速度）
        stocks = stocks[:50]
        
        monthly_returns = {}
        valid_stocks = 0
        
        for code in stocks:
            try:
                df = get_stock_monthly_data(code, start_date, end_date)
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        ym = row['year_month']
                        ret = row['return']
                        if pd.notna(ret):
                            if ym not in monthly_returns:
                                monthly_returns[ym] = []
                            monthly_returns[ym].append(ret)
                    valid_stocks += 1
            except Exception as e:
                continue
        
        # 计算每月平均涨幅
        avg_returns = {}
        for ym, returns in monthly_returns.items():
            if returns:
                avg_returns[ym] = round(sum(returns) / len(returns), 2)
        
        if avg_returns:
            industry_returns[industry] = avg_returns
        
        print(f'进度: {i+1}/{len(industries)} - {industry}: {valid_stocks}只有效股票')
    
    return industry_returns


def get_top3_per_month(industry_returns):
    """获取每个月涨幅前3的板块"""
    
    # 收集所有月份
    all_months = set()
    for industry, returns in industry_returns.items():
        all_months.update(returns.keys())
    
    all_months = sorted(list(all_months))
    
    result = {}
    
    for month in all_months:
        # 获取该月所有板块的涨幅
        month_data = []
        for industry, returns in industry_returns.items():
            if month in returns:
                month_data.append({
                    'industry': industry,
                    'return': returns[month]
                })
        
        # 按涨幅排序，取前3
        month_data.sort(key=lambda x: x['return'], reverse=True)
        top3 = month_data[:3]
        
        result[month] = top3
    
    return result


def main():
    """主函数"""
    
    # 创建输出目录
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # 登录
    if not login():
        return
    
    try:
        # 获取行业分类
        industry_df = get_industry_stocks()
        
        # 计算行业月度涨幅 (2023-2025)
        print('\n开始计算行业月度涨幅（这可能需要一些时间）...\n')
        industry_returns = calculate_industry_returns(
            industry_df,
            start_date='2023-01-01',
            end_date='2025-12-31'
        )
        
        # 获取每月Top3
        top3_per_month = get_top3_per_month(industry_returns)
        
        # 保存完整数据
        output_data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'industry_returns': industry_returns,
            'top3_per_month': top3_per_month
        }
        
        output_file = output_dir / 'sector_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f'\n数据已保存到: {output_file}')
        
        # 打印预览
        print('\n=== 每月涨幅前3板块预览 ===')
        for month, top3 in list(top3_per_month.items())[-6:]:  # 最近6个月
            print(f'\n{month}:')
            for i, item in enumerate(top3, 1):
                print(f'  {i}. {item["industry"]}: {item["return"]}%')
        
    finally:
        bs.logout()
        print('\n已退出登录')


if __name__ == '__main__':
    main()

