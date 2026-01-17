# utils/ticker_data.py

# Dictionary mapping "Display Name" to "Ticker Symbol"
# Categories: Tech, Semis, Finance, Crypto, Indices, Commodities, ETFs, etc.

ASSET_DATABASE = {
    # ---------------------------------------------------------
    # 👑 MAGNIFICENT 7 & BIG TECH
    # ---------------------------------------------------------
    "NVIDIA Corp. (NVDA)": "NVDA",
    "Apple Inc. (AAPL)": "AAPL",
    "Microsoft Corp. (MSFT)": "MSFT",
    "Amazon.com Inc. (AMZN)": "AMZN",
    "Alphabet Inc. Class A (GOOGL)": "GOOGL",
    "Meta Platforms (META)": "META",
    "Tesla Inc. (TSLA)": "TSLA",
    "Netflix Inc. (NFLX)": "NFLX",
    "Salesforce (CRM)": "CRM",
    "Adobe Inc. (ADBE)": "ADBE",
    "Oracle Corp. (ORCL)": "ORCL",
    "IBM (IBM)": "IBM",

    # ---------------------------------------------------------
    # 💾 SEMICONDUCTORS (CHIP WAR)
    # ---------------------------------------------------------
    "AMD (AMD)": "AMD",
    "Intel Corp. (INTC)": "INTC",
    "Taiwan Semi (TSM)": "TSM",
    "Broadcom (AVGO)": "AVGO",
    "Qualcomm (QCOM)": "QCOM",
    "Micron Technology (MU)": "MU",
    "Texas Instruments (TXN)": "TXN",
    "Applied Materials (AMAT)": "AMAT",
    "Lam Research (LRCX)": "LRCX",
    "Arm Holdings (ARM)": "ARM",
    "ASML Holding (ASML)": "ASML",
    "Super Micro Computer (SMCI)": "SMCI",

    # ---------------------------------------------------------
    # 🚀 HIGH GROWTH & INNOVATION
    # ---------------------------------------------------------
    "Palantir Technologies (PLTR)": "PLTR",
    "MicroStrategy (MSTR)": "MSTR",
    "Snowflake (SNOW)": "SNOW",
    "Uber Technologies (UBER)": "UBER",
    "Airbnb (ABNB)": "ABNB",
    "Shopify (SHOP)": "SHOP",
    "Block Inc. (SQ)": "SQ",
    "Coinbase Global (COIN)": "COIN",
    "Roblox (RBLX)": "RBLX",
    "Unity Software (U)": "U",
    "C3.ai (AI)": "AI",

    # ---------------------------------------------------------
    # 🏦 FINANCIALS & BANKS
    # ---------------------------------------------------------
    "JPMorgan Chase (JPM)": "JPM",
    "Bank of America (BAC)": "BAC",
    "Wells Fargo (WFC)": "WFC",
    "Goldman Sachs (GS)": "GS",
    "Morgan Stanley (MS)": "MS",
    "Berkshire Hathaway B (BRK-B)": "BRK-B",
    "BlackRock (BLK)": "BLK",
    "Visa Inc. (V)": "V",
    "Mastercard (MA)": "MA",
    "PayPal Holdings (PYPL)": "PYPL",

    # ---------------------------------------------------------
    # 🏥 HEALTHCARE & PHARMA
    # ---------------------------------------------------------
    "Eli Lilly (LLY)": "LLY",
    "Novo Nordisk (NVO)": "NVO",
    "Johnson & Johnson (JNJ)": "JNJ",
    "UnitedHealth Group (UNH)": "UNH",
    "Merck & Co. (MRK)": "MRK",
    "AbbVie (ABBV)": "ABBV",
    "Pfizer (PFE)": "PFE",
    "Moderna (MRNA)": "MRNA",

    # ---------------------------------------------------------
    # 🛒 CONSUMER & RETAIL
    # ---------------------------------------------------------
    "Walmart (WMT)": "WMT",
    "Costco Wholesale (COST)": "COST",
    "Target (TGT)": "TGT",
    "Coca-Cola (KO)": "KO",
    "PepsiCo (PEP)": "PEP",
    "McDonald's (MCD)": "MCD",
    "Starbucks (SBUX)": "SBUX",
    "Nike (NKE)": "NKE",
    "Lululemon (LULU)": "LULU",
    "Disney (DIS)": "DIS",

    # ---------------------------------------------------------
    # 🏭 INDUSTRIAL, ENERGY & AUTO
    # ---------------------------------------------------------
    "Exxon Mobil (XOM)": "XOM",
    "Chevron (CVX)": "CVX",
    "Boeing (BA)": "BA",
    "Lockheed Martin (LMT)": "LMT",
    "Caterpillar (CAT)": "CAT",
    "General Electric (GE)": "GE",
    "Ford Motor (F)": "F",
    "General Motors (GM)": "GM",
    "Rivian Automotive (RIVN)": "RIVN",

    # ---------------------------------------------------------
    # 📉 INDICES & ETFS (MACRO)
    # ---------------------------------------------------------
    "S&P 500 ETF (SPY)": "SPY",
    "Nasdaq 100 ETF (QQQ)": "QQQ",
    "Dow Jones ETF (DIA)": "DIA",
    "Russell 2000 (IWM)": "IWM",
    "VIX Volatility Index (^VIX)": "^VIX",
    "Semiconductor ETF (SOXX)": "SOXX",
    "Tech Select Sector (XLK)": "XLK",
    "Financial Select Sector (XLF)": "XLF",
    "Energy Select Sector (XLE)": "XLE",
    "Ark Innovation ETF (ARKK)": "ARKK",
    "20+ Year Treasury Bond (TLT)": "TLT",
    "US Dollar Index (DXY)": "DX-Y.NYB",

    # ---------------------------------------------------------
    # 🪙 CRYPTOCURRENCY (24/7)
    # ---------------------------------------------------------
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Ethereum (ETH-USD)": "ETH-USD",
    "Solana (SOL-USD)": "SOL-USD",
    "Ripple (XRP-USD)": "XRP-USD",
    "Dogecoin (DOGE-USD)": "DOGE-USD",
    "Cardano (ADA-USD)": "ADA-USD",
    "Shiba Inu (SHIB-USD)": "SHIB-USD",

    # ---------------------------------------------------------
    # 🛢️ COMMODITIES (FUTURES)
    # ---------------------------------------------------------
    "Gold Futures (GC=F)": "GC=F",
    "Silver Futures (SI=F)": "SI=F",
    "Crude Oil WTI (CL=F)": "CL=F",
    "Natural Gas (NG=F)": "NG=F",
    "Copper Futures (HG=F)": "HG=F",
    "Corn Futures (ZC=F)": "ZC=F"
}

def get_ticker(display_name):
    """Returns the ticker symbol for a given display name."""
    return ASSET_DATABASE.get(display_name, "NVDA") # Default to NVDA