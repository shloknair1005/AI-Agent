"""
StockPulse - Bloomberg-Style Finance Terminal
A professional financial dashboard with real-time data and AI analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from groq import Groq
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()
# Page configuration
st.set_page_config(
    page_title="StockPulse Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Bloomberg-style terminal
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        font-family: 'IBM Plex Mono', monospace;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header styling */
    .terminal-header {
        background: linear-gradient(180deg, #0d1226 0%, #151b35 100%);
        border-bottom: 1px solid #2a3f5f;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 2px 20px rgba(0, 150, 255, 0.1);
    }
    
    .terminal-logo {
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(135deg, #0096ff 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.5px;
    }
    
    .market-status {
        font-size: 10px;
        background: #00ff88;
        color: #000;
        padding: 3px 8px;
        border-radius: 3px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-left: 16px;
    }
    
    .market-closed {
        background: #ff4444;
    }
    
    .header-time {
        color: #0096ff;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Search box */
    .stTextInput > div > div > input {
        background: rgba(42, 63, 95, 0.3);
        border: 1px solid #2a3f5f;
        border-radius: 4px;
        color: #e8eaed;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 16px;
        padding: 16px;
        text-transform: uppercase;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0096ff;
        box-shadow: 0 0 0 3px rgba(0, 150, 255, 0.1);
    }
    
    /* Price display card */
    .price-card {
        background: linear-gradient(135deg, rgba(42, 63, 95, 0.2) 0%, rgba(21, 27, 53, 0.4) 100%);
        border: 1px solid #2a3f5f;
        border-radius: 4px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }
    
    .ticker-symbol {
        font-size: 48px;
        font-weight: 700;
        color: #0096ff;
        letter-spacing: -1px;
        margin-bottom: 8px;
    }
    
    .current-price {
        font-size: 56px;
        font-weight: 700;
        color: #e8eaed;
        font-family: 'Space Grotesk', monospace;
        margin-bottom: 8px;
    }
    
    .price-change-positive {
        color: #00ff88;
        font-size: 20px;
        font-weight: 600;
    }
    
    .price-change-negative {
        color: #ff4466;
        font-size: 20px;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(42, 63, 95, 0.2);
        border: 1px solid #2a3f5f;
        border-radius: 4px;
        padding: 16px;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: rgba(42, 63, 95, 0.4);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 10px;
        color: #8a95a8;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 600;
    }
    
    /* AI Analysis panel */
    .analysis-panel {
        background: linear-gradient(135deg, rgba(42, 63, 95, 0.2) 0%, rgba(21, 27, 53, 0.4) 100%);
        border: 1px solid #2a3f5f;
        border-radius: 4px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }
    
    .analysis-header {
        color: #0096ff;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
        border-left: 4px solid #0096ff;
        padding-left: 12px;
    }
    
    .analysis-text {
        color: #c9d1d9;
        font-size: 13px;
        line-height: 1.8;
        font-family: 'IBM Plex Mono', monospace;
        white-space: pre-wrap;
    }
    
    /* Streamlit metric override */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #0096ff;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 10px;
        color: #8a95a8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Chart styling */
    .js-plotly-plot {
        border-radius: 4px;
    }
    
    /* Loading indicator */
    .stSpinner > div {
        border-top-color: #0096ff !important;
    }
    
    /* Error messages */
    .stAlert {
        background: rgba(255, 68, 102, 0.1);
        border: 1px solid #ff4466;
        color: #ff4466;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'ticker' not in st.session_state:
        st.session_state.ticker = ''
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None
    if 'analysis' not in st.session_state:
        st.session_state.analysis = ''
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True

# Fetch stock data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol: str) -> Optional[Dict]:
    """Fetch stock data from yfinance"""
    try:
        stock = yf.Ticker(symbol)

        # Get historical data
        hist = stock.history(period="3mo")
        if hist.empty:
            return None

        # Get stock info
        info = stock.info

        # Calculate metrics
        latest = hist.iloc[-1]
        previous = hist.iloc[-2] if len(hist) > 1 else latest

        day_change = latest['Close'] - previous['Close']
        day_change_pct = (day_change / previous['Close']) * 100

        return {
            'symbol': symbol.upper(),
            'current_price': latest['Close'],
            'day_change': day_change,
            'day_change_pct': day_change_pct,
            'volume': int(latest['Volume']),
            'avg_volume': int(hist['Volume'].mean()),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'history': hist,
            'timestamp': datetime.now()
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

# Generate AI analysis
def generate_ai_analysis(stock_data: Dict, api_key: str) -> str:
    """Generate AI-powered educational stock analysis"""
    try:
        client = Groq(api_key=api_key)

        symbol = stock_data['symbol']
        current_price = stock_data['current_price']
        day_change = stock_data['day_change']
        day_change_pct = stock_data['day_change_pct']
        volume = stock_data['volume']
        avg_volume = stock_data['avg_volume']
        market_cap = stock_data['market_cap']
        pe_ratio = stock_data['pe_ratio']
        high_52w = stock_data['fifty_two_week_high']
        low_52w = stock_data['fifty_two_week_low']

        # Calculate 52-week position
        if high_52w > 0 and low_52w > 0:
            position_52w = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        else:
            position_52w = 0

        prompt = f"""You are a finance education AI. Provide educational analysis for {symbol} stock.

