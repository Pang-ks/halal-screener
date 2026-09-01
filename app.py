import streamlit as st
from data_fetcher import get_stock_data, get_historical_prices 
from halal_engine import screen

st.set_page_config(page_title="Shariah Screener", page_icon="🕌", layout="wide", initial_sidebar_state="collapsed")

# CSS สไตล์ Neumorphism, Input, Button และ Footer
st.markdown("""
<style>
    /* สีพื้นหลังหลัก */
    .stApp, .block-container {
        background-color: #e0e5ec !important;
    }
    
    h1, h2, h3, h4, p, span, div, label {
        color: #4a4a4a !important;
    }

    .neumorphic-card {
        background-color: #e0e5ec;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 9px 9px 16px rgb(163,177,198,0.6), 
                   -9px -9px 16px rgba(255,255,255, 0.5);
    }
    
    .neumorphic-inset {
        background-color: #e0e5ec;
        border-radius: 20px;
        padding: 20px;
        box-shadow: inset 6px 6px 10px 0 rgba(163,177,198, 0.7),
                    inset -6px -6px 10px 0 rgba(255,255,255, 0.8);
    }

    .card-title { font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #7a7a7a !important; }
    .card-value { font-size: 1.8rem; font-weight: 700; margin: 10px 0; color: #2d3748 !important; }
    
    /* 🌟 แต่งช่องกรอกข้อมูลให้ยุบลงไปแบบ Neumorphism */
    div[data-testid="stTextInput"] input {
        background-color: #e0e5ec !important;
        color: #4a4a4a !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: inset 5px 5px 10px rgba(163,177,198,0.6), 
                   inset -5px -5px 10px rgba(255,255,255, 0.5) !important;
        padding: 10px 15px !important;
    }

    /* 🌟 แต่งปุ่มกดให้นูนขึ้นมา และยุบเวลากด */
    div[data-testid="stButton"] button {
        background-color: #e0e5ec !important;
        color: #7a7a7a !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        height: 42px !important;
        width: 100% !important;
        box-shadow: 5px 5px 10px rgba(163,177,198,0.6), 
                   -5px -5px 10px rgba(255,255,255, 0.5) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stButton"] button:hover, 
    div[data-testid="stButton"] button:active {
        color: #2d3748 !important;
        box-shadow: inset 4px 4px 8px rgba(163,177,198,0.6), 
                   inset -4px -4px 8px rgba(255,255,255, 0.5) !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #e0e5ec;
        text-align: center;
        padding: 15px;
        font-size: 0.95rem;
        font-weight: 600;
        color: #7a7a7a !important;
        box-shadow: 0px -5px 15px rgba(163,177,198,0.3);
        z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

# 🌟 แบ่งหน้าจอเป็น 3 คอลัมน์ (หัวข้อ, ช่องค้นหา, ปุ่มกด)
col_title, col_search, col_btn = st.columns([5, 3, 1])
with col_title:
    st.markdown("<h1>🕌 Shariah Screener</h1>", unsafe_allow_html=True)
    st.markdown("<p>Analyze global equities & ETFs for Shariah compliance.</p>", unsafe_allow_html=True)
with col_search:
    st.write("") 
    ticker = st.text_input("Search Asset", placeholder="Enter Ticker (e.g., AAPL, SPTE)", label_visibility="collapsed")
with col_btn:
    st.write("") 
    search_btn = st.button("Search 🔍")

st.markdown("<br>", unsafe_allow_html=True)

# 🌟 เงื่อนไข: ทำงานเมื่อมีการพิมพ์ข้อความ หรือ มีการกดปุ่ม
if ticker or search_btn:
    if not ticker:
        st.warning("⚠️ Please enter a ticker symbol first.")
    else:
        with st.spinner("Fetching market data..."):
            try:
                data = get_stock_data(ticker.upper())
                
                if data is None:
                    st.warning(f"⚠️ Data not found for '{ticker.upper()}'.")
                else:
                    result = screen(data)
                    
                    top_col1, top_col2 = st.columns([7, 3])
                    
                    with top_col1:
                        st.markdown(f"<h3>{data['name']} ({result['ticker']})</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p>Sector: {data['sector']} | Price: ${data['price']}</p>", unsafe_allow_html=True)
                        
                        history_data = get_historical_prices(ticker.upper(), period="1y")
                        if history_data is not None:
                            st.line_chart(history_data, height=280)

                    with top_col2:
                        st.write("") 
                        status_color = "🟢 PASS" if "PASS" in result['status'] else ("🟡 DOUBTFUL" if "DOUBTFUL" in result['status'] else "🔴 FAIL")
                        st.markdown(f"""
                        <div class="neumorphic-inset" style="height: 280px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
                            <div class="card-title">Compliance Status</div>
                            <div class="card-value" style="font-size: 2.2rem;">{status_color}</div>
                            <p style="font-size: 0.85rem; margin-top: 15px; font-weight: 500;">
                                AAOIFI benchmarks applied.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h3>Shariah Metrics</h3>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    
                    is_etf_text = "ETF (Check Holdings)" if data.get("is_etf") else "Passed"
                    
                    with c1:
                        debt_val = f"{data['debt_ratio']*100:.1f}%"
                        st.markdown(f"""
                        <div class="neumorphic-card">
                            <div class="card-title">Debt Ratio</div>
                            <div class="card-value">{debt_val}</div>
                            <p style="font-weight: 500;">Target: < 33.0% {'✅' if result.get('debt_ok', True) else '❌'}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with c2:
                        int_val = f"{data['interest_ratio']*100:.1f}%"
                        st.markdown(f"""
                        <div class="neumorphic-card">
                            <div class="card-title">Interest Income</div>
                            <div class="card-value">{int_val}</div>
                            <p style="font-weight: 500;">Target: < 5.0% {'✅' if result.get('interest_ok', True) else '❌'}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with c3:
                        sector_val = data['sector'][:15] + "..." if len(data['sector']) > 15 else data['sector']
                        st.markdown(f"""
                        <div class="neumorphic-card">
                            <div class="card-title">Business Sector</div>
                            <div class="card-value">{sector_val}</div>
                            <p style="font-weight: 500;">{is_etf_text if data.get('is_etf') else 'Permissible'} {'✅' if result.get('business_ok', True) else '❌'}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h3>Financial Fundamentals</h3>", unsafe_allow_html=True)
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("Market Cap", f"${data['market_cap']:,.0f}" if data['market_cap'] else "N/A")
                    f2.metric("P/E Ratio", f"{data['pe_ratio']:.2f}" if data['pe_ratio'] else "N/A")
                    f3.metric("ROE", f"{data['roe']*100:.2f}%" if data['roe'] else "N/A")
                    f4.metric("Dividend Yield", f"{data.get('dividend_yield', 0)*100:.2f}%" if data.get('dividend_yield') else "N/A")
                    st.markdown("<br><br>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ System Error: ({e})")
else:
    st.markdown("""
    <div class="neumorphic-inset" style="text-align: center; margin-top: 50px; padding: 40px;">
        <h3 style="color: #7a7a7a !important;">Trending Halal Assets</h3>
        <p style="font-weight: 500;">💡 Type a ticker symbol in the search bar above and press Search to generate a report.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="custom-footer">
    Developed by <strong>Arfam Kasa</strong> | Halal Stock Screener System
</div>
""", unsafe_allow_html=True)
