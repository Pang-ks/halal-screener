import streamlit as st
from data_fetcher import get_stock_data, get_historical_prices 
from halal_engine import screen

# 🌟 1. ตั้งค่าหน้าเพจให้กว้างสุด
st.set_page_config(page_title="Qubix Halal Screener", page_icon="🕌", layout="wide", initial_sidebar_state="collapsed")

# 🌟 2. CSS สำหรับ Dark Theme Terminal & แปลง Radio เป็น Nav Bar
st.markdown("""
<style>
    .stApp, .block-container { background-color: #0B0E14 !important; color: #FFFFFF !important; }
    h1, h2, h3, h4, p, span, label { color: #FFFFFF; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 🌟 เปลี่ยนหน้าตา Radio ให้เป็นปุ่ม Nav Bar แบบกดได้ */
    div[data-testid="stRadio"] div[role="radiogroup"] { flex-direction: row; gap: 10px; }
    div[data-testid="stRadio"] div[role="radio"] > div:first-child { display: none !important; } /* ซ่อนวงกลม */
    div[data-testid="stRadio"] div[role="radio"] {
        background-color: #1A1F2C;
        padding: 8px 20px;
        border-radius: 8px;
        margin: 0;
        cursor: pointer;
        transition: all 0.2s;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stRadio"] div[role="radio"] p { color: #8F9BBA !important; font-size: 14px; font-weight: 600; margin: 0; }
    
    /* สถานะ Active และ Hover */
    div[data-testid="stRadio"] div[role="radio"][data-checked="true"],
    div[data-testid="stRadio"] div[role="radio"]:hover { background-color: #FFFFFF !important; }
    div[data-testid="stRadio"] div[role="radio"][data-checked="true"] p,
    div[data-testid="stRadio"] div[role="radio"]:hover p { color: #0B0E14 !important; }
    
    .chart-stats-label { font-size: 12px; color: #64748B; margin-bottom: 2px; margin-top: 10px; }
    .chart-stats-val { font-size: 14px; font-weight: bold; color: #E2E8F0; }
    
    .white-card { background-color: #FFFFFF; border-radius: 16px; padding: 24px; color: #121212 !important; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .white-card h1, .white-card h2, .white-card h3, .white-card h4, .white-card p, .white-card span, .white-card div { color: #121212 !important; }
    .card-subtitle { font-size: 14px; color: #64748B !important; font-weight: 600; margin-bottom: 15px;}
    .card-big-val { font-size: 36px; font-weight: bold; margin: 10px 0; }
    
    .badge-pass { background: #E6F4EA; color: #137333 !important; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: bold;}
    .badge-fail { background: #FCE8E6; color: #C5221F !important; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: bold;}

    div[data-testid="stTextInput"] input { background-color: #1A1F2C !important; color: white !important; border: 1px solid #2D3748 !important; border-radius: 8px !important; }
    div[data-testid="stButton"] button { background-color: #FFFFFF !important; color: #0B0E14 !important; font-weight: bold !important; border-radius: 8px !important; height: 42px !important; width: 100%; border: none !important;}
    div[data-testid="stButton"] button:hover { background-color: #E2E8F0 !important; color: #0B0E14 !important; }
    div[data-testid="stButton"] button p { color: #0B0E14 !important; font-weight: bold !important; }

    .custom-footer { position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0B0E14; text-align: center; padding: 15px; font-size: 0.9rem; font-weight: 500; color: #64748B !important; border-top: 1px solid #1A1F2C; z-index: 100; }
</style>
""", unsafe_allow_html=True)

# 🌟 3. แถบ Navigation ด้านบน (เปลี่ยนเป็นระบบคลิกได้จริง)
col_logo, col_nav = st.columns([2, 8])
with col_logo:
    st.markdown("<div style='font-size: 24px; font-weight: bold; margin-top: 5px;'>🕌 HalalScreener</div>", unsafe_allow_html=True)
