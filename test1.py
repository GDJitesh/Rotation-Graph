import requests
import pandas as pd

# 1. Fetch Sectors AND Sub-sectors
def get_sectors_hierarchy():
    url = "https://api-t1.fyers.in/indus/data/v1/get-sector"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('code') == 200:
            return data['data']
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# 2. Get Stocks for a specific Sub-Sector
def get_stocks(sector_code, subsector_code, page=1):
    url = "https://api-t1.fyers.in/indus/data/v1/get-stocks"
    
    params = {
        'sector': sector_code,       
        'subsector': subsector_code, 
        'sort_by': 'percentage_change', 
        'sort_type': 'asc', 
        'page': page
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get('code') == 200:
            return data['data']
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# --- Main Execution ---

# A. Get the Master List
all_sectors = get_sectors_hierarchy()
print(f"Found {len(all_sectors)} Main Sectors.\n")

# Variables to store our target codes
finance_sector_code = None
housing_sub_code = None

# B. Find the specific codes dynamically
for sector in all_sectors:
    s_name = sector.get('name')
    s_code = sector.get('code')
    sub_sectors = sector.get('sub_sectors', [])
    
    # We want the 'Finance' sector
    if s_name == 'Finance': 
        finance_sector_code = s_code
        print(f"Found Finance Sector: {s_code}")
        
        # Now find 'Housing' inside Finance
        for sub in sub_sectors:
            if sub['name'] == 'Housing':
                housing_sub_code = sub['code']
                print(f"Found Housing Sub-Sector: {housing_sub_code}")
                break

# C. Fetch Stocks if we found both codes
if finance_sector_code and housing_sub_code:
    print(f"\nFetching stocks for {finance_sector_code} -> {housing_sub_code}...\n")
    
    stocks = get_stocks(finance_sector_code, housing_sub_code)
    
    if stocks:
        df = pd.DataFrame(stocks)
        
        # Added 'market_cap' to the display columns
        # Note: 'lp' is Last Price, 'chp' is Change Percentage
        display_cols = ['ex_sym', 'description', 'lp', 'chp', 'market_cap']
        
        # Optional: Format Market Cap to Crores for readability (assuming input is in raw value)
        # If market_cap is missing/NaN, fill with 0
        if 'market_cap' in df.columns:
            df['market_cap'] = df['market_cap'].fillna(0).astype(float)
            # Format: 12345678 -> 1.23 Cr (Example logic, adjust divisor as needed based on raw unit)
            # Usually API returns full value, so / 10000000 gives Crores
            df['mcap_cr'] = (df['market_cap'] / 10000000).round(2)
            
            # Update display to show the formatted column instead
            display_cols = ['ex_sym', 'description', 'lp', 'chp', 'mcap_cr']

        print(df[display_cols].head(15).to_string(index=False))
    else:
        print("No stocks found.")
else:
    print("Could not find 'Finance' sector or 'Housing' sub-sector.")