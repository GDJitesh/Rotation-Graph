import pandas as pd
import numpy as np
import json
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
SECTORS = ['Technology', 'Finance', 'Healthcare', 'Energy', 'Consumer', 'Utilities']
BENCHMARK_NAME = 'NIFTY_50'
YEARS_OF_HISTORY = 3  # We need >2 years to visualize 1 year of rotation

def generate_random_walk(start_price, days, drift, vol):
    """Generates a list of OHLCV dictionaries for a random walk."""
    price_path = []
    current_price = start_price
    
    # Generate dates
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D') # Daily data
    
    for date in date_range:
        if date.weekday() > 4: continue # Skip weekends
        
        # Random daily return
        change = np.random.normal(drift, vol)
        current_price = current_price * (1 + change)
        
        # Fake OHLC logic
        high = current_price * (1 + abs(np.random.normal(0, 0.005)))
        low = current_price * (1 - abs(np.random.normal(0, 0.005)))
        open_p = (high + low) / 2 # Approx
        
        price_path.append({
            "Date": date.strftime('%Y-%m-%d'),
            "Open": round(open_p, 2),
            "High": round(high, 2),
            "Low": round(low, 2),
            "Close": round(current_price, 2),
            "Volume": int(np.random.uniform(10000, 500000))
        })
        
    return price_path

def main():
    print(f"Generating {YEARS_OF_HISTORY} years of daily mock data...")
    days = YEARS_OF_HISTORY * 365
    
    # 1. Generate Benchmark Data
    # Benchmark usually has lower volatility (0.008) and slight positive drift
    print(f"Creating {BENCHMARK_NAME} data...")
    bench_data = generate_random_walk(10000, days, 0.0004, 0.008)
    
    with open('mock_benchmark.json', 'w') as f:
        json.dump(bench_data, f, indent=2)

    # 2. Generate Sectors Data
    print("Creating Sector data...")
    sectors_payload = {}
    
    for sector in SECTORS:
        # Randomize sector personality
        start_price = np.random.randint(100, 500)
        # Randomize drift (some sectors boom, some crash)
        sector_drift = np.random.uniform(-0.0002, 0.0008) 
        # Randomize volatility (some are wilder than others)
        sector_vol = np.random.uniform(0.01, 0.02)
        
        sector_data = generate_random_walk(start_price, days, sector_drift, sector_vol)
        sectors_payload[sector] = sector_data
        
    with open('mock_sectors.json', 'w') as f:
        json.dump(sectors_payload, f, indent=2)

    print("\n✅ SUCCESS: Data generation complete.")
    print("1. 'mock_benchmark.json' (The Index)")
    print("2. 'mock_sectors.json' (The Sectors)")
    print("\nNext Step: Run 'python -m http.server 8000' and expose this folder via ngrok.")

if __name__ == "__main__":
    main()