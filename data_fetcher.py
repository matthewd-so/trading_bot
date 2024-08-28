import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol='AAPL', timeframe='1y'):
    stock = yf.Ticker(symbol)
    
    if timeframe == '1d':
        data = stock.history(period='1d', interval='1m')
    elif timeframe == '5d':
        data = stock.history(period='5d')
    elif timeframe == '1mo':
        data = stock.history(period='1mo')
    elif timeframe == '6mo':
        data = stock.history(period='6mo')
    elif timeframe == '1y':
        data = stock.history(period='1y')
    else:
        data = stock.history(period='max')
    
    # Only keep the necessary columns
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data.columns = ['open', 'high', 'low', 'close', 'volume']
    
    return data
