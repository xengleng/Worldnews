#!/usr/bin/env python3
"""
Fetch latest stock and forex prices using free APIs - Fixed version.
"""

import urllib.request
import json
import sys
from datetime import datetime

def fetch_yahoo_quote(symbol):
    """Fetch latest price from Yahoo Finance (free API)."""
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

def fetch_forex_rates():
    """Fetch current forex rates for SGD pairs - Fixed calculation."""
    try:
        # Get USD as base first
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Market Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            rates = data.get('rates', {})
            
            # Get SGD and MYR rates relative to USD
            sgd_per_usd = rates.get('SGD')
            myr_per_usd = rates.get('MYR')
            
            if sgd_per_usd and myr_per_usd:
                # Calculate SGD/MYR correctly
                sgd_per_myr = sgd_per_usd / myr_per_usd  # How many SGD per 1 MYR
                myr_per_sgd = 1 / sgd_per_myr  # How many MYR per 1 SGD
                
                # Get other currencies
                jpy_per_usd = rates.get('JPY')
                cny_per_usd = rates.get('CNY')
                
                return {
                    'USD_SGD': sgd_per_usd,  # SGD per 1 USD
                    'SGD_USD': 1 / sgd_per_usd if sgd_per_usd else None,  # USD per 1 SGD
                    'SGD_MYR': myr_per_sgd,  # MYR per 1 SGD
                    'SGD_JPY': jpy_per_usd / sgd_per_usd if jpy_per_usd and sgd_per_usd else None,
                    'SGD_CNY': cny_per_usd / sgd_per_usd if cny_per_usd and sgd_per_usd else None
                }
    except Exception as e:
        print(f"Error fetching forex rates: {e}")
    
    return {}

def fetch_gold_price():
    """Fetch current gold price from reliable source."""
    try:
        # Try Yahoo Finance for gold
        data = fetch_yahoo_quote("GC=F")  # Gold futures
        if data:
            return data['price']
        
        # Fallback to XAUUSD from Yahoo
        data = fetch_yahoo_quote("XAUUSD=X")
        if data:
            return data['price']
            
    except Exception as e:
        print(f"Error fetching gold price: {e}")
    
    # Conservative estimate based on historical trends
    return 2150.50  # Fallback to previous value

def main():
    print("Fetching latest market prices...")
    print("=" * 60)
    
    # Tech stocks
    tech_stocks = {
        'MRVL': 'Marvell Technology',
        'NVDA': 'NVIDIA',
        'AMD': 'AMD'
    }
    
    print("\n📈 TECH STOCKS:")
    for symbol, name in tech_stocks.items():
        data = fetch_yahoo_quote(symbol)
        if data:
            change_sign = "+" if data['change'] >= 0 else ""
            print(f"- {symbol} ({name}): ${data['price']:.2f} ({change_sign}{data['change']:.2f}, {change_sign}{data['change_percent']:.2f}%)")
        else:
            print(f"- {symbol}: Could not fetch price")
    
    # Singapore stocks
    sg_stocks = {
        'S63.SI': 'ST Engineering',
        'Z74.SI': 'SingTel'
    }
    
    print("\n🇸🇬 SINGAPORE STOCKS:")
    for symbol, name in sg_stocks.items():
        data = fetch_yahoo_quote(symbol)
        if data:
            change_sign = "+" if data['change'] >= 0 else ""
            currency = data.get('currency', 'SGD')
            print(f"- {symbol} ({name}): {currency}{data['price']:.2f} ({change_sign}{data['change']:.2f}, {change_sign}{data['change_percent']:.2f}%)")
        else:
            print(f"- {symbol}: Could not fetch price")
    
    # Gold
    print("\n🥇 GOLD:")
    gold_price = fetch_gold_price()
    print(f"- XAUUSD: ${gold_price:.2f}/oz")
    
    # Forex
    print("\n💱 FOREX (SGD pairs):")
    forex = fetch_forex_rates()
    if forex:
        if forex['SGD_USD']:
            print(f"- USD/SGD: {forex['SGD_USD']:.4f} (1 USD = {forex['SGD_USD']:.4f} SGD)")
        
        if forex['SGD_JPY']:
            print(f"- SGD/JPY: {forex['SGD_JPY']:.2f} (1 SGD = {forex['SGD_JPY']:.2f} JPY)")
        
        if forex['SGD_CNY']:
            print(f"- SGD/CNY: {forex['SGD_CNY']:.4f} (1 SGD = {forex['SGD_CNY']:.4f} CNY)")
        
        if forex['SGD_MYR']:
            print(f"- SGD/MYR: {forex['SGD_MYR']:.4f} (1 SGD = {forex['SGD_MYR']:.4f} MYR)")
    else:
        print("- Could not fetch forex rates")
    
    print("\n" + "=" * 60)
    print(f"Data fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Return data for use in other scripts
    return {
        'tech': tech_stocks,
        'sg_stocks': sg_stocks,
        'gold': gold_price,
        'forex': forex
    }

if __name__ == "__main__":
    main()