with col_nav:
    nav_selection = st.radio(
        "Nav",
        ["Dashboard", "Stocks", "Portfolio", "📖 Shariah Guide"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("<hr style='border-color: #1A1F2C; margin: 5px 0 20px 0;'>", unsafe_allow_html=True)

# 🌟 4. คอนเทนต์: หน้าคำแนะนำกฎชะรีอะห์
if nav_selection == "📖 Shariah Guide":
    st.markdown("## 📖 กฎหลักชะรีอะห์สำหรับการลงทุน")
    st.markdown("<p style='color: #8F9BBA; font-size: 16px;'>มาตรฐานอ้างอิงจาก AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions)</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1A1F2C; padding: 25px; border-radius: 12px; margin-top: 20px; border-left: 5px solid #3B82F6;">
        <h4 style="color: #FFFFFF; margin-bottom: 10px;">1. การคัดกรองธุรกิจ (Business Activity Screening)</h4>
        <p style="color: #E2E8F0; font-size: 14px;">ธุรกิจหลักของบริษัทต้องไม่เกี่ยวข้องกับสิ่งต้องห้าม (Haram) ได้แก่:</p>
        <ul style="color: #8F9BBA; font-size: 14px;">
            <li>สถาบันการเงินที่คิดดอกเบี้ย (ธนาคารพาณิชย์, ประกันภัยทั่วไป)</li>
            <li>ธุรกิจที่เกี่ยวข้องกับแอลกอฮอล์, ยาสูบ, การพนัน/คาสิโน, เนื้อหมู</li>
            <li>ธุรกิจที่เกี่ยวกับอาวุธสงคราม และสื่อลามกอนาจาร</li>
        </ul>
    </div>
    
    <div style="background-color: #1A1F2C; padding: 25px; border-radius: 12px; margin-top: 15px; border-left: 5px solid #8B5CF6;">
        <h4 style="color: #FFFFFF; margin-bottom: 10px;">2. การคัดกรองอัตราส่วนทางการเงิน (Financial Screening)</h4>
        <p style="color: #E2E8F0; font-size: 14px;">เพื่อจำกัดการมีส่วนร่วมกับ "ริบา" (ดอกเบี้ย) อย่างเข้มงวด:</p>
        <ul style="color: #8F9BBA; font-size: 14px;">
            <li><strong>สัดส่วนหนี้สินที่มีดอกเบี้ย (Debt Ratio):</strong> ต้องน้อยกว่า 33% ของสินทรัพย์รวม</li>
            <li><strong>รายได้ที่ไม่บริสุทธิ์ (Interest Income):</strong> ดอกเบี้ยรับ ต้องไม่เกิน 5% ของรายได้รวม</li>
        </ul>
    </div>
    
    <div style="background-color: #1A1F2C; padding: 25px; border-radius: 12px; margin-top: 15px; border-left: 5px solid #10B981;">
        <h4 style="color: #FFFFFF; margin-bottom: 10px;">3. การทำความสะอาดรายได้ (Purification)</h4>
        <p style="color: #8F9BBA; font-size: 14px; line-height: 1.6;">
            แม้บริษัทจะผ่านเกณฑ์รายได้ดอกเบี้ยที่ < 5% แล้ว แต่รายได้ส่วนนั้นยังถือเป็นสิ่งไม่บริสุทธิ์ 
            นักลงทุนมุสลิมมีหน้าที่คำนวณสัดส่วนรายได้ที่ไม่บริสุทธิ์ออกจาก "เงินปันผล" ที่ได้รับ 
            แล้วนำไปบริจาคเพื่อการกุศล (โดยไม่หวังผลบุญ) เพื่อทำความสะอาด (Purify) พอร์ตการลงทุนของตนเอง
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)

# 🌟 5. คอนเทนต์: หน้า Coming Soon
elif nav_selection in ["Stocks", "Portfolio"]:
    st.markdown(f"## 🚧 {nav_selection} (Coming Soon)")
    st.info("หน้านี้กำลังอยู่ในระหว่างการพัฒนาครับ!")

# 🌟 6. คอนเทนต์: หน้า Dashboard (ระบบค้นหาหลัก)
else:
    col_search, col_btn, _ = st.columns([3, 1, 6])
    with col_search:
        ticker = st.text_input("Search", placeholder="Search ticker (e.g. AAPL, SPTE)", label_visibility="collapsed")
    with col_btn:
        search_btn = st.button("Search")

    if ticker or search_btn:
        if not ticker:
            st.warning("⚠️ Please enter a ticker symbol.")
        else:
            with st.spinner("Loading market data..."):
                try:
                    data = get_stock_data(ticker.upper())
                    
                    if data is None:
                        st.error("⚠️ Data not found.")
                    else:
                        result = screen(data)
                        
                        st.markdown(f"<h3 style='margin-bottom: 0;'>{data['name']} ({result['ticker']})</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #8F9BBA; font-size: 14px;'>Sector: {data['sector']}</p>", unsafe_allow_html=True)
                        
                        chart_col, stats_col = st.columns([8, 2])
                        
                        with chart_col:
                            history_data = get_historical_prices(ticker.upper(), period="1y")
                            if history_data is not None:
                                st.line_chart(history_data, height=350)
                                
                        with stats_col:
                            html_stats = (
                                '<div class="chart-stats-label">Market Capitalization</div>'
                                f'<div class="chart-stats-val">${data["market_cap"]:,.0f}</div>'
                                '<div class="chart-stats-label">P/E Ratio (TTM)</div>'
                                f'<div class="chart-stats-val">{data["pe_ratio"]:.2f}</div>'
                                '<div class="chart-stats-label">ROE</div>'
                                f'<div class="chart-stats-val">{data["roe"]*100:.2f}%</div>'
                                '<div class="chart-stats-label">Dividend Yield</div>'
                                f'<div class="chart-stats-val">{data.get("dividend_yield", 0)*100:.2f}%</div>'
                                '<div class="chart-stats-label">Current Price</div>'
                                f'<div class="chart-stats-val" style="font-size: 24px; color: #FFFFFF;">${data["price"]}</div>'
                            )
                            st.markdown(html_stats, unsafe_allow_html=True)

                        st.write("")
                        
                        c1, c2, c3 = st.columns(3)
                        
                        is_pass = "PASS" in result['status']
                        badge_class = "badge-pass" if is_pass else "badge-fail"
                        status_text = "Halal Certified" if is_pass else ("Doubtful" if "DOUBTFUL" in result['status'] else "Not Halal")
                        
                        with c1:
                            html_c1 = (
                                '<div class="white-card">'
                                '<div class="card-subtitle">Compliance Status</div>'
                                f'<div class="card-big-val">{status_text}</div>'
                                f'<span class="{badge_class}">AAOIFI Standards</span>'
                                '<div style="margin-top: 20px; font-size: 14px; color: #64748B;">'
                                'Analyzed based on latest financial statements and business activities.'
                                '</div>'
                                '</div>'
                            )
                            st.markdown(html_c1, unsafe_allow_html=True)
                            
                        with c2:
                            debt_pct = data['debt_ratio'] * 100
                            int_pct = data['interest_ratio'] * 100
                            debt_status = "✅" if result.get('debt_ok', True) else "❌"
                            int_status = "✅" if result.get('interest_ok', True) else "❌"
                            
                            html_c2 = (
                                '<div class="white-card">'
                                '<div class="card-subtitle">Shariah Metrics (Financials)</div>'
                                '<div style="display:flex; justify-content:space-between; font-size: 14px; margin-top: 15px;">'
                                '<span>Debt Ratio (&lt;33%)</span>'
                                f'<strong>{debt_pct:.1f}% {debt_status}</strong>'
                                '</div>'
                                '<div style="background:#F1F5F9; height:8px; border-radius:4px; margin-top:5px; margin-bottom: 20px;">'
                                f'<div style="width:{min(debt_pct, 100)}%; background:#3B82F6; height:8px; border-radius:4px;"></div>'
                                '</div>'
                                '<div style="display:flex; justify-content:space-between; font-size: 14px;">'
                                '<span>Interest Income (&lt;5%)</span>'
                                f'<strong>{int_pct:.1f}% {int_status}</strong>'
                                '</div>'
                                '<div style="background:#F1F5F9; height:8px; border-radius:4px; margin-top:5px;">'
                                f'<div style="width:{min(int_pct*5, 100)}%; background:#8B5CF6; height:8px; border-radius:4px;"></div>'
                                '</div>'
                                '</div>'
                            )
                            st.markdown(html_c2, unsafe_allow_html=True)
                            
                        with c3:
                            bus_color = "#137333" if result.get("business_ok", True) else "#C5221F"
                            bus_text = "✅ Permissible" if result.get("business_ok", True) else "❌ Non-Permissible"
                            html_c3 = (
                                '<div class="white-card">'
                                '<div class="card-subtitle">Business Activity Screening</div>'
                                '<div style="margin-top: 15px; padding-bottom: 10px; border-bottom: 1px solid #E2E8F0;">'
                                '<div style="font-size: 12px; color: #64748B;">Primary Sector</div>'
                                f'<div style="font-weight: bold; font-size: 16px;">{data["sector"]}</div>'
                                '</div>'
                                '<div style="margin-top: 15px;">'
                                '<div style="font-size: 12px; color: #64748B;">Business Activity Result</div>'
                                f'<div style="font-weight: bold; font-size: 16px; color: {bus_color};">'
                                f'{bus_text}'
                                '</div>'
                                '</div>'
                                '</div>'
                            )
                            st.markdown(html_c3, unsafe_allow_html=True)
                            
                        st.markdown("<br><br><br>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"⚠️ System Error: ({e})")

# 🌟 7. Footer ลายเซ็นนักพัฒนา
st.markdown("""
<div class="custom-footer">
    Developed by <strong>Arfam Kasa</strong> | Professional Halal Stock Screener
</div>
""", unsafe_allow_html=True)
