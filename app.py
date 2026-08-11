import streamlit as st
from data_fetcher import get_stock_data, get_historical_prices 
from halal_engine import screen

st.set_page_config(page_title="Halal Screener", page_icon="🕌")
st.title("🕌 Halal Stock Screener")
st.caption("ตรวจสอบหุ้น Halal ตามหลักชะรีอะห์ AAOIFI")

with st.expander("📖 เกณฑ์มาตรฐานที่ใช้วิเคราะห์"):
    st.markdown("""
    ### 🕌 เกณฑ์ Halal (AAOIFI)
    | เกณฑ์ | ค่าที่ดี | ค่าสูงสุด | หมายเหตุ |
    |---|---|---|---|
    | Debt Ratio | < 20% | < 33% | หนี้ต่อสินทรัพย์รวม |
    | Interest Income | < 2% | < 5% | รายได้ดอกเบี้ยต่อรายได้รวม |
    ### 📊 เกณฑ์ Valuation
    | ตัวชี้วัด | ค่าที่ดี | ระวัง | หมายเหตุ |
    |---|---|---|---|
    | P/E Ratio | 10-20x | > 30x | ยิ่งต่ำยิ่งถูก |
    | P/B Ratio | < 1-3x | > 5x | ราคาเทียบมูลค่าบัญชี |
    | EPS | บวกและเติบโต | ติดลบ | กำไรต่อหุ้น |
    ### 💰 เกณฑ์ Profitability
    | ตัวชี้วัด | ค่าที่ดี | ระวัง | หมายเหตุ |
    |---|---|---|---|
    | ROE | > 15% | < 8% | ผลตอบแทนต่อส่วนทุน |
    | Net Margin | > 10% | < 5% | กำไรสุทธิต่อรายได้ |
    | Dividend Yield | 2-5% | > 8% | ปันผลสูงเกินอาจเสี่ยง |
    """)

# 🌟 ปรับปรุงส่วนป้อนข้อมูลและเพิ่มปุ่ม
ticker = st.text_input("ป้อน Ticker", placeholder="เช่น NVDA, AAPL, TSM, AMD")
st.button("ตรวจสอบ ↗")

