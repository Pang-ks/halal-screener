import streamlit as st
from data_fetcher import get_stock_data, get_historical_prices 
from halal_engine import screen

# 1. Page Config (Wide layout for Dashboard feel)
st.set_page_config(page_title="Shariah Screener Pro", page_icon="🕌", layout="wide", initial_sidebar_state="expanded")

# 2. Custom CSS for Modern FinTech UI (Pastel Cards & Dark Sidebar)
# 2. Custom CSS for Modern FinTech UI (Pastel Cards & White Background)
st.markdown("""
<style>
    /* บังคับพื้นหลังด้านนอกสุดให้เป็นสีเทาอ่อนมากแบบแอปพรีเมียม */
    .stApp {
        background-color: #F4F7FE;
    }
    
    /* สร้างกรอบสีขาวล้วนตรงกลางให้เหมือนหน้าต่าง Dashboard */
    .block-container { 
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 3rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0px 10px 30px rgba(112, 144, 176, 0.12);
        max-width: 95%;
    }
    
    /* Custom Colored Cards */
    .dash-card { border-radius: 16px; padding: 20px; margin-bottom: 15px; font-family: 'Inter', sans-serif; transition: transform 0.2s; }
    .dash-card:hover { transform: translateY(-3px); }
    
    .card-blue { background-color: #F4F7FE; color: #2B3674; }
    .card-purple { background-color: #F3E8FF; color: #4C1D95; }
    .card-green { background-color: #DCFCE7; color: #14532D; }
    .card-dark { background-color: #1B254B; color: #FFFFFF; }
    
    /* Typography inside cards */
    .card-title { font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.8; }
    .card-value { font-size: 1.8rem; font-weight: 700; margin: 5px 0; }
    .card-sub { font-size: 0.85rem; font-weight: 500; opacity: 0.9; }
    
    /* ซ่อนลิงก์ด้านบนของ Streamlit */
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Sidebar (Navigation mimicking the left panel)
with st.sidebar:
    st.markdown("### 🕌 ShariahPro")
    st.markdown("---")
    st.button("📊 Overview", use_container_width=True)
    st.button("⭐ Watchlist", use_container_width=True)
    st.button("📈 Market Trends", use_container_width=True)
    st.button("⚙️ Settings", use_container_width=True)
    st.markdown("---")
    st.caption("AAOIFI Standards Applied")

# 4. Top Header & Search Bar
col_title, col_search = st.columns([2, 1])
with col_title:
    st.title("Market Overview")
    st.markdown("Analyze global equities & ETFs for Shariah compliance.")
with col_search:
    st.write("") # Spacing
    ticker = st.text_input("Search Asset", placeholder="Enter Ticker (e.g., AAPL, SPTE, PTT.BK)", label_visibility="collapsed")

st.divider()

# 5. Main Dashboard Logic
if ticker:
    with st.spinner("Fetching market data..."):
        try:
            data = get_stock_data(ticker.upper())
            
            if data is None:
                st.warning(f"⚠️ Data not found for '{ticker.upper()}'. Please verify the ticker symbol.")
            else:
                result = screen(data)
                
                # --- TOP SECTION: Chart & Status Card ---
                top_col1, top_col2 = st.columns([7, 3])
                
                with top_col1:
                    st.subheader(f"{data['name']} ({result['ticker']})")
                    st.caption(f"Sector: {data['sector']} | Price: ${data['price']}")
                    
                    history_data = get_historical_prices(ticker.upper(), period="1y")
                    if history_data is not None:
                        st.line_chart(history_data, height=280)
                    else:
                        st.info("Chart data unavailable.")

                with top_col2:
                    st.write("") # Alignment spacing
                    st.write("")
                    # Dark Promo-style Card for Status
                    status_color = "🟢 PASS" if "PASS" in result['status'] else ("🟡 DOUBTFUL" if "DOUBTFUL" in result['status'] else "🔴 FAIL")
                    st.markdown(f"""
                    <div class="dash-card card-dark" style="height: 280px; display:flex; flex-direction:column; justify-content:center;">
                        <div class="card-title">Compliance Status</div>
                        <div class="card-value" style="font-size: 2.2rem;">{status_color}</div>
                        <p style="font-size: 0.9rem; margin-top: 15px; color: #A0AEC0;">
                            Analyzed using AAOIFI benchmarks. Debt < 33%, Interest < 5%, and permissible business activities.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # --- MIDDLE SECTION: Shariah Criteria (Colored Cards) ---
                st.markdown("### Shariah Metrics")
                c1, c2, c3 = st.columns(3)
                
                is_etf_text = "ETF (Check Holdings)" if data.get("is_etf") else "Passed"
                
                with c1:
                    debt_val = f"{data['debt_ratio']*100:.1f}%"
                    debt_sub = "Target: < 33.0%"
                    st.markdown(f"""
                    <div class="dash-card card-blue">
                        <div class="card-title">Debt Ratio</div>
                        <div class="card-value">{debt_val}</div>
                        <div class="card-sub">{debt_sub} {'✅' if result.get('debt_ok', True) else '❌'}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    int_val = f"{data['interest_ratio']*100:.1f}%"
                    int_sub = "Target: < 5.0%"
                    st.markdown(f"""
                    <div class="dash-card card-purple">
                        <div class="card-title">Interest Income</div>
                        <div class="card-value">{int_val}</div>
                        <div class="card-sub">{int_sub} {'✅' if result.get('interest_ok', True) else '❌'}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    sector_val = data['sector'][:15] + "..." if len(data['sector']) > 15 else data['sector']
                    st.markdown(f"""
                    <div class="dash-card card-green">
                        <div class="card-title">Business Sector</div>
                        <div class="card-value">{sector_val}</div>
                        <div class="card-sub">{is_etf_text if data.get('is_etf') else 'Permissible'} {'✅' if result.get('business_ok', True) else '❌'}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Show failure reasons if any
                if "PASS" not in result['status']:
                    st.error("**Non-Compliance Flags:** Please review debt, interest, or sector violations.")

                # --- BOTTOM SECTION: Financial Fundamentals ---
                st.markdown("### Financial Fundamentals")
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("Market Cap", f"${data['market_cap']:,.0f}" if data['market_cap'] else "N/A")
                f2.metric("P/E Ratio", f"{data['pe_ratio']:.2f}" if data['pe_ratio'] else "N/A")
                f3.metric("ROE (Return on Equity)", f"{data['roe']*100:.2f}%" if data['roe'] else "N/A")
                f4.metric("Dividend Yield", f"{data.get('dividend_yield', 0)*100:.2f}%" if data.get('dividend_yield') else "N/A")

        except Exception as e:
            st.error(f"⚠️ System Error: Unable to process data at this time. ({e})")
else:
    # Default state when no ticker is searched (Mimicking the bottom table in your reference)
    st.markdown("### Trending Halal Assets")
    st.info("💡 Type a ticker symbol in the search bar above (e.g., AAPL, SPTE) to generate a full Shariah compliance report.")
