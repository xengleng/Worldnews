#!/usr/bin/env python3
import urllib.request
import json

def check_gold():
    try:
        # Try gold ETF GLD
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GLD'
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                price = data['chart']['result'][0]['meta']['regularMarketPrice']
                print(f'GLD ETF: ${price:.2f}')
                # GLD is approximately 1/10th of gold price per ounce
                print(f'Estimated gold price: ${price*10:.2f}/oz')
                return price * 10
    except Exception as e:
        print(f'Error: {e}')
    
    return None

if __name__ == "__main__":
    check_gold()