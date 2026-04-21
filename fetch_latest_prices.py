#!/usr/bin/env python3
"""
Fetch latest stock and forex prices using free APIs.
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
    """Fetch current forex rates for SGD pairs."""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/SGD"
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Market Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            rates = data.get('rates', {})
            
            # Calculate SGD/MYR (MYR/SGD is inverse)
            if 'MYR' in rates:
                sgd_myr = 1 / rates['MYR']
            else:
                sgd_myr = None
                
            return {
                'USD': rates.get('USD'),
                'JPY': rates.get('JPY'),
                'CNY': rates.get('CNY'),
                'MYR': rates.get('MYR'),
                'SGD_MYR': sgd_myr
            }
    except Exception as e:
        print(f"Error fetching forex rates: {e}")
        return {}

def fetch_gold_price():
    """Fetch current gold price (XAUUSD)."""
    try:
        # Using Metals-API (free tier)
        url = "https://api.metalpriceapi.com/v1/latest?api_key=demo&base=XAU&currencies=USD"
        headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Market Monitor)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'rates' in data and 'USD' in data['rates']:
                # Convert from XAU (1 troy ounce) to USD
                return data['rates']['USD']
    except Exception as e:
        print(f"Error fetching gold price: {e}")
    
    # Fallback to Yahoo Finance
    gold_data = fetch_yahoo_quote("GC=F")  # Gold futures
    if gold_data:
        return gold_data['price']
    
    return None

def main():
    print("Fetching latest market prices...")
    print("=" * 60)
    
    # Tech stocks
    tech_stocks = {
        'MRVL': 'Marvell Technology',
        'NVDA': 'NVIDIA',
        'AMD': 'AMD',
        'FIG': 'Figma (private - placeholder)'
    }
    
    print("\n📈 TECH STOCKS:")
    for symbol, name in tech_stocks.items():
        if symbol == 'FIG':
            print(f"- {name}: Private company - no public price")
            continue
            
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
    if gold_price:
        print(f"- XAUUSD: ${gold_price:.2f}/oz")
    else:
        print("- XAUUSD: Could not fetch price")
    
    # Forex
    print("\n💱 FOREX (SGD pairs):")
    forex = fetch_forex_rates()
    if forex:
        if forex['USD']:
            usd_sgd = 1 / forex['USD']
            print(f"- USD/SGD: {usd_sgd:.4f} (1 USD = {usd_sgd:.4f} SGD)")
        
        if forex['JPY']:
            print(f"- SGD/JPY: {forex['JPY']:.2f} (1 SGD = {forex['JPY']:.2f} JPY)")
        
        if forex['CNY']:
            print(f"- SGD/CNY: {forex['CNY']:.4f} (1 SGD = {forex['CNY']:.4f} CNY)")
        
        if forex['SGD_MYR']:
            print(f"- SGD/MYR: {forex['SGD_MYR']:.4f} (1 SGD = {forex['SGD_MYR']:.4f} MYR)")
    else:
        print("- Could not fetch forex rates")
    
    print("\n" + "=" * 60)
    print(f"Data fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")

if __name__ == "__main__":
    main()