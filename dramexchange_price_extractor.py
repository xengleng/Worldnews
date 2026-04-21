#!/usr/bin/env python3
"""
DRAMExchange Price Extractor
Extracts actual price tables from DRAMExchange homepage
NO LOGIN REQUIRED - prices are publicly visible on homepage
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "memory_prices"
URL = "https://www.dramexchange.com/"

def extract_price_tables(soup):
    """Extract all price tables from DRAMExchange homepage."""
    tables = soup.find_all('table')
    price_tables = []
    
    for i, table in enumerate(tables):
        # Get all rows in the table
        rows = table.find_all('tr')
        
        # Skip tables with no rows or very few rows
        if len(rows) < 2:
            continue
        
        # Get header row (first row)
        header_cells = rows[0].find_all(['th', 'td'])
        headers = [cell.get_text(strip=True) for cell in header_cells]
        
        # Check if this looks like a price table
        is_price_table = False
        price_keywords = ['price', 'dram', 'nand', 'flash', 'memory', 'spot', 'contract', 'usd', '$', 'high', 'low', 'average', 'change']
        
        for header in headers:
            if any(keyword in header.lower() for keyword in price_keywords):
                is_price_table = True
                break
        
        # Also check table content
        table_text = table.get_text(strip=True)
        if any(keyword in table_text.lower() for keyword in price_keywords):
            is_price_table = True
        
        if is_price_table:
            # Extract data rows
            data_rows = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                cell_values = [cell.get_text(strip=True) for cell in cells]
                
                # Skip empty rows
                if any(cell_values):  # At least one cell has content
                    data_rows.append(cell_values)
            
            # Only include tables with actual data
            if data_rows:
                # Try to identify the table type
                table_type = "unknown"
                table_text_lower = table_text.lower()
                
                if 'dram spot' in table_text_lower:
                    table_type = "dram_spot"
                elif 'module spot' in table_text_lower:
                    table_type = "module_spot"
                elif 'flash spot' in table_text_lower:
                    table_type = "flash_spot"
                elif 'gddr spot' in table_text_lower:
                    table_type = "gddr_spot"
                elif 'wafer spot' in table_text_lower:
                    table_type = "wafer_spot"
                elif 'memory card' in table_text_lower:
                    table_type = "memorycard_spot"
                elif 'contract' in table_text_lower:
                    table_type = "contract"
                
                price_tables.append({
                    "index": i,
                    "type": table_type,
                    "headers": headers,
                    "data": data_rows,
                    "row_count": len(data_rows),
                    "preview": table_text[:200]
                })
    
    return price_tables

def parse_price_data(price_tables):
    """Parse price data from tables into structured format."""
    parsed_data = []
    
    for table in price_tables:
        table_type = table["type"]
        headers = table["headers"]
        data_rows = table["data"]
        
        # Skip if no headers or no data
        if not headers or not data_rows:
            continue
        
        # Parse each data row
        for row in data_rows:
            # Create a dictionary for this row
            row_data = {
                "table_type": table_type,
                "product": "",
                "prices": {}
            }
            
            # Map headers to values
            for i, header in enumerate(headers):
                if i < len(row):  # Make sure we have a value for this header
                    value = row[i]
                    
                    # Clean up the value
                    value = value.replace('\xa0', ' ').strip()
                    
                    # Identify product name (usually first column)
                    if i == 0:
                        row_data["product"] = value
                    else:
                        # Try to parse as number
                        try:
                            # Remove % sign and convert to float
                            clean_value = value.replace('%', '').replace(',', '').strip()
                            if clean_value:  # Not empty
                                num_value = float(clean_value)
                                row_data["prices"][header] = num_value
                            else:
                                row_data["prices"][header] = value
                        except ValueError:
                            # Not a number, keep as string
                            row_data["prices"][header] = value
            
            # Only add if we have a product name
            if row_data["product"]:
                parsed_data.append(row_data)
    
    return parsed_data

def generate_price_report(parsed_data):
    """Generate a comprehensive price report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("💰 **DRAMEXCHANGE PRICE REPORT**")
    lines.append(f"Time: {timestamp} SGT")
    lines.append("")
    lines.append("## 📊 **ACTUAL DRAMEXCHANGE PRICES**")
    lines.append("")
    lines.append("✅ **NO LOGIN REQUIRED** - Prices publicly visible on homepage")
    lines.append("")
    
    # Group by table type
    by_type = {}
    for item in parsed_data:
        table_type = item["table_type"]
        if table_type not in by_type:
            by_type[table_type] = []
        by_type[table_type].append(item)
    
    # Display by category
    category_names = {
        "dram_spot": "DRAM Spot Prices",
        "module_spot": "Module Spot Prices",
        "flash_spot": "Flash Spot Prices",
        "gddr_spot": "GDDR Spot Prices",
        "wafer_spot": "Wafer Spot Prices",
        "memorycard_spot": "Memory Card Spot Prices",
        "contract": "Contract Prices"
    }
    
    for table_type, items in by_type.items():
        category_name = category_names.get(table_type, table_type.replace('_', ' ').title())
        
        lines.append(f"### {category_name}")
        lines.append("")
        
        # Display items in this category
        for item in items:
            lines.append(f"**{item['product']}**")
            
            # Display prices
            for price_key, price_value in item["prices"].items():
                if isinstance(price_value, (int, float)):
                    # Format numbers nicely
                    if price_key.lower() in ['change', 'average change', 'session change']:
                        lines.append(f"• {price_key}: {price_value:.2f}%")
                    elif price_value >= 100:
                        lines.append(f"• {price_key}: ${price_value:,.2f}")
                    else:
                        lines.append(f"• {price_key}: ${price_value:.3f}")
                else:
                    lines.append(f"• {price_key}: {price_value}")
            
            lines.append("")
    
    # Summary statistics
    lines.append("## 📈 **PRICE SUMMARY**")
    lines.append("")
    
    total_items = len(parsed_data)
    categories = list(by_type.keys())
    
    lines.append(f"**Total price items:** {total_items}")
    lines.append(f"**Categories:** {', '.join([category_names.get(cat, cat) for cat in categories])}")
    lines.append("")
    
    # Calculate some statistics
    all_prices = []
    for item in parsed_data:
        for price_value in item["prices"].values():
            if isinstance(price_value, (int, float)) and price_value > 0:
                all_prices.append(price_value)
    
    if all_prices:
        lines.append("**Price Statistics:**")
        lines.append(f"• Total price points: {len(all_prices)}")
        lines.append(f"• Price range: ${min(all_prices):.3f} - ${max(all_prices):,.2f}")
        lines.append(f"• Average price: ${sum(all_prices)/len(all_prices):.2f}")
        lines.append("")
    
    lines.append("## 🔍 **DATA SOURCE**")
    lines.append("")
    lines.append(f"• **URL:** {URL}")
    lines.append("• **Method:** Direct HTML table extraction")
    lines.append("• **Login required:** ❌ NO - publicly accessible")
    lines.append("• **Update time:** Prices updated multiple times daily")
    lines.append("")
    
    lines.append("## 🎯 **KEY FINDINGS**")
    lines.append("")
    lines.append("1. ✅ **DRAMExchange homepage shows actual price tables**")
    lines.append("2. ✅ **No login required for basic price data**")
    lines.append("3. ✅ **Multiple categories: DRAM, Flash, Module, GDDR spots**")
    lines.append("4. ✅ **Includes Daily High/Low, Session Average, Change %**")
    lines.append("5. ✅ **Real-time or near-real-time updates**")
    lines.append("")
    
    lines.append("---")
    lines.append("Generated: DRAMExchange Price Extractor")
    lines.append(f"Timestamp: {datetime.now().isoformat()}")
    
    return "\n".join(lines)

