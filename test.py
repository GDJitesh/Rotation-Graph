import pandas as pd
import requests
import io

url = "https://public.fyers.in/sym_details/NSE_CM.csv"

try:
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')), header=None)
except Exception as e:
    print(f"Error downloading CSV: {e}")
    exit()

# 1. Setup Columns
df.rename(columns={
    0: 'FyToken',
    1: 'Description',
    9: 'Symbol',
    13: 'ShortSymbol'
}, inplace=True)

# 2. Filter for Indices only
df = df[df['Symbol'].str.endswith('-INDEX', na=False)].copy()

# 3. Define YOUR Specific Sector List (Target List)
# I have normalized them to uppercase to ensure matching works
target_sectors = [
    "NIFTY AUTO",
    "NIFTY BANK",
    "NIFTY CHEMICALS", # Note: Might not exist in Fyers yet if very new
    "NIFTY FINANCIAL SERVICES", # Captures FINNIFTY
    "NIFTY FINANCIAL SERVICES 25/50",
    "NIFTY FINANCIAL SERVICES EX BANK",
    "NIFTY FMCG",
    "NIFTY HEALTHCARE",
    "NIFTY IT",
    "NIFTY MEDIA",
    "NIFTY METAL",
    "NIFTY PHARMA",
    "NIFTY PRIVATE BANK",
    "NIFTY PSU BANK",
    "NIFTY REALTY",
    "NIFTY CONSUMER DURABLES", # Fyers often names this "NIFTY CONSR DURBL"
    "NIFTY OIL AND GAS",
    "NIFTY500 HEALTHCARE", # Watch for spacing issues in CSV
    "NIFTY MIDSMALL FINANCIAL SERVICES",
    "NIFTY MIDSMALL HEALTHCARE",
    "NIFTY MIDSMALL IT & TELECOM"
]

# 4. Normalization Function for Matching
# This handles differences like "Nifty Consumer Durables" vs "Nifty Consr Durbl"
def check_match(row_desc):
    desc = str(row_desc).upper().replace("  ", " ").strip()
    
    # Handle specific Fyers abbreviations manually
    if "CONSR DURBL" in desc: desc = desc.replace("CONSR DURBL", "CONSUMER DURABLES")
    if "PVT BANK" in desc: desc = desc.replace("PVT BANK", "PRIVATE BANK")
    if "FINSRV25 50" in desc: desc = desc.replace("FINSRV25 50", "FINANCIAL SERVICES 25/50")
    if "FINSEREXBNK" in desc: desc = desc.replace("FINSEREXBNK", "FINANCIAL SERVICES EX BANK")
    if "MS IT TELCM" in desc: desc = desc.replace("MS IT TELCM", "MIDSMALL IT & TELECOM")
    if "MIDSML HLTH" in desc: desc = desc.replace("MIDSML HLTH", "MIDSMALL HEALTHCARE")
    if "MS FIN SERV" in desc: desc = desc.replace("MS FIN SERV", "MIDSMALL FINANCIAL SERVICES")

    # Check if the normalized description exists in our target list
    # We check if the desc STARTS with any of our targets to avoid partial matches
    for target in target_sectors:
        # Exact match or very close match
        if desc == target or desc.replace("&", "AND") == target.replace("&", "AND"):
            return True
    return False

# Apply Filter
df['IsMySector'] = df['Description'].apply(check_match)
final_list = df[df['IsMySector'] == True].copy()

# 5. Display Results
print(f"Found {len(final_list)} matching sectors from your list:\n")
output_cols = ['FyToken', 'ShortSymbol', 'Description', 'Symbol']
print(final_list[output_cols].to_string(index=False))