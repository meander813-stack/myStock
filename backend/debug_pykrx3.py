# debug_pykrx3.py
from pykrx import stock
from datetime import datetime, timedelta

def get_date(days_back=0):
    d = datetime.now() - timedelta(days=days_back)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")

td = get_date(0)
pd = get_date(10)
print(f"조회 기간: {pd} ~ {td}\n")

# 1. 지수 ticker 목록 (market 파라미터 없이)
print("=== get_index_ticker_list (파라미터 없이) ===")
try:
    tickers = stock.get_index_ticker_list()
    print(f"티커 수: {len(tickers)}, 처음 5개: {tickers[:5]}")
    # 이름 확인
    for t in tickers[:5]:
        try:
            name = stock.get_index_ticker_name(t)
            print(f"  {t} → {name}")
        except:
            pass
except Exception as e:
    print(f"에러: {e}")

print()

# 2. KOSPI/KOSDAQ 이름으로 ticker 찾기
print("=== KOSPI ticker 찾기 ===")
try:
    for market in ["KOSPI", "KOSDAQ", None]:
        try:
            if market:
                tickers = stock.get_index_ticker_list(td, market=market)
            else:
                tickers = stock.get_index_ticker_list(td)
            print(f"market={market}: {tickers[:3]}")
            for t in tickers[:3]:
                name = stock.get_index_ticker_name(t)
                print(f"  {t} → {name}")
            break
        except Exception as e:
            print(f"market={market} 에러: {e}")
except Exception as e:
    print(f"전체 에러: {e}")

print()

# 3. 직접 숫자 코드 시도
print("=== 숫자 코드 직접 시도 ===")
for code in ["0001", "1001", "2001", "001", "101", "201"]:
    try:
        df = stock.get_index_ohlcv(pd, td, code)
        if not df.empty:
            print(f"코드 {code} 성공! 컬럼: {df.columns.tolist()}")
            print(df.tail(1))
    except Exception as e:
        print(f"코드 {code} 실패: {e}")