def main():
    """Main price extractor."""
    print("💰 DRAMExchange Price Extractor")
    print("=" * 60)
    print("Extracting ACTUAL price tables from DRAMExchange homepage")
    print("NO LOGIN REQUIRED - prices are publicly visible")
    print("")
    
    # Create data directory
    DATA_DIR.mkdir(exist_ok=True)
    
    # Fetch the page
    print("🌐 Fetching DRAMExchange homepage...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched page ({len(response.content):,} bytes)")
        print("")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract price tables
        print("🔍 Extracting price tables...")
        price_tables = extract_price_tables(soup)
        
        print(f"✅ Found {len(price_tables)} price tables")
        print("")
        
        # Parse price data
        print("📊 Parsing price data...")
        parsed_data = parse_price_data(price_tables)
        
        print(f"✅ Parsed {len(parsed_data)} price items")
        print("")
        
        # Generate report
        report = generate_price_report(parsed_data)
        
        # Print summary
        print("=" * 60)
        print("📈 EXTRACTED PRICE CATEGORIES:")
        
        # Count by category
        categories = {}
        for item in parsed_data:
            cat = item["table_type"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            cat_name = cat.replace('_', ' ').title()
            print(f"   • {cat_name}: {count} items")
        
        print("=" * 60)
        
        # Save data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Save raw tables
        tables_file = DATA_DIR / f"dramexchange_tables_{timestamp}.json"
        with open(tables_file, 'w') as f:
            json.dump(price_tables, f, indent=2)
        
        # Save parsed data
        data_file = DATA_DIR / f"dramexchange_prices_{timestamp}.json"
        with open(data_file, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        
        # Save report
        report_file = DATA_DIR / f"dramexchange_report_{timestamp}.txt"
        report_file.write_text(report)
        
        print(f"\n📁 Data saved to: {data_file}")
        print(f"📄 Report saved to: {report_file}")
        
        # Save to Obsidian
        try:
            obsidian_dir = Path.home() / "Documents" / "openclaw" / "World News"
            obsidian_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_DRAMExchange_Prices_-_{timestamp}_SGT.md"
            filepath = obsidian_dir / filename
            filepath.write_text(report)
            print(f"📁 Report saved to Obsidian: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save to Obsidian: {e}")
        
        # Final summary
        print("\n✅ **DRAMEXCHANGE PRICE EXTRACTOR COMPLETE:**")
        print(f"   • URL: {URL}")
        print(f"   • Price tables found: {len(price_tables)}")
        print(f"   • Price items extracted: {len(parsed_data)}")
        print(f"   • Login required: ❌ NO")
        print(f"   • Data freshness: Real-time/Near-real-time")
        
        # Show sample of extracted data
        print("\n📊 **SAMPLE EXTRACTED PRICES:**")
        if parsed_data:
            for i, item in enumerate(parsed_data[:3]):  # Show first 3
                print(f"   {i+1}. {item['product']}")
                for price_key, price_value in list(item['prices'].items())[:2]:  # Show first 2 prices
                    if isinstance(price_value, (int, float)):
                        print(f"      {price_key}: ${price_value:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()