# เรายังคงใช้เงื่อนไขนี้ เพื่อไม่ให้หน้าเว็บรีเซ็ตเมื่อกดเปลี่ยนช่วงเวลากราฟ
if ticker:
    with st.spinner("กำลังดึงข้อมูล..."):
        try:
            data = get_stock_data(ticker.upper())
            
            if data is None:
                st.warning(f"⚠️ ไม่พบข้อมูลของหุ้น '{ticker.upper()}' หรือหุ้นนี้ไม่มีข้อมูลการเงินในระบบ กรุณาตรวจสอบชื่อ Ticker อีกครั้งครับ")
            else:
                result = screen(data)

                st.subheader(f"{result['ticker']} — {data['name']}")

                if "PASS" in result['status']:
                    st.success(result['status'])
                elif "DOUBTFUL" in result['status']:
                    st.warning(result['status'])
                else:
                    st.error(result['status'])

                col1, col2 = st.columns(2)
                col1.metric("ราคา", f"${data['price']}" if data['price'] else "N/A")
                col2.metric("Market Cap", f"${data['market_cap']:,.0f}" if data['market_cap'] else "N/A")

                st.markdown("### 📈 กราฟราคาหุ้น (ราคาปิด)")
                
                selected_period = st.radio(
                    "เลือกช่วงเวลา:",
                    options=["1mo", "6mo", "1y", "5y", "max"],
                    format_func=lambda x: {"1mo": "1 เดือน", "6mo": "6 เดือน", "1y": "1 ปี", "5y": "5 ปี", "max": "ตั้งแต่เข้าตลาด"}[x],
                    horizontal=True
                )
                
                history_data = get_historical_prices(ticker.upper(), period=selected_period)
                if history_data is not None:
                    st.line_chart(history_data)
                else:
                    st.info("ℹ️ ไม่มีข้อมูลกราฟราคาย้อนหลังสำหรับช่วงเวลานี้")

                st.divider()

                st.subheader("🕌 เกณฑ์ชะรีอะห์")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Debt Ratio", f"{data['debt_ratio']*100:.1f}%",
                          delta="ผ่าน ✅" if result['debt_ok'] else "ไม่ผ่าน ❌")
                c2.metric("Interest Ratio", f"{data['interest_ratio']*100:.1f}%",
                          delta="ผ่าน ✅" if result['interest_ok'] else "ไม่ผ่าน ❌")
                c3.metric("Sector", data['sector'])
                c4.metric("Business", "ผ่าน ✅" if result['business_ok'] else "ไม่ผ่าน ❌")

                st.info(f"""
                **📌 คำแนะนำ Halal**
                - Debt Ratio ควร **< 33%** (เกณฑ์ AAOIFI) | ค่าที่ดีคือ **< 20%** | ตัวนี้อยู่ที่ {data['debt_ratio']*100:.1f}%
                - Interest Ratio ควร **< 5%** | ค่าที่ดีคือ **< 2%** | ตัวนี้อยู่ที่ {data['interest_ratio']*100:.1f}%
                """)

                st.divider()

                st.subheader("📊 Valuation")
                v1, v2, v3 = st.columns(3)
                pe = data['pe_ratio']
                pb = data['pb_ratio']
                eps = data['eps']
                v1.metric("P/E Ratio", f"{pe:.1f}x" if pe else "N/A")
                v2.metric("P/B Ratio", f"{pb:.1f}x" if pb else "N/A")
                v3.metric("EPS", f"${eps:.2f}" if eps else "N/A")

                pe_comment = "✅ ราคาสมเหตุสมผล" if pe and pe < 25 else ("⚠️ แพงพอสมควร" if pe and pe < 40 else "❌ แพงมาก") if pe else "ไม่มีข้อมูล"
                pb_comment = "✅ ราคาเหมาะสม" if pb and pb < 3 else ("⚠️ ควรพิจารณา" if pb and pb < 5 else "❌ แพงเกินไป") if pb else "ไม่มีข้อมูล"
                st.info(f"""
                **📌 คำแนะนำ Valuation**
                - P/E ควร **10-20x** | ระวังถ้า **> 30x** → {pe_comment}
                - P/B ควร **< 3x** | ระวังถ้า **> 5x** → {pb_comment}
                - EPS ควร **บวกและเติบโต** ทุกปี
                """)

                st.divider()

                st.subheader("💰 ผลประกอบการ")
                p1, p2, p3 = st.columns(3)
                roe = data['roe']
                margin = data['net_margin']
                div_yield = data.get('dividend_yield')
                
                p1.metric("ROE", f"{roe*100:.1f}%")
                p2.metric("Net Margin", f"{margin*100:.1f}%")
                p3.metric("Dividend Yield",
                          f"{div_yield*100:.1f}%" if div_yield else "ไม่มีปันผล")

                roe_comment = "✅ ดีมาก" if roe > 0.15 else ("⚠️ พอใช้" if roe > 0.08 else "❌ ต่ำเกินไป")
                margin_comment = "✅ ดีมาก" if margin > 0.10 else ("⚠️ พอใช้" if margin > 0.05 else "❌ ต่ำเกินไป")
                st.info(f"""
                **📌 คำแนะนำ Profitability**
                - ROE ควร **> 15%** | ต่ำสุดที่ยอมรับได้ **8%** → {roe_comment}
                - Net Margin ควร **> 10%** | ต่ำสุด **5%** → {margin_comment}
                - Dividend Yield ที่ดี **2-5%** | ถ้า **> 8%** อาจเสี่ยงปันผลไม่ยั่งยืน
                """)

                st.divider()

                st.subheader("📈 รายได้และกำไร")
                r1, r2 = st.columns(2)
                r1.metric("Revenue", f"${data['revenue']:,.0f}" if data['revenue'] else "N/A")
                r2.metric("Net Income", f"${data['net_income']:,.0f}" if data['net_income'] else "N/A")

        except Exception as e:
            st.error(f"⚠️ ระบบขัดข้อง: ไม่สามารถประมวลผลข้อมูลได้ในขณะนี้ ({e})")