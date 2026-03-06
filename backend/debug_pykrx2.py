# debug_pykrx2.py
from pykrx import stock
from datetime import datetime, timedelta

def get_date(days_back=0):
    d = datetime.now() - timedelta(days=days_back)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")

td = get_date(0)
pd = get_date(10)

print(f"조회 기간: {pd} ~ {td}")
print()

# 1. 지수 티커 목록 확인
print("=== 지수 티커 목록 ===")
try:
    tickers = stock.get_index_ticker_list(td)
    print(f"티커 수: {len(tickers)}")
    print(f"처음 10개: {tickers[:10]}")
except Exception as e:
    print(f"에러: {e}")

print()

# 2. KOSPI 티커 코드로 시도
print("=== KOSPI 티커 코드 1001 시도 ===")
try:
    df = stock.get_index_ohlcv(pd, td, "1001")
    print(f"컬럼: {df.columns.tolist()}")
    print(df.tail(2))
except Exception as e:
    print(f"에러: {e}")

print()

# 3. KOSDAQ 티커 코드 2001 시도
print("=== KOSDAQ 티커 코드 2001 시도 ===")
try:
    df = stock.get_index_ohlcv(pd, td, "2001")
    print(f"컬럼: {df.columns.tolist()}")
    print(df.tail(2))
except Exception as e:
    print(f"에러: {e}")

print()

# 4. 개별 종목 시세 확인 (삼성전자)
print("=== 삼성전자(005930) 시세 ===")
try:
    df = stock.get_market_ohlcv(pd, td, "005930")
    print(f"컬럼: {df.columns.tolist()}")
    print(df.tail(2))
except Exception as e:
    print(f"에러: {e}")
