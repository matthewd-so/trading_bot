def moving_average_strategy(data, short_window=20, long_window=50):
    data['short_ma'] = data['close'].rolling(window=short_window).mean()
    data['long_ma'] = data['close'].rolling(window=long_window).mean()

    #(1 = buy signal, 0 = no signal)
    signals = (data['short_ma'].iloc[short_window:] > data['long_ma'].iloc[short_window:]).astype(int)
    
    data.loc[data.index[short_window:], 'signal'] = signals

    data['signal'].fillna(0, inplace=True)

    signals_df = data[data['signal'] != 0][['signal']]

    return data, signals_df


    return data
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
