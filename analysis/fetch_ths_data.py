#!/usr/bin/env python3
"""
获取同花顺概念板块历史数据
使用 AkShare 接口获取更贴近实际炒作的板块数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import json
import time

def get_concept_boards():
    """获取同花顺概念板块列表"""
    print("正在获取同花顺概念板块列表...")
    df = ak.stock_board_concept_name_ths()
    return df

def get_board_history(board_code, board_name, start_date, end_date):
    """获取单个板块的历史行情"""
    try:
        df = ak.stock_board_concept_hist_ths(
            symbol=board_name,
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
        if df is not None and not df.empty:
            return df
    except Exception as e:
        pass
    return None

def calculate_monthly_returns(df):
    """计算月度涨跌幅"""
    if df is None or df.empty:
        return {}
    
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.sort_values('日期')
    
    # 按月分组
    df['年月'] = df['日期'].dt.strftime('%Y-%m')
    
    monthly_returns = {}
    for ym, group in df.groupby('年月'):
        if len(group) >= 2:
            first_close = group.iloc[0]['收盘']
            last_close = group.iloc[-1]['收盘']
            if first_close > 0:
                ret = (last_close - first_close) / first_close * 100
                monthly_returns[ym] = round(ret, 2)
    
    return monthly_returns

def main():
    print("=" * 60)
    print("同花顺概念板块数据获取")
    print("=" * 60)
    
    # 日期范围
    start_date = "20230101"
    end_date = datetime.now().strftime("%Y%m%d")
    
    # 获取板块列表
    boards = get_concept_boards()
    print(f"共获取 {len(boards)} 个概念板块")
    
    # 选择一些热门板块进行分析
    hot_boards = [
        'AI PC', 'AI手机', 'AI语料', '白酒概念', '半导体', '锂电池',
        '新能源汽车', '光伏概念', '消费电子', '芯片概念', '算力',
        '人工智能', '机器人概念', '无人驾驶', '虚拟现实', '元宇宙',
        '数字经济', '东数西算', '充电桩', '储能', '风电',
        '医药商业', '医疗器械', '中药', '创新药', '疫苗',
        '银行', '证券', '保险', '房地产', '煤炭概念',
        '钢铁', '有色金属', '稀土永磁', '黄金概念', '石油',
        '电力', '水利', '军工', '航天航空', '船舶',
        '旅游酒店', '食品饮料', '家电', '汽车整车', '农业种植',
        '教育', '游戏', '传媒', '网红经济', '直播电商',
        '跨境电商', '预制菜', '减肥药', 'CPO', 'HBM',
        '华为概念', '苹果概念', '小米概念', '特斯拉', '比亚迪概念',
        '券商', '酿酒', '家居用品', '物流', '电商',
        '供暖', '天然气', '水泥', '建材', '装修'
    ]
    
    # 匹配板块
    board_dict = {}
    for _, row in boards.iterrows():
        name = row['name']
        code = row['code']
        # 模糊匹配
        for hot in hot_boards:
            if hot in name or name in hot:
                board_dict[name] = code
                break
    
    print(f"匹配到 {len(board_dict)} 个热门板块")
    
    # 获取每个板块的历史数据
    all_returns = {}
    success_count = 0
    
    for i, (name, code) in enumerate(board_dict.items()):
        print(f"[{i+1}/{len(board_dict)}] 获取 {name} 数据...")
        try:
            df = get_board_history(code, name, start_date, end_date)
            if df is not None and not df.empty:
                returns = calculate_monthly_returns(df)
                if returns:
                    all_returns[name] = returns
                    success_count += 1
                    print(f"    ✓ 获取到 {len(returns)} 个月数据")
            time.sleep(0.5)  # 避免请求过快
        except Exception as e:
            print(f"    ✗ 失败: {e}")
    
    print(f"\n成功获取 {success_count} 个板块数据")
    
    # 统计每月涨幅Top3
    all_months = set()
    for returns in all_returns.values():
        all_months.update(returns.keys())
    
    top3_per_month = {}
    for ym in sorted(all_months):
        month_data = []
        for board, returns in all_returns.items():
            if ym in returns:
                month_data.append({
                    'board': board,
                    'return': returns[ym]
                })
        
        month_data.sort(key=lambda x: x['return'], reverse=True)
        top3_per_month[ym] = month_data[:3]
    
    # 保存数据
    result = {
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_source': '同花顺概念板块 (via AkShare)',
        'board_returns': all_returns,
        'top3_per_month': top3_per_month
    }
    
    with open('data/ths_sector_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n数据已保存到 data/ths_sector_analysis.json")
    
    # 打印结果预览
    print("\n=== 每月涨幅 Top3 板块预览 ===")
    for ym in sorted(top3_per_month.keys())[-12:]:  # 最近12个月
        print(f"\n{ym}:")
        for item in top3_per_month[ym]:
            print(f"  {item['board']}: {item['return']:+.2f}%")

if __name__ == '__main__':
    main()