CRITICAL DISCLAIMERS:
- You do NOT provide investment advice or recommendations
- You do NOT tell users to buy, sell, or hold
- All information is educational only
- Users must consult licensed financial advisors for decisions

Current Data:
- Price: ${current_price:.2f}
- Day Change: {'+' if day_change >= 0 else ''}{day_change:.2f} ({day_change_pct:.2f}%)
- Volume: {volume:,}
- Average Volume: {avg_volume:,}
- Market Cap: ${market_cap:,}
- P/E Ratio: {pe_ratio:.2f}
- 52W Range: ${low_52w:.2f} - ${high_52w:.2f}
- 52W Position: {position_52w:.0f}th percentile

Provide a structured educational analysis covering:
1. CURRENT METRICS OVERVIEW
2. VALUATION CONTEXT
3. TRADING VOLUME ANALYSIS
4. 52-WEEK RANGE POSITIONING
5. SHORT-TERM TRADING CONSIDERATIONS (educational)
6. IMPORTANT RISKS

Format with clear section headers. Be concise but informative."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a finance education AI that provides objective, educational analysis without giving investment advice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating analysis: {str(e)}\n\nPlease ensure your GROQ_API_KEY is set correctly."

# Format large numbers
def format_number(num: float) -> str:
    """Format large numbers with K, M, B, T suffixes"""
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

def format_volume(num: float) -> str:
    """Format volume numbers"""
    if num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif num >= 1e3:
        return f"{num/1e3:.2f}K"
    else:
        return str(int(num))

# Check if market is open
def is_market_open() -> bool:
    """Check if US stock market is currently open"""
    now = datetime.now()
    # Market hours: Monday-Friday, 9:30 AM - 4:00 PM EST
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    hour = now.hour
    return 9 <= hour < 16

# Create price chart
def create_price_chart(hist_data: pd.DataFrame, symbol: str):
    """Create interactive price chart using Plotly"""
    fig = go.Figure()

    # Add price line
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        mode='lines',
        name='Price',
        line=dict(color='#0096ff', width=2),
        hovertemplate='<b>%{x|%b %d}</b><br>Price: $%{y:.2f}<extra></extra>'
    ))

    # Update layout for Bloomberg style
    fig.update_layout(
        title=f'{symbol} - 90 Day Price Chart',
        title_font=dict(size=14, color='#0096ff', family='IBM Plex Mono'),
        xaxis_title='Date',
        yaxis_title='Price ($)',
        plot_bgcolor='rgba(42, 63, 95, 0.1)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family='IBM Plex Mono', size=11, color='#8a95a8'),
        hovermode='x unified',
        height=400,
        margin=dict(l=60, r=20, t=40, b=40),
        xaxis=dict(
            gridcolor='rgba(42, 63, 95, 0.3)',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='rgba(42, 63, 95, 0.3)',
            showgrid=True,
            zeroline=False
        )
    )

    return fig

