# debug_market.py
from pykrx import stock
from datetime import datetime, timedelta

def get_today():
    now = datetime.now()
    if now.hour < 9:
        now -= timedelta(days=1)
    while now.weekday() >= 5:
        now -= timedelta(days=1)
    return now.strftime("%Y%m%d")

def get_prev(days=7):
    d = datetime.strptime(get_today(), "%Y%m%d") - timedelta(days=days)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")

td = get_today()
pd_ = get_prev()

print(f"오늘: {td}, 이전: {pd_}\n")

# 전체 종목 OHLCV
print("=== get_market_ohlcv (전체, 날짜 하나) ===")
try:
    df = stock.get_market_ohlcv(td, market="ALL")
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 날짜 범위로 전체
print("=== get_market_ohlcv (날짜범위, 전체) ===")
try:
    df = stock.get_market_ohlcv(pd_, td, market="ALL")
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 거래대금 상위 함수 따로 있는지 확인
print("=== get_market_ohlcv_by_ticker ===")
try:
    df = stock.get_market_ohlcv_by_ticker(td)
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")
