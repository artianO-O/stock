"""
板块月度涨幅分析脚本 - AkShare版本
使用 AkShare 获取行业板块历史数据，计算每月涨幅前3的板块
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
import time
import requests
warnings.filterwarnings('ignore')

# 设置请求超时和重试
requests.adapters.DEFAULT_RETRIES = 3


def retry_request(func, max_retries=3, delay=2):
    """带重试的请求函数"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                print(f'\n请求失败，{delay}秒后重试... ({i+1}/{max_retries})')
                time.sleep(delay)
            else:
                raise e
    return None


def get_sector_list():
    """获取所有行业板块列表"""
    print('正在获取行业板块列表...')
    try:
        df = retry_request(lambda: ak.stock_board_industry_name_em())
        if df is not None:
            print(f'获取到 {len(df)} 个行业板块')
            return df
    except Exception as e:
        print(f'获取板块列表失败: {e}')
    return None


def get_sector_history(sector_name, start_date, end_date):
    """获取单个板块的历史数据"""
    try:
        df = ak.stock_board_industry_hist_em(
            symbol=sector_name,
            period="日k",
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
        return df
    except Exception as e:
        return None


def calculate_monthly_returns(df):
    """计算月度涨幅"""
    if df is None or df.empty:
        return {}
    
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df['year_month'] = df['日期'].dt.strftime('%Y-%m')
    
    monthly_returns = {}
    
    for ym in df['year_month'].unique():
        month_data = df[df['year_month'] == ym].sort_values('日期')
        if len(month_data) >= 2:
            first_open = float(month_data.iloc[0]['开盘'])
            last_close = float(month_data.iloc[-1]['收盘'])
            if first_open > 0:
                ret = (last_close - first_open) / first_open * 100
                monthly_returns[ym] = round(ret, 2)
    
    return monthly_returns


def get_top3_stocks_simple():
    """简化版：获取股票月度数据"""
    print('\n正在获取股票数据...')
    
    try:
        df = retry_request(lambda: ak.stock_zh_a_spot_em())
        if df is None:
            return {}
        df = df.sort_values('成交额', ascending=False).head(80)
        stocks = df[['代码', '名称']].values.tolist()
        print(f'获取到 {len(stocks)} 只活跃股票')
    except Exception as e:
        print(f'获取股票列表失败: {e}')
        return {}
    
    all_monthly_data = []
    total = len(stocks)
    
    for i, (code, name) in enumerate(stocks):
        try:
            hist = ak.stock_zh_a_hist(
                symbol=code,
                period="monthly",
                start_date="20230101",
                end_date=datetime.now().strftime('%Y%m%d'),
                adjust="qfq"
            )
            
            if hist is not None and not hist.empty:
                hist = hist.copy()
                hist['代码'] = code
                hist['名称'] = name
                hist['日期'] = pd.to_datetime(hist['日期'])
                hist['year_month'] = hist['日期'].dt.strftime('%Y-%m')
                hist['涨幅'] = (hist['收盘'] - hist['开盘']) / hist['开盘'] * 100
                all_monthly_data.append(hist[['代码', '名称', 'year_month', '涨幅', '收盘']])
            
            time.sleep(0.15)
            
        except Exception as e:
            pass
        
        if (i + 1) % 20 == 0:
            print(f'\r股票进度: {i+1}/{total}', end='', flush=True)
    
    print()
    
    if not all_monthly_data:
        print('未获取到股票数据')
        return {}
    
    combined = pd.concat(all_monthly_data, ignore_index=True)
    
    top3_stocks = {}
    for ym in combined['year_month'].unique():
        month_data = combined[combined['year_month'] == ym].copy()
        month_data = month_data.sort_values('涨幅', ascending=False).head(3)
        top3_stocks[ym] = [
            {
                'code': str(row['代码']),
                'name': str(row['名称']),
                'return': round(float(row['涨幅']), 2),
                'price': round(float(row['收盘']), 2)
            }
            for _, row in month_data.iterrows()
        ]
    
    print(f'获取到 {len(top3_stocks)} 个月份的股票数据')
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
        top3 = month_data[:3]
        result[month] = top3
    
    return result


def main():
    """主函数"""
    
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # 获取板块列表
    sector_df = get_sector_list()
    if sector_df is None:
        print('无法获取板块列表，请检查网络连接后重试')
        return
    
    start_date = '20230101'
    end_date = datetime.now().strftime('%Y%m%d')
    
    print(f'\n开始获取板块历史数据 ({start_date} - {end_date})...\n')
    
    industry_returns = {}
    total = len(sector_df)
    
    for i, row in sector_df.iterrows():
        sector_name = row['板块名称']
        
        try:
            df = get_sector_history(sector_name, start_date, end_date)
            
            if df is not None and not df.empty:
                monthly_returns = calculate_monthly_returns(df)
                if monthly_returns:
                    industry_returns[sector_name] = monthly_returns
        except:
            pass
        
        progress = (i + 1) / total * 100
        print(f'\r板块进度: {i+1}/{total} ({progress:.1f}%) - {sector_name}', end='', flush=True)
        
        time.sleep(0.1)
    
    print('\n\n板块数据获取完成!')
    print(f'成功获取 {len(industry_returns)} 个板块的数据')
    
    if len(industry_returns) == 0:
        print('未获取到任何数据，请稍后重试')
        return
    
    top3_per_month = get_top3_per_month(industry_returns)
    
    # 获取股票数据
    top3_stocks = get_top3_stocks_simple()
    
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
    
    print('\n=== 每月涨幅前3板块预览 ===')
    for month, top3 in list(top3_per_month.items())[-6:]:
        print(f'\n{month}:')
        for i, item in enumerate(top3, 1):
            print(f'  {i}. {item["industry"]}: {item["return"]}%')


if __name__ == '__main__':
    main()
