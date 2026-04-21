#!/usr/bin/env python3
import urllib.request
import json

def fetch_yahoo_quote(symbol):
    """Fetch latest price from Yahoo Finance."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Market Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                regular_price = meta.get('regularMarketPrice')
                previous_close = meta.get('previousClose')
                
                if regular_price and previous_close:
                    change = regular_price - previous_close
                    change_percent = (change / previous_close) * 100
                    return {
                        'price': regular_price,
                        'change': change,
                        'change_percent': change_percent,
                        'previous_close': previous_close,
                        'currency': meta.get('currency', 'USD')
                    }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    
    return None

# Test fetching prices
print("Testing price fetching...")
symbols = ['MRVL', 'NVDA', 'S63.SI', 'Z74.SI', 'GLD']

for symbol in symbols:
    data = fetch_yahoo_quote(symbol)
    if data:
        change_sign = "+" if data['change'] >= 0 else ""
        currency = data.get('currency', 'USD')
        print(f"{symbol}: {currency}{data['price']:.2f} ({change_sign}{data['change']:.2f}, {change_sign}{data['change_percent']:.2f}%)")
    else:
        print(f"{symbol}: Could not fetch")