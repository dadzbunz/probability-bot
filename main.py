print("=== CRYPTO BOT LIVE ===")

import requests
import random
from datetime import datetime

def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    data = requests.get(url, timeout=5).json()
    return data["bitcoin"]["usd"]

def get_signal(price):
    # simple normalization into 0–1 range
    return (price % 10000) / 10000

def decide(signal):
    if signal > 0.55:
        return "BUY"
    return "NO TRADE"

def run():
    price = get_btc_price()
    signal = get_signal(price)
    decision = decide(signal)

    print("\nTime:", datetime.now())
    print("BTC Price:", price)
    print("Signal:", round(signal, 4))
    print("Decision:", decision)

run()