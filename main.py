import ccxt
import time
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

SYMBOL = "XBT/USD"          # Kraken uses XBT not BTC
LIVE_TRADING = False       # KEEP FALSE FIRST
STARTING_EQUITY = 1000

RISK_PER_TRADE = 0.01      # 1%
TAKE_PROFIT = 8            # dollars
STOP_LOSS = -4            # dollars

LOOP_DELAY = 5

# =====================================================
# EXCHANGE
# =====================================================

exchange = ccxt.kraken({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True
})

# =====================================================
# CONNECTION TEST
# =====================================================

def test_connection():
    print("Testing Kraken connection...")

    try:
        balance = exchange.fetch_balance()
        ticker = exchange.fetch_ticker(SYMBOL)

        print("CONNECTED SUCCESSFULLY")
        print("Live Price:", ticker["last"])
        print("Balance Available")

        return True

    except Exception as e:
        print("CONNECTION FAILED")
        print(e)
        return False

# =====================================================
# PRICE
# =====================================================

def get_price():
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        return ticker["last"]
    except Exception as e:
        print("Price Error:", e)
        return None

# =====================================================
# INDICATORS
# =====================================================

def ema(data, n):
    if len(data) < n:
        return sum(data) / len(data)

    k = 2 / (n + 1)
    value = data[0]

    for p in data[1:]:
        value = p * k + value * (1 - k)

    return value


def get_signal(history):
    if len(history) < 20:
        return 0

    short = ema(history[-5:], 5)
    long = ema(history[-20:], 20)

    if long == 0:
        return 0

    return (short - long) / long

# =====================================================
# LIVE EXECUTION
# =====================================================

def place_order(side, amount):

    if not LIVE_TRADING:
        print("PAPER MODE:", side, amount)
        return {"paper": True}

    try:
        order = exchange.create_market_order(
            SYMBOL,
            side.lower(),
            amount
        )

        print("LIVE ORDER EXECUTED:", order)
        return order

    except Exception as e:
        print("ORDER FAILED:", e)
        return None

# =====================================================
# CANCEL OPEN ORDERS
# =====================================================

def cancel_all_orders():

    if not LIVE_TRADING:
        print("PAPER MODE CANCEL")
        return

    try:
        orders = exchange.fetch_open_orders(SYMBOL)

        for order in orders:
            exchange.cancel_order(order["id"], SYMBOL)

        print("Open orders cancelled")

    except Exception as e:
        print("Cancel failed:", e)

# =====================================================
# POSITION STATE
# =====================================================

position = None
equity = STARTING_EQUITY
history = []

# =====================================================
# ENTRY
# =====================================================

def enter_trade(price, side):
    global position

    size = equity * RISK_PER_TRADE

    place_order(side, size)

    position = {
        "entry": price,
        "side": side,
        "size": size,
        "time": str(datetime.now())
    }

    print("ENTERED:", side, price)

# =====================================================
# EXIT
# =====================================================

def exit_trade(price):
    global position, equity

    if not position:
        return

    pnl = (
        price - position["entry"]
        if position["side"] == "BUY"
        else position["entry"] - price
    )

    reverse = "SELL" if position["side"] == "BUY" else "BUY"

    place_order(reverse, position["size"])

    equity += pnl

    print("EXIT:", reverse)
    print("PnL:", round(pnl, 2))
    print("Equity:", round(equity, 2))

    position = None

# =====================================================
# MAIN
# =====================================================

if not test_connection():
    raise SystemExit("Fix API issue first")

print("BOT RUNNING")

while True:

    price = get_price()

    if not price:
        time.sleep(LOOP_DELAY)
        continue

    history.append(price)
    history = history[-50:]

    signal = get_signal(history)

    print("\n====================")
    print("Time:", datetime.now())
    print("Price:", price)
    print("Signal:", round(signal, 5))
    print("Position:", position)
    print("Equity:", round(equity, 2))

    # ENTRY

    if not position:

        if signal > 0.001:
            enter_trade(price, "BUY")

        elif signal < -0.001:
            enter_trade(price, "SELL")

    # EXIT

    else:

        pnl = (
            price - position["entry"]
            if position["side"] == "BUY"
            else position["entry"] - price
        )

        if pnl >= TAKE_PROFIT:
            exit_trade(price)

        elif pnl <= STOP_LOSS:
            exit_trade(price)

    time.sleep(LOOP_DELAY)