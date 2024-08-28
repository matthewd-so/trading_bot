import tkinter as tk
from tkinter import ttk
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
from data_fetcher import fetch_stock_data
from trading_logic import moving_average_strategy, simulate_trading
import datetime
from notifications import send_sms_notification

def plot_candlestick(data, stock_symbol):
    fig, ax = mpf.plot(
        data,
        type='candle',
        style='charles',
        ylabel='Price',
        volume=True,
        returnfig=True,
        figratio=(10, 7),
        figscale=1.2
    )

    fig.suptitle(f'Candlestick Chart for {stock_symbol}', fontsize=14, y=0.95)
    
    ax[0].spines['bottom'].set_color('white')
    ax[1].spines['top'].set_color('white')
    
    ax[1].set_ylabel('Volume (10^6)', fontsize=12)

    for label in ax[0].get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    return fig

def start_gui():
    def update_chart():
        selected_symbol = symbol_entry.get().upper()
        selected_timeframe = timeframe_var.get()
        selected_balance = float(balance_entry.get())
        
        data = fetch_stock_data(symbol=selected_symbol, timeframe=selected_timeframe)
        data, signals_df = moving_average_strategy(data)
        data, trades = simulate_trading(data, selected_balance)
        
        for widget in chart_frame.winfo_children():
            widget.destroy()

        fig = plot_candlestick(data, selected_symbol)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        update_price_and_time(selected_symbol)
        
        # Send SMS notifications for buy/sell signals
        for index, row in signals_df.iterrows():
            signal_message = f"Signal: {row['signal']} at {index}"
            send_sms_notification(signal_message)

    
    def update_price_and_time(symbol):
        stock = yf.Ticker(symbol)
        current_price = stock.history(period="1d")['Close'].iloc[-1]
        now = datetime.datetime.now()
        formatted_time = now.strftime('%m/%d/%Y at %I:%M %p')

        latest_data_label.config(text=f"Current Price: ${current_price:.2f}\n{formatted_time}")

        root.after(2000, lambda: update_price_and_time(symbol))

    root = tk.Tk()
    root.title("Stock Trading Bot")
    root.geometry("900x700")
    root.configure(bg="#2b2b2b")

    input_frame = tk.Frame(root, padx=10, pady=10, bg="#2b2b2b")
    input_frame.pack(side=tk.TOP, pady=10)

    tk.Label(input_frame, text="Stock Symbol:", font=("Helvetica", 12), fg="white", bg="#2b2b2b").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    symbol_entry = tk.Entry(input_frame, font=("Helvetica", 12), width=10, bg="#444", fg="white", insertbackground="white")
    symbol_entry.grid(row=0, column=1, padx=5, pady=5)
    symbol_entry.insert(0, 'AAPL')
    
    tk.Label(input_frame, text="Starting Balance:", font=("Helvetica", 12), fg="white", bg="#2b2b2b").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    balance_entry = tk.Entry(input_frame, font=("Helvetica", 12), width=10, bg="#444", fg="white", insertbackground="white")
    balance_entry.grid(row=1, column=1, padx=5, pady=5)
    balance_entry.insert(0, "10000")

    tk.Label(input_frame, text="Timeframe:", font=("Helvetica", 12), fg="white", bg="#2b2b2b").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    timeframe_var = tk.StringVar(value='1y')
    timeframe_menu = ttk.Combobox(input_frame, textvariable=timeframe_var, font=("Helvetica", 12), width=8)
    timeframe_menu['values'] = ('1d', '5d', '1mo', '6mo', '1y', 'all time')
    timeframe_menu.grid(row=2, column=1, padx=5, pady=5)

    update_button = tk.Button(input_frame, text="Update Chart", command=update_chart, font=("Helvetica", 12), bg="lightblue", width=15)
    update_button.grid(row=3, column=0, columnspan=2, pady=10)

    input_frame.grid_columnconfigure(0, weight=1)
    input_frame.grid_columnconfigure(1, weight=1)

    latest_data_label = tk.Label(root, text="", font=("Helvetica", 16), fg="white", bg="#2b2b2b", justify="left")
    latest_data_label.pack(side=tk.TOP, anchor="w", padx=10, pady=0) 

    chart_frame = tk.Frame(root, padx=10, pady=10, bg="#2b2b2b")
    chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


    root.mainloop()