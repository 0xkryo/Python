import asyncio
import json
import websockets
import pandas as pd
import aiohttp
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
import datetime

# List of coins to monitor (binance symbols)
COINS = ['btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'adausdt', 'xrpusdt', 'dogeusdt', 'maticusdt', 'dotusdt', 'ltcusdt']

TRADE_ACTIVITY = {coin: {'buys': 0, 'sells': 0} for coin in COINS}
PRICE_HISTORY = {coin: [] for coin in COINS}  # Store candle closes

# Fetch historical data from CoinGecko
async def fetch_historical_prices(coin_id, session):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
    async with session.get(url) as resp:
        data = await resp.json()
        return [price[1] for price in data['prices']]

# Websocket connection to Binance
async def binance_ws():
    uri = f"wss://stream.binance.com:9443/stream?streams=" + '/'.join([f"{coin}@trade" for coin in COINS])
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            msg = json.loads(response)
            data = msg['data']
            symbol = data['s'].lower()
            quantity = float(data['q'])
            is_buyer_maker = data['m']

            if not is_buyer_maker:
                TRADE_ACTIVITY[symbol]['buys'] += quantity
            else:
                TRADE_ACTIVITY[symbol]['sells'] += quantity

# Refresh and plot every X seconds
async def plot_refresh():
    while True:
        await asyncio.sleep(60)  # Refresh every minute
        async with aiohttp.ClientSession() as session:
            for coin in COINS:
                # Mapping Binance symbol to CoinGecko id
                gecko_id = coin.replace('usdt', '')
                history = await fetch_historical_prices(gecko_id, session)
                PRICE_HISTORY[coin] = history

        draw_table()

def compute_rsi(prices, window):
    rsi = RSIIndicator(pd.Series(prices), window=window)
    return rsi.rsi().iloc[-1]

def draw_table():
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.axis('off')

    # Build the table data
    rows = []
    for coin in sorted(COINS, key=lambda c: TRADE_ACTIVITY[c]['buys'] + TRADE_ACTIVITY[c]['sells'], reverse=True):
        act_score = TRADE_ACTIVITY[coin]['buys'] + TRADE_ACTIVITY[coin]['sells']
        rsi_1h = compute_rsi(PRICE_HISTORY[coin], window=14)
        rsi_4h = compute_rsi(PRICE_HISTORY[coin][-4*14:], window=14)
        rsi_1d = compute_rsi(PRICE_HISTORY[coin][-24*14:], window=14)

        rows.append([coin.upper(), int(act_score), round(rsi_1h, 2), round(rsi_4h, 2), round(rsi_1d, 2)])

    df = pd.DataFrame(rows, columns=['Coin', 'Activity', 'RSI 1h', 'RSI 4h', 'RSI 1D'])

    # Break into 3 columns
    parts = [df.iloc[i::3] for i in range(3)]

    for idx, part in enumerate(parts):
        table = ax.table(cellText=part.values,
                         colLabels=part.columns,
                         cellLoc='center',
                         loc='center',
                         bbox=[0.01 + idx*0.32, 0.05, 0.3, 0.9])

        # Color cells based on RSI values
        for (i, j), cell in table.get_celld().items():
            if i == 0:  # Skip header
                cell.set_fontsize(12)
                continue

            if j in [2, 3, 4]:  # RSI columns
                val = part.iloc[i-1, j]
                if val < 30:
                    cell.set_facecolor('#006400')  # Dark Green
                elif 30 <= val < 50:
                    cell.set_facecolor('#32CD32')  # Light Green
                elif 50 <= val < 70:
                    cell.set_facecolor('#FFD700')  # Yellow
                else:
                    cell.set_facecolor('#FF6347')  # Red

    plt.title(f"Crypto Activity & RSI Heatmap - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
              fontsize=16)
    plt.tight_layout()
    plt.savefig('crypto_heatmap.png')
    plt.close()

async def main():
    await asyncio.gather(binance_ws(), plot_refresh())

if __name__ == "__main__":
    asyncio.run(main())
