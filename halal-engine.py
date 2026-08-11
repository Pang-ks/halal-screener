FORBIDDEN_SECTORS = [
    "Financial Services",
    "Consumer Defensive",
]

FORBIDDEN_KEYWORDS = [
    "tobacco", "alcohol", "casino",
    "gambling", "weapons", "pork"
]

def screen(data: dict) -> dict:
    debt_ok = data["debt_ratio"] < 0.33
    interest_ok = data["interest_ratio"] < 0.05
    sector_ok = data["sector"] not in FORBIDDEN_SECTORS

    desc = str(data.get("description", "")).lower()
    business_ok = not any(k in desc for k in FORBIDDEN_KEYWORDS)

    passed = debt_ok and interest_ok and sector_ok and business_ok
    doubtful = passed and data["debt_ratio"] > 0.20

    if not passed:
        status = "FAIL ❌"
    elif doubtful:
        status = "DOUBTFUL ⚠️"
    else:
        status = "PASS ✅"

    return {
        "ticker": data["ticker"],
        "name": data["name"],
        "status": status,
        "debt_ok": debt_ok,
        "interest_ok": interest_ok,
        "sector_ok": sector_ok,
        "business_ok": business_ok,
    }