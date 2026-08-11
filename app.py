import streamlit as st
from data_fetcher import get_stock_data, get_historical_prices 
from halal_engine import screen

st.set_page_config(page_title="Halal Screener", page_icon="🕌", layout="wide")

st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: rgba(128, 128, 128, 0.1);
    border: 1px solid rgba(128, 128, 128, 0.2);
    padding: 15px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🕌 Halal Stock Screener")
st.caption("ตรวจสอบหุ้นและ ETF ตามหลักชะรีอะห์ (AAOIFI Standard)")

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
    """)

col_search, col_btn = st.columns([4, 1])
with col_search:
    ticker = st.text_input("ป้อน Ticker (พิมพ์เสร็จแล้วกด Enter ได้เลย)", placeholder="เช่น NVDA, AAPL, SPTE, PTT.BK", label_visibility="collapsed")
with col_btn:
    search_btn = st.button("ตรวจสอบ ↗", use_container_width=True)

if ticker or search_btn:
    with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
        try:
            data = get_stock_data(ticker.upper())
            
            if data is None:
                st.warning(f"⚠️ ไม่พบข้อมูลของ '{ticker.upper()}' กรุณาตรวจสอบชื่อ Ticker อีกครั้งครับ")
            else:
                result = screen(data)

                st.header(f"{result['ticker']} — {data['name']}")
                
                if "PASS" in result['status']:
                    st.success(f"**สถานะ:** {result['status']}")
                elif "DOUBTFUL" in result['status']:
                    st.warning(f"**สถานะ:** {result['status']}")
                else:
                    st.error(f"**สถานะ:** {result['status']}")

                # ==========================================
                # 🌟 ส่วนที่เพิ่มใหม่: ตรวจสอบและแสดงสาเหตุที่ไม่ผ่านเกณฑ์
                if "PASS" not in result['status']:
                    reasons = []
                    
                    # ถ้าเป็น ETF แล้วไม่ผ่าน
                    if data.get("is_etf"):
                        reasons.append("- ⚠️ เป็นกองทุน ETF ทั่วไปที่ไม่ได้ระบุว่าเป็น Sharia-compliant (ต้องตรวจสอบหุ้นในกองทุนเพิ่มเติมด้วยตัวเอง)")
                    # ถ้าเป็นหุ้นปกติ แล้วไม่ผ่าน
                    else:
                        if not result.get('debt_ok'):
                            reasons.append(f"- ❌ **หนี้สิน (Debt Ratio):** สูงเกิน 33% (ปัจจุบันอยู่ที่ {data['debt_ratio']*100:.1f}%)")
                        if not result.get('interest_ok'):
                            reasons.append(f"- ❌ **รายได้จากดอกเบี้ย (Interest Ratio):** สูงเกิน 5% (ปัจจุบันอยู่ที่ {data['interest_ratio']*100:.1f}%)")
                        if not result.get('sector_ok'):
                            reasons.append(f"- ❌ **หมวดหมู่ธุรกิจ (Sector):** อยู่ในกลุ่มต้องห้าม ({data['sector']})")
                        if not result.get('business_ok'):
                            reasons.append(f"- ❌ **ลักษณะธุรกิจ:** มีคำอธิบายเกี่ยวข้องกับสิ่งต้องห้าม (เช่น ธุรกิจการเงิน, ยาสูบ, แอลกอฮอล์, อาวุธ ฯลฯ)")
                    
                    if reasons:
                        st.error("**สาเหตุที่ทำให้ไม่ผ่านเกณฑ์:**\n" + "\n".join(reasons))
                # ==========================================

                st.divider()

                tab1, tab2, tab3 = st.tabs(["📈 ภาพรวม & กราฟ", "🕌 เกณฑ์ Halal", "📊 งบการเงิน & มูลค่า"])

                with tab1:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("ราคาปัจจุบัน", f"${data['price']}" if data['price'] else "N/A")
                    col2.metric("Market Cap", f"${data['market_cap']:,.0f}" if data['market_cap'] else "N/A")
                    col3.metric("หมวดหมู่ธุรกิจ (Sector)", data['sector'])
                    
                    st.markdown("### กราฟราคาย้อนหลัง")
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

                with tab2:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Debt Ratio", f"{data['debt_ratio']*100:.1f}%",
                              delta="ผ่าน ✅" if result.get('debt_ok', True) else "ไม่ผ่าน ❌")
                    c2.metric("Interest Ratio", f"{data['interest_ratio']*100:.1f}%",
                              delta="ผ่าน ✅" if result.get('interest_ok', True) else "ไม่ผ่าน ❌")
                    c3.metric("Business Sector", "ผ่าน ✅" if result.get('business_ok', True) else "ไม่ผ่าน ❌")

                    st.info(f"""
                    **📌 บทวิเคราะห์ชะรีอะห์เบื้องต้น**
                    - **หนี้สิน (Debt Ratio):** ควร < 33% (เกณฑ์ AAOIFI) | ปัจจุบันอยู่ที่ {data['debt_ratio']*100:.1f}%
                    - **รายได้ดอกเบี้ย (Interest Ratio):** ควร < 5% | ปัจจุบันอยู่ที่ {data['interest_ratio']*100:.1f}%
                    - **ธุรกิจหลัก:** {data['description'][:300]}...
                    """)

                with tab3:
                    st.markdown("#### 📊 มูลค่าหุ้น (Valuation)")
                    v1, v2, v3 = st.columns(3)
                    pe = data['pe_ratio']
                    pb = data['pb_ratio']
                    eps = data['eps']
                    v1.metric("P/E Ratio", f"{pe:.1f}x" if pe else "N/A")
                    v2.metric("P/B Ratio", f"{pb:.1f}x" if pb else "N/A")
                    v3.metric("EPS", f"${eps:.2f}" if eps else "N/A")

                    st.markdown("#### 💰 ผลประกอบการ (Profitability)")
                    p1, p2, p3 = st.columns(3)
                    roe = data['roe']
                    margin = data['net_margin']
                    div_yield = data.get('dividend_yield')
                    p1.metric("ROE", f"{roe*100:.1f}%")
                    p2.metric("Net Margin", f"{margin*100:.1f}%")
                    p3.metric("Dividend Yield", f"{div_yield*100:.1f}%" if div_yield else "ไม่มีปันผล")

        except Exception as e:
            st.error(f"⚠️ ระบบขัดข้อง: ไม่สามารถประมวลผลข้อมูลได้ในขณะนี้ ({e})")
