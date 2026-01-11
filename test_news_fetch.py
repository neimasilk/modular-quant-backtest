
import yfinance as yf
import pandas as pd

def test_news():
    ticker = yf.Ticker("NVDA")
    news = ticker.news
    
    print(f"Found {len(news)} news items.")
    if news:
        print("Sample news:")
        print(news[0])
        
    # Check if we can search by date (unlikely with free API but worth checking)
    # yfinance doesn't officially support historical news search in the Ticker object easily
    
if __name__ == "__main__":
    test_news()
