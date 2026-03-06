# debug_market2.py
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
pd_ = (datetime.strptime(td, "%Y%m%d") - timedelta(days=7)).strftime("%Y%m%d")

print(f"오늘: {td}\n")

# 1. 날짜 하나로 by_ticker
print("=== get_market_ohlcv_by_ticker(날짜) ===")
try:
    df = stock.get_market_ohlcv_by_ticker(td)
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 2. KOSPI만
print("=== get_market_ohlcv_by_ticker(날짜, KOSPI) ===")
try:
    df = stock.get_market_ohlcv_by_ticker(td, "KOSPI")
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.head(3))
except Exception as e:
    print(f"에러: {e}")

print()

# 3. 날짜범위 단일종목 컬럼 재확인
print("=== 삼성전자 단일종목 컬럼 ===")
try:
    df = stock.get_market_ohlcv(pd_, td, "005930")
    print(f"컬럼: {df.columns.tolist()}")
    print(f"인덱스명: {df.index.name}")
    print(df.tail(2))
except Exception as e:
    print(f"에러: {e}")

print()

# 4. pykrx stock 모듈 함수 목록
print("=== stock 모듈 함수 목록 (ohlcv 관련) ===")
funcs = [f for f in dir(stock) if 'ohlcv' in f.lower() or 'market' in f.lower()]
print(funcs)