# Main application
def main():
    load_custom_css()
    init_session_state()

    # Header
    current_time = datetime.now()
    market_status = "MARKET OPEN" if is_market_open() else "MARKET CLOSED"
    status_class = "" if is_market_open() else "market-closed"

    st.markdown(f"""
    <div class="terminal-header">
        <div style="display: flex; align-items: center;">
            <div class="terminal-logo">STOCKPULSE</div>
            <div class="market-status {status_class}">{market_status}</div>
        </div>
        <div style="display: flex; align-items: center; gap: 24px;">
            <div class="header-time">
                🕐 {current_time.strftime('%H:%M:%S')}
            </div>
            <div style="color: #8a95a8; font-size: 14px;">
                {current_time.strftime('%a, %b %d, %Y')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search bar
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ticker_input = st.text_input(
            "Enter Ticker Symbol",
            value=st.session_state.ticker if st.session_state.ticker else "",
            placeholder="e.g., AAPL, GOOGL, TSLA",
            label_visibility="collapsed"
        ).upper()

        if ticker_input and ticker_input != st.session_state.ticker:
            st.session_state.ticker = ticker_input
            with st.spinner('📊 Fetching stock data...'):
                st.session_state.stock_data = fetch_stock_data(ticker_input)
                st.session_state.analysis = ''

    st.markdown("<br>", unsafe_allow_html=True)

    # Display stock data
    if st.session_state.stock_data:
        data = st.session_state.stock_data

        # Main price display
        change_class = "price-change-positive" if data['day_change'] >= 0 else "price-change-negative"
        change_icon = "📈" if data['day_change'] >= 0 else "📉"

        st.markdown(f"""
        <div class="price-card">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div style="font-size: 14px; color: #8a95a8; margin-bottom: 8px;">TICKER</div>
                    <div class="ticker-symbol">{data['symbol']}</div>
                    <div class="current-price">${data['current_price']:.2f}</div>
                    <div class="{change_class}">
                        {change_icon} {'+' if data['day_change'] >= 0 else ''}{data['day_change']:.2f} 
                        ({'+' if data['day_change_pct'] >= 0 else ''}{data['day_change_pct']:.2f}%)
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 11px; color: #8a95a8; margin-bottom: 4px;">LAST UPDATE</div>
                    <div style="font-size: 13px; color: #e8eaed;">
                        {data['timestamp'].strftime('%H:%M:%S')}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Key metrics grid
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.metric("VOLUME", format_volume(data['volume']))
        with col2:
            st.metric("AVG VOLUME", format_volume(data['avg_volume']))
        with col3:
            st.metric("MARKET CAP", format_number(data['market_cap']))
        with col4:
            st.metric("P/E RATIO", f"{data['pe_ratio']:.2f}" if data['pe_ratio'] else "N/A")
        with col5:
            st.metric("52W HIGH", f"${data['fifty_two_week_high']:.2f}" if data['fifty_two_week_high'] else "N/A")
        with col6:
            st.metric("52W LOW", f"${data['fifty_two_week_low']:.2f}" if data['fifty_two_week_low'] else "N/A")

        # Price chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(
            create_price_chart(data['history'].tail(90), data['symbol']),
            use_container_width=True
        )

        # AI Analysis section
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="analysis-panel">
            <div class="analysis-header">🤖 AI EDUCATIONAL ANALYSIS</div>
        """, unsafe_allow_html=True)

        # Generate analysis if not already done
        if not st.session_state.analysis:
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                st.warning("⚠️ GROQ_API_KEY not found. Please set it in your environment variables.")
                st.code("export GROQ_API_KEY='your_api_key_here'")
            else:
                with st.spinner('🧠 Generating AI analysis...'):
                    st.session_state.analysis = generate_ai_analysis(data, groq_api_key)

        if st.session_state.analysis:
            st.markdown(f"""
            <div class="analysis-text">{st.session_state.analysis}</div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    elif not st.session_state.ticker:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; color: #8a95a8;">
            <div style="font-size: 48px; margin-bottom: 16px; color: #2a3f5f;">📊</div>
            <div style="font-size: 18px; margin-bottom: 8px; color: #e8eaed;">Enter a ticker symbol to begin</div>
            <div style="font-size: 14px;">Real-time data, charts, and AI-powered analysis</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()