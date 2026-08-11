import yfinance as yf

def get_stock_data(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # 1. เช็คว่ามีหุ้นตัวนี้จริงๆ ไหม (ถ้าไม่มี info แสดงว่าพิมพ์ผิด)
    if not info or 'symbol' not in info:
        return None

    balance = stock.balance_sheet
    income = stock.income_stmt

    # 2. เช็คว่างบการเงินมีข้อมูลไหม
    if balance.empty or income.empty:
        return None

    # ฟังก์ชันช่วยดึงข้อมูลแบบปลอดภัย (ถ้าหาไม่เจอให้คืนค่า 0 แทนการพัง)
    def safe_get(df, row_name):
        try:
            return df.loc[row_name].iloc[0]
        except:
            return 0

    total_assets = safe_get(balance, "Total Assets")
    total_debt = safe_get(balance, "Total Debt")
    total_equity = safe_get(balance, "Stockholders Equity")
    net_income = safe_get(income, "Net Income")
    revenue = safe_get(income, "Total Revenue")
    interest_expense = safe_get(income, "Interest Expense")

    # 3. ป้องกันปัญหา "ตัวหารเป็น 0" (ZeroDivisionError)
    debt_ratio = round(total_debt / total_assets, 4) if total_assets != 0 else 0
    interest_ratio = round(abs(interest_expense) / revenue, 4) if revenue != 0 else 0
    roe = round(net_income / total_equity, 4) if total_equity != 0 else 0
    net_margin = round(net_income / revenue, 4) if revenue != 0 else 0

    return {
        "ticker": ticker,
        "name": info.get("longName", info.get("shortName", "N/A")),
        "sector": info.get("sector", "N/A"),
        "description": info.get("longBusinessSummary", "ไม่มีคำอธิบายธุรกิจ"),
        "price": info.get("currentPrice", 0),
        "market_cap": info.get("marketCap", 0),
        
        "debt_ratio": debt_ratio,
        "interest_ratio": interest_ratio,
        
        "pe_ratio": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "eps": info.get("trailingEps"),
        
        "roe": roe,
        "net_margin": net_margin,
        "revenue": revenue,
        "net_income": net_income,
        
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
    }

def get_historical_prices(ticker: str, period="1y"):
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    
    # ถ้าดึงกราฟไม่ได้ ให้ส่งค่าว่างกลับไป
    if history.empty:
        return None
        
    return history[['Close']]