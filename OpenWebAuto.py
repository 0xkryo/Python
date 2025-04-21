import webbrowser
import time

# List of websites to open
websites = [
    "https://www.tradingview.com",
    "https://www.coinmarketcap.com",
    "https://x.com/lookonchain",
    "https://www.aggr.trade/0xkryo"
]

# Delay between each site (in seconds)
delay = 3  # Change this to whatever delay you want

def open_websites_sequentially(urls, delay_between):
    for url in urls:
        print(f"Opening: {url}")
        webbrowser.open(url)
        time.sleep(delay_between)

if __name__ == "__main__":
    open_websites_sequentially(websites, delay)
