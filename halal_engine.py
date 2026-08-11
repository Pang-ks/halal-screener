FORBIDDEN_SECTORS = [
    "Financial Services",
    "Consumer Defensive",
]

FORBIDDEN_KEYWORDS = [
    "tobacco", "alcohol", "casino",
    "gambling", "weapons", "pork"
]

def screen(data: dict) -> dict:
    # 🌟 ถ้าเป็นกองทุน ETF ให้ใช้ตรรกะใหม่
    if data.get("is_etf"):
        desc = str(data.get("description", "")).lower()
        name = str(data.get("name", "")).lower()
        
        # ตรวจสอบชื่อ/คำอธิบาย ว่าเป็นกองทุนที่ถูกหลักชะรีอะห์หรือไม่
        is_halal_etf = any(k in desc or k in name for k in ["sharia", "islamic", "halal", "sukuk", "sp funds"])
        
        if is_halal_etf:
            status = "PASS ✅ (Halal ETF)"
        else:
            status = "DOUBTFUL ⚠️ (ETF - ตรวจสอบหุ้นในกองทุนเพิ่มเติม)"
            
        return {
            "ticker": data["ticker"],
            "name": data["name"],
            "status": status,
            "debt_ok": True,
            "interest_ok": True,
            "sector_ok": True,
            "business_ok": True,
        }

    # เงื่อนไขสำหรับหุ้นปกติ (แบบเดิม)
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
