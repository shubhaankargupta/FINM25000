import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import time

# Load your keys
API_KEY = 'API KEY'
SECRET_KEY = 'SECRET KEY'
BASE_URL = 'https://paper-api.alpaca.markets'


symbol      = 'JNJ'
window      = 20
z_entry     = 1.0
qty         = 10

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL)
account = api.get_account()
print(account.status, account.buying_power)



end   = datetime.today()
start = end - timedelta(days=60)

end_str   = end.strftime("%Y-%m-%d")
start_str = start.strftime("%Y-%m-%d")

jnj_df = api.get_bars("JNJ", TimeFrame.Day, start=start_str, end=end_str, feed="iex").df
print(jnj_df.tail())

jnj_df['mean'] = jnj_df['close'].rolling(window).mean()
jnj_df['std']  = jnj_df['close'].rolling(window).std()
jnj_df.dropna(inplace=True)


current = jnj_df.iloc[-1]

# Z-score
z = (current['close'] - current['mean']) / current['std']

print(f"close={current['close']:.2f}, mean={current['mean']:.2f}, std={current['std']:.2f}, z={z:.2f}")

try:
    pos = api.get_position(symbol)
    current_qty = int(pos.qty)
except Exception:
    current_qty = 0

if z < -z_entry and current_qty <= 0:
    print(f"BUY {qty} shares")
    api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')

elif z > z_entry and current_qty >= 0:
    print(f"SELL SHORT {qty} shares")
    api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')

elif abs(z) < 0.5 and current_qty != 0:
    side = 'sell' if current_qty > 0 else 'buy'
    print("Close position")
    api.submit_order(symbol=symbol, qty=abs(current_qty), side=side, type='market', time_in_force='gtc')
else:
    print("No trade action")

jnj_df.to_csv("jnj_bars.csv")
jnj_df = pd.read_csv("jnj_bars.csv", index_col=0)
