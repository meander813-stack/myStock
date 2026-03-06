# debug_pykrx.py
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

# 지수 컬럼 확인
for name in ["KOSPI", "KOSDAQ", "KOSPI200"]:
    try:
        df = stock.get_index_ohlcv(pd, td, name)
        print(f"[{name}] 컬럼: {df.columns.tolist()}")
        print(f"[{name}] 마지막 행:\n{df.tail(2)}")
        print()
    except Exception as e:
        print(f"[{name}] 에러: {e}")
