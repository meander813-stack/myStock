# debug_ranking.py
from pykrx import stock
from datetime import datetime, timedelta

def get_today():
    now = datetime.now()
    if now.hour < 9:
        now -= timedelta(days=1)
    while now.weekday() >= 5:
        now -= timedelta(days=1)
    return now.strftime("%Y%m%d")

td = get_today()
pd_ = (datetime.strptime(td, "%Y%m%d") - timedelta(days=3)).strftime("%Y%m%d")
pd_week = (datetime.strptime(td, "%Y%m%d") - timedelta(days=7)).strftime("%Y%m%d")

print(f"오늘: {td}, 3일전: {pd_}, 7일전: {pd_week}\n")

# 1. price_change_by_ticker
print("=== get_market_price_change_by_ticker (3일) ===")
try:
    df = stock.get_market_price_change_by_ticker(pd_, td)
    print(f"행 수: {len(df)}")
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 2. KOSPI만
print("=== get_market_price_change_by_ticker (KOSPI) ===")
try:
    df = stock.get_market_price_change_by_ticker(pd_, td, "KOSPI")
    print(f"행 수: {len(df)}")
    print(f"컬럼: {df.columns.tolist()}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 3. trading_value_and_volume
print("=== get_market_trading_value_and_volume_by_ticker ===")
try:
    df = stock.get_market_trading_value_and_volume_by_ticker(td)
    print(f"행 수: {len(df)}")
    print(f"컬럼: {df.columns.tolist()}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 4. market_cap
print("=== get_market_cap_by_ticker ===")
try:
    df = stock.get_market_cap_by_ticker(td)
    print(f"행 수: {len(df)}")
    print(f"컬럼: {df.columns.tolist()}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")
