def moving_average_strategy(data, short_window=20, long_window=50):
    data['short_ma'] = data['close'].rolling(window=short_window).mean()
    data['long_ma'] = data['close'].rolling(window=long_window).mean()

    #(1 = buy signal, 0 = no signal)
    signals = (data['short_ma'].iloc[short_window:] > data['long_ma'].iloc[short_window:]).astype(int)
    
    data.loc[data.index[short_window:], 'signal'] = signals

    data['signal'].fillna(0, inplace=True)

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df

# Relative Strength Index
def rsi_strategy(data, window=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['rsi'] = rsi

    data['signal'] = 0
    data.loc[data['rsi'] < 30, 'signal'] = 1  # Buy signal
    data.loc[data['rsi'] > 70, 'signal'] = -1  # Sell signal

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df

# MACD
def macd_strategy(data, fast_window=12, slow_window=26, signal_window=9):
    data['ema_fast'] = data['close'].ewm(span=fast_window, min_periods=slow_window).mean()
    data['ema_slow'] = data['close'].ewm(span=slow_window, min_periods=slow_window).mean()
    data['macd'] = data['ema_fast'] - data['ema_slow']
    data['macd_signal'] = data['macd'].ewm(span=signal_window, min_periods=signal_window).mean()

    data['signal'] = 0
    data.loc[data['macd'] > data['macd_signal'], 'signal'] = 1  # Buy signal
    data.loc[data['macd'] < data['macd_signal'], 'signal'] = -1  # Sell signal

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df

# Bollinger Bands
def bollinger_bands_strategy(data, window=20, num_std_dev=2):
    data['middle_band'] = data['close'].rolling(window=window).mean()
    data['upper_band'] = data['middle_band'] + num_std_dev * data['close'].rolling(window=window).std()
    data['lower_band'] = data['middle_band'] - num_std_dev * data['close'].rolling(window=window).std()

    data['signal'] = 0
    data.loc[data['close'] < data['lower_band'], 'signal'] = 1  # Buy signal
    data.loc[data['close'] > data['upper_band'], 'signal'] = -1  # Sell signal

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df

# Stochastic Oscillator
def stochastic_oscillator_strategy(data, k_window=14, d_window=3):
    data['low_k'] = data['low'].rolling(window=k_window).min()
    data['high_k'] = data['high'].rolling(window=k_window).max()
    data['%K'] = (data['close'] - data['low_k']) / (data['high_k'] - data['low_k']) * 100
    data['%D'] = data['%K'].rolling(window=d_window).mean()

    data['signal'] = 0
    data.loc[(data['%K'] < 20) & (data['%D'] < 20), 'signal'] = 1  # Buy signal
    data.loc[(data['%K'] > 80) & (data['%D'] > 80), 'signal'] = -1  # Sell signal

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df

# SMA Crossover
def sma_crossover_strategy(data, short_window=50, long_window=200):
    data['short_sma'] = data['close'].rolling(window=short_window).mean()
    data['long_sma'] = data['close'].rolling(window=long_window).mean()

    data['signal'] = 0
    data.loc[data['short_sma'] > data['long_sma'], 'signal'] = 1  # Buy signal
    data.loc[data['short_sma'] < data['long_sma'], 'signal'] = -1  # Sell signal

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df


def simulate_trading(data, initial_capital):
    position = 0  # 0 means no position, 1 means we have bought
    balance = initial_capital
    data['portfolio_value'] = balance
    data['trade_signal'] = 0  # 0 means no signal, 1 means buy, -1 means sell

    for i in range(1, len(data)):
        if data['signal'].iloc[i] == 1 and position == 0:  # Buy signal
            position = 1
            balance -= data['close'].iloc[i]
            data.loc[data.index[i], 'portfolio_value'] = balance + data['close'].iloc[i] * position
            data.loc[data.index[i], 'trade_signal'] = 1  # Record buy signal
        elif data['signal'].iloc[i] == 0 and position == 1:  # Sell signal
            position = 0
            balance += data['close'].iloc[i]
            data.loc[data.index[i], 'portfolio_value'] = balance
            data.loc[data.index[i], 'trade_signal'] = -1  # Record sell signal
        else:
            data.loc[data.index[i], 'portfolio_value'] = balance + data['close'].iloc[i] * position

    # Filter out rows where trade_signal is 1 (buy) or -1 (sell)
    signals = data[data['trade_signal'] != 0][['trade_signal', 'portfolio_value']]

    return data, signals
