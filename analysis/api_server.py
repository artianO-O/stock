#!/usr/bin/env python3
"""
股票数据API服务器
提供个股K线数据查询接口
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
import ssl

# 忽略SSL证书验证
ssl._create_default_https_context = ssl._create_unverified_context

class StockAPIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # API路由
        if parsed_path.path == '/api/kline':
            self.handle_kline_api(parsed_path.query)
        else:
            # 静态文件服务
            super().do_GET()
    
    def handle_kline_api(self, query_string):
        """处理K线数据请求"""
        params = urllib.parse.parse_qs(query_string)
        code = params.get('code', [''])[0]
        
        if not code:
            self.send_json_response({'error': '请提供股票代码'}, 400)
            return
        
        try:
            # 获取股票数据
            data = self.get_stock_kline(code)
            self.send_json_response(data)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def get_stock_kline(self, code):
        """获取股票K线数据 - 使用腾讯财经接口"""
        import re
        
        # 确定市场前缀
        if code.startswith('6'):
            symbol = f"sh{code}"
            market = "上海"
        elif code.startswith('0') or code.startswith('3'):
            symbol = f"sz{code}"
            market = "深圳"
        else:
            symbol = f"sh{code}"
            market = "未知"
        
        try:
            # 1. 获取股票实时信息（名称、价格）
            info_url = f"http://qt.gtimg.cn/q={symbol}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(info_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                info_content = response.read().decode('gbk')
            
            # 解析腾讯数据格式: v_sh600519="1~贵州茅台~600519~1856.00~1868.00~..."
            info_parts = info_content.split('~')
            if len(info_parts) < 5:
                raise Exception(f"股票 {code} 不存在或已退市")
            
            name = info_parts[1]
            price = float(info_parts[3])
            yesterday_close = float(info_parts[4])
            change = (price - yesterday_close) / yesterday_close * 100 if yesterday_close > 0 else 0
            
            # 2. 获取K线数据
            # 腾讯日K线接口
            kline_url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,320,qfq"
            req = urllib.request.Request(kline_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                kline_content = response.read().decode('utf-8')
            
            kline_json = json.loads(kline_content)
            
            # 解析K线数据
            kline_data = []
            if 'data' in kline_json and symbol in kline_json['data']:
                stock_data = kline_json['data'][symbol]
                day_data = stock_data.get('qfqday', stock_data.get('day', []))
                
                for item in day_data:
                    if len(item) >= 5:
                        # 腾讯API格式: [日期, 开盘, 收盘, 最高, 最低, 成交量]
                        kline_data.append({
                            'date': item[0],
                            'open': float(item[1]),
                            'close': float(item[2]),
                            'high': float(item[3]),
                            'low': float(item[4]),
                            'volume': float(item[5]) if len(item) > 5 else 0,
                            'amount': 0
                        })
            
            if not kline_data:
                raise Exception(f"获取 {code} K线数据失败")
            
            print(f"[成功] 获取 {name}({code}) 数据，共 {len(kline_data)} 条")
            
            return {
                'code': code,
                'name': name,
                'market': market,
                'price': price,
                'change': round(change, 2),
                'kline': kline_data
            }
            
        except Exception as e:
            raise Exception(f"获取数据失败: {str(e)}")
    
    def send_json_response(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        if '/api/' in args[0]:
            print(f"[API] {args[0]}")

def run_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), StockAPIHandler)
    print(f"=" * 50)
    print(f"股票数据API服务器已启动")
    print(f"访问地址: http://localhost:{port}")
    print(f"K线API: http://localhost:{port}/api/kline?code=600519")
    print(f"=" * 50)
    server.serve_forever()

if __name__ == '__main__':
    run_server()

