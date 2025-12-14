"""
板块月度涨幅分析脚本 - Baostock版本
使用 Baostock 获取行业板块历史数据
"""

import baostock as bs
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


def get_industry_stocks():
    """获取所有股票的行业分类"""
    print('正在获取行业分类数据...')
    rs = bs.query_stock_industry()
    
    data = []
    while rs.next():
        data.append(rs.get_row_data())
    
    df = pd.DataFrame(data, columns=rs.fields)
    df = df[df['industry'] != '']  # 过滤空行业
    
    # 按行业分组
    industry_stocks = defaultdict(list)
    for _, row in df.iterrows():
        industry = row['industry']
        # 简化行业名称
        if industry:
            # 去掉行业代码，只保留名称
            industry_name = industry.split('货币')[0] if '货币' in industry else industry
            industry_name = industry_name[3:] if len(industry_name) > 3 and industry_name[0].isalpha() else industry_name
            if industry_name:
                industry_stocks[industry_name].append(row['code'])
    
    print(f'获取到 {len(industry_stocks)} 个行业')
    return industry_stocks


def get_stock_monthly_data(code, start_date, end_date):
    """获取单只股票的月度数据"""
    rs = bs.query_history_k_data_plus(
        code,
        "date,open,close",
        start_date=start_date,
        end_date=end_date,
        frequency="m",  # 月度
        adjustflag="2"  # 前复权
    )
    
    data = []
    while rs.next():
        data.append(rs.get_row_data())
    
    if not data:
        return None
    
    df = pd.DataFrame(data, columns=['date', 'open', 'close'])
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['year_month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    df['return'] = (df['close'] - df['open']) / df['open'] * 100
    
    return df[['year_month', 'return']]


def calculate_industry_returns(industry_stocks, start_date, end_date):
    """计算每个行业每个月的平均涨幅"""
    print(f'\n开始计算行业月度涨幅...\n')
    
    industry_returns = {}
    industries = list(industry_stocks.keys())
    total = len(industries)
    
    for i, industry in enumerate(industries):
        stocks = industry_stocks[industry][:30]  # 每个行业最多取30只股票
        
        monthly_returns = defaultdict(list)
        valid_stocks = 0
        
        for code in stocks:
            try:
                df = get_stock_monthly_data(code, start_date, end_date)
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        ym = row['year_month']
                        ret = row['return']
                        if pd.notna(ret) and ret > -99 and ret < 200:  # 过滤异常值
                            monthly_returns[ym].append(ret)
                    valid_stocks += 1
            except:
                pass
        
        # 计算每月平均涨幅
        avg_returns = {}
        for ym, returns in monthly_returns.items():
            if len(returns) >= 3:  # 至少3只股票才计算
                avg_returns[ym] = round(sum(returns) / len(returns), 2)
        
        if avg_returns:
            industry_returns[industry] = avg_returns
        
        progress = (i + 1) / total * 100
        print(f'\r进度: {i+1}/{total} ({progress:.1f}%) - {industry} ({valid_stocks}只股票)', end='', flush=True)
    
    print('\n')
    return industry_returns


def get_top_stocks(start_date, end_date):
    """获取每月涨幅前3的股票"""
    print('正在获取Top股票数据...')
    
    # 获取沪深300成分股作为样本
    rs = bs.query_hs300_stocks()
    stocks = []
    while rs.next():
        stocks.append(rs.get_row_data())
    
    if not stocks:
        return {}
    
    stock_df = pd.DataFrame(stocks, columns=rs.fields)
    stock_list = stock_df[['code', 'code_name']].values.tolist()[:100]  # 取前100只
    
    print(f'获取到 {len(stock_list)} 只股票')
    
    all_monthly_data = []
    total = len(stock_list)
    
    for i, (code, name) in enumerate(stock_list):
        try:
            df = get_stock_monthly_data(code, start_date, end_date)
            if df is not None and not df.empty:
                df = df.copy()
                df['code'] = code.split('.')[1]  # 去掉 sh. 或 sz. 前缀
                df['name'] = name
                
                # 获取收盘价
                rs = bs.query_history_k_data_plus(
                    code, "date,close",
                    start_date=start_date, end_date=end_date,
                    frequency="m", adjustflag="2"
                )
                prices = []
                while rs.next():
                    prices.append(rs.get_row_data())
                if prices:
                    price_df = pd.DataFrame(prices, columns=['date', 'close'])
                    price_df['year_month'] = pd.to_datetime(price_df['date']).dt.strftime('%Y-%m')
                    price_df['close'] = pd.to_numeric(price_df['close'], errors='coerce')
                    df = df.merge(price_df[['year_month', 'close']], on='year_month', how='left')
                    df = df.rename(columns={'close': 'price'})
                
                all_monthly_data.append(df)
        except:
            pass
        
        if (i + 1) % 20 == 0:
            print(f'\r股票进度: {i+1}/{total}', end='', flush=True)
    
    print()
    
    if not all_monthly_data:
        return {}
    
    combined = pd.concat(all_monthly_data, ignore_index=True)
    combined = combined.dropna(subset=['return'])
    
    top3_stocks = {}
    for ym in combined['year_month'].unique():
        month_data = combined[combined['year_month'] == ym].copy()
        month_data = month_data.sort_values('return', ascending=False).head(3)
        top3_stocks[ym] = [
            {
                'code': str(row['code']),
                'name': str(row['name']),
                'return': round(float(row['return']), 2),
                'price': round(float(row.get('price', 0)), 2) if pd.notna(row.get('price')) else 0
            }
            for _, row in month_data.iterrows()
        ]
    
    return top3_stocks


def get_top3_per_month(industry_returns):
    """获取每个月涨幅前3的板块"""
    all_months = set()
    for industry, returns in industry_returns.items():
        all_months.update(returns.keys())
    
    all_months = sorted(list(all_months))
    result = {}
    
    for month in all_months:
        month_data = []
        for industry, returns in industry_returns.items():
            if month in returns:
                month_data.append({
                    'industry': industry,
                    'return': returns[month]
                })
        
        month_data.sort(key=lambda x: x['return'], reverse=True)
        result[month] = month_data[:3]
    
    return result


def main():
    """主函数"""
    
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # 登录
    print('正在登录 Baostock...')
    lg = bs.login()
    if lg.error_code != '0':
        print(f'登录失败: {lg.error_msg}')
        return
    print('登录成功!\n')
    
    try:
        # 获取行业分类
        industry_stocks = get_industry_stocks()
        
        # 时间范围
        start_date = '2023-01-01'
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算行业月度涨幅
        industry_returns = calculate_industry_returns(industry_stocks, start_date, end_date)
        
        print(f'成功计算 {len(industry_returns)} 个行业的数据')
        
        # 获取每月Top3板块
        top3_per_month = get_top3_per_month(industry_returns)
        
        # 获取每月Top3股票
        top3_stocks = get_top_stocks(start_date, end_date)
        
        # 保存数据
        output_data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'industry_returns': industry_returns,
            'top3_per_month': top3_per_month,
            'top3_stocks': top3_stocks
        }
        
        output_file = output_dir / 'sector_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f'\n数据已保存到: {output_file}')
        
        # 打印预览
        print('\n=== 每月涨幅前3板块预览 ===')
        for month, top3 in list(top3_per_month.items())[-6:]:
            print(f'\n{month}:')
            for i, item in enumerate(top3, 1):
                print(f'  {i}. {item["industry"]}: {item["return"]}%')
        
    finally:
        bs.logout()
        print('\n已退出 Baostock')


if __name__ == '__main__':
    main()

