import yfinance as yf

def get_stock_data(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    if not info or 'symbol' not in info:
        return None

    # 🌟 เช็คว่าคือหุ้นบริษัท (Equity) หรือ กองทุน (ETF)
    quote_type = info.get('quoteType', '')
    is_etf = (quote_type == 'ETF' or quote_type == 'MUTUALFUND')

    balance = stock.balance_sheet
    income = stock.income_stmt

    # ถ้าเป็นหุ้นปกติ แต่ไม่มีงบการเงิน แสดงว่าระบบข้อมูลมีปัญหา
    if not is_etf and (balance.empty or income.empty):
        return None

    def safe_get(df, row_name):
        try:
            return df.loc[row_name].iloc[0]
        except:
            return 0

    if is_etf:
        # 🌟 ETF จะไม่มีหนี้/รายได้ของตัวเอง ให้ตั้งค่าเป็น 0
        debt_ratio = 0
        interest_ratio = 0
        roe = 0
        net_margin = 0
        revenue = 0
        net_income = 0
        price = info.get("navPrice", info.get("currentPrice", 0))
        market_cap = info.get("totalAssets", info.get("marketCap", 0))
        sector = info.get("category", "ETF")
    else:
        total_assets = safe_get(balance, "Total Assets")
        total_debt = safe_get(balance, "Total Debt")
        total_equity = safe_get(balance, "Stockholders Equity")
        net_income_val = safe_get(income, "Net Income")
        revenue_val = safe_get(income, "Total Revenue")
        interest_expense = safe_get(income, "Interest Expense")

        debt_ratio = round(total_debt / total_assets, 4) if total_assets != 0 else 0
        interest_ratio = round(abs(interest_expense) / revenue_val, 4) if revenue_val != 0 else 0
        roe = round(net_income_val / total_equity, 4) if total_equity != 0 else 0
        net_margin = round(net_income_val / revenue_val, 4) if revenue_val != 0 else 0
        revenue = revenue_val
        net_income = net_income_val
        price = info.get("currentPrice", 0)
        market_cap = info.get("marketCap", 0)
        sector = info.get("sector", "N/A")

    return {
        "ticker": ticker,
        "name": info.get("longName", info.get("shortName", "N/A")),
        "sector": sector,
        "description": info.get("longBusinessSummary", "ไม่มีคำอธิบาย"),
        "price": price,
        "market_cap": market_cap,
        "debt_ratio": debt_ratio,
        "interest_ratio": interest_ratio,
        "pe_ratio": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "eps": info.get("trailingEps"),
        "roe": roe,
        "net_margin": net_margin,
        "revenue": revenue,
        "net_income": net_income,
        "dividend_yield": info.get("dividendYield", info.get("yield")),
        "is_etf": is_etf  # 🌟 ส่งตัวแปรนี้ไปบอก Halal Engine
    }

def get_historical_prices(ticker: str, period="1y"):
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    
    if history.empty:
        return None
        
    return history[['Close']]
