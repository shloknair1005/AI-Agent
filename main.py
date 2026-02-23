from groq import Groq
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv

client = Groq(api_key="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")
load_dotenv()

def get_stock_analysis_data(symbol):
    try:
        stock = yf.Ticker(symbol)

        for period in ["3mo", "1mo", "5d", "1d"]:
            print(f"Trying period: {period}")
            hist = stock.history(period=period)
            if not hist.empty:
                print(f"Success with period: {period}")
                break

        if hist.empty:
            return {"error": f"No data found for {symbol} after trying multiple periods"}

        try:
            info = stock.info
        except:
            info = {}

        return {
            "symbol": symbol,
            "current_price": round(hist["Close"].iloc[-1], 2),
            "day_change": round(hist["Close"].iloc[-1] - hist["Close"].iloc[-2], 2) if len(hist) > 1 else 0,
            "day_change_pct": round(((hist["Close"].iloc[-1] / hist["Close"].iloc[-2]) - 1) * 100, 2) if len(
                hist) > 1 else 0,
            "volume": int(hist["Volume"].iloc[-1]),
            "avg_volume": int(hist["Volume"].mean()),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": len(hist)
        }
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}


def finance_agent(user_query, stock_data=None):

    system_prompt = """You are a finance education AI that helps users understand stocks and markets.

CRITICAL DISCLAIMERS:
- You do NOT provide investment advice or recommendations
- You do NOT tell users to buy, sell, or hold
- All information is educational only
- Users must consult licensed financial advisors for decisions

Your approach:
- Analyze data objectively
- Explain what metrics mean
- Present multiple viewpoints
- Highlight risks and uncertainties
- Encourage further research"""

    user_message = user_query
    if stock_data and "error" not in stock_data:
        user_message += f"\n\nCurrent data: {stock_data}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    symbol = "GOOGL"

    print(f"Fetching data for {symbol}...")
    stock_data = get_stock_analysis_data(symbol)

    if "error" in stock_data:
        print(f"\n❌ Error: {stock_data['error']}")
        print("\nTroubleshooting steps:")
        print("1. Run: pip install curl_cffi")
        print("2. Run: pip install --upgrade yfinance")
        print("3. Check your internet connection")
    else:
        print(f"\n✓ {symbol} Current Price: ${stock_data['current_price']}")
        print(f"✓ Change: ${stock_data['day_change']} ({stock_data['day_change_pct']}%)")
        print(f"✓ Data points retrieved: {stock_data['data_points']}\n")

        print("Generating analysis...\n")
        analysis = finance_agent(
            f"Provide educational analysis of {symbol} for someone considering short-term trading. "
            f"Explain what the key metrics indicate and what risks to consider.",
            stock_data
        )

        print("=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        print(analysis)
        print("=" * 